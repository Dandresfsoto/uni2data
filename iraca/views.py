import io
import json

import pdfkit
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.contrib.messages import get_messages
from django.core.files import File
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View

from config.settings.base import DEFAULT_FROM_EMAIL, EMAIL_HOST_USER
from delta import html
# ------------------------------- SELECTION ----------------------------------------
from iraca import forms, models, models_instruments, tasks
from iraca.models import Certificates
from mis_contratos import functions
from mobile.models import FormMobile
from recursos_humanos import models as rh_models
from reportes.models import Reportes
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

        if self.request.user.has_perm('usuarios.iraca.bd.ver'):
            items.append({
                'sican_categoria': 'Base de datos',
                'sican_color': 'red darken-4',
                'sican_order': 1,
                'sican_url': 'bd/',
                'sican_name': 'Base de datos',
                'sican_icon': 'data_usage',
                'sican_description': 'Información general de los hogares atendidos en la intervención.'
            })

        if self.request.user.has_perm('usuarios.iraca.entregables.ver'):
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

        if self.request.user.has_perm('usuarios.iraca.resguardos.ver'):
            items.append({
                'sican_categoria': 'Resguardos',
                'sican_color': 'teal darken-4',
                'sican_order': 8,
                'sican_url': 'resguard/',
                'sican_name': 'Resguardo',
                'sican_icon': 'people_outline',
                'sican_description': 'Modulo de Resguardos indigenas'
            })

        if self.request.user.has_perm('usuarios.iraca.informes.ver'):
            items.append({
                'sican_categoria': 'Informe de actividades',
                'sican_color': 'grey darken-4',
                'sican_order': 8,
                'sican_url': 'inform/',
                'sican_name': 'Informe de actividades',
                'sican_icon': 'assignment',
                'sican_description': 'Informes de actividades cargadas'
            })

        if self.request.user.has_perm('usuarios.iraca.liquidaciones.ver'):
            items.append({
                'sican_categoria': 'liquidaciones',
                'sican_color': 'red darken-4',
                'sican_order': 9,
                'sican_url': 'liquidaciones/',
                'sican_name': 'Liquidaciones',
                'sican_icon': 'account_balance',
                'sican_description': 'Informes de actividades y liquidaciones'
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
                "usuarios.iraca.ver",
                "usuarios.iraca.db.ver",
                "usuarios.iraca.db.crear"
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

        if self.request.user.has_perm('usuarios.iraca.entregables.ver'):
            items.append({
                'sican_categoria': 'Implementacion',
                'sican_color': 'purple darken-4',
                'sican_order': 1,
                'sican_url': 'implementation/',
                'sican_name': 'Implementacion',
                'sican_icon': 'featured_play_list',
                'sican_description': 'Entregables del modulo de implementacion'
            })

        if self.request.user.has_perm('usuarios.iraca.entregables.ver'):
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
        moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        kwargs['title'] = "Entregables: Instrumentos"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/deliverables/implementation/{0}/instruments/'.format(moment.id)
        kwargs['breadcrum_active'] = moment.name
        kwargs['breadcrum_1'] = "Formulacion"
        return super(InstrumentListView,self).get_context_data(**kwargs)

class ImplementationControlPanel(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.entregables.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:

            if request.user.has_perms(self.permissions['ver']):
                reporte = Reportes.objects.create(
                    usuario=self.request.user,
                    nombre=f'Tablero de Control de Implementacion Iraca 2021',
                    consecutivo=Reportes.objects.filter(usuario=self.request.user).count() + 1
                )
                #colocar delay
                tasks.build_control_panel_Implementation.delay(reporte.id)
                return redirect('/reportes/')
            else:
                return HttpResponseRedirect('../../')

class ImplementationInstrumentReport(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.instrument = models.Instruments.objects.get(id=self.kwargs['pk_instrument'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])

        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.entregables.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:

            if request.user.has_perms(self.permissions['ver']):
                reporte = Reportes.objects.create(
                    usuario=self.request.user,
                    nombre='Instrumento: {0} - Momento: {1} - Implementacion'.format(self.instrument.name,self.moment.name),
                    consecutivo=Reportes.objects.filter(usuario=self.request.user).count() + 1
                )

                tasks.build_report_instrument.delay(reporte.id, self.instrument.id)
                return redirect('/reportes/')
            else:
                return HttpResponseRedirect('../../')

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

class FormulationControlPanel(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.entregables.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:

            if request.user.has_perms(self.permissions['ver']):
                reporte = Reportes.objects.create(
                    usuario=self.request.user,
                    nombre=f'Tablero de Control de Formulacion Iraca 2021',
                    consecutivo=Reportes.objects.filter(usuario=self.request.user).count() + 1
                )
                #colocar delay
                tasks.build_control_panel_Formulation.delay(reporte.id)
                return redirect('/reportes/')
            else:
                return HttpResponseRedirect('../../')

class FormulationInstrumentReport(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.instrument = models.Instruments.objects.get(id=self.kwargs['pk_instrument'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])

        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.entregables.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:

            if request.user.has_perms(self.permissions['ver']):
                reporte = Reportes.objects.create(
                    usuario=self.request.user,
                    nombre='Instrumento: {0} - Momento: {1} - Formulacion'.format(self.instrument.name,self.moment.name),
                    consecutivo=Reportes.objects.filter(usuario=self.request.user).count() + 1
                )

                tasks.build_report_instrument.delay(reporte.id, self.instrument.id)
                return redirect('/reportes/')
            else:
                return HttpResponseRedirect('../../')

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
            "usuarios.iraca.socializacion.hitos.ver",
            "usuarios.iraca.socializacion.hitos.crear",
            "usuarios.iraca.socializacion.hitos.editar",
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

#-------------------------------- IMPLEMENTACION -----------------------------------

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
            resguard=form.cleaned_data['resguard'],
            name=form.cleaned_data['name'],
            creation_user=self.request.user,
            user_update=self.request.user,
        )
        message = 'Se creó la ruta: {0}'.format(form.cleaned_data['name'])
        messages.add_message(self.request, messages.INFO, message)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVA RUTA"
        kwargs['url_resguard'] = '/rest/v1.0/iraca_new/implementation/autocomplete/resguard/'
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
            resguard=form.cleaned_data['resguard'],
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
        kwargs['url_resguard'] = '/rest/v1.0/iraca_new/implementation/autocomplete/resguard/'
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

#----------------------------------------------------------------------------------

#-------------------------------- FORMULACION -------------------------------------

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

#----------------------------------------------------------------------------------

#------------------------------------- BONDING ------------------------------------


class HouseholdsListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.vinculacion.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/bonding/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "BASE DE DATOS HOGARES"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/bonding/'
        return super(HouseholdsListView,self).get_context_data(**kwargs)

class BondingListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.vinculacion.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/bonding/polls/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "BASE DE DATOS DE VINCULACION"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/bonding/{0}/'.format(kwargs['pk_household'])
        kwargs['breadcrum_1'] = models.Households.objects.get(id=kwargs['pk_household']).document
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.iraca.vinculacion.crear')
        return super(BondingListView,self).get_context_data(**kwargs)

class BondingView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.vinculaciones.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/bonding/polls/view.html'

    def estate(self):
        mobile = FormMobile.objects.get(id=self.kwargs['pk_mobile'])
        json_code = mobile.data
        data_disponibility = json_code["PP-22"]
        diccionario = dict(enumerate(data_disponibility))
        return diccionario

    def products_add(self):
        mobile = FormMobile.objects.get(id=self.kwargs['pk_mobile'])
        json_code = mobile.data
        data_disponibility = json_code["PP-23"]
        diccionario = dict(enumerate(data_disponibility))
        return diccionario

    def products_register(self):
        mobile = FormMobile.objects.get(id=self.kwargs['pk_mobile'])
        json_code = mobile.data
        data_disponibility = json_code["PP-24"]
        diccionario = dict(enumerate(data_disponibility))
        return diccionario

    def products_quantity(self):
        mobile = FormMobile.objects.get(id=self.kwargs['pk_mobile'])
        json_code = mobile.data
        data_disponibility = json_code["PP-26"]
        diccionario = dict(enumerate(data_disponibility))
        return diccionario

    def products_market(self):
        mobile = FormMobile.objects.get(id=self.kwargs['pk_mobile'])
        json_code = mobile.data
        data_disponibility = json_code["PP-30"]
        diccionario = dict(enumerate(data_disponibility))
        return diccionario

    def products_market_medium(self):
        mobile = FormMobile.objects.get(id=self.kwargs['pk_mobile'])
        json_code = mobile.data
        data_disponibility = json_code["PP-31"]
        diccionario = dict(enumerate(data_disponibility))
        return diccionario

    def products_support(self):
        mobile = FormMobile.objects.get(id=self.kwargs['pk_mobile'])
        json_code = mobile.data
        data_disponibility = json_code["PP-31"]
        diccionario = dict(enumerate(data_disponibility))
        return diccionario

    def products_support_strengthen(self):
        mobile = FormMobile.objects.get(id=self.kwargs['pk_mobile'])
        json_code = mobile.data
        data_disponibility = json_code["PP-41"]
        diccionario = dict(enumerate(data_disponibility))
        return diccionario

    def financial_instruments(self):
        mobile = FormMobile.objects.get(id=self.kwargs['pk_mobile'])
        json_code = mobile.data
        data_disponibility = json_code["IEF-2"]
        diccionario = dict(enumerate(data_disponibility))
        return diccionario

    def self_consumption(self):
        mobile = FormMobile.objects.get(id=self.kwargs['pk_mobile'])
        json_code = mobile.data
        data_disponibility = json_code["AU-2"]
        diccionario = dict(enumerate(data_disponibility))
        return diccionario

    def fertilizer(self):
        mobile = FormMobile.objects.get(id=self.kwargs['pk_mobile'])
        json_code = mobile.data
        data_disponibility = json_code["AU-8"]
        diccionario = dict(enumerate(data_disponibility))
        return diccionario

    def surplus(self):
        mobile = FormMobile.objects.get(id=self.kwargs['pk_mobile'])
        json_code = mobile.data
        data_disponibility = json_code["AU-18"]
        diccionario = dict(enumerate(data_disponibility))
        return diccionario

    def foodsafety(self):
        mobile = FormMobile.objects.get(id=self.kwargs['pk_mobile'])
        json_code = mobile.data
        data_disponibility = json_code["SA-1"]
        diccionario = dict(enumerate(data_disponibility))
        return diccionario

    def affectations(self):
        mobile = FormMobile.objects.get(id=self.kwargs['pk_mobile'])
        json_code = mobile.data
        data_disponibility = json_code["MC-1"]
        diccionario = dict(enumerate(data_disponibility))
        return diccionario

    def electricity(self):
        mobile = FormMobile.objects.get(id=self.kwargs['pk_mobile'])
        json_code = mobile.data
        data_disponibility = json_code["MC-2"]
        diccionario = dict(enumerate(data_disponibility))
        return diccionario


    def get_context_data(self, **kwargs):
        mobile = FormMobile.objects.get(id = kwargs['pk_mobile'])
        kwargs['title'] = "VER CARACTERIZACION"
        kwargs['breadcrum_1'] = models.Households.objects.get(id=kwargs['pk_household']).document
        kwargs['objeto'] = mobile.data
        kwargs['earth'] = mobile.json_read_earth()
        kwargs['water'] = mobile.json_read_water()
        kwargs['boss'] = mobile.json_read_members_boss()
        kwargs['estate'] = self.estate()
        kwargs['products_add'] = self.products_add()
        kwargs['products_register'] = self.products_register()
        kwargs['products_quantity'] = self.products_quantity()
        kwargs['products_market'] = self.products_market()
        kwargs['products_support'] = self.products_support()
        kwargs['products_support_strengthen'] = self.products_support_strengthen()
        kwargs['financial_instruments'] = self.financial_instruments()
        kwargs['consumption'] = self.self_consumption()
        kwargs['fertilizer'] = self.fertilizer()
        kwargs['surplus'] = self.surplus()
        kwargs['foodsafety'] = self.foodsafety()
        kwargs['affectations'] = self.affectations()
        kwargs['electricity'] = self.electricity()
        return super(BondingView,self).get_context_data(**kwargs)


class BondingDeleteView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.mobile = models.FormMobile.objects.get(id=self.kwargs['pk_mobile'])

        self.permissions = {
            "eliminar": [
                "usuarios.iraca.ver",
                "usuarios.iraca.vinculacion.ver",
                "usuarios.iraca.vinculacion.editar",
                "usuarios.iraca.vinculacion.eliminar",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions['eliminar']):
                self.mobile.delete()
                return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')


class HouseholdsReportView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.vinculacion.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:

            if request.user.has_perms(self.permissions['ver']):
                reporte = Reportes.objects.create(
                    usuario=self.request.user,
                    nombre=f'Reportes de vinculacion Iraca 2021',
                    consecutivo=Reportes.objects.filter(usuario=self.request.user).count() + 1
                )
                #colocar delay
                tasks.build_bonding_report.delay(reporte.id)
                return redirect('/reportes/')
            else:
                return HttpResponseRedirect('../../')

class HouseholdsReportTotalView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.vinculacion.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:

            if request.user.has_perms(self.permissions['ver']):
                reporte = Reportes.objects.create(
                    usuario=self.request.user,
                    nombre=f'Reportes de vinculaciones aplicacion uni2data',
                    consecutivo=Reportes.objects.filter(usuario=self.request.user).count() + 1
                )
                #colocar delay
                tasks.build_bonding_total_report.delay(reporte.id)
                return redirect('/reportes/')
            else:
                return HttpResponseRedirect('../../')


#----------------------------------------------------------------------------------

#------------------------------------- RESGUARD ------------------------------------



class ResguardListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.resguardos.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/resguard/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "RESGUARDOS"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/resguard/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.iraca.resguardo.crear')
        return super(ResguardListView,self).get_context_data(**kwargs)

class ResguardCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/resguard/create.html'
    form_class = forms.ResguardCreateForm
    success_url = "../"
    models = models.Resguards

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.resguardo.ver",
                "usuarios.iraca.resguardo.crear"
            ]
        }
        return permissions

    def form_valid(self, form):
        self.object = form.save()
        message = 'Se creó la comunidad: {0}'.format(form.cleaned_data['name'])
        messages.add_message(self.request, messages.INFO, message)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVA COMUNIDAD"
        return super(ResguardCreateView,self).get_context_data(**kwargs)

class ResguardUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/resguard/edit.html'
    form_class = forms.ResguardCreateForm
    success_url = "../../"
    model = models.Resguards

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.resguardo.ver",
                "usuarios.iraca.resguardo.editar"
            ]
        }
        return permissions

    def get_initial(self):
        return {'pk':self.kwargs['pk']}

    def form_valid(self, form):
        self.object = form.save()
        message = 'Se edito la comunidad: {0}'.format(form.cleaned_data['name'])
        messages.add_message(self.request, messages.INFO, message)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "EDITAR COMUNIDAD"
        return super(ResguardUpdateView,self).get_context_data(**kwargs)

#---------------------------------------------------------------------------------

#------------------------------------- INFORMS -----------------------------------


class InformListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.informes.ver"
        ],
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/inform/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "CORTES"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/inform/'
        return super(InformListView,self).get_context_data(**kwargs)


class InformCollectsAccountListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.informes.ver",
        ],
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/inform/collect_account/list.html'


    def get_context_data(self, **kwargs):
        cut = rh_models.Cuts.objects.get(id=self.kwargs['pk_cut'])
        kwargs['title'] = "CORTE {0}".format(cut.consecutive)
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/inform/view/{0}/'.format(cut.id)
        kwargs['breadcrum_active'] = cut.consecutive
        return super(InformCollectsAccountListView,self).get_context_data(**kwargs)

