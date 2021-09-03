from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View


#------------------------------- SELECTION ----------------------------------------
from iraca import forms, models
from iraca.models import Certificates
from usuarios.models import Municipios


class IracaOptionsView(LoginRequiredMixin,
                          MultiplePermissionsRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'iraca/list.html'
    permissions = {
        "all": [
            "usuarios.iraca.ver"
        ]
    }

    def dispatch(self, request, *args, **kwargs):
        items = self.get_items()
        if len(items) == 0:
            return redirect(self.login_url)
        return super(IracaOptionsView, self).dispatch(request, *args, **kwargs)

    def get_items(self):
        items = []

        if self.request.user.has_perm('usuarios.iraca.actas.ver'):
            items.append({
                'sican_categoria': 'Actas',
                'sican_color': 'brown darken-4',
                'sican_order': 1,
                'sican_url': 'certificate/',
                'sican_name': 'Actas',
                'sican_icon': 'assignment',
                'sican_description': 'Actas diligenciadas para el proyecto Iraca 2021'
            })

        if self.request.user.has_perm('usuarios.iraca.socializacion.ver'):
            items.append({
                'sican_categoria': 'Socializacion y concertacion',
                'sican_color': 'green darken-4',
                'sican_order': 2,
                'sican_url': 'socialization/',
                'sican_name': 'Socializacion',
                'sican_icon': 'assignment_ind',
                'sican_description': 'Actas de socializacion y concertacion para el proyecto Iraca 2021'
            })

        if self.request.user.has_perm('usuarios.iraca.vinculacion.ver'):
            items.append({
                'sican_categoria': 'Vinculacion y caracterizacion',
                'sican_color': 'blue darken-4',
                'sican_order': 3,
                'sican_url': 'bonding/',
                'sican_name': 'Vinculacion',
                'sican_icon': 'people',
                'sican_description': 'Informacion de Vinculacion y caracterizacion proyecto Iraca 2021'
            })

        if self.request.user.has_perm('usuarios.iraca.formulacion.ver'):
            items.append({
                'sican_categoria': 'Formulacion y convalidacion',
                'sican_color': 'orange darken-4',
                'sican_order': 4,
                'sican_url': 'formulation/',
                'sican_name': 'Formulacion',
                'sican_icon': 'pie_chart',
                'sican_description': 'Informacion de Formulacion y convalidacion proyecto Iraca 2021'
            })

        if self.request.user.has_perm('usuarios.iraca.implementacion.ver'):
            items.append({
                'sican_categoria': 'Implementacion',
                'sican_color': 'purple darken-4',
                'sican_order': 5,
                'sican_url': 'implementation/',
                'sican_name': 'Implementacion',
                'sican_icon': 'work',
                'sican_description': 'Informacion de implementacion del proyecto Iraca 2021'
            })

        return items

    def get_context_data(self, **kwargs):
        kwargs['title'] = "IRACA"
        kwargs['items'] = self.get_items()
        return super(IracaOptionsView,self).get_context_data(**kwargs)



#----------------------------------------------------------------------------------

#------------------------------- CERTIFICATES -------------------------------------


class CerticateOptionsView(TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/list.html'

    def get_items(self):
        items = []

        for certificate in Certificates.objects.all().order_by('code'):
            if self.request.user.has_perm('usuarios.certificate.ver'):
                items.append({
                    'sican_categoria': '{0}'.format(certificate.name),
                    'sican_color': certificate.color,
                    'sican_order': certificate.code,
                    'sican_url': '{0}/'.format(str(certificate.id)),
                    'sican_name': '{0}'.format(certificate.name),
                    'sican_description': 'Actas de {0}.'.format(certificate.name).lower()
                })


        return items

    def dispatch(self, request, *args, **kwargs):

        self.permissions = {
            "all": [
                "usuarios.actas.ver",
            ]
        }

        items = self.get_items()
        if len(items) == 0:
            return HttpResponseRedirect('../')

        else:
            if not request.user.is_authenticated:
                return HttpResponseRedirect(self.login_url)
            else:
                if request.user.has_perms(self.permissions.get('all')):
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTAS"
        kwargs['items'] = self.get_items()
        return super(CerticateOptionsView,self).get_context_data(**kwargs)



#----------------------------------------------------------------------------------

#------------------------------- MEEETINGS -------------------------------------


class CerticateListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.iraca.actas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/municipalities.html'


    def get_context_data(self, **kwargs):
        certificate = Certificates.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = str(certificate.name).upper()
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/certificate/{0}/'.format(certificate.id)
        kwargs['breadcrum_1'] = certificate.name
        return super(CerticateListView,self).get_context_data(**kwargs)


class CerticateCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.iraca.actas.ver",
            "usuarios.iraca.actas.crear",

        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/create.html'
    form_class = forms.CertificateForm
    success_url = "../"

    def form_valid(self, form):
        certificate = Certificates.objects.get(id=self.kwargs['pk'])
        municipality = Municipios.objects.get(id = str(form.cleaned_data['municipality']))

        models.Meetings.objects.create(
            creation_user = self.request.user,
            user_update = self.request.user,
            municipality = municipality,
            certificate = certificate
        )

        #self.object = form.save(commit=False)

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        certificate = Certificates.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "NUEVA GESTIÓN"
        kwargs['breadcrum_1'] = certificate.name
        kwargs['url_autocomplete_municipality'] = '/rest/v1.0/iraca_new/certificate/autocomplete/municipios/'
        return super(CerticateCreateView,self).get_context_data(**kwargs)


#----------------------------------------------------------------------------------

#------------------------------- MILTONES -------------------------------------



class MiltoneslistView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.iraca.actas.ver",
            "usuarios.iraca.actas.hitos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/miltones/list.html'


    def get_context_data(self, **kwargs):
        certificate = models.Certificates.objects.get(id=self.kwargs['pk'])
        meeting = models.Meetings.objects.get(id=self.kwargs['pk_meeting'])
        kwargs['title'] = "ACTAS DE {0} DE {1}".format(certificate.name,meeting.municipality.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/certificate/{0}/milestones/{1}/'.format(certificate.id,meeting.id)
        kwargs['breadcrum_1'] = certificate.name
        return super(MiltoneslistView,self).get_context_data(**kwargs)

class MiltonescreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.iraca.actas.ver",
            "usuarios.iraca.actas.hitos.ver",
            "usuarios.iraca.actas.hitos.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/miltones/create.html'
    form_class = forms.MiltonesForm
    success_url = "../"

    def form_valid(self, form):

        type = form.cleaned_data['type']
        date = form.cleaned_data['date']
        file = form.cleaned_data['file']
        file2 = form.cleaned_data['file2']
        file3 = form.cleaned_data['file3']
        foto_1 = form.cleaned_data['foto_1']
        foto_2 = form.cleaned_data['foto_2']
        foto_3 = form.cleaned_data['foto_3']
        foto_4 = form.cleaned_data['foto_4']

        miltone = models.Milestones.objects.create(
            meeting=models.Meetings.objects.get(id=self.kwargs['pk_meeting']),
            type = type,
            file = file,
            file2 = file2,
            file3 = file3,
            date = date,
            foto_1 = foto_1,
            foto_2 = foto_2,
            foto_3 = foto_3,
            foto_4 = foto_4,
        )


        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        meeting = models.Meetings.objects.get(id=self.kwargs['pk_meeting'])
        certificate = models.Certificates.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "AÑADIR ACTA"
        kwargs['breadcrum_2'] = str(meeting.municipality)
        kwargs['file_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['file2_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['file3_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['breadcrum_1'] = str(certificate.name)
        return super(MiltonescreateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk':self.kwargs['pk'],
            'pk_meeting':self.kwargs['pk_meeting'],
        }

class MilestonesUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.iraca.actas.ver",
            "usuarios.iraca.actas.hitos.ver",
            "usuarios.iraca.actas.hitos.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/miltones/edit.html'
    form_class = forms.MiltonesForm
    success_url = "../../"


    def form_valid(self, form):

        type = form.cleaned_data['type']
        date = form.cleaned_data['date']
        observation = form.cleaned_data['observation']
        file = form.cleaned_data['file']
        file2 = form.cleaned_data['file2']
        file3 = form.cleaned_data['file3']
        foto_1 = form.cleaned_data['foto_1']
        foto_2 = form.cleaned_data['foto_2']
        foto_3 = form.cleaned_data['foto_3']
        foto_4 = form.cleaned_data['foto_4']

        milestone = models.Milestones.objects.get(id=self.kwargs['pk_milestone'])
        #registro = models.Registro.objects.filter(hito=hito)

        milestone.type = type
        milestone.date = date
        milestone.observation = observation

        if file != None:
            milestone.file = file

        if file2 != None:
            milestone.file2 = file2

        if file3 != None:
            milestone.file3 = file3

        if foto_1 != None:
            milestone.foto_1 = foto_1

        if foto_2 != None:
            milestone.foto_2 = foto_2

        if foto_3 != None:
            milestone.foto_3 = foto_3

        if foto_4 != None:
            milestone.foto_4 = foto_4

        milestone.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        meeting = models.Meetings.objects.get(id=self.kwargs['pk_meeting'])
        certificate = models.Certificates.objects.get(id=self.kwargs['pk'])
        milestone = models.Milestones.objects.get(id=self.kwargs['pk_milestone'])
        kwargs['title'] = "EDITAR ACTA"
        kwargs['breadcrum_2'] = str(meeting.municipality)
        kwargs['breadcrum_1'] = str(certificate.name)
        kwargs['file_url'] = milestone.pretty_print_url_file()
        kwargs['file2_url'] = milestone.pretty_print_url_file2()
        kwargs['file3_url'] = milestone.pretty_print_url_file3()
        return super(MilestonesUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk': self.kwargs['pk'],
            'pk_meeting': self.kwargs['pk_meeting'],
            'pk_milestone': self.kwargs['pk_milestone'],
        }

class MilestonesView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.iraca.actas.ver",
            "usuarios.iraca.actas.hitos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/miltones/view.html'


    def get_context_data(self, **kwargs):
        meeting = models.Meetings.objects.get(id=self.kwargs['pk_meeting'])
        certificate = models.Certificates.objects.get(id=self.kwargs['pk'])
        milestone = models.Milestones.objects.get(id=self.kwargs['pk_milestone'])
        kwargs['title'] = "VER ACTAS"
        kwargs['breadcrum_1'] = certificate.name
        kwargs['breadcrum_2'] = meeting.municipality.nombre
        kwargs['milestone'] = models.Milestones.objects.get(id=self.kwargs['pk_milestone'])
        return super(MilestonesView,self).get_context_data(**kwargs)


class MilestonesDeleteView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):
    permissions = {
        "all": [
            "usuarios.iraca.actas.ver",
            "usuarios.iraca.actas.hitos.ver",
            "usuarios.iraca.actas.hitos.eliminar",
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):
        milestone = models.Milestones.objects.get(id = self.kwargs['pk_milestone'])

        if milestone.estate == 'Esperando aprobación':

            milestone.delete()

        return HttpResponseRedirect('../../')


#----------------------------------------------------------------------------------

#------------------------------- CONTACTS -----------------------------------------


class ContactslistView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.iraca.actas.ver",
            "usuarios.iraca.actas.contactos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/contacts/list.html'


    def get_context_data(self, **kwargs):
        certificate = models.Certificates.objects.get(id = self.kwargs['pk'])
        meeting = models.Meetings.objects.get(id = self.kwargs['pk_meeting'])
        kwargs['title'] = "CONTACTOS"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/certificate/{0}/contacts/{1}/'.format(certificate.id,meeting.id)
        kwargs['breadcrum_1'] = certificate.name
        kwargs['breadcrum_active'] = meeting.municipality.nombre
        return super(ContactslistView,self).get_context_data(**kwargs)

class ContactsCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.iraca.actas.ver",
            "usuarios.iraca.actas.contactos.ver",
            "usuarios.iraca.actas.contactos.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/contacts/create.html'
    form_class = forms.ContactForm
    success_url = "../"
    model = models.Contacts

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.meting = models.Meetings.objects.get(id=self.kwargs['pk_meeting'])
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        certificate = models.Certificates.objects.get(id=self.kwargs['pk'])
        meeting = models.Meetings.objects.get(id=self.kwargs['pk_meeting'])
        kwargs['title'] = "NUEVO CONTACTO"
        kwargs['breadcrum_1'] = certificate.name
        kwargs['breadcrum_2'] = meeting.municipality.nombre
        return super(ContactsCreateView,self).get_context_data(**kwargs)

class ContactsUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.iraca.actas.ver",
            "usuarios.iraca.actas.contactos.ver",
            "usuarios.iraca.actas.contactos.crear",
            "usuarios.iraca.actas.contactos.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/contacts/edit.html'
    form_class = forms.ContactForm
    success_url = "../../"
    model = models.Contacts
    pk_url_kwarg = 'pk_contact'


    def form_valid(self, form):

        self.object = form.save()

        return HttpResponseRedirect(self.get_success_url())



    def get_context_data(self, **kwargs):
        certificate = models.Certificates.objects.get(id=self.kwargs['pk'])
        meeting = models.Meetings.objects.get(id=self.kwargs['pk_meeting'])
        kwargs['title'] = "EDITAR CONTACTO"
        kwargs['breadcrum_2'] = meeting.municipality.nombre
        kwargs['breadcrum_1'] = certificate.name
        return super(ContactsUpdateView,self).get_context_data(**kwargs)
