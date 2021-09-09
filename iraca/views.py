from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages import get_messages
from django.utils import timezone
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View


#------------------------------- SELECTION ----------------------------------------
from iraca import forms, models, models_instruments
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
                'sican_url': 'deliverables/',
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
                'sican_url': 'supports/',
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


class HouseholdListView(LoginRequiredMixin,
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
        return super(HouseholdListView,self).get_context_data(**kwargs)

class HouseholdCreateView(LoginRequiredMixin,
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
        return super(HouseholdCreateView,self).get_context_data(**kwargs)

class HouseholdUpdateView(LoginRequiredMixin,
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
        message = 'Se edito el hogar: {0}'.format(self.object.document)
        messages.add_message(self.request, messages.INFO, message)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "EDITAR HOGAR"
        return super(HouseholdUpdateView,self).get_context_data(**kwargs)


#----------------------------------------------------------------------------------

#------------------------------- deliverables -----------------------------------------

class DeliverablesOptionsView(LoginRequiredMixin,
                          MultiplePermissionsRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'iraca/deliverables/option.html'
    permissions = {
        "all": [
            "usuarios.iraca.ver"
            "usuarios.iraca.entregables.ver",
        ]
    }

    def dispatch(self, request, *args, **kwargs):
        items = self.get_items()
        if len(items) == 0:
            return redirect(self.login_url)
        return super(DeliverablesOptionsView, self).dispatch(request, *args, **kwargs)

    def get_items(self):
        items = []

        if self.request.user.has_perm('usuarios.iraca_2021.entregables.ver'):
            items.append({
                'sican_categoria': 'Implementacion',
                'sican_color': 'purple darken-4',
                'sican_order': 1,
                'sican_url': 'implementation/',
                'sican_name': 'Implementacion',
                'sican_icon': 'featured_play_list',
                'sican_description': 'Entregables del modulo de implementacion'
            })

        if self.request.user.has_perm('usuarios.iraca_2021.entregables.ver'):
            items.append({
                'sican_categoria': 'Formulacion',
                'sican_color': 'brown darken-4',
                'sican_order': 2,
                'sican_url': 'formulation/',
                'sican_name': 'Formulacion',
                'sican_icon': 'data_usage',
                'sican_description': 'Entregables del modulo de formulacion'
            })
        return items

    def get_context_data(self, **kwargs):
        kwargs['title'] = "ENTREGABLES"
        kwargs['items'] = self.get_items()
        return super(DeliverablesOptionsView,self).get_context_data(**kwargs)

class VisitsListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.entregables.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/deliverables/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Entregables: Momentos"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/deliverables/implementation/'
        kwargs['breadcrum_active'] = "Implementacion"
        return super(VisitsListView,self).get_context_data(**kwargs)

class InstrumentListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.entregables.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/deliverables/instruments/list.html'


    def get_context_data(self, **kwargs):
        moment = models.Moments.objects.get(id=self.kwargs['pk_momento'])
        kwargs['title'] = "Entregables: Instrumentos"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/deliverables/implementation/{0}/instruments/'.format(moment.id)
        kwargs['breadcrum_active'] = moment.name
        kwargs['breadcrum_1'] = "Formulacion"
        return super(InstrumentListView,self).get_context_data(**kwargs)

class FormulationVisitsListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.entregables.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/deliverables/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Entregables: Momentos"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/deliverables/formulation/'
        kwargs['breadcrum_active'] = "Formulacion"
        return super(FormulationVisitsListView,self).get_context_data(**kwargs)

class FormulationInstrumentListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.entregables.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/deliverables/instruments/list.html'


    def get_context_data(self, **kwargs):
        moment = models.Moments.objects.get(id=self.kwargs['pk_momento'])
        kwargs['title'] = "Entregables: Instrumentos"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/deliverables/formulation/{0}/instruments/'.format(moment.id)
        kwargs['breadcrum_active'] = moment.name
        kwargs['breadcrum_1'] = "Formulacion"
        return super(FormulationInstrumentListView,self).get_context_data(**kwargs)

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

#------------------------------- MILTONES -----------------------------------------



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

#----------------------------------------------------------------------------------

#---------------------------------------- RUTAS -----------------------------------

class ImplementationListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.implementacion.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/implementation/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Implementacion"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/implementation/'
        kwargs['permiso_crear'] = self.request.user.has_perm("usuarios.iraca.rutas.crear")
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ImplementationListView ,self).get_context_data(**kwargs)

class ImplementationCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/implementation/create.html'
    form_class = forms.implementationCreateForm
    success_url = "../"

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver",
                "usuarios.iraca.implementacion.crear"
            ]
        }
        return permissions

    def form_valid(self, form):


        self.object = models.Routes.objects.create(
            name=form.cleaned_data['name'],
            creation_user=self.request.user,
            user_update=self.request.user,
        )
        message = 'Se creó la ruta: {0}'.format(form.cleaned_data['name'])
        messages.add_message(self.request, messages.INFO, message)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVA RUTA"
        return super(ImplementationCreateView,self).get_context_data(**kwargs)

class ImplementationUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/implementation/edit.html'
    form_class = forms.implementationCreateForm
    success_url = "../../"

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver",
                "usuarios.iraca.implementacion.editar"
            ]
        }
        return permissions

    def form_valid(self, form):

        models.Routes.objects.filter(id = self.kwargs['pk']).update(
            name=form.cleaned_data['name'],
            visible=form.cleaned_data['visible'],
            goal=form.cleaned_data['goal']
        )

        message = 'Se actualizo la ruta: {0}'.format(form.cleaned_data['name'])
        messages.add_message(self.request, messages.INFO, message)

        models.Routes.objects.get(id=self.kwargs['pk']).update_novedades()
        models.Routes.objects.get(id=self.kwargs['pk']).update_progreso()
        models.Routes.objects.get(id=self.kwargs['pk']).update_progres_formulation()
        models.Routes.objects.get(id=self.kwargs['pk']).update_novelties_form()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        route = models.Routes.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "EDITAR RUTA"
        kwargs['route_name'] = route.name
        return super(ImplementationUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk':self.kwargs['pk']}

class ImplementationActivitiesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/implementation/activities/list.html'

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        routes = models.Routes.objects.get(id = kwargs['pk'])
        kwargs['title'] = "Actividades"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/implementation/activities/{0}/'.format(kwargs['pk'])
        kwargs['breadcrum_active'] = routes.name
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ImplementationActivitiesListView,self).get_context_data(**kwargs)

class ImplementationHouseholdsListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/implementation/activities/instruments/list.html'


    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver",
                "usuarios.iraca.implementacion.crear",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        kwargs['title'] = "ACTIVIDADES"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/implementation/activities/{0}/instruments/{1}/'.format(
            kwargs['pk'],
            kwargs['pk_moment'],
        )
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_active'] = self.moment.name
        kwargs['instruments'] = self.route.get_instruments_list(self.moment)
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ImplementationHouseholdsListView,self).get_context_data(**kwargs)

class ImplementationInstrumentsListView(CreateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'


    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument = models.Instruments.objects.get(id=self.kwargs['pk_instrument'])

        try:
            self.models = models_instruments.get_model(self.instrument.model)
        except:
            pass

        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver",
                "usuarios.iraca.implementacion.crear",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)

    def get_template_names(self):
        return self.models.get('template')


    def get_form_class(self):
        self.model = self.models.get('model')
        return self.models.get('form')


    def update_objet_instrument(self,id,model,creation):

        instrument = models.ObjectRouteInstrument.objects.get(id = id)

        if creation:
            models.ObjectRouteInstrument.objects.filter(id = id).update(
                creacion_user=self.request.user
            )

            models.InstrumentTraceabilityRouteObject.objects.create(
                instrument = instrument,
                user = self.request.user,
                observation = 'Creación del soporte'
            )

        else:
            models.InstrumentTraceabilityRouteObject.objects.create(
                instrument = instrument,
                user=self.request.user,
                observation='Actualización del soporte'
            )

        models.ObjectRouteInstrument.objects.filter(id=id).update(
            model = self.instrument.name,
            support = model.id,
            update_date = timezone.now(),
            update_user = self.request.user,
            consecutive = self.instrument.consecutive,
            name = self.instrument.short_name,
            estate = 'cargado'
        )

        self.route.update_novedades()

        return 'Ok'



    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.route = self.route
        self.object.instrument = self.instrument
        self.object.name = self.instrument.short_name
        self.object.save()

        self.object.households.clear()

        if self.instrument.level == 'individual':
            self.object.households.add(form.cleaned_data['households'])

        elif self.instrument.level == 'route':
            pass

        else:
            self.object.households.add(*form.cleaned_data['households'])


        object = models.ObjectRouteInstrument.objects.create(route=self.route, moment=self.moment, instrument=self.instrument)
        ids = self.object.households.all().values_list('id',flat = True)
        object.households.add(*ids)
        models.ObservationsInstrumentRouteObject.objects.create(instrument = object,user_creation = self.request.user,observation = "Creación del instrumento")

        self.update_objet_instrument(object.id, self.object, True)
        #objeto.clean_similares()


        return HttpResponseRedirect(self.get_success_url())


    def get_context_data(self, **kwargs):
        kwargs['title'] = "AGREGAR"
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_2'] = self.moment.name
        kwargs['breadcrum_active'] = self.instrument.short_name
        kwargs['ruta_breadcrum_1'] = 'Rutas'
        kwargs['url'] = 'Implementacion'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ImplementationInstrumentsListView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk': self.route.id, 'short_name': self.instrument.short_name, 'pk_instrument': self.instrument.pk}