class InformCollectsAccountAprobListView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.collect_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])


        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.informes.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if request.user.is_superuser:
                    self.collect_account.estate_inform = 'Aprobado'
                    self.collect_account.save()
                    collect_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])
                    rh_models.Registration.objects.create(
                        cut=collect_account.cut,
                        user=self.request.user,
                        collect_account=collect_account,
                        delta="Informe de actividades aprobado"
                    )

                    return HttpResponseRedirect('../../')
                else:
                    if request.user.has_perms(self.permissions.get('all')):
                        self.collect_account.estate_inform = 'Aprobado'
                        self.collect_account.save()
                        collect_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])
                        rh_models.Registration.objects.create(
                            cut=collect_account.cut,
                            user=self.request.user,
                            collect_account=collect_account,
                            delta="Informe de actividades aprobado"
                        )
                        return HttpResponseRedirect('../../')
                    else:
                        return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

class InformCollectsAccountRejectListView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'iraca/inform/collect_account/reject.html'
    form_class = forms.CollectsAccountInformsRejectForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        self.collect_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])

        self.permissions = {
            "all": [
                "usuarios.iraca.informes.ver",
                "usuarios.iraca.informes.cortes.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if request.user.is_superuser:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def form_valid(self, form):

        collect_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])

        if collect_account.estate_inform != 'Rechazado':
            collect_account.estate_inform = 'Rechazado'
            collect_account.observaciones_inform = form.cleaned_data['observaciones_inform']
            collect_account.save()

            user = collect_account.contract.get_user_or_none()

            if user != None:
                tasks.send_mail_templated_cuenta_cobro(
                    'mail/recursos_humanos/reject_ia.tpl',
                    {
                        'url_base': 'https://' + self.request.META['HTTP_HOST'],
                        'Contrato': collect_account.contract.nombre,
                        'nombre': collect_account.contract.contratista.nombres,
                        'nombre_completo': collect_account.contract.contratista.get_full_name(),
                        'valor': '$ {:20,.2f}'.format(collect_account.value_fees.amount),
                        'observaciones': collect_account.observaciones_inform,
                    },
                    DEFAULT_FROM_EMAIL,
                    [user.email, EMAIL_HOST_USER, settings.EMAIL_DIRECCION_FINANCIERA, settings.EMAIL_GERENCIA]
                )

        collect_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])
        rh_models.Registration.objects.create(
            cut=collect_account.cut,
            user=self.request.user,
            collect_account=collect_account,
            delta="Informe de actividades rechazado por: " + collect_account.observaciones_inform
        )

        return super(InformCollectsAccountRejectListView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        cuts = rh_models.Cuts.objects.get(id=self.kwargs['pk_cut'])
        kwargs['title'] = "Rechazar Informe de actividades"
        kwargs['breadcrum_1'] = cuts.consecutive


        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(InformCollectsAccountRejectListView, self).get_context_data(**kwargs)

class InformCollectsAccountView(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'
    template_name = 'iraca/inform/collect_account/view.html'


    def dispatch(self, request, *args, **kwargs):

        self.cuts = rh_models.Cuts.objects.get(id=self.kwargs['pk_cut'])
        self.collect = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])

        self.permissions = {
            "all": [
                "usuarios.iraca.informes.ver",
                "usuarios.iraca.informes.cortes.ver",
            ]
        }

        return super(InformCollectsAccountView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        cuts = rh_models.Cuts.objects.get(id=self.kwargs['pk_cut'])
        collect = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])
        kwargs['title'] = "Ver evidencias"
        kwargs['breadcrum_1'] = cuts.consecutive
        kwargs['objeto'] = collect
        return super(InformCollectsAccountView,self).get_context_data(**kwargs)

