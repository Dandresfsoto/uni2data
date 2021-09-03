from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages import get_messages

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

        if self.request.user.has_perm('usuarios.iraca_2021.bd.ver'):
            items.append({
                'sican_categoria': 'Base de datos',
                'sican_color': 'red darken-4',
                'sican_order': 1,
                'sican_url': 'bd/',
                'sican_name': 'Base de datos',
                'sican_icon': 'data_usage',
                'sican_description': 'Información general de los hogares atendidos en la intervención.'
            })

        if self.request.user.has_perm('usuarios.iraca_2021.entregables.ver'):
            items.append({
                'sican_categoria': 'Entregables',
                'sican_color': 'orange darken-4',
                'sican_order': 2,
                'sican_url': 'entregables/',
                'sican_name': 'Entregables',
                'sican_icon': 'view_list',
                'sican_description': 'Estructura de entregables por cada uno de los componentes.'
            })

        if self.request.user.has_perm('usuarios.iraca.actas.ver'):
            items.append({
                'sican_categoria': 'Actas',
                'sican_color': 'brown darken-4',
                'sican_order': 3,
                'sican_url': 'certificate/',
                'sican_name': 'Actas',
                'sican_icon': 'assignment',
                'sican_description': 'Actas diligenciadas para el proyecto Iraca 2021'
            })

        if self.request.user.has_perm('usuarios.iraca.socializacion.ver'):
            items.append({
                'sican_categoria': 'Socializacion y concertacion',
                'sican_color': 'green darken-4',
                'sican_order': 4,
                'sican_url': 'socialization/',
                'sican_name': 'Socializacion',
                'sican_icon': 'assignment_ind',
                'sican_description': 'Actas de socializacion y concertacion para el proyecto Iraca 2021'
            })

        if self.request.user.has_perm('usuarios.iraca.vinculacion.ver'):
            items.append({
                'sican_categoria': 'Vinculacion y caracterizacion',
                'sican_color': 'blue darken-4',
                'sican_order': 5,
                'sican_url': 'bonding/',
                'sican_name': 'Vinculacion',
                'sican_icon': 'people',
                'sican_description': 'Informacion de Vinculacion y caracterizacion proyecto Iraca 2021'
            })

        if self.request.user.has_perm('usuarios.iraca.formulacion.ver'):
            items.append({
                'sican_categoria': 'Formulacion y convalidacion',
                'sican_color': 'orange darken-4',
                'sican_order': 6,
                'sican_url': 'formulation/',
                'sican_name': 'Formulacion',
                'sican_icon': 'pie_chart',
                'sican_description': 'Informacion de Formulacion y convalidacion proyecto Iraca 2021'
            })

        if self.request.user.has_perm('usuarios.iraca.implementacion.ver'):
            items.append({
                'sican_categoria': 'Implementacion',
                'sican_color': 'purple darken-4',
                'sican_order': 7,
                'sican_url': 'implementation/',
                'sican_name': 'Implementacion',
                'sican_icon': 'work',
                'sican_description': 'Informacion de implementacion del proyecto Iraca 2021'
            })

        if self.request.user.has_perm('usuarios.iraca.soportes.ver'):
            items.append({
                'sican_categoria': 'Soportes',
                'sican_color': 'pink darken-4',
                'sican_order': 8,
                'sican_url': 'soportes/',
                'sican_name': 'Soportes',
                'sican_icon': 'apps',
                'sican_description': 'Modulo de soportes'
            })
            if self.request.user.has_perm('usuarios.iraca.informes.ver'):
                items.append({
                    'sican_categoria': 'Informes',
                    'sican_color': 'cyan darken-4',
                    'sican_order': 9,
                    'sican_url': 'informes/',
                    'sican_name': 'Informes',
                    'sican_icon': 'poll',
                    'sican_description': 'Modulo de Informes'
                })

        return items

    def get_context_data(self, **kwargs):
        kwargs['title'] = "IRACA"
        kwargs['items'] = self.get_items()
        return super(IracaOptionsView,self).get_context_data(**kwargs)


#----------------------------------------------------------------------------------

#------------------------------- BD -----------------------------------------------


class HogaresListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.db.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/bd/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "BASE DE DATOS HOGARES"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/bd/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.iraca.db.crear')
        return super(HogaresListView,self).get_context_data(**kwargs)

class HogaresCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/bd/create.html'
    form_class = forms.HogarCreateForm
    success_url = "../"
    models = models.Households

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.iraca_2021.ver",
                "usuarios.iraca_2021.db.ver",
                "usuarios.iraca_2021.db.crear"
            ]
        }
        return permissions

    def form_valid(self, form):
        self.object = form.save()
        message = 'Se creó el hogar: {0}'.format(form.cleaned_data['document'])
        messages.add_message(self.request, messages.INFO, message)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVO HOGAR"
        return super(HogaresCreateView,self).get_context_data(**kwargs)

class HogaresUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/bd/edit.html'
    form_class = forms.HogarCreateForm
    success_url = "../../"
    model = models.Households

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.db.ver",
                "usuarios.iraca.db.editar"
            ]
        }
        return permissions

    def get_initial(self):
        return {'pk':self.kwargs['pk']}

    def form_valid(self, form):
        self.object = form.save()
        message = 'Se edito el hogar: {0}'.format(self.object.documento)
        messages.add_message(self.request, messages.INFO, message)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "EDITAR HOGAR"
        return super(HogaresUpdateView,self).get_context_data(**kwargs)




#----------------------------------------------------------------------------------

#------------------------------- CERTIFICATES -------------------------------------


class CerticateOptionsView(TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/list.html'

    def get_items(self):
        items = []

        for certificate in Certificates.objects.all().filter(code=1).order_by('name'):
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

#------------------------------- MEEETINGS ----------------------------------------


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

    def get_initial(self):
        return {
            'pk': self.kwargs['pk'],
        }

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
        kwargs['title'] = "ACTAS DE {0}".format(meeting.municipality.nombre)
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

class MilestonesEstateUpdateView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      UpdateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.iraca.actas.ver",
            "usuarios.iraca.actas.contactos.ver",
            "usuarios.iraca.actas.contactos.crear",
            "usuarios.iraca.actas.contactos.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/miltones/estate.html'
    pk_url_kwarg = 'pk_milestone'
    success_url = '../../'
    form_class = forms.MiltonesEstateForm
    model = models.Milestones


    def get_context_data(self, **kwargs):
        meeting = models.Meetings.objects.get(id=self.kwargs['pk_meeting'])
        certificate = models.Certificates.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "ACTAS"
        kwargs['breadcrum_active'] = str(meeting.municipality.nombre)
        kwargs['milestone'] = models.Milestones.objects.get(id = self.kwargs['pk_milestone'])
        kwargs['breadcrum_1'] = certificate.name
        kwargs['breadcrum_2'] = "Hitos de {0}".format(meeting.municipality.nombre)
        return super(MilestonesEstateUpdateView,self).get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save()

        return super().form_valid(form)


#----------------------------------------------------------------------------------

#------------------------------- SOCIALIZATION ------------------------------------



class SocializationOptionsView(TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'iraca/socialization/list.html'

    def get_items(self):
        items = []

        for certificate in Certificates.objects.all().filter(code=2).order_by('name'):
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
        kwargs['title'] = "ACTAS DE SOCIALIZACION Y CONCERTACION"
        kwargs['items'] = self.get_items()
        return super(SocializationOptionsView,self).get_context_data(**kwargs)


#----------------------------------------------------------------------------------

#------------------------------- SOCIALIZATION MEEETINGS --------------------------


class SocializationListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.iraca.socializacion.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/socialization/municipalities.html'


    def get_context_data(self, **kwargs):
        certificate = Certificates.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = str(certificate.name).upper()
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/certificate/{0}/'.format(certificate.id)
        kwargs['breadcrum_1'] = certificate.name
        return super(SocializationListView,self).get_context_data(**kwargs)


class SocializationCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.iraca.socializacion.ver",
            "usuarios.iraca.socializacion.crear",

        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/socialization/create.html'
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
        return super(SocializationCreateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk': self.kwargs['pk'],
        }


#----------------------------------------------------------------------------------

#------------------------------- MILTONES -------------------------------------



class SocializationMiltoneslistView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.iraca.socializacion.ver",
            "usuarios.iraca.socializacion.hitos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/socialization/milestones/list.html'


    def get_context_data(self, **kwargs):
        certificate = models.Certificates.objects.get(id=self.kwargs['pk'])
        meeting = models.Meetings.objects.get(id=self.kwargs['pk_meeting'])
        kwargs['title'] = "ACTAS DE SOCIALIZACION DE {0}".format(meeting.municipality.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/certificate/{0}/milestones/{1}/'.format(certificate.id,meeting.id)
        kwargs['breadcrum_1'] = certificate.name
        return super(SocializationMiltoneslistView,self).get_context_data(**kwargs)

class SocializationMiltonescreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.iraca.socializacion.ver",
            "usuarios.iraca.socializacion.hitos.ver",
            "usuarios.iraca.socializacion.hitos.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/socialization/milestones/create.html'
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
        kwargs['title'] = "AÑADIR ACTA DE SOCIALIZACION"
        kwargs['breadcrum_2'] = str(meeting.municipality)
        kwargs['file_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['file2_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['file3_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['breadcrum_1'] = str(certificate.name)
        return super(SocializationMiltonescreateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk':self.kwargs['pk'],
            'pk_meeting':self.kwargs['pk_meeting'],
        }

class SocializationMilestonesUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.iraca.socializacion.ver",
            "usuarios.iraca.socializacion.hitos.ver",
            "usuarios.iraca.socializacion.hitos.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/socialization/milestones/edit.html'
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
        kwargs['title'] = "EDITAR ACTA DE SOCIALIZACION"
        kwargs['breadcrum_2'] = str(meeting.municipality)
        kwargs['breadcrum_1'] = str(certificate.name)
        kwargs['file_url'] = milestone.pretty_print_url_file()
        kwargs['file2_url'] = milestone.pretty_print_url_file2()
        kwargs['file3_url'] = milestone.pretty_print_url_file3()
        return super(SocializationMilestonesUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk': self.kwargs['pk'],
            'pk_meeting': self.kwargs['pk_meeting'],
            'pk_milestone': self.kwargs['pk_milestone'],
        }

class SocializationMilestonesView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.iraca.socializacion.ver",
            "usuarios.iraca.socializacion.hitos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/certificate/miltones/view.html'


    def get_context_data(self, **kwargs):
        meeting = models.Meetings.objects.get(id=self.kwargs['pk_meeting'])
        certificate = models.Certificates.objects.get(id=self.kwargs['pk'])
        milestone = models.Milestones.objects.get(id=self.kwargs['pk_milestone'])
        kwargs['title'] = "VER ACTAS DE SOCIALIZACION"
        kwargs['breadcrum_1'] = certificate.name
        kwargs['breadcrum_2'] = meeting.municipality.nombre
        kwargs['milestone'] = models.Milestones.objects.get(id=self.kwargs['pk_milestone'])
        return super(SocializationMilestonesView,self).get_context_data(**kwargs)

class SocializationMilestonesDeleteView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):
    permissions = {
        "all": [
            "usuarios.iraca.socializacion.ver",
            "usuarios.iraca.socializacion.hitos.ver",
            "usuarios.iraca.socializacion.hitos.eliminar",
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):
        milestone = models.Milestones.objects.get(id = self.kwargs['pk_milestone'])

        if milestone.estate == 'Esperando aprobación':

            milestone.delete()

        return HttpResponseRedirect('../../')

class SocializationMilestonesEstateUpdateView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      UpdateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.iraca.socializacion.ver",
            "usuarios.iraca.socializacion.contactos.ver",
            "usuarios.iraca.socializacion.contactos.crear",
            "usuarios.iraca.sociali zacion.contactos.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/socialization/milestones/estate.html'
    pk_url_kwarg = 'pk_milestone'
    success_url = '../../'
    form_class = forms.MiltonesEstateForm
    model = models.Milestones


    def get_context_data(self, **kwargs):
        meeting = models.Meetings.objects.get(id=self.kwargs['pk_meeting'])
        certificate = models.Certificates.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "ACTAS"
        kwargs['breadcrum_active'] = str(meeting.municipality.nombre)
        kwargs['milestone'] = models.Milestones.objects.get(id = self.kwargs['pk_milestone'])
        kwargs['breadcrum_1'] = certificate.name
        kwargs['breadcrum_2'] = "Hitos de {0}".format(meeting.municipality.nombre)
        return super(SocializationMilestonesEstateUpdateView,self).get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save()

        return super().form_valid(form)


#----------------------------------------------------------------------------------

#------------------------------- CONTACTS SOCIALIZATION----------------------------


class SocializationContactslistView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.iraca.socializacion.ver",
            "usuarios.iraca.socializacion.contactos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/socialization/contacts/list.html'


    def get_context_data(self, **kwargs):
        certificate = models.Certificates.objects.get(id = self.kwargs['pk'])
        meeting = models.Meetings.objects.get(id = self.kwargs['pk_meeting'])
        kwargs['title'] = "CONTACTOS"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/certificate/{0}/contacts/{1}/'.format(certificate.id,meeting.id)
        kwargs['breadcrum_1'] = certificate.name
        kwargs['breadcrum_active'] = meeting.municipality.nombre
        return super(SocializationContactslistView,self).get_context_data(**kwargs)

class SocializationContactsCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.iraca.socializacion.ver",
            "usuarios.iraca.socializacion.contactos.ver",
            "usuarios.iraca.socializacion.contactos.crear",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/socialization/contacts/create.html'
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
        return super(SocializationContactsCreateView,self).get_context_data(**kwargs)

class SocializationContactsUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.iraca.socializacion.ver",
            "usuarios.iraca.socializacion.contactos.ver",
            "usuarios.iraca.socializacion.contactos.crear",
            "usuarios.iraca.socializacion.contactos.editar",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/socialization/contacts/edit.html'
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
        return super(SocializationContactsUpdateView,self).get_context_data(**kwargs)