class ImplementationInstrumentsObjectListView(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'


    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])
        self.instrument = self.instrument_object.instrument
        self.models = models_instruments.get_model(self.instrument.model)
        self.object = self.models.get('model').objects.get(id=self.instrument_object.support)


        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)

    def get_template_names(self):
        return self.models.get('template_view')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "VER"
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_2'] = self.moment.name
        kwargs['breadcrum_active'] = self.instrument.short_name
        kwargs['objeto'] = self.object
        kwargs['ruta_breadcrum'] = 'Implementacion'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ImplementationInstrumentsObjectListView,self).get_context_data(**kwargs)

class ImplementationHouseholdsObjectListView(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'
    template_name = 'iraca/implementation/activities/instruments/household/list.html'


    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])
        self.instrument = self.instrument_object.instrument

        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementation.ver",
            ]
        }

        return super(ImplementationHouseholdsObjectListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "HOGARES"
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_2'] = self.moment.name
        kwargs['breadcrum_active'] = self.instrument.short_name
        kwargs['ruta_breadcrum'] = 'Rutas'
        kwargs['households'] = self.instrument_object.households.all()
        kwargs['url_ruta_breadcrum'] = '/iraca_new/implementation/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ImplementationHouseholdsObjectListView,self).get_context_data(**kwargs)

class ImplementationTraceabilityObjectListView(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'
    template_name = 'iraca/implementation/activities/instruments/traceability/traceability.html'

    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])
        self.instrument = self.instrument_object.instrument
        self.models = models_instruments.get_model(self.instrument.model)
        self.object = self.models.get('model').objects.get(id=self.instrument_object.support)


        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementation.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "TRAZABILIDAD"
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_2'] = self.moment.name
        kwargs['breadcrum_active'] = self.instrument.short_name
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/implementation/activities/{0}/instruments/{1}/traceability/{2}/'.format(
            kwargs['pk'],
            kwargs['pk_moment'],
            kwargs['pk_instrument_object']
        )

        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ImplementationTraceabilityObjectListView,self).get_context_data(**kwargs)

class ImplementationUpdateObjectListView(UpdateView):
    login_url = settings.LOGIN_URL
    success_url = '../../'

    def get_object(self, queryset=None):
        self.model = self.models.get('model')
        return self.model.objects.get(id=self.instrument_object.support)

    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])
        self.instrument = self.instrument_object.instrument

        try:
            self.models = models_instruments.get_model(self.instrument.model)
        except:
            return HttpResponseRedirect('../../')

        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver"
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if self.instrument_object.estate in ['cargado', 'rechazado']:

                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_template_names(self):
        return self.models.get('template')

    def get_form_class(self):
        self.model = self.models.get('model')
        return self.models.get('form')

    def update_objet_instrument(self, id, model, creation):

        instrument = models.ObjectRouteInstrument.objects.get(id=id)

        if creation:
            models.ObjectRouteInstrument.objects.filter(id=id).update(
                creacion_user=self.request.user
            )

            models.InstrumentTraceabilityRouteObject.objects.create(
                instrument=instrument,
                user=self.request.user,
                observation='Creación del soporte'
            )

        else:
            models.InstrumentTraceabilityRouteObject.objects.create(
                instrument=instrument,
                user=self.request.user,
                observation='Actualización del soporte'
            )

        models.ObjectRouteInstrument.objects.filter(id=id).update(
            model=self.instrument.name,
            support=model.id,
            update_date=timezone.now(),
            update_user=self.request.user,
            consecutive=self.instrument.consecutive,
            name=self.instrument.short_name,
            estate='cargado'
        )

        self.route.update_novedades()

        return 'Ok'

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.route = self.route
        self.object.instrument = self.instrument
        self.object.name = self.instrument.short_name
        self.object.save()

        self.object.households.clear()
        if self.instrument.level == 'individual':
            self.object.households.add(form.cleaned_data['households'])

        elif self.instrument.level == 'ruta':
            pass

        else:
            self.object.households.add(*form.cleaned_data['households'])

        object = self.instrument_object

        ids = self.object.households.all().values_list('id', flat=True)
        object.households.clear()
        object.households.add(*ids)

        models.ObservationsInstrumentRouteObject.objects.create(instrument=object, user_creation=self.request.user,
                                                                 observation="Actualización del instrumento")

        self.update_objet_instrument(object.id, self.object, False)


        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "EDITAR"
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_2'] = self.moment.name
        kwargs['breadcrum_active'] = self.instrument.short_name
        kwargs['url'] = 'Implementacion'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ImplementationUpdateObjectListView, self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk': self.route.id, 'short_name': self.instrument.short_name,
                'pk_instrument': self.instrument.pk, 'pk_instrument_object': self.instrument_object.pk}