class ReportCollectsAccountListView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.iraca.informes.ver",
            "usuarios.iraca.informes.cortes.ver",
        ]
    }
    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        cuts = rh_models.Cuts.objects.get(id=self.kwargs['pk_cut'])
        id_cuts = cuts.id
        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Reporte estado del corte' + str(cuts.consecutive),
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_list_collects_account.delay(reporte.id,id_cuts)

        return HttpResponseRedirect('/reportes/')

class HistorialCollectsAccountView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.informes.ver",
            "usuarios.iraca.informes.cortes.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/inform/collect_account/register.html'

    def get_items_registers(self):

        list = []
        registers = rh_models.Registration.objects.filter(collect_account__id = self.kwargs['pk_collect_account']).order_by('-creation')

        for register in registers:
            list.append({
                'propio': True if register.user == self.request.user else False,
                'fecha': register.pretty_creation_datetime(),
                'usuario': register.user.get_full_name_string(),
                'html': register.delta,
            })

        return list

    def get_context_data(self, **kwargs):
        registers = self.get_items_registers()
        collect_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])
        kwargs['title'] = "GESTIÓN"
        kwargs['registros'] = registers
        kwargs['registros_cantidad'] = len(registers)
        kwargs['breadcrum_1'] = collect_account.cut.consecutive
        kwargs['breadcrum_active'] = collect_account.contract.nombre
        return super(HistorialCollectsAccountView,self).get_context_data(**kwargs)

class InformCollectsAccountgenerateListView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    model = rh_models.Collects_Account
    template_name = 'iraca/inform/collect_account/activity.html'
    form_class = forms.AccountActivityForm
    success_url = "../../"
    pk_url_kwarg = 'pk_accounts'

    permissions = {
        "all": [
            "usuarios.iraca.informes.ver",
            "usuarios.iraca.informes.cortes.ver",
        ]
    }

    def form_valid(self, form):

        day = timezone.now()
        date = day.strftime("%Y/%m/%d")
        collect_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])
        date_any= str(collect_account.contract.inicio)


        collect_account.delta = form.cleaned_data['contenido']
        collect_account.save()
        delta = json.loads(form.cleaned_data['contenido'])

        delta_2 = BeautifulSoup(html.render(delta['ops']),"html.parser",from_encoding='utf-8')

        collect_account.file6.delete()

        collect_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])

        if collect_account.liquidacion==True:
            month_inform = collect_account.month
        else:
            month = int(collect_account.month) - 1
            month_inform = functions.month_converter(month)

        template_header = BeautifulSoup(
            open(settings.TEMPLATES[0]['DIRS'][0] + '/pdfkit/informe_actividades/inform.html', 'rb'), "html.parser")

        template_header_tag = template_header.find(class_='date_span')
        template_header_tag.insert(1, date_any)

        template_header_tag = template_header.find(class_='charge_span')
        template_header_tag.insert(1, str(collect_account.contract.cargo.nombre))

        template_header_tag = template_header.find(class_='name_span')
        template_header_tag.insert(1, str(collect_account.contract.contratista.get_full_name()))

        template_header_tag = template_header.find(class_='document_span')
        template_header_tag.insert(1, str(collect_account.contract.contratista.get_cedula()))

        template_header_tag = template_header.find(class_='month_span')
        template_header_tag.insert(1, month_inform)

        template_header_tag = template_header.find(class_='name_span_1')
        template_header_tag.insert(1, str(collect_account.contract.contratista.get_full_name()))

        template_header_tag = template_header.find(class_='document_span_1')
        template_header_tag.insert(1, str(collect_account.contract.contratista.cedula))

        template_header_tag = template_header.find(class_='content_span_1')
        template_header_tag.insert(1, delta_2)

        template_header_tag = template_header.find(class_='name_span_2')
        template_header_tag.insert(1, str(collect_account.contract.contratista.get_full_name()))

        template_header_tag = template_header.find(class_='document_span_2')
        template_header_tag.insert(1, str(collect_account.contract.contratista.get_cedula()))


        collect_account.html_3.save('informe_actividades.html',
                                    File(io.BytesIO(template_header.prettify(encoding='utf-8'))))

        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

        collect_account.file6.save('informe_actividades.pdf',
                                   File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf', 'rb')))

        if settings.DEBUG:
            config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
            pdfkit.from_file([collect_account.html_3.path], collect_account.file6.path, {
                '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/informe_actividades/header/header.html',
                '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/informe_actividades/footer/footer.html',
                '--enable-local-file-access': None,
                '--page-size': 'Letter'
            }, configuration=config)
        else:
            data = pdfkit.from_url(
                url=collect_account.html_3.url,
                output_path=False,
                options={
                    '--header-html': settings.STATICFILES_DIRS[0] + '/pdfkit/informe_actividades/header/header.html',
                    '--footer-html': settings.STATICFILES_DIRS[0] + '/pdfkit/informe_actividades/footer/footer.html',
                    '--enable-local-file-access': None,
                    '--page-size': 'Letter'
                }
            )
            collect_account.file6.save('informe_actividades.pdf', File(io.BytesIO(data)))

        rh_models.Registration.objects.create(
            cut=collect_account.cut,
            user=self.request.user,
            collect_account=collect_account,
            delta="Genero el informe de actividades"
        )


        return super(InformCollectsAccountgenerateListView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        collec_account = rh_models.Collects_Account.objects.get(id=self.kwargs['pk_collect_account'])
        kwargs['title'] = "CREAR INFORME DE ACTIVIDADES"
        kwargs['breadcrum_active'] = collec_account.contract.nombre
        return super(InformCollectsAccountgenerateListView,self).get_context_data(**kwargs)


    def get_initial(self):
        return {'pk_cut':self.kwargs['pk_cut'],
                'pk_collect_account':self.kwargs['pk_collect_account']}
#----------------------------------------------------------------------------------

#-------------------------------Liquidaciones--------------------------------------

class LiquidacionesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.iraca.liquidaciones.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/liquidaciones/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Liquidaciones"
        kwargs['url_datatable'] = '/rest/v1.0/iraca_new/liquidaciones/'
        return super(LiquidacionesListView,self).get_context_data(**kwargs)

class LiquidacionesAporbarInforme(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.liquidacion = rh_models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])


        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.liquidaciones.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if request.user.is_superuser:
                    self.liquidacion.estado_informe = 'Aprobado'
                    self.liquidacion.save()

                    liquidacion = rh_models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
                    cuenta = rh_models.Collects_Account.objects.get(contract=liquidacion.contrato, liquidacion=True)
                    cuenta.estate_inform="Aprobado"
                    cuenta.save()

                    rh_models.Registration.objects.create(
                        cut=cuenta.cut,
                        user=self.request.user,
                        collect_account=cuenta,
                        delta="Aprobo el informe de actividades de la liquidacion"
                    )
                    return HttpResponseRedirect('../../')
                else:
                    if request.user.has_perms(self.permissions.get('all')):
                        self.liquidacion.estado_informe = 'Aprobado'
                        self.liquidacion.save()


                        liquidacion = rh_models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
                        cuenta = rh_models.Collects_Account.objects.get(contract=liquidacion.contrato, liquidacion=True)
                        cuenta.estate_inform = "Aprobado"
                        cuenta.save()

                        rh_models.Registration.objects.create(
                            cut=cuenta.cut,
                            user=self.request.user,
                            collect_account=cuenta,
                            delta="Aprobo el informe de actividades de la liquidacion"
                        )
                        return HttpResponseRedirect('../../')
                    else:
                        return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

class LiquidacionesRechazarInforme(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.liquidacion = rh_models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])


        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.liquidaciones.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if request.user.is_superuser:
                    self.liquidacion.estado_informe = 'Rechazado'
                    self.liquidacion.save()

                    liquidacion = rh_models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
                    cuenta = rh_models.Collects_Account.objects.get(contract=liquidacion.contrato, liquidacion=True)
                    cuenta.estate_inform="Rechazado"
                    cuenta.save()

                    rh_models.Registration.objects.create(
                        cut=cuenta.cut,
                        user=self.request.user,
                        collect_account=cuenta,
                        delta="Rechazo el informe de actividades de la liquidacion"
                    )
                    return HttpResponseRedirect('../../')
                else:
                    if request.user.has_perms(self.permissions.get('all')):
                        self.liquidacion.estado_informe = 'Rechazado'
                        self.liquidacion.save()


                        liquidacion = rh_models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
                        cuenta = rh_models.Collects_Account.objects.get(contract=liquidacion.contrato, liquidacion=True)
                        cuenta.estate_inform = "Rechazado"
                        cuenta.save()

                        rh_models.Registration.objects.create(
                            cut=cuenta.cut,
                            user=self.request.user,
                            collect_account=cuenta,
                            delta="Rechazo el informe de actividades de la liquidacion"
                        )
                        return HttpResponseRedirect('../../')
                    else:
                        return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