class ApproveInstrumentHouseholdView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.models = models_instruments.get_model(self.instrument_object.instrument.model)

        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver",
                "usuarios.iraca.implementacion.aprobar",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.is_superuser:
                self.instrument_object.estate = 'aprobado'
                models.InstrumentTraceabilityRouteObject.objects.create(
                    instrument=self.instrument_object,
                    user=self.request.user,
                    observation='Aprobación del soporte'
                )
                models.ObservationsInstrumentRouteObject.objects.create(
                    user_creation=self.request.user,
                    instrument=self.instrument_object,
                    observation="Soporte aprobado"
                )
                self.instrument_object.save()

                self.route.update_novedades()
                self.route.update_progreso()

                return HttpResponseRedirect('../../')
            elif request.user.has_perms(self.permissions.get('all')):
                self.instrument_object.estate = 'aprobado'
                models.InstrumentTraceabilityRouteObject.objects.create(
                    instrument=self.instrument_object,
                    user=self.request.user,
                    observation='Aprobación del soporte'
                )
                models.ObservationsInstrumentRouteObject.objects.create(
                    user_creation=self.request.user,
                    instrument=self.instrument_object,
                    observation="Soporte aprobado"
                )
                self.instrument_object.save()

                self.route.update_novedades()
                self.route.update_progreso()

                return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

class RejectInstrumentHouseholdView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/implementation/activities/instruments/reject.html'
    form_class = forms.InstrumentsRejectForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])

        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)

    def form_valid(self, form):

        if self.instrument != 'rechazado':
            self.instrument.estate = 'rechazado'
            models.InstrumentTraceabilityRouteObject.objects.create(
                instrument=self.instrument,
                user=self.request.user,
                observation=form.cleaned_data['observation']
            )
            models.ObservationsInstrumentRouteObject.objects.create(
                user_creation=self.request.user,
                instrument=self.instrument,
                observation=form.cleaned_data['observation']
            )
            self.instrument.save()
            self.route.update_novedades()

        return super(RejectInstrumentHouseholdView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_2'] = self.moment.name
        kwargs['breadcrum_active'] = self.instrument.instrument.short_name

        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RejectInstrumentHouseholdView, self).get_context_data(**kwargs)

class DeleteInstrumentHouseholdView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])
        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.models = models_instruments.get_model(self.instrument_object.instrument.model)

        self.permissions = {
            "eliminar": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver",
                "usuarios.iraca.implementacion.actividades.ver",
                "usuarios.iraca.implementacion.actividades.eliminar",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions['eliminar']):
                if self.instrument_object.estate == 'cargado' or self.instrument_object.estate == 'rechazado':
                    self.models.get('model').objects.get(id = self.instrument_object.support).delete()
                    models.InstrumentTraceabilityRouteObject.objects.filter(instrument = self.instrument_object).delete()
                    models.ObservationsInstrumentRouteObject.objects.filter(instrument = self.instrument_object).delete()
                    self.instrument_object.delete()
                    self.route.update_novedades()
                    return HttpResponseRedirect('../../')
                else:
                    return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

class ImplementationHouseholdListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/implementation/household/list.html'

    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])

        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver",
                "usuarios.iraca.implementacion.hogares.ver",
            ],
        }
        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ruta = models.Routes.objects.get(id = kwargs['pk'])
        kwargs['title'] = "HOGARES"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/implementation/household/{0}/'.format(kwargs['pk'])
        kwargs['breadcrum_active'] = ruta.name
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ImplementationHouseholdListView,self).get_context_data(**kwargs)

class ImplementationHouseholdView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/implementation/household/view.html'

    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.household = models.Households.objects.get(id=self.kwargs['pk_household'])

        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver",
                "usuarios.iraca.implementacion.hogares.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['hogar'] = self.household
        kwargs['title'] = "HOGAR"
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_active'] = self.household.document
        return super(ImplementationHouseholdView,self).get_context_data(**kwargs)

class FormulationListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.formulacion.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/formulation/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Formulacion"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/formulation/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(FormulationListView,self).get_context_data(**kwargs)

class FormulationActivitiesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/formulation/activities/list.html'

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.formulacion.ver",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        routes = models.Routes.objects.get(id = kwargs['pk'])
        kwargs['title'] = "Actividades"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/formulation/activities/{0}/'.format(kwargs['pk'])
        kwargs['breadcrum_active'] = routes.name
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(FormulationActivitiesListView,self).get_context_data(**kwargs)

class FormulationHouseholdsListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/formulation/activities/instruments/list.html'


    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.formulation.ver",
                "usuarios.iraca.formulation.crear",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        kwargs['title'] = "ACTIVIDADES"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/formulation/activities/{0}/instruments/{1}/'.format(
            kwargs['pk'],
            kwargs['pk_moment'],
        )
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_active'] = self.moment.name
        kwargs['instruments'] = self.route.get_instruments_list(self.moment)
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(FormulationHouseholdsListView,self).get_context_data(**kwargs)

class FormulationInstrumentsListView(CreateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'


    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument = models.Instruments.objects.get(id=self.kwargs['pk_instrument'])

        try:
            self.models = models_instruments.get_model(self.instrument.model)
        except:
            pass

        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.formulacion.ver",
                "usuarios.iraca.formulacion.crear",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)

    def get_template_names(self):
        return self.models.get('template')


    def get_form_class(self):
        self.model = self.models.get('model')
        return self.models.get('form')


    def update_objet_instrument(self,id,model,creation):

        instrument = models.ObjectRouteInstrument.objects.get(id = id)

        if creation:
            models.ObjectRouteInstrument.objects.filter(id = id).update(
                creacion_user=self.request.user
            )

            models.InstrumentTraceabilityRouteObject.objects.create(
                instrument = instrument,
                user = self.request.user,
                observation = 'Creación del soporte'
            )

        else:
            models.InstrumentTraceabilityRouteObject.objects.create(
                instrument = instrument,
                user=self.request.user,
                observation='Actualización del soporte'
            )

        models.ObjectRouteInstrument.objects.filter(id=id).update(
            model = self.instrument.name,
            support = model.id,
            update_date = timezone.now(),
            update_user = self.request.user,
            consecutive = self.instrument.consecutive,
            name = self.instrument.short_name,
            estate = 'cargado'
        )

        self.route.update_novelties_form()

        return 'Ok'



    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.route = self.route
        self.object.instrument = self.instrument
        self.object.name = self.instrument.short_name
        self.object.save()

        self.object.households.clear()

        if self.instrument.level == 'individual':
            self.object.households.add(form.cleaned_data['households'])

        elif self.instrument.level == 'route':
            pass

        else:
            self.object.households.add(*form.cleaned_data['households'])


        object = models.ObjectRouteInstrument.objects.create(route=self.route, moment=self.moment, instrument=self.instrument)
        ids = self.object.households.all().values_list('id',flat = True)
        object.households.add(*ids)
        models.ObservationsInstrumentRouteObject.objects.create(instrument = object,user_creation = self.request.user,observation = "Creación del instrumento")

        self.update_objet_instrument(object.id, self.object, True)
        #objeto.clean_similares()


        return HttpResponseRedirect(self.get_success_url())


    def get_context_data(self, **kwargs):
        kwargs['title'] = "AGREGAR"
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_2'] = self.moment.name
        kwargs['breadcrum_active'] = self.instrument.short_name
        kwargs['ruta_breadcrum_1'] = 'Rutas'
        kwargs['url'] = 'Formulacion'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(FormulationInstrumentsListView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk': self.route.id, 'short_name': self.instrument.short_name, 'pk_instrument': self.instrument.pk}

class FormulationInstrumentsObjectListView(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'


    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])
        self.instrument = self.instrument_object.instrument
        self.models = models_instruments.get_model(self.instrument.model)
        self.object = self.models.get('model').objects.get(id=self.instrument_object.support)


        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.formulacion.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)

    def get_template_names(self):
        return self.models.get('template_view')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "VER"
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_2'] = self.moment.name
        kwargs['breadcrum_active'] = self.instrument.short_name
        kwargs['objeto'] = self.object
        kwargs['ruta_breadcrum'] = 'Formulacion'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(FormulationInstrumentsObjectListView,self).get_context_data(**kwargs)