class LiquidacionesVerInforme(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'
    template_name = 'iraca/liquidaciones/ver.html'


    def dispatch(self, request, *args, **kwargs):

        self.permissions = {
            "all": [
                "usuarios.iraca.ver",
                "usuarios.iraca.liquidaciones.ver",
            ]
        }

        return super(LiquidacionesVerInforme, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        liquidacion = rh_models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
        collect = rh_models.Collects_Account.objects.get(contract=liquidacion.contrato, liquidacion=True)
        kwargs['title'] = "Ver evidencias"
        kwargs['objeto'] = collect
        kwargs['breadcum_active'] = liquidacion.contrato.nombre
        return super(LiquidacionesVerInforme,self).get_context_data(**kwargs)

class LiquidationsHistorialInforme(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,TemplateView):

    permissions = {
        "all": [
            "usuarios.iraca.ver",
            "usuarios.iraca.liquidaciones.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'iraca/liquidaciones/historial.html'

    def get_items_registers(self):

        list = []
        liquidacion = rh_models.Liquidations.objects.get(id= self.kwargs['pk_liquidacion'])

        cuenta= rh_models.Collects_Account.objects.get(contract=liquidacion.contrato, liquidacion=True)

        registers = rh_models.Registration.objects.filter(collect_account=cuenta).order_by('-creation')

        for register in registers:
            list.append({
                'propio': True if register.user == self.request.user else False,
                'fecha': register.pretty_creation_datetime(),
                'usuario': register.user.get_full_name_string(),
                'html': register.delta,
            })

        return list

    def get_context_data(self, **kwargs):
        registers = self.get_items_registers()
        liquidacion = rh_models.Liquidations.objects.get(id=self.kwargs['pk_liquidacion'])
        collect_account = rh_models.Collects_Account.objects.get(contract=liquidacion.contrato, liquidacion=True)
        kwargs['title'] = "GESTIÓN"
        kwargs['registros'] = registers
        kwargs['registros_cantidad'] = len(registers)
        kwargs['breadcrum_active'] = collect_account.contract.nombre
        return super(LiquidationsHistorialInforme,self).get_context_data(**kwargs)