class FormulationHouseholdsObjectListView(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'
    template_name = 'iraca/formulation/activities/instruments/household/list.html'


    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])
        self.instrument = self.instrument_object.instrument

        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.formulacion.ver",
            ]
        }

        return super(FormulationHouseholdsObjectListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "HOGARES"
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_2'] = self.moment.name
        kwargs['breadcrum_active'] = self.instrument.short_name
        kwargs['households'] = self.instrument_object.households.all()
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(FormulationHouseholdsObjectListView,self).get_context_data(**kwargs)

class FormulationTraceabilityObjectListView(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'
    template_name = 'iraca/formulation/activities/instruments/traceability/traceability.html'

    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])
        self.instrument = self.instrument_object.instrument
        self.models = models_instruments.get_model(self.instrument.model)
        self.object = self.models.get('model').objects.get(id=self.instrument_object.support)


        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.formulacion.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "TRAZABILIDAD"
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_2'] = self.moment.name
        kwargs['breadcrum_active'] = self.instrument.short_name
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/formulation/activities/{0}/instruments/{1}/traceability/{2}/'.format(
            kwargs['pk'],
            kwargs['pk_moment'],
            kwargs['pk_instrument_object']
        )

        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(FormulationTraceabilityObjectListView,self).get_context_data(**kwargs)

class FormulationUpdateObjectListView(UpdateView):
    login_url = settings.LOGIN_URL
    success_url = '../../'

    def get_object(self, queryset=None):
        self.model = self.models.get('model')
        return self.model.objects.get(id=self.instrument_object.support)

    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])
        self.instrument = self.instrument_object.instrument

        try:
            self.models = models_instruments.get_model(self.instrument.model)
        except:
            return HttpResponseRedirect('../../')

        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.formulacion.ver"
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if self.instrument_object.estate in ['cargado', 'rechazado']:

                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_template_names(self):
        return self.models.get('template')

    def get_form_class(self):
        self.model = self.models.get('model')
        return self.models.get('form')

    def update_objet_instrument(self, id, model, creation):

        instrument = models.ObjectRouteInstrument.objects.get(id=id)

        if creation:
            models.ObjectRouteInstrument.objects.filter(id=id).update(
                creacion_user=self.request.user
            )

            models.InstrumentTraceabilityRouteObject.objects.create(
                instrument=instrument,
                user=self.request.user,
                observation='Creación del soporte'
            )

        else:
            models.InstrumentTraceabilityRouteObject.objects.create(
                instrument=instrument,
                user=self.request.user,
                observation='Actualización del soporte'
            )

        models.ObjectRouteInstrument.objects.filter(id=id).update(
            model=self.instrument.name,
            support=model.id,
            update_date=timezone.now(),
            update_user=self.request.user,
            consecutive=self.instrument.consecutive,
            name=self.instrument.short_name,
            estate='cargado'
        )

        self.route.update_novelties_form()

        return 'Ok'

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.route = self.route
        self.object.instrument = self.instrument
        self.object.name = self.instrument.short_name
        self.object.save()

        self.object.households.clear()
        if self.instrument.level == 'individual':
            self.object.households.add(form.cleaned_data['households'])

        elif self.instrument.level == 'ruta':
            pass

        else:
            self.object.households.add(*form.cleaned_data['households'])

        object = self.instrument_object

        ids = self.object.households.all().values_list('id', flat=True)
        object.households.clear()
        object.households.add(*ids)

        models.ObservationsInstrumentRouteObject.objects.create(instrument=object, user_creation=self.request.user,
                                                                 observation="Actualización del instrumento")

        self.update_objet_instrument(object.id, self.object, False)


        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "EDITAR"
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_2'] = self.moment.name
        kwargs['breadcrum_active'] = self.instrument.short_name
        kwargs['url'] = 'Formulacion'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(FormulationUpdateObjectListView, self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk': self.route.id, 'short_name': self.instrument.short_name,
                'pk_instrument': self.instrument.pk, 'pk_instrument_object': self.instrument_object.pk}

class FormulationApproveInstrumentHouseholdView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.models = models_instruments.get_model(self.instrument_object.instrument.model)

        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.formulacion.ver",
                "usuarios.iraca.formulacion.aprobar",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.is_superuser:
                self.instrument_object.estate = 'aprobado'
                models.InstrumentTraceabilityRouteObject.objects.create(
                    instrument=self.instrument_object,
                    user=self.request.user,
                    observation='Aprobación del soporte'
                )
                models.ObservationsInstrumentRouteObject.objects.create(
                    user_creation=self.request.user,
                    instrument=self.instrument_object,
                    observation="Soporte aprobado"
                )
                self.instrument_object.save()

                self.route.update_novelties_form()
                self.route.update_progres_formulation()

                return HttpResponseRedirect('../../')
            elif request.user.has_perms(self.permissions.get('all')):
                self.instrument_object.estate = 'aprobado'
                models.InstrumentTraceabilityRouteObject.objects.create(
                    instrument=self.instrument_object,
                    user=self.request.user,
                    observation='Aprobación del soporte'
                )
                models.ObservationsInstrumentRouteObject.objects.create(
                    user_creation=self.request.user,
                    instrument=self.instrument_object,
                    observation="Soporte aprobado"
                )
                self.instrument_object.save()

                self.route.update_novelties_form()
                self.route.update_progres_formulation()

                return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

class FormulationRejectInstrumentHouseholdView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/formulation/activities/instruments/reject.html'
    form_class = forms.InstrumentsRejectForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])

        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.formulacion.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)

    def form_valid(self, form):

        if self.instrument != 'rechazado':
            self.instrument.estate = 'rechazado'
            models.InstrumentTraceabilityRouteObject.objects.create(
                instrument=self.instrument,
                user=self.request.user,
                observation=form.cleaned_data['observation']
            )
            models.ObservationsInstrumentRouteObject.objects.create(
                user_creation=self.request.user,
                instrument=self.instrument,
                observation=form.cleaned_data['observation']
            )
            self.instrument.save()
            self.route.update_novelties_form()

        return super(FormulationRejectInstrumentHouseholdView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_2'] = self.moment.name
        kwargs['breadcrum_active'] = self.instrument.instrument.short_name

        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(FormulationRejectInstrumentHouseholdView, self).get_context_data(**kwargs)

class FormulationDeleteInstrumentHouseholdView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])
        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.models = models_instruments.get_model(self.instrument_object.instrument.model)

        self.permissions = {
            "eliminar": [
                "usuarios.iraca.ver",
                "usuarios.iraca.formulacion.ver",
                "usuarios.iraca.formulacion.actividades.ver",
                "usuarios.iraca.formulacion.actividades.eliminar",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions['eliminar']):
                if self.instrument_object.estate == 'cargado' or self.instrument_object.estate == 'rechazado':
                    self.models.get('model').objects.get(id = self.instrument_object.support).delete()
                    models.InstrumentTraceabilityRouteObject.objects.filter(instrument = self.instrument_object).delete()
                    models.ObservationsInstrumentRouteObject.objects.filter(instrument = self.instrument_object).delete()
                    self.instrument_object.delete()
                    self.route.update_novedades()
                    return HttpResponseRedirect('../../')
                else:
                    return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

class FormulationHouseholdListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/formulation/household/list.html'


    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])

        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.formulacion.ver",
                "usuarios.iraca.formulacion.hogares.ver",
            ],
        }
        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        ruta = models.Routes.objects.get(id = kwargs['pk'])
        kwargs['title'] = "HOGARES"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/formulation/household/{0}/'.format(kwargs['pk'])
        kwargs['breadcrum_active'] = ruta.name
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(FormulationHouseholdListView,self).get_context_data(**kwargs)

class FormulationtionHouseholdView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/formulation/household/view.html'

    def dispatch(self, request, *args, **kwargs):

        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.household = models.Households.objects.get(id=self.kwargs['pk_household'])

        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver",
                "usuarios.iraca.implementacion.hogares.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        kwargs['hogar'] = self.household
        kwargs['title'] = "HOGAR"
        kwargs['breadcrum_1'] = self.route.name
        kwargs['breadcrum_active'] = self.household.document
        return super(FormulationtionHouseholdView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#------------------------------------- SUPPORTS -----------------------------------

class SupportsOptionsView(LoginRequiredMixin,
                          MultiplePermissionsRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'iraca/support/options.html'
    permissions = {
        "all": [
            "usuarios.iraca.ver"
            "usuarios.iraca.soportes.ver",
        ]
    }

    def dispatch(self, request, *args, **kwargs):
        items = self.get_items()
        if len(items) == 0:
            return redirect(self.login_url)
        return super(SupportsOptionsView, self).dispatch(request, *args, **kwargs)

    def get_items(self):
        items = []

        if self.request.user.has_perm('usuarios.iraca.soportes.ver'):
            items.append({
                'sican_categoria': 'Implementacion',
                'sican_color': 'purple darken-4',
                'sican_order': 1,
                'sican_url': 'implementation/',
                'sican_name': 'Implementacion',
                'sican_icon': 'featured_play_list',
                'sican_description': 'Soportes del modulo de implementacion'
            })

        if self.request.user.has_perm('usuarios.iraca.soportes.ver'):
            items.append({
                'sican_categoria': 'Formulacion',
                'sican_color': 'brown darken-4',
                'sican_order': 2,
                'sican_url': 'formulation/',
                'sican_name': 'Formulacion',
                'sican_icon': 'data_usage',
                'sican_description': 'Soportes del modulo de formulacion'
            })
        return items

    def get_context_data(self, **kwargs):
        kwargs['title'] = "SOPORTES"
        kwargs['items'] = self.get_items()
        return super(SupportsOptionsView,self).get_context_data(**kwargs)

class SupportsHouseholdsImplementationListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.soportes.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/support/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "HOGARES"
        kwargs['breadcrum_active'] = "Implementacion"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/supports/implementation/'
        return super(SupportsHouseholdsImplementationListView,self).get_context_data(**kwargs)

class SupportsHouseholdsImplementationMomentsListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.soportes.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/support/moments/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "MOMENTOS"
        kwargs['breadcrum_active'] = models.Households.objects.get(id = kwargs['pk_household']).document
        kwargs['breadcrum_1'] = "Implementacion"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/supports/implementation/{0}/'.format(kwargs['pk_household'])
        return super(SupportsHouseholdsImplementationMomentsListView,self).get_context_data(**kwargs)

class SupportImplementationHouseholdMomentsListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.soportes.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/support/moments/instruments/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "INSTRUMENTOS"
        kwargs['breadcrum_2'] = models.Households.objects.get(id=kwargs['pk_household']).document
        kwargs['breadcrum_active'] = models.Moments.objects.get(id = kwargs['pk_moment']).name
        kwargs['breadcrum_1'] = "Implementacion"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/supports/implementation/{0}/instrument/{1}/'.format(
            kwargs['pk_household'],
            kwargs['pk_moment']
        )
        return super(SupportImplementationHouseholdMomentsListView,self).get_context_data(**kwargs)

class SupportHouseholdInstrumentsView(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'


    def dispatch(self, request, *args, **kwargs):

        self.household = models.Households.objects.get(id=self.kwargs['pk_household'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])

        self.models = models_instruments.get_model(self.instrument_object.instrument.model)
        self.object = self.models.get('model').objects.get(id=self.instrument_object.support)


        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.soportes.ver",
            ]
        }

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
                return HttpResponseRedirect('../../')

    def get_template_names(self):
        return self.models.get('template_support')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_2'] = self.household.document
        kwargs['breadcrum_1'] = "Implementacion"
        kwargs['breadcrum_3'] = self.moment.name
        kwargs['breadcrum_active'] = self.instrument_object.instrument.short_name
        kwargs['objeto'] = self.object
        kwargs['ruta_breadcrum'] = 'Soportes'
        kwargs['url_ruta_breadcrum'] = '/iraca_new/supports/implementation/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(SupportHouseholdInstrumentsView,self).get_context_data(**kwargs)

class SupportsHouseholdsFormulationListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.soportes.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/support/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "HOGARES"
        kwargs['breadcrum_active'] = "Implementacion"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/supports/formulation/'
        return super(SupportsHouseholdsFormulationListView,self).get_context_data(**kwargs)

class SupportsHouseholdsFormulationMomentsListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.soportes.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/support/moments/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "MOMENTOS"
        kwargs['breadcrum_active'] = models.Households.objects.get(id = kwargs['pk_household']).document
        kwargs['breadcrum_1'] = "Implementacion"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/supports/formulation/{0}/'.format(kwargs['pk_household'])
        return super(SupportsHouseholdsFormulationMomentsListView,self).get_context_data(**kwargs)

class SupportFormulationHouseholdMomentsListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.soportes.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/support/moments/instruments/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "INSTRUMENTOS"
        kwargs['breadcrum_2'] = models.Households.objects.get(id=kwargs['pk_household']).document
        kwargs['breadcrum_active'] = models.Moments.objects.get(id = kwargs['pk_moment']).name
        kwargs['breadcrum_1'] = "Implementacion"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/supports/formulation/{0}/instrument/{1}/'.format(
            kwargs['pk_household'],
            kwargs['pk_moment']
        )
        return super(SupportFormulationHouseholdMomentsListView,self).get_context_data(**kwargs)

class FormulationSupportHouseholdInstrumentsView(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'


    def dispatch(self, request, *args, **kwargs):

        self.household = models.Households.objects.get(id=self.kwargs['pk_household'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])

        self.models = models_instruments.get_model(self.instrument_object.instrument.model)
        self.object = self.models.get('model').objects.get(id=self.instrument_object.support)


        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.soportes.ver",
            ]
        }

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
                return HttpResponseRedirect('../../')

    def get_template_names(self):
        return self.models.get('template_support')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_2'] = self.household.document
        kwargs['breadcrum_1'] = "Implementacion"
        kwargs['breadcrum_3'] = self.moment.name
        kwargs['breadcrum_active'] = self.instrument_object.instrument.short_name
        kwargs['objeto'] = self.object
        kwargs['ruta_breadcrum'] = 'Soportes'
        kwargs['url_ruta_breadcrum'] = '/iraca_new/supports/formulation/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(FormulationSupportHouseholdInstrumentsView,self).get_context_data(**kwargs)


