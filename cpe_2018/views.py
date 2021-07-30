import mimetypes

from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from recursos_humanos import models as rh_models
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from direccion_financiera.tasks import send_mail_templated_pago, send_mail_templated_reporte
from cpe_2018 import tasks
from config.settings.base import DEFAULT_FROM_EMAIL, EMAIL_HOST_USER, EMAIL_DIRECCION_FINANCIERA
from reportes.models import Reportes
import json
from recursos_humanos import models as models_rh
from cpe_2018 import models, forms
from django.db.models import Sum
from cpe_2018 import functions
from delta import html
from bs4 import BeautifulSoup
import pdfkit
from django.core.files import File
import io
from django.utils import timezone
from django.db import transaction
from django.db.models.functions import Now
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

import itertools
from random import randint
from statistics import mean
from PyPDF2 import PdfFileMerger

# Create your views here.

#------------------------------- SELECCIÓN ----------------------------------------

class Cpe2018OptionsView(LoginRequiredMixin,
                          MultiplePermissionsRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/lista.html'
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver"
        ]
    }

    def dispatch(self, request, *args, **kwargs):
        items = self.get_items()
        if len(items) == 0:
            return redirect(self.login_url)
        return super(Cpe2018OptionsView, self).dispatch(request, *args, **kwargs)

    def get_items(self):
        items = []

        if self.request.user.has_perm('usuarios.cpe_2018.entes_territoriales.ver'):
            items.append({
                'sican_categoria': 'Entes territoriales',
                'sican_color': 'teal darken-4',
                'sican_order': 1,
                'sican_url': 'entes_territoriales/',
                'sican_name': 'Entes territoriales',
                'sican_icon': 'assistant',
                'sican_description': 'Registro de información y gestión con entes territoriales.'
            })

        if self.request.user.has_perm('usuarios.cpe_2018.solicitudes_desplazamiento.ver'):
            items.append({
                'sican_categoria': 'Solicitudes de desplazamiento',
                'sican_color': 'pink darken-4',
                'sican_order': 2,
                'sican_url': 'solicitudes_desplazamiento/',
                'sican_name': 'Desplazamiento',
                'sican_icon': 'map',
                'sican_description': 'Solicitudes de desplazamiento a sedes educativas y municipios.'
            })

        if self.request.user.has_perm('usuarios.cpe_2018.rutas.ver'):
            items.append({
                'sican_categoria': 'Rutas',
                'sican_color': 'green darken-3',
                'sican_order': 3,
                'sican_url': 'rutas/',
                'sican_name': 'Rutas',
                'sican_icon': 'autorenew',
                'sican_description': 'Asignación, cambio y trazabilidad de las rutas para los contratistas.'
            })

        if self.request.user.has_perm('usuarios.cpe_2018.db.ver'):
            items.append({
                'sican_categoria': 'Base de datos',
                'sican_color': 'brown darken-3',
                'sican_order': 4,
                'sican_url': 'bd/',
                'sican_name': 'Base de datos',
                'sican_icon': 'data_usage',
                'sican_description': 'División general del proyecto, regiones, departamentos, municipios y radicados.'
            })

        if self.request.user.has_perm('usuarios.cpe_2018.componentes.ver'):
            items.append({
                'sican_categoria': 'Componentes',
                'sican_color': 'orange darken-3',
                'sican_order': 5,
                'sican_url': 'componentes/',
                'sican_name': 'Componentes',
                'sican_icon': 'view_list',
                'sican_description': 'Estructura de componentes, subcomponentes y entregables del proyecto.'
            })

        if self.request.user.has_perm('usuarios.cpe_2018.formatos.ver'):
            items.append({
                'sican_categoria': 'Formatos',
                'sican_color': 'red darken-4',
                'sican_order': 6,
                'sican_url': 'formatos/',
                'sican_name': 'Formatos',
                'sican_icon': 'attach_file',
                'sican_description': 'Formatos de entregables y productos de la estrategia.'
            })


        if self.request.user.has_perm('usuarios.cpe_2018.misrutas.ver'):
            items.append({
                'sican_categoria': 'Mis rutas',
                'sican_color': 'blue-grey darken-3',
                'sican_order': 7,
                'sican_url': 'misrutas/',
                'sican_name': 'Mis rutas',
                'sican_icon': 'assignment_ind',
                'sican_description': 'Ruteos, cuentas de cobro e información de pagos.'
            })


        if self.request.user.has_perm('usuarios.cpe_2018.cortes.ver'):
            items.append({
                'sican_categoria': 'Cortes de pago',
                'sican_color': 'pink darken-3',
                'sican_order': 8,
                'sican_url': 'cortes/',
                'sican_name': 'Cortes de pago',
                'sican_icon': 'attach_money',
                'sican_description': 'Cortes de pago y cuentas de cobro de la vigencia 2018'
            })


        if self.request.user.has_perm('usuarios.cpe_2018.red.ver'):
            items.append({
                'sican_categoria': 'RED',
                'sican_color': 'deep-purple darken-4',
                'sican_order': 9,
                'sican_url': 'red/',
                'sican_name': 'RED',
                'sican_icon': 'archive',
                'sican_description': 'Reporte y generación de RED (Relación de envio documental)'
            })


        if self.request.user.has_perm('usuarios.cpe_2018.informes.ver'):
            items.append({
                'sican_categoria': 'Informes',
                'sican_color': 'orange darken-4',
                'sican_order': 10,
                'sican_url': 'informes/',
                'sican_name': 'Informes',
                'sican_icon': 'dashboard',
                'sican_description': 'Informes de avance en la ejecución'
            })


        if self.request.user.has_perm('usuarios.cpe_2018.soportes.ver'):
            items.append({
                'sican_categoria': 'Soportes',
                'sican_color': 'red darken-4',
                'sican_order': 11,
                'sican_url': 'soportes/',
                'sican_name': 'Soportes',
                'sican_icon': 'insert_drive_file',
                'sican_description': 'Soportes de la ejecución de la estrategia'
            })

        if self.request.user.has_perm('usuarios.cpe_2018.liquidaciones.ver'):
            items.append({
                'sican_categoria': 'Liquidaciones',
                'sican_color': 'teal darken-4',
                'sican_order': 12,
                'sican_url': 'liquidaciones/',
                'sican_name': 'Liquidaciones',
                'sican_icon': 'insert_drive_file',
                'sican_description': 'Liquidación de contratos vigencia 2018'
            })


        return items

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CPE 2018"
        kwargs['items'] = self.get_items()
        return super(Cpe2018OptionsView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#----------------------------------- REGIONES -------------------------------------

class RegionesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.db.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/bd/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "BASE DE DATOS"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/bd/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.db.crear')
        return super(RegionesListView,self).get_context_data(**kwargs)


class ActualizacionDbListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.db.ver",
            "usuarios.cpe_2018.db.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/bd/actualizar/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZACIÓN DE RADICADOS"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/bd/actualizar/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.acceso.db.crear')
        kwargs['link_formato'] = '/static/documentos/actualizacion_radicados.xlsx'
        return super(ActualizacionDbListView,self).get_context_data(**kwargs)


class ActualizacionDbDocentesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.db.ver",
            "usuarios.cpe_2018.db.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/bd/actualizar_docentes/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZACIÓN DE DOCENTES"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/bd/actualizar_docentes/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.acceso.db.crear')
        return super(ActualizacionDbDocentesListView,self).get_context_data(**kwargs)


class CreateActualizacionDbView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.db.ver",
            "usuarios.cpe_2018.db.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/bd/actualizar/crear.html'
    form_class = forms.ActualizacionRadicadosForm
    success_url = "../"

    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZACIÓN DE RADICADOS"
        return super(CreateActualizacionDbView,self).get_context_data(**kwargs)


    def form_valid(self, form):
        actualizacion = models.ActualizacionRadicados.objects.create(
                            usuario_creacion = self.request.user,
                            file = form.cleaned_data['file']
                        )
        tasks.build_resultado_actualizacion_radicados.delay(actualizacion.id)
        return super(CreateActualizacionDbView,self).form_valid(form)

class CreateActualizacionDbDocentesView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.db.ver",
            "usuarios.cpe_2018.db.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/bd/actualizar_docentes/crear.html'
    form_class = forms.ActualizacionDocentesForm
    success_url = "../"

    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZACIÓN DE RADICADOS"
        return super(CreateActualizacionDbDocentesView,self).get_context_data(**kwargs)


    def form_valid(self, form):
        actualizacion = models.ActualizacionDocentes.objects.create(
                            usuario_creacion = self.request.user,
                            file = form.cleaned_data['file']
                        )
        tasks.build_resultado_actualizacion_docentes.delay(actualizacion.id)
        return super(CreateActualizacionDbDocentesView,self).form_valid(form)

#----------------------------------------------------------------------------------



#----------------------------------- INFORMES -------------------------------------


class InformesListView(TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/informes/opciones.html'

    def get_items(self):
        items = []

        for region in models.Regiones.objects.all().order_by('numero'):
            if self.request.user.has_perm('usuarios.cpe_2018.informes.informes_{}.ver'.format(region.numero)):
                items.append({
                    'sican_categoria': 'Informes: {0}'.format(region.nombre),
                    'sican_color': region.color,
                    'sican_order': 1,
                    'sican_url': '{0}/'.format(str(region.id)),
                    'sican_name': '{0}'.format(region.nombre),
                    'sican_icon': 'data_usage',
                    'sican_description': 'Informes estado de ejecución de la {0}.'.format(region.nombre)
                })


        return items

    def dispatch(self, request, *args, **kwargs):

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.informes.ver"
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
        kwargs['title'] = "INFORMES"
        kwargs['items'] = self.get_items()
        return super(InformesListView,self).get_context_data(**kwargs)


class InformesRegionListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/informes/region/opciones.html'


    def get_items(self):
        items = [
            {
                'sican_categoria': 'Matricula de docentes',
                'sican_color': 'teal darken-4',
                'sican_order': 1,
                'sican_url': 'matricula',
                'sican_name': 'Matricula de docentes',
                'sican_icon': 'apps',
                'sican_description': 'Conformación de grupos de formación'
            },
            {
                'sican_categoria': 'Gestión en sedes',
                'sican_color': 'orange darken-4',
                'sican_order': 2,
                'sican_url': 'sedes',
                'sican_name': 'Gestión en sedes',
                'sican_icon': 'apps',
                'sican_description': 'Progreso de talleres y legalización en sedes educativas'
            },
            {
                'sican_categoria': 'Retoma',
                'sican_color': 'pink darken-4',
                'sican_order': 3,
                'sican_url': 'retoma',
                'sican_name': 'Retoma',
                'sican_icon': 'apps',
                'sican_description': 'Retoma de equipos en desuso'
            },
            {
                'sican_categoria': 'Formación',
                'sican_color': 'blue darken-4',
                'sican_order': 4,
                'sican_url': 'formacion',
                'sican_name': 'Formación',
                'sican_icon': 'apps',
                'sican_description': 'Desarrollo y avance de la estrategia de formación'
            }
        ]

        return items

    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.informes.ver",
                "usuarios.cpe_2018.informes.informes_{0}.ver".format(region.numero)
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "INFORMES - {0}".format(region.nombre)
        kwargs['items'] = self.get_items()
        kwargs['breadcrum_active'] = region.nombre
        return super(InformesRegionListView,self).get_context_data(**kwargs)


class InformeMatriculaRegionListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/informes/region/matricula.html'


    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.informes.ver",
                "usuarios.cpe_2018.informes.informes_{0}.ver".format(region.numero)
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "INFORMES - {0}".format(region.nombre)
        kwargs['breadcrum_active'] = region.nombre
        kwargs['region_pk'] = region.pk
        kwargs['url_municipios'] = '/rest/v1.0/cpe_2018/rutas/autocomplete/municipios/{0}/'.format(region.pk)
        return super(InformeMatriculaRegionListView,self).get_context_data(**kwargs)



class InformeSedesRegionListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/informes/region/sedes.html'


    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.informes.ver",
                "usuarios.cpe_2018.informes.informes_{0}.ver".format(region.numero)
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "INFORMES - {0}".format(region.nombre)
        kwargs['breadcrum_active'] = region.nombre
        kwargs['region_pk'] = region.pk
        kwargs['url_municipios'] = '/rest/v1.0/cpe_2018/rutas/autocomplete/municipios/{0}/'.format(region.pk)
        return super(InformeSedesRegionListView,self).get_context_data(**kwargs)



class InformeRetomaRegionListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/informes/region/retoma.html'


    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.informes.ver",
                "usuarios.cpe_2018.informes.informes_{0}.ver".format(region.numero)
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "INFORMES - {0}".format(region.nombre)
        kwargs['breadcrum_active'] = region.nombre
        kwargs['region_pk'] = region.pk
        kwargs['url_municipios'] = '/rest/v1.0/cpe_2018/rutas/autocomplete/municipios/{0}/'.format(region.pk)
        return super(InformeRetomaRegionListView,self).get_context_data(**kwargs)


class InformeFormacionRegionListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/informes/region/formacion.html'


    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.informes.ver",
                "usuarios.cpe_2018.informes.informes_{0}.ver".format(region.numero)
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "INFORMES - {0}".format(region.nombre)
        kwargs['breadcrum_active'] = region.nombre
        kwargs['region_pk'] = region.pk
        kwargs['url_municipios'] = '/rest/v1.0/cpe_2018/rutas/autocomplete/municipios/{0}/'.format(region.pk)
        return super(InformeFormacionRegionListView,self).get_context_data(**kwargs)


#----------------------------------- SOPORTES -------------------------------------

class SoportesListView(TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/soportes/opciones.html'

    def get_items(self):
        items = []

        for region in models.Regiones.objects.all().order_by('numero'):
            if self.request.user.has_perm('usuarios.cpe_2018.soportes.soportes_{0}.ver'.format(region.numero)):
                items.append({
                    'sican_categoria': 'Soportes: {0}'.format(region.nombre),
                    'sican_color': region.color,
                    'sican_order': 1,
                    'sican_url': '{0}/'.format(str(region.id)),
                    'sican_name': '{0}'.format(region.nombre),
                    'sican_icon': 'insert_drive_file',
                    'sican_description': 'Soportes de ejecución de la estrategia en la {0}.'.format(region.nombre)
                })


        return items

    def dispatch(self, request, *args, **kwargs):

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.soportes.ver"
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
        kwargs['title'] = "SOPORTES"
        kwargs['items'] = self.get_items()
        return super(SoportesListView,self).get_context_data(**kwargs)


class SoportesRegionListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/soportes/region/opciones.html'


    def get_items(self):
        items = [
            {
                'sican_categoria': 'Sedes',
                'sican_color': 'teal darken-4',
                'sican_order': 1,
                'sican_url': 'sedes',
                'sican_name': 'Sedes',
                'sican_icon': 'apps',
                'sican_description': 'Busqueda de radicados sedes educativas.'
            },
            {
                'sican_categoria': 'Docentes',
                'sican_color': 'orange darken-4',
                'sican_order': 2,
                'sican_url': 'docentes',
                'sican_name': 'Docentes',
                'sican_icon': 'apps',
                'sican_description': 'Busqueda de soportes estrategia de formación.'
            },
            {
                'sican_categoria': 'Retomas',
                'sican_color': 'pink darken-4',
                'sican_order': 3,
                'sican_url': 'retomas',
                'sican_name': 'Retomas',
                'sican_icon': 'apps',
                'sican_description': 'Busqueda de actas de legalización de retoma.'
            }
        ]

        return items

    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.soportes.ver",
                "usuarios.cpe_2018.soportes.soportes_{0}.ver".format(region.numero)
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "SOPORTES - {0}".format(region.nombre)
        kwargs['items'] = self.get_items()
        kwargs['breadcrum_active'] = region.nombre
        return super(SoportesRegionListView,self).get_context_data(**kwargs)

class SoportesSedesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/soportes/region/lista_sedes.html'

    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.soportes.ver",
                "usuarios.cpe_2018.soportes.soportes_{0}.ver".format(region.numero)
            ]
        }
        return permissions


    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "SOPORTES - {0}".format(region.nombre)
        kwargs['breadcrum_active'] = region.nombre
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/soportes/{0}/sedes/'.format(region.id)
        return super(SoportesSedesListView,self).get_context_data(**kwargs)

class SoportesVerSedesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/soportes/region/lista_sedes_soportes.html'

    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.soportes.ver",
                "usuarios.cpe_2018.soportes.soportes_{0}.ver".format(region.numero)
            ]
        }
        return permissions


    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        kwargs['title'] = "SOPORTES - {0}".format(region.nombre)
        kwargs['breadcrum_1'] = region.nombre
        kwargs['breadcrum_active'] = radicado.numero
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/soportes/{0}/sedes/ver/{1}/'.format(region.id,radicado.id)
        return super(SoportesVerSedesListView,self).get_context_data(**kwargs)

class SoportesDocentesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/soportes/region/lista_docentes.html'

    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.soportes.ver",
                "usuarios.cpe_2018.soportes.soportes_{0}.ver".format(region.numero)
            ]
        }
        return permissions


    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "SOPORTES - {0}".format(region.nombre)
        kwargs['breadcrum_active'] = region.nombre
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/soportes/{0}/docentes/'.format(region.id)
        return super(SoportesDocentesListView,self).get_context_data(**kwargs)

class SoportesVerDocentesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/soportes/region/lista_docentes_soportes.html'

    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        docente = models.Docentes.objects.get(id=self.kwargs['pk_docente'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.soportes.ver",
                "usuarios.cpe_2018.soportes.soportes_{0}.ver".format(region.numero)
            ]
        }
        return permissions


    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        docente = models.Docentes.objects.get(id=self.kwargs['pk_docente'])
        kwargs['title'] = "SOPORTES - {0}".format(region.nombre)
        kwargs['breadcrum_1'] = region.nombre
        kwargs['breadcrum_active'] = docente.cedula
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/soportes/{0}/docentes/ver/{1}/'.format(region.id,docente.id)
        return super(SoportesVerDocentesListView,self).get_context_data(**kwargs)

class SoportesRetomasListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/soportes/region/lista_retomas.html'

    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.soportes.ver",
                "usuarios.cpe_2018.soportes.soportes_{0}.ver".format(region.numero)
            ]
        }
        return permissions


    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "SOPORTES - {0}".format(region.nombre)
        kwargs['breadcrum_active'] = region.nombre
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/soportes/{0}/retomas/'.format(region.id)
        return super(SoportesRetomasListView,self).get_context_data(**kwargs)

#--------------------------------- DEPARTAMENTOS ----------------------------------

class DepartamentosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.db.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/bd/departamentos/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "departamentos"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/bd/{0}/'.format(self.kwargs['pk'])
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.acceso.db.crear')
        kwargs['breadcrum_active'] = models.Regiones.objects.get(id=self.kwargs['pk']).nombre
        return super(DepartamentosListView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------
#----------------------------------- MUNICIPIOS -----------------------------------

class MunicipiosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.db.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/bd/departamentos/municipios/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Municipios"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/bd/{0}/departamentos/{1}/municipios/'.format(self.kwargs['pk'],self.kwargs['pk_departamento'])
        kwargs['breadcrum_active'] = models.Regiones.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active_1'] = models.Departamentos.objects.get(id=self.kwargs['pk_departamento']).nombre
        return super(MunicipiosListView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------


#------------------------------------ RADICADOS -----------------------------------

class RadicadosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.db.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/bd/departamentos/municipios/radicados/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Radicados"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/bd/{0}/departamentos/{1}/municipios/{2}/radicados/'.format(self.kwargs['pk'],self.kwargs['pk_departamento'],self.kwargs['pk_municipio'])
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.acceso.db.crear')
        kwargs['breadcrum_active'] = models.Regiones.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active_1'] = models.Departamentos.objects.get(id=self.kwargs['pk_departamento']).nombre
        kwargs['breadcrum_active_2'] = models.Municipios.objects.get(id=self.kwargs['pk_municipio']).nombre
        return super(RadicadosListView,self).get_context_data(**kwargs)

class DocentesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.db.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/bd/departamentos/municipios/docentes/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Docentes"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/bd/{0}/departamentos/{1}/municipios/{2}/docentes/'.format(self.kwargs['pk'],self.kwargs['pk_departamento'],self.kwargs['pk_municipio'])
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.acceso.db.crear')
        kwargs['breadcrum_active'] = models.Regiones.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active_1'] = models.Departamentos.objects.get(id=self.kwargs['pk_departamento']).nombre
        kwargs['breadcrum_active_2'] = models.Municipios.objects.get(id=self.kwargs['pk_municipio']).nombre
        return super(DocentesListView,self).get_context_data(**kwargs)


class RadicadosCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.db.ver",
            "usuarios.cpe_2018.db.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/bd/departamentos/municipios/radicados/crear.html'
    form_class = forms.RadicadosForm
    success_url = "../"
    model = models.Radicados

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.municipio = models.Municipios.objects.get(id = self.kwargs['pk_municipio'])
        self.object.save()
        return super(RadicadosCreateView,self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CREAR RADICADO"
        kwargs['breadcrum_active'] = models.Regiones.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active_1'] = models.Departamentos.objects.get(id=self.kwargs['pk_departamento']).nombre
        kwargs['breadcrum_active_2'] = models.Municipios.objects.get(id=self.kwargs['pk_municipio']).nombre
        return super(RadicadosCreateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk_municipio':self.kwargs['pk_municipio'],'create':True}


class RadicadosUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.cpe_2018.acceso.ver",
            "usuarios.cpe_2018.acceso.db.ver",
            "usuarios.cpe_2018.acceso.db.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/bd/departamentos/municipios/radicados/editar.html'
    form_class = forms.RadicadosForm
    success_url = "../../"
    model = models.Radicados
    pk_url_kwarg = 'pk_radicado'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZAR DEPARTAMENTO"
        kwargs['breadcrum_active'] = models.Regiones.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active_1'] = models.Departamentos.objects.get(id=self.kwargs['pk_departamento']).nombre
        kwargs['breadcrum_active_2'] = models.Municipios.objects.get(id=self.kwargs['pk_municipio']).nombre
        kwargs['breadcrum_active_3'] = models.Radicados.objects.get(id=self.kwargs['pk_radicado']).numero
        return super(RadicadosUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk_municipio':self.kwargs['pk_municipio'],'create':False}

#----------------------------------------------------------------------------------

#----------------------------------- COMPONENTES ----------------------------------

class ComponentesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.componentes.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/componentes/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Componentes"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/componentes/'
        return super(ComponentesListView,self).get_context_data(**kwargs)


class EstrategiasListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.componentes.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/componentes/estrategias/lista.html'


    def get_context_data(self, **kwargs):
        componente = models.Componentes.objects.get(id = self.kwargs['pk_componente'])
        kwargs['title'] = "Estrategias"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/componentes/{0}/estrategias/'.format(componente.id)
        kwargs['breadcrum_active'] = componente.nombre
        return super(EstrategiasListView,self).get_context_data(**kwargs)


class MomentosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.componentes.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/componentes/estrategias/momentos/lista.html'


    def get_context_data(self, **kwargs):
        componente = models.Componentes.objects.get(id = self.kwargs['pk_componente'])
        estrategia = models.Estrategias.objects.get(id=self.kwargs['pk_estrategia'])
        kwargs['title'] = "Momentos"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/componentes/{0}/estrategias/{1}/momentos/'.format(
            componente.id,
            estrategia.id
        )
        kwargs['breadcrum_1'] = componente.nombre
        kwargs['breadcrum_active'] = estrategia.nombre
        return super(MomentosListView,self).get_context_data(**kwargs)

class EntregablesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.componentes.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/componentes/estrategias/momentos/entregables/lista.html'


    def get_context_data(self, **kwargs):
        componente = models.Componentes.objects.get(id = self.kwargs['pk_componente'])
        estrategia = models.Estrategias.objects.get(id=self.kwargs['pk_estrategia'])
        momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        kwargs['title'] = "Entregables"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/componentes/{0}/estrategias/{1}/momentos/{2}/entregables/'.format(
            componente.id,
            estrategia.id,
            momento.id
        )
        kwargs['breadcrum_1'] = componente.nombre
        kwargs['breadcrum_2'] = estrategia.nombre
        kwargs['breadcrum_active'] = momento.nombre
        return super(EntregablesListView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#---------------------------------- RUTAS -----------------------------------------


#----------------------------------- MIS RUTAS -------------------------------------


class MisRutasOptionsView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/lista.html'

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        kwargs['title'] = "MIS RUTAS"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/'
        return super(MisRutasOptionsView,self).get_context_data(**kwargs)


class ComponentesMisRutasListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/componentes/lista.html'

    def get_permission_required(self, request=None):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/actividades/{0}/'.format(self.ruta.id)
        kwargs['breadcrum_active'] = self.ruta.nombre
        return super(ComponentesMisRutasListView,self).get_context_data(**kwargs)



class ActividadesComponenteMisRutasListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/componentes/actividades/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/actividades/{0}/componente/{1}/'.format(
            self.ruta.id,
            self.componente.id
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.componente.nombre
        return super(ActividadesComponenteMisRutasListView,self).get_context_data(**kwargs)


class MisRutasCuentasCobroListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/cuentas_cobro/{0}/'.format(self.ruta.id)
        kwargs['breadcrum_active'] = self.ruta.nombre
        return super(MisRutasCuentasCobroListView,self).get_context_data(**kwargs)


#----------------------------------- RETOMA -------------------------------------


class ActividadesRetomaMisRutasListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/componentes/actividades/retoma/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
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
                return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/actividades/{0}/componente/{1}/retoma/'.format(
            self.ruta.id,
            self.componente.id
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.componente.nombre
        return super(ActividadesRetomaMisRutasListView,self).get_context_data(**kwargs)


class RetomaMisRutasVerView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/componentes/actividades/retoma/ver.html'


    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }
        return permissions


    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        retoma = models.Retoma.objects.get(id=self.kwargs['pk_retoma'])
        kwargs['title'] = "RUTA - {0} - {1}".format(ruta.nombre, ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/actividades/{0}/componente/{1}/retoma/'.format(
            ruta.id,
            componente.id
        )
        kwargs['retoma'] = retoma
        kwargs['breadcrum_1'] = ruta.nombre
        kwargs['breadcrum_active'] = retoma.radicado
        return super(RetomaMisRutasVerView,self).get_context_data(**kwargs)



class TrazabilidadRetomaMisRutasVerView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/componentes/actividades/retoma/trazabilidad.html'


    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }
        return permissions

    def get_items_registros(self):

        lista = []
        registros = models.RegistroRetoma.objects.filter(retoma = self.kwargs['pk_retoma']).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        retoma = models.Retoma.objects.get(id=self.kwargs['pk_retoma'])
        kwargs['title'] = "RUTA - {0} - {1}".format(ruta.nombre, ruta.contrato.contratista.get_full_name())
        kwargs['retoma'] = retoma
        kwargs['breadcrum_1'] = ruta.nombre
        kwargs['breadcrum_2'] = componente.nombre
        kwargs['breadcrum_active'] = retoma.radicado
        kwargs['registros'] = self.get_items_registros()
        return super(TrazabilidadRetomaMisRutasVerView,self).get_context_data(**kwargs)


#----------------------------- ACTIVIDADES X RUTA -------------------------------

class ActividadesSedeMisRutasListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/componentes/actividades/sede_ruta/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if self.objeto_ruta.entregable.modelo == 'talleres_fomento_uso':
                    return HttpResponseRedirect('../../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/actividades/{0}/componente/{1}/cargar/{2}/'.format(
            self.ruta.id,
            self.componente.id,
            self.objeto_ruta.id
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)
            if modelo != None:
                try:
                    objeto = modelo.objects.get(ruta = self.ruta)
                except:
                    pass
                else:
                    kwargs['objeto'] = objeto
                    kwargs['permiso_crear'] = False
            else:
                pass
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        return super(ActividadesSedeMisRutasListView,self).get_context_data(**kwargs)


class ActividadesSedeMisRutasVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/componentes/actividades/sede_ruta/ver.html'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")

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

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['soporte'] = self.soporte
        kwargs['objeto_ruta'] = self.objeto_ruta

        return super(ActividadesSedeMisRutasVerView,self).get_context_data(**kwargs)


class TrazabilidadSedeMisRutasVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/componentes/actividades/sede_ruta/trazabilidad.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")

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

    def get_items_registros(self):

        lista = []
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])


        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
            registros = registro.objects.filter(modelo = self.soporte).order_by('-creation')
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['registros'] = self.get_items_registros()

        return super(TrazabilidadSedeMisRutasVerView,self).get_context_data(**kwargs)


#--------------------------------- RADICADOS -----------------------------------


class ActividadesComponenteMisRutasRadicadoListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/componentes/actividades/radicados/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
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
                return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/actividades/{0}/componente/{1}/radicado/{2}/'.format(
            self.ruta.id,
            self.componente.id,
            self.radicado.id
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.componente.nombre
        kwargs['breadcrum_active'] = self.radicado.numero
        return super(ActividadesComponenteMisRutasRadicadoListView,self).get_context_data(**kwargs)


class ActividadesMisRutasSedeListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/componentes/actividades/sede/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
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

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/actividades/{0}/componente/{1}/radicado/{2}/cargar/{3}/'.format(
            self.ruta.id,
            self.componente.id,
            self.radicado.id,
            self.objeto_ruta.id
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.radicado.numero
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre


        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            try:
                objeto = modelo.objects.get(ruta = self.ruta,radicado = self.radicado)
            except:
                kwargs['permiso_crear'] = False
            else:
                kwargs['permiso_crear'] = False
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        return super(ActividadesMisRutasSedeListView,self).get_context_data(**kwargs)


class ActividadesRadicadoSedeMisRutasVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/componentes/actividades/sede/ver.html'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")



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

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.radicado.numero
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['soporte'] = self.soporte
        kwargs['objeto_ruta'] = self.objeto_ruta

        return super(ActividadesRadicadoSedeMisRutasVerView,self).get_context_data(**kwargs)


class TrazabilidadSedeMisrutasRadicadoVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/componentes/actividades/sede/trazabilidad.html'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
        else:
            raise NotImplementedError("EL modelo no esta establecido")


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

    def get_items_registros(self):

        lista = []

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
            registros = registro.objects.filter(modelo = self.soporte).order_by('-creation')
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.radicado.numero
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['registros'] = self.get_items_registros()

        return super(TrazabilidadSedeMisrutasRadicadoVerView,self).get_context_data(**kwargs)

#------------------------------------ FORMACION ---------------------------------

class FormacionMisRutasListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/formacion/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        actividades_json = json.loads(self.ruta.actividades_json)
        cantidad_formacion = actividades_json['componente_' + str(models.Componentes.objects.get(numero='2').id)]

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if cantidad_formacion <= 0:
                    return HttpResponseRedirect('../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/actividades/{0}/formacion/'.format(
            self.ruta.id
        )
        kwargs['breadcrum_active'] = self.ruta.nombre
        return super(FormacionMisRutasListView,self).get_context_data(**kwargs)


class DocentesGrupoMisRutasListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/formacion/grupos/docentes/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/actividades/{0}/formacion/docentes/{1}/'.format(
            self.ruta.id,
            self.grupo.id
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.grupo.get_nombre_grupo()
        return super(DocentesGrupoMisRutasListView,self).get_context_data(**kwargs)


class DocentesActividadesMisRutasListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/formacion/grupos/actividades/lista.html'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/actividades/{0}/formacion/actividades/{1}/'.format(
            self.ruta.id,
            self.grupo.id
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.grupo.get_nombre_grupo()
        return super(DocentesActividadesMisRutasListView,self).get_context_data(**kwargs)


class DocentesActividadesEntregablesMisRutasListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/formacion/grupos/actividades/evidencias/lista.html'

    def dispatch(self, request, *args, **kwargs):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/actividades/{0}/formacion/actividades/{1}/evidencias/{2}/'.format(
            self.ruta.id,
            self.grupo.id,
            self.entregable.id
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_active'] = self.entregable.nombre
        return super(DocentesActividadesEntregablesMisRutasListView,self).get_context_data(**kwargs)


class DocentesActividadesEntregablesMisRutasVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/formacion/grupos/actividades/evidencias/ver.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
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

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_3'] = self.entregable.nombre


        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])

        kwargs['objeto'] = objeto
        kwargs['breadcrum_active'] = objeto.id

        return super(DocentesActividadesEntregablesMisRutasVerView,self).get_context_data(**kwargs)


class TrazabilidadDocentesActividadesEntregablesMisRutasVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/formacion/grupos/actividades/evidencias/trazabilidad.html'

    def dispatch(self, request, *args, **kwargs):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
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
                return HttpResponseRedirect('../')

    def get_items_registros(self):

        lista = []

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            registro = self.modelos[self.entregable.modelo]['registro']
            modelo = self.modelos[self.entregable.modelo]['modelo']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])
            registros = registro.objects.filter(modelo = objeto).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_3'] = self.entregable.nombre

        kwargs['registros'] = self.get_items_registros()


        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])

        kwargs['breadcrum_active'] = objeto.id

        return super(TrazabilidadDocentesActividadesEntregablesMisRutasVerView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------


#-------------------------------------- RUTAS -------------------------------------


class RutasOptionsView(TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/opciones.html'

    def get_items(self):
        items = []

        for region in models.Regiones.objects.all().order_by('numero'):
            if self.request.user.has_perm('usuarios.cpe_2018.rutas_{}.ver'.format(region.numero)):
                items.append({
                    'sican_categoria': 'Rutas: {0}'.format(region.nombre),
                    'sican_color': region.color,
                    'sican_order': 1,
                    'sican_url': '{0}/'.format(str(region.id)),
                    'sican_name': '{0}'.format(region.nombre),
                    'sican_icon': 'data_usage',
                    'sican_description': 'Asignación, cambio y trazabilidad de las rutas para los contratistas de la {0}.'.format(region.nombre)
                })


        return items

    def dispatch(self, request, *args, **kwargs):

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver"
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
        kwargs['title'] = "RUTAS"
        kwargs['items'] = self.get_items()
        return super(RutasOptionsView,self).get_context_data(**kwargs)


class RutasRegionListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/lista.html'


    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(region.numero)
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "RUTAS - {0}".format(region.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/'.format(region.id)
        kwargs['breadcrum_active'] = region.nombre
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.rutas_{0}.crear'.format(region.numero))
        kwargs['permiso_ruteo'] = self.request.user.has_perm('usuarios.cpe_2018.rutas_{0}.ruteo'.format(region.numero))
        return super(RutasRegionListView,self).get_context_data(**kwargs)





class ActividadesComponenteRutaListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero)
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/actividades/{1}/componente/{2}/'.format(
            self.region.id,
            self.ruta.id,
            self.componente.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.componente.nombre
        return super(ActividadesComponenteRutaListView,self).get_context_data(**kwargs)



class ToogleActividadesComponenteRutaListView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.entregable_ruta_object = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_entregable_ruta_object'])


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.is_superuser:

                self.entregable_ruta_object.para_pago = not self.entregable_ruta_object.para_pago
                self.entregable_ruta_object.save()

                return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')



class RutasRegionCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/crear.html'
    form_class = forms.RutasCreateForm
    success_url = "../"

    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(region.numero),
                "usuarios.cpe_2018.rutas_{0}.crear".format(region.numero)
            ]
        }
        return permissions

    def form_valid(self, form):

        contrato = models.Contratos.objects.get(id = form.cleaned_data['contrato'])
        estado = ''


        actividades_json = {}


        self.object = models.Rutas.objects.create(
            usuario_creacion = self.request.user,
            usuario_actualizacion = self.request.user,
            region = models.Regiones.objects.get(id = self.kwargs['pk']),
            nombre = form.cleaned_data['nombre'],
            contrato = contrato,
            estado = estado,
            actividades_json = json.dumps(actividades_json),
            visible = form.cleaned_data['visible']
        )

        form.cleaned_data.pop('nombre')
        form.cleaned_data.pop('contrato')
        radicados = form.cleaned_data['radicados']
        form.cleaned_data.pop('radicados')
        form.cleaned_data.pop('visible')

        for key in form.cleaned_data.keys():
            actividades_json[key] = form.cleaned_data[key]

        self.object.actividades_json = json.dumps(actividades_json)
        self.object.save()

        models.TrazabilidadRutas.objects.create(
            ruta = self.object,
            usuario_creacion = self.request.user,
            observacion = 'Creación de la ruta'
        )

        for radicado_id in radicados:
            radicado = models.Radicados.objects.get(id = radicado_id)
            radicado.ruta = self.object
            radicado.save()

            models.TrazabilidadRadicados.objects.create(
                radicado=radicado,
                usuario_creacion=self.request.user,
                observacion='Asignación a la ruta {0} del contratista {1}'.format(
                    self.object.nombre,
                    self.object.contrato.contratista.get_full_name()
                )
            )

        self.object.update_objects()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "NUEVA RUTA"
        kwargs['breadcrum_active'] = region.nombre
        kwargs['url_radicados'] = '/rest/v1.0/cpe_2018/rutas/autocomplete/radicados/{0}/'.format(region.id)
        kwargs['url_contratos'] = '/rest/v1.0/cpe_2018/rutas/autocomplete/contratos/'
        return super(RutasRegionCreateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk':self.kwargs['pk']}


class RutasRegionUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/editar.html'
    form_class = forms.RutasCreateForm
    success_url = "../../"

    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(region.numero),
                "usuarios.cpe_2018.rutas_{0}.editar".format(region.numero)
            ],
            "liquidacion": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(region.numero),
                "usuarios.cpe_2018.rutas_{0}.editar".format(region.numero),
                "usuarios.cpe_2018.rutas_{0}.liquidar".format(region.numero)
            ]
        }
        return permissions

    def form_valid(self, form):

        contrato = models.Contratos.objects.get(id=form.cleaned_data['contrato'])

        ruta_obj = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        ruta = models.Rutas.objects.filter(id = self.kwargs['pk_ruta'])


        actividades_json = {}


        ruta.update(
            usuario_actualizacion=self.request.user,
            nombre=form.cleaned_data['nombre'],
            contrato=contrato,
            actividades_json = json.dumps(actividades_json),
            visible=form.cleaned_data['visible']
        )

        form.cleaned_data.pop('nombre')
        form.cleaned_data.pop('contrato')
        radicados = form.cleaned_data['radicados']
        form.cleaned_data.pop('radicados')
        form.cleaned_data.pop('visible')

        for key in form.cleaned_data.keys():
            actividades_json[key] = form.cleaned_data[key]

        ruta.update(actividades_json = json.dumps(actividades_json))

        models.TrazabilidadRutas.objects.create(
            ruta = ruta_obj,
            usuario_creacion = self.request.user,
            observacion = 'Actualización de la ruta'
        )

        radicados_to_clean = []

        for radicado in models.Radicados.objects.filter(ruta = ruta_obj):

            if str(radicado.id) in radicados:
                radicados.remove(str(radicado.id))
                radicados_to_clean.append('sede&{0}'.format(str(radicado.id)))
            else:
                radicado.ruta = None
                radicado.save()

        models.EntregableRutaObject.objects.filter(
            estado__in = ['disponible','asignado'],
            padre__in = radicados_to_clean
        ).delete()


        for radicado_id in radicados:
            radicado = models.Radicados.objects.get(id = radicado_id)
            radicado.ruta = ruta_obj
            radicado.save()

            models.TrazabilidadRadicados.objects.create(
                radicado=radicado,
                usuario_creacion=self.request.user,
                observacion='Asignación a la ruta {0} del contratista {1}'.format(
                    ruta_obj.nombre,
                    ruta_obj.contrato.contratista.get_full_name()
                )
            )

        ruta_obj.update_objects()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        permissions = {
            "liquidacion": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(region.numero),
                "usuarios.cpe_2018.rutas_{0}.editar".format(region.numero),
                "usuarios.cpe_2018.rutas_{0}.liquidar".format(region.numero)
            ]
        }
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        kwargs['title'] = "EDITAR RUTA"
        kwargs['breadcrum_active'] = region.nombre
        kwargs['url_radicados'] = '/rest/v1.0/cpe_2018/rutas/autocomplete/radicados/{0}/'.format(region.id)
        kwargs['url_contratos'] = '/rest/v1.0/cpe_2018/rutas/autocomplete/contratos/'
        kwargs['breadcrum_active'] = region.nombre
        kwargs['breadcrum_active_1'] = ruta.nombre
        kwargs['permiso_liquidacion'] = self.request.user.has_perms(permissions.get('liquidacion'))
        return super(RutasRegionUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk': self.kwargs['pk'],
            'pk_ruta': self.kwargs['pk_ruta'],
        }



class RutasRegionEstadoView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/estado.html'
    form_class = forms.RutasEstadoForm
    success_url = "../"
    pk_url_kwarg = 'pk_ruta'
    model = models.Rutas

    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(region.numero),
                "usuarios.cpe_2018.rutas_{0}.editar".format(region.numero),
                "usuarios.cpe_2018.rutas_{0}.liquidar".format(region.numero)
            ]
        }
        return permissions

    def form_valid(self, form):
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.object = form.save()

        if form.cleaned_data['estado'] == 'Liquidación':
            ruta.cerrar_ruta()
        elif form.cleaned_data['estado'] == 'Reabrir':
            ruta.abrir_ruta()
            ruta.estado = ''
            ruta.save()
        else:
            pass
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        kwargs['title'] = "EDITAR RUTA"
        kwargs['breadcrum_1'] = region.nombre
        kwargs['breadcrum_active'] = ruta.nombre
        return super(RutasRegionEstadoView,self).get_context_data(**kwargs)



class ReportesRuteoView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    login_url = settings.LOGIN_URL

    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(region.numero),
                "usuarios.cpe_2018.rutas_{0}.informes".format(region.numero)
            ]
        }
        return permissions

    def dispatch(self, request, *args, **kwargs):
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Ruteo región {0}'.format(region.numero),
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_ruteo.delay(reporte.id, str(region.id))

        return HttpResponseRedirect('/reportes/')


class ComponentesRutasListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/lista.html'


    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(region.numero)
            ]
        }
        return permissions


    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        kwargs['title'] = "RUTA - {0} - {1}".format(ruta.nombre, ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/actividades/{1}/'.format(region.id, self.kwargs['pk_ruta'])
        kwargs['breadcrum_1'] = region.nombre
        kwargs['breadcrum_active'] = ruta.nombre
        return super(ComponentesRutasListView,self).get_context_data(**kwargs)



#---------------------------------- CUENTAS COBRO ---------------------------------


class RutasCuentasCobroListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/lista.html'


    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(region.numero)
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        kwargs['title'] = "CUENTAS DE COBRO RUTA - {0}".format(ruta.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/cuentas_cobro/{1}/'.format(region.id,ruta.id)
        kwargs['breadcrum_1'] = region.nombre
        kwargs['breadcrum_active'] = ruta.nombre
        return super(RutasCuentasCobroListView,self).get_context_data(**kwargs)


class RutasCuentasCobroDetalleListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/detalle.html'


    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(region.numero)
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        kwargs['title'] = "CUENTAS DE COBRO RUTA - {0}".format(ruta.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/cuentas_cobro/{1}/detalle/{2}/'.format(region.id,ruta.id,cuenta_cobro.id)
        kwargs['breadcrum_1'] = region.nombre
        kwargs['breadcrum_active'] = ruta.nombre
        kwargs['cuenta_cobro'] = cuenta_cobro
        return super(RutasCuentasCobroDetalleListView,self).get_context_data(**kwargs)



class RutasCuentasCobroDetalleComponenteListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/detalle_componente.html'


    def get_permission_required(self, request=None):
        self.region = models.Regiones.objects.get(id = self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CUENTAS DE COBRO RUTA - {0}".format(self.ruta.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/cuentas_cobro/{1}/detalle/{2}/componente/{3}/'.format(
            self.region.id,
            self.ruta.id,
            self.cuenta_cobro.id,
            self.componente.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.componente.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        return super(RutasCuentasCobroDetalleComponenteListView,self).get_context_data(**kwargs)


class RutasCuentasCobroDetalleRetomaListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/detalle_retoma.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
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
                return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CUENTAS DE COBRO RUTA - {0}".format(self.ruta.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/cuentas_cobro/{1}/detalle/{2}/componente/{3}/retoma'.format(
            self.region.id,
            self.ruta.id,
            self.cuenta_cobro.id,
            self.componente.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.componente.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        return super(RutasCuentasCobroDetalleRetomaListView,self).get_context_data(**kwargs)


class RutasCuentasCobroDetalleVerRetomaListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/detalle_retoma_ver.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.retoma = models.Retoma.objects.get(id=self.kwargs['pk_retoma'])
        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
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
                return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CUENTAS DE COBRO RUTA - {0}".format(self.ruta.nombre)
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.componente.nombre
        kwargs['breadcrum_active'] = self.retoma.radicado
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        kwargs['retoma'] = self.retoma
        return super(RutasCuentasCobroDetalleVerRetomaListView,self).get_context_data(**kwargs)


class RutasCuentasCobroDetalleVerRetomaTrazabilidadListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/detalle_retoma_trazabilidad.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.retoma = models.Retoma.objects.get(id=self.kwargs['pk_retoma'])
        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
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
                return HttpResponseRedirect('../')

    def get_items_registros(self):

        lista = []
        registros = models.RegistroRetoma.objects.filter(retoma = self.retoma).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CUENTAS DE COBRO RUTA - {0}".format(self.ruta.nombre)
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.componente.nombre
        kwargs['breadcrum_active'] = self.retoma.radicado
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        kwargs['retoma'] = self.retoma
        kwargs['registros'] = self.get_items_registros()
        return super(RutasCuentasCobroDetalleVerRetomaTrazabilidadListView,self).get_context_data(**kwargs)


class RutasCuentasCobroDetalleRadicadoListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/detalle_radicado.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
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
                return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/cuentas_cobro/{1}/detalle/{2}/componente/{3}/radicado/{4}/'.format(
            self.region.id,
            self.ruta.id,
            self.cuenta_cobro.id,
            self.componente.id,
            self.radicado.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.componente.nombre
        kwargs['breadcrum_active'] = self.radicado.numero
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        return super(RutasCuentasCobroDetalleRadicadoListView,self).get_context_data(**kwargs)


class RutasCuentasCobroDetalleRadicadoSoportesListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/detalle_radicado_lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
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

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/cuentas_cobro/{1}/detalle/{2}/componente/{3}/radicado/{4}/cargar/{5}/'.format(
            self.region.id,
            self.ruta.id,
            self.cuenta_cobro.id,
            self.componente.id,
            self.radicado.id,
            self.objeto_ruta.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.componente.nombre
        kwargs['breadcrum_4'] = self.radicado.numero
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro


        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            objetos = modelo.objects.filter(ruta=self.ruta, radicado=self.radicado)
            if objetos.count() > 0:
                if objetos.filter(estado = 'Nuevo').count() > 1:
                    raise NotImplementedError("No puede haber mas de 1 objeto nuevo")
                elif objetos.filter(estado = 'Nuevo').count() == 1:
                    kwargs['permiso_crear'] = False
                else:
                    if objetos.filter(estado='Aprobado').count() > 1:
                        raise NotImplementedError("No puede haber mas de 1 objeto aprobado")
                    elif objetos.filter(estado='Aprobado').count() == 1:
                        kwargs['permiso_crear'] = False
                    else:
                        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions.get('crear_actividad'))
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        return super(RutasCuentasCobroDetalleRadicadoSoportesListView,self).get_context_data(**kwargs)


class ActividadesSedeCuentaCobroVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/detalle_radicado_ver.html'


    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")



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

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.componente.nombre
        kwargs['breadcrum_4'] = self.radicado.numero
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        kwargs['soporte'] = self.soporte
        kwargs['objeto_ruta'] = self.objeto_ruta


        return super(ActividadesSedeCuentaCobroVerView,self).get_context_data(**kwargs)


class TrazabilidadSedeCuentaCobroRutaVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/detalle_radicado_ver_trazabilidad.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")

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

    def get_items_registros(self):

        lista = []
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])


        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
            registros = registro.objects.filter(modelo = self.soporte).order_by('-creation')
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.componente.nombre
        kwargs['breadcrum_4'] = self.radicado.numero
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        kwargs['soporte'] = self.soporte
        kwargs['objeto_ruta'] = self.objeto_ruta
        kwargs['registros'] = self.get_items_registros()

        return super(TrazabilidadSedeCuentaCobroRutaVerView,self).get_context_data(**kwargs)


class ActividadesSedeRutaCuentaCobroListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/lista_sede_ruta.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if self.objeto_ruta.entregable.modelo == 'talleres_fomento_uso':
                    return HttpResponseRedirect('../../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/cuentas_cobro/{1}/detalle/{2}/componente/{3}/cargar/{4}/'.format(
            self.region.id,
            self.ruta.id,
            self.cuenta_cobro.id,
            self.componente.id,
            self.objeto_ruta.id
        )

        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.componente.nombre
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)
            if modelo != None:
                try:
                    objeto = modelo.objects.get(ruta = self.ruta)
                except:
                    pass
                else:
                    kwargs['objeto'] = objeto
                    kwargs['permiso_crear'] = False
            else:
                pass
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        return super(ActividadesSedeRutaCuentaCobroListView,self).get_context_data(**kwargs)


class ActividadesSedeRutaCuentaCobroVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/ver_sede_ruta.html'


    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")

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

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.componente.nombre
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        kwargs['soporte'] = self.soporte
        kwargs['objeto_ruta'] = self.objeto_ruta

        return super(ActividadesSedeRutaCuentaCobroVerView,self).get_context_data(**kwargs)


class TrazabilidadSedeRutaCuentaCobroRutaVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/sede_ruta_trazabilidad.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")

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

    def get_items_registros(self):

        lista = []
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])


        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
            registros = registro.objects.filter(modelo = self.soporte).order_by('-creation')
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.componente.nombre
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        kwargs['soporte'] = self.soporte
        kwargs['objeto_ruta'] = self.objeto_ruta
        kwargs['registros'] = self.get_items_registros()

        return super(TrazabilidadSedeRutaCuentaCobroRutaVerView,self).get_context_data(**kwargs)


class FormacionRutaCuentaCobroListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/formacion/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        actividades_json = json.loads(self.ruta.actividades_json)
        cantidad_formacion = actividades_json['componente_' + str(models.Componentes.objects.get(numero='2').id)]

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if cantidad_formacion <= 0:
                    return HttpResponseRedirect('../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/cuentas_cobro/{1}/detalle/{2}/formacion/'.format(
            self.region.id,
            self.ruta.id,
            self.cuenta_cobro.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.cuenta_cobro.id

        return super(FormacionRutaCuentaCobroListView,self).get_context_data(**kwargs)


class DocentesActividadesRutaCuentaCobroListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/formacion/grupos/lista.html'


    def dispatch(self, request, *args, **kwargs):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])


        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/cuentas_cobro/{1}/detalle/{2}/formacion/actividades/{3}/'.format(
            self.region.id,
            self.ruta.id,
            self.cuenta_cobro.id,
            self.grupo.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.cuenta_cobro.id
        kwargs['breadcrum_active'] = self.grupo.get_nombre_grupo()
        return super(DocentesActividadesRutaCuentaCobroListView,self).get_context_data(**kwargs)


class DocentesActividadesEntregablesRutaCuentaCobroListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/formacion/grupos/evidencias/lista.html'

    def dispatch(self, request, *args, **kwargs):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/cuentas_cobro/{1}/detalle/{2}/formacion/actividades/{3}/evidencias/{4}/'.format(
            self.region.id,
            self.ruta.id,
            self.cuenta_cobro.id,
            self.grupo.id,
            self.entregable.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.cuenta_cobro.id
        kwargs['breadcrum_4'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_active'] = self.entregable.nombre

        return super(DocentesActividadesEntregablesRutaCuentaCobroListView,self).get_context_data(**kwargs)


class DocentesActividadesEntregablesRutaVerCuentaCobroView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/formacion/grupos/evidencias/ver.html'

    def dispatch(self, request, *args, **kwargs):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])


        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
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

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.cuenta_cobro.id
        kwargs['breadcrum_4'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_5'] = self.entregable.nombre


        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])

        kwargs['objeto'] = objeto
        kwargs['breadcrum_active'] = objeto.id

        return super(DocentesActividadesEntregablesRutaVerCuentaCobroView,self).get_context_data(**kwargs)


class TrazabilidadDocentesActividadesEntregablesRutaVerCuentaCobroView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/cuentas_cobro/formacion/grupos/evidencias/trazabilidad.html'

    def dispatch(self, request, *args, **kwargs):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])


        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
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
                return HttpResponseRedirect('../')

    def get_items_registros(self):

        lista = []

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            registro = self.modelos[self.entregable.modelo]['registro']
            modelo = self.modelos[self.entregable.modelo]['modelo']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])
            registros = registro.objects.filter(modelo = objeto).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())

        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.cuenta_cobro.id
        kwargs['breadcrum_4'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_5'] = self.entregable.nombre

        kwargs['registros'] = self.get_items_registros()


        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])

        kwargs['breadcrum_active'] = objeto.id

        return super(TrazabilidadDocentesActividadesEntregablesRutaVerCuentaCobroView,self).get_context_data(**kwargs)




#----------------------------- CUENTAS COBRO MIS RUTAS ------------------------------


class MisRutasCuentasCobroDetalleListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/detalle.html'


    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        kwargs['title'] = "CUENTAS DE COBRO RUTA - {0}".format(ruta.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/cuentas_cobro/{0}/detalle/{1}/'.format(ruta.id,cuenta_cobro.id)
        kwargs['breadcrum_active'] = ruta.nombre
        kwargs['cuenta_cobro'] = cuenta_cobro
        return super(MisRutasCuentasCobroDetalleListView,self).get_context_data(**kwargs)


class MisRutasCuentasCobroDetalleComponenteListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/detalle_componente.html'


    def get_permission_required(self, request=None):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CUENTAS DE COBRO RUTA - {0}".format(self.ruta.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/cuentas_cobro/{0}/detalle/{1}/componente/{2}/'.format(
            self.ruta.id,
            self.cuenta_cobro.id,
            self.componente.id
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.componente.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        return super(MisRutasCuentasCobroDetalleComponenteListView,self).get_context_data(**kwargs)


class MisRutasCuentasCobroDetalleRetomaListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/detalle_retoma.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
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
                return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CUENTAS DE COBRO RUTA - {0}".format(self.ruta.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/cuentas_cobro/{0}/detalle/{1}/componente/{2}/retoma'.format(
            self.ruta.id,
            self.cuenta_cobro.id,
            self.componente.id
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.componente.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        return super(MisRutasCuentasCobroDetalleRetomaListView,self).get_context_data(**kwargs)

class MisRutasCuentasCobroDetalleVerRetomaListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/detalle_retoma_ver.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.retoma = models.Retoma.objects.get(id=self.kwargs['pk_retoma'])
        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
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
                return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CUENTAS DE COBRO RUTA - {0}".format(self.ruta.nombre)
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.componente.nombre
        kwargs['breadcrum_active'] = self.retoma.radicado
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        kwargs['retoma'] = self.retoma
        return super(MisRutasCuentasCobroDetalleVerRetomaListView,self).get_context_data(**kwargs)

class MisRutasCuentasCobroDetalleVerRetomaTrazabilidadListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/detalle_retoma_trazabilidad.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.retoma = models.Retoma.objects.get(id=self.kwargs['pk_retoma'])
        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
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
                return HttpResponseRedirect('../')

    def get_items_registros(self):

        lista = []
        registros = models.RegistroRetoma.objects.filter(retoma = self.retoma).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CUENTAS DE COBRO RUTA - {0}".format(self.ruta.nombre)
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.componente.nombre
        kwargs['breadcrum_active'] = self.retoma.radicado
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        kwargs['retoma'] = self.retoma
        kwargs['registros'] = self.get_items_registros()
        return super(MisRutasCuentasCobroDetalleVerRetomaTrazabilidadListView,self).get_context_data(**kwargs)


class ActividadesSedeMisRutasCuentaCobroListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/lista_sede_ruta.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if self.objeto_ruta.entregable.modelo == 'talleres_fomento_uso':
                    return HttpResponseRedirect('../../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/cuentas_cobro/{0}/detalle/{1}/componente/{2}/cargar/{3}/'.format(
            self.ruta.id,
            self.cuenta_cobro.id,
            self.componente.id,
            self.objeto_ruta.id
        )

        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.componente.nombre
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)
            if modelo != None:
                try:
                    objeto = modelo.objects.get(ruta = self.ruta)
                except:
                    pass
                else:
                    kwargs['objeto'] = objeto
                    kwargs['permiso_crear'] = False
            else:
                pass
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        return super(ActividadesSedeMisRutasCuentaCobroListView,self).get_context_data(**kwargs)


class ActividadesSedeMisRutaCuentaCobroVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/ver_sede_ruta.html'


    def dispatch(self, request, *args, **kwargs):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")

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

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.componente.nombre
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        kwargs['soporte'] = self.soporte
        kwargs['objeto_ruta'] = self.objeto_ruta

        return super(ActividadesSedeMisRutaCuentaCobroVerView,self).get_context_data(**kwargs)


class TrazabilidadSedeRutaCuentaCobroMisRutasVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/sede_ruta_trazabilidad.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")

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

    def get_items_registros(self):

        lista = []
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])


        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
            registros = registro.objects.filter(modelo = self.soporte).order_by('-creation')
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.componente.nombre
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        kwargs['soporte'] = self.soporte
        kwargs['objeto_ruta'] = self.objeto_ruta
        kwargs['registros'] = self.get_items_registros()

        return super(TrazabilidadSedeRutaCuentaCobroMisRutasVerView,self).get_context_data(**kwargs)


class MisRutasCuentasCobroDetalleRadicadoListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/detalle_radicado.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
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
                return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/cuentas_cobro/{0}/detalle/{1}/componente/{2}/radicado/{3}/'.format(
            self.ruta.id,
            self.cuenta_cobro.id,
            self.componente.id,
            self.radicado.id
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.componente.nombre
        kwargs['breadcrum_active'] = self.radicado.numero
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        return super(MisRutasCuentasCobroDetalleRadicadoListView,self).get_context_data(**kwargs)


class MisRutasCuentasCobroDetalleRadicadoSoportesListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/detalle_radicado_lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
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

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/cuentas_cobro/{0}/detalle/{1}/componente/{2}/radicado/{3}/cargar/{4}/'.format(
            self.ruta.id,
            self.cuenta_cobro.id,
            self.componente.id,
            self.radicado.id,
            self.objeto_ruta.id
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.componente.nombre
        kwargs['breadcrum_3'] = self.radicado.numero
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro


        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            objetos = modelo.objects.filter(ruta=self.ruta, radicado=self.radicado)
            if objetos.count() > 0:
                if objetos.filter(estado = 'Nuevo').count() > 1:
                    raise NotImplementedError("No puede haber mas de 1 objeto nuevo")
                elif objetos.filter(estado = 'Nuevo').count() == 1:
                    kwargs['permiso_crear'] = False
                else:
                    if objetos.filter(estado='Aprobado').count() > 1:
                        raise NotImplementedError("No puede haber mas de 1 objeto aprobado")
                    elif objetos.filter(estado='Aprobado').count() == 1:
                        kwargs['permiso_crear'] = False
                    else:
                        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions.get('crear_actividad'))
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        return super(MisRutasCuentasCobroDetalleRadicadoSoportesListView,self).get_context_data(**kwargs)


class MisActividadesSedeCuentaCobroVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/detalle_radicado_ver.html'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")



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

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.componente.nombre
        kwargs['breadcrum_3'] = self.radicado.numero
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        kwargs['soporte'] = self.soporte
        kwargs['objeto_ruta'] = self.objeto_ruta


        return super(MisActividadesSedeCuentaCobroVerView,self).get_context_data(**kwargs)


class MisTrazabilidadSedeCuentaCobroRutaVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/detalle_radicado_ver_trazabilidad.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")

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

    def get_items_registros(self):

        lista = []
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])


        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
            registros = registro.objects.filter(modelo = self.soporte).order_by('-creation')
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.componente.nombre
        kwargs['breadcrum_3'] = self.radicado.numero
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['cuenta_cobro'] = self.cuenta_cobro
        kwargs['soporte'] = self.soporte
        kwargs['objeto_ruta'] = self.objeto_ruta
        kwargs['registros'] = self.get_items_registros()

        return super(MisTrazabilidadSedeCuentaCobroRutaVerView,self).get_context_data(**kwargs)


class MiFormacionRutaCuentaCobroListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/formacion/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        actividades_json = json.loads(self.ruta.actividades_json)
        cantidad_formacion = actividades_json['componente_' + str(models.Componentes.objects.get(numero='2').id)]

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if cantidad_formacion <= 0:
                    return HttpResponseRedirect('../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/cuentas_cobro/{0}/detalle/{1}/formacion/'.format(
            self.ruta.id,
            self.cuenta_cobro.id
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.cuenta_cobro.id

        return super(MiFormacionRutaCuentaCobroListView,self).get_context_data(**kwargs)


class MisDocentesActividadesRutaCuentaCobroListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/formacion/grupos/lista.html'


    def dispatch(self, request, *args, **kwargs):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])


        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/cuentas_cobro/{0}/detalle/{1}/formacion/actividades/{2}/'.format(
            self.ruta.id,
            self.cuenta_cobro.id,
            self.grupo.id
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.cuenta_cobro.id
        kwargs['breadcrum_active'] = self.grupo.get_nombre_grupo()
        return super(MisDocentesActividadesRutaCuentaCobroListView,self).get_context_data(**kwargs)


class MisDocentesActividadesEntregablesRutaCuentaCobroListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/formacion/grupos/evidencias/lista.html'

    def dispatch(self, request, *args, **kwargs):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/misrutas/cuentas_cobro/{0}/detalle/{1}/formacion/actividades/{2}/evidencias/{3}/'.format(
            self.ruta.id,
            self.cuenta_cobro.id,
            self.grupo.id,
            self.entregable.id
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.cuenta_cobro.id
        kwargs['breadcrum_3'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_active'] = self.entregable.nombre

        return super(MisDocentesActividadesEntregablesRutaCuentaCobroListView,self).get_context_data(**kwargs)


class MisDocentesActividadesEntregablesRutaVerCuentaCobroView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/formacion/grupos/evidencias/ver.html'

    def dispatch(self, request, *args, **kwargs):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])


        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
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

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.cuenta_cobro.id
        kwargs['breadcrum_3'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_4'] = self.entregable.nombre


        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])

        kwargs['objeto'] = objeto
        kwargs['breadcrum_active'] = objeto.id

        return super(MisDocentesActividadesEntregablesRutaVerCuentaCobroView,self).get_context_data(**kwargs)


class MisTrazabilidadDocentesActividadesEntregablesRutaVerCuentaCobroView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/misrutas/cuentas_cobro/detalle/formacion/grupos/evidencias/trazabilidad.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])


        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
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
                return HttpResponseRedirect('../')

    def get_items_registros(self):

        lista = []

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            registro = self.modelos[self.entregable.modelo]['registro']
            modelo = self.modelos[self.entregable.modelo]['modelo']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])
            registros = registro.objects.filter(modelo = objeto).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())

        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.cuenta_cobro.id
        kwargs['breadcrum_3'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_4'] = self.entregable.nombre

        kwargs['registros'] = self.get_items_registros()


        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])

        kwargs['breadcrum_active'] = objeto.id

        return super(MisTrazabilidadDocentesActividadesEntregablesRutaVerCuentaCobroView,self).get_context_data(**kwargs)


#------------------------------------- ACCESO -------------------------------------


class ActividadesComponenteRutaListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero)
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/actividades/{1}/componente/{2}/'.format(
            self.region.id,
            self.ruta.id,
            self.componente.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.componente.nombre
        return super(ActividadesComponenteRutaListView,self).get_context_data(**kwargs)


#-------------------------- RETOMA ---------------------------


class ActividadesRetomaRutaListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/retoma/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "ver_retoma": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.ver".format(self.region.numero)
            ],
            "crear_retoma": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.crear".format(self.region.numero)
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_retoma')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/actividades/{1}/componente/{2}/retoma/'.format(
            self.region.id,
            self.ruta.id,
            self.componente.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.componente.nombre
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions.get('crear_retoma'))
        return super(ActividadesRetomaRutaListView,self).get_context_data(**kwargs)




class VerificarRetomaRutaListView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.retoma = models.Retoma.objects.get(id=self.kwargs['pk_retoma'])


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.is_superuser:

                objetos_disponibles = models.EntregableRutaObject.objects.filter(ruta=self.ruta, estado='asignado',padre="ruta&estrategia&{0}".format(self.ruta.id))

                objetos_retoma = models.EntregableRutaObject.objects.filter(soporte = "retoma&{0}".format(self.retoma.id))

                if objetos_retoma.count() < self.retoma.bolsas and self.retoma.estado == "Aprobado":
                    pendientes = self.retoma.bolsas - objetos_retoma.count()

                    if objetos_disponibles.count() < pendientes:
                        objetos_disponibles.update(estado='Reportado',soporte="retoma&{0}".format(self.retoma.id))

                    else:
                        ids = objetos_disponibles[0:pendientes].values_list('id', flat = True)
                        models.EntregableRutaObject.objects.filter(id__in=ids).update(estado='Reportado',soporte="retoma&{0}".format(self.retoma.id))
                        self.retoma.estado_observacion = ''
                        self.retoma.save()

                return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')





class RetomaRutaCreateListView(CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/retoma/crear.html'
    form_class = forms.RetomaForm
    success_url = "../"
    model = models.Retoma

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "crear_retoma": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.crear".format(self.region.numero)
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if self.ruta.estado == 'Liquidación':
                return HttpResponseRedirect('../')
            else:
                if request.user.has_perms(self.permissions.get('crear_retoma')):
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect('../')

    def get_bolsas_calculadora(self, cpu, trc, lcd, portatil, impresora, tableta):
        bolsas = cpu*0.5 + trc*0.5 + lcd*0.5 + portatil*0.1 + impresora*0.5 + tableta*0.033
        if bolsas > 0.0 and bolsas < 1.0:
            return round(1)
        else:
            return round(bolsas)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        self.object.bolsas = self.get_bolsas_calculadora(
            form.cleaned_data['cpu'],
            form.cleaned_data['trc'],
            form.cleaned_data['lcd'],
            form.cleaned_data['portatil'],
            form.cleaned_data['impresora'],
            form.cleaned_data['tableta']
        )
        self.object.estado = 'Nuevo'
        self.object.save()
        models.RegistroRetoma.objects.create(
            retoma = self.object,
            usuario = self.request.user,
            delta = json.dumps(functions.delta_registro_retoma(self.request,self.object,form.cleaned_data['delta'], 'CREACIÓN RETOMA'))
        )
        return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())

        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.componente.nombre
        kwargs['url_autocomplete_municipio'] = '/rest/v1.0/cpe_2018/rutas/autocomplete/municipios/'
        kwargs['file_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['file2_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'

        return super(RetomaRutaCreateListView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk_ruta': self.kwargs['pk_ruta']
        }


class RetomaRutaUpdateListView(UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/retoma/editar.html'
    form_class = forms.RetomaForm
    success_url = "../"
    model = models.Retoma
    pk_url_kwarg = 'pk_retoma'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.retoma = models.Retoma.objects.get(id=self.kwargs['pk_retoma'])

        self.permissions = {
            "editar_retoma": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.editar".format(self.region.numero)
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('editar_retoma')):
                if self.retoma.estado == 'Aprobado' or self.retoma.estado == 'Rechazado':
                    return HttpResponseRedirect('../../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_bolsas_calculadora(self, cpu, trc, lcd, portatil, impresora, tableta):
        bolsas = cpu*0.5 + trc*0.5 + lcd*0.5 + portatil*0.1 + impresora*0.5 + tableta*0.033
        if bolsas > 0.0 and bolsas < 1.0:
            return round(1)
        else:
            return round(bolsas)

    def form_valid(self, form):
        self.object = form.save()
        self.object.estado = 'Actualizado'
        self.object.bolsas = self.get_bolsas_calculadora(
            form.cleaned_data['cpu'],
            form.cleaned_data['trc'],
            form.cleaned_data['lcd'],
            form.cleaned_data['portatil'],
            form.cleaned_data['impresora'],
            form.cleaned_data['tableta']
        )
        self.object.save()
        models.RegistroRetoma.objects.create(
            retoma=self.object,
            usuario=self.request.user,
            delta = json.dumps(functions.delta_registro_retoma(self.request,self.object,form.cleaned_data['delta'], 'ACTUALIZACIÓN RETOMA'))
        )
        return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.retoma.radicado
        kwargs['breadcrum_active'] = self.componente.nombre
        kwargs['url_autocomplete_municipio'] = '/rest/v1.0/cpe_2018/rutas/autocomplete/municipios/'
        kwargs['file_url'] = self.retoma.pretty_print_url_file()
        kwargs['file2_url'] = self.retoma.pretty_print_url_file2()

        return super(RetomaRutaUpdateListView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk_retoma': self.kwargs['pk_retoma'],
            'pk_ruta': self.kwargs['pk_ruta'],
            'update': True
        }


class RetomaRutaDeleteListView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.retoma = models.Retoma.objects.get(id=self.kwargs['pk_retoma'])

        self.permissions = {
            "eliminar_retoma": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.eliminar".format(self.region.numero)
            ]
        }


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('eliminar_retoma')):
                if self.retoma.estado == 'Aprobado' or self.retoma.estado == 'Rechazado':
                    return HttpResponseRedirect('../../')

                else:
                    if self.retoma.red == None:
                        if request.user.has_perms(self.permissions.get('eliminar_retoma')):
                            models.RegistroRetoma.objects.filter(retoma=self.retoma).delete()
                            self.retoma.delete()

                    return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')


class RetomaRutaVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/retoma/ver.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.retoma = models.Retoma.objects.get(id=self.kwargs['pk_retoma'])

        self.permissions = {
            "ver_retoma": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.ver".format(self.region.numero)
            ],
            "calificar_retoma": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.calificar".format(self.region.numero)
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_retoma')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['retoma'] = self.retoma
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.retoma.radicado
        kwargs['breadcrum_active'] = self.componente.nombre
        kwargs['permiso_calificacion'] = self.request.user.has_perms(self.permissions.get('calificar_retoma')) and self.retoma.estado == 'Nuevo'
        return super(RetomaRutaVerView,self).get_context_data(**kwargs)


class TrazabilidadRetomaRutaVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/retoma/trazabilidad.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.retoma = models.Retoma.objects.get(id=self.kwargs['pk_retoma'])

        self.permissions = {
            "ver_retoma": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.ver".format(self.region.numero)
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_retoma')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def get_items_registros(self):

        lista = []
        registros = models.RegistroRetoma.objects.filter(retoma = self.retoma).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/actividades/{1}/componente/{2}/retoma/'.format(
            self.region.id,
            self.ruta.id,
            self.componente.id
        )
        kwargs['retoma'] = self.retoma
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.retoma.radicado
        kwargs['breadcrum_active'] = self.componente.nombre
        kwargs['registros'] = self.get_items_registros()
        return super(TrazabilidadRetomaRutaVerView,self).get_context_data(**kwargs)


class CalificarRetomaRutaView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/retoma/calificar.html'
    form_class = forms.CalificacionRetomaForm
    success_url = "../"

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.retoma = models.Retoma.objects.get(id=self.kwargs['pk_retoma'])

        self.permissions = {
            "calificar_retoma": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.calificar".format(self.region.numero)
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('calificar_retoma')):
                if self.retoma.estado == 'Aprobado' or self.retoma.estado == 'Rechazado':
                    return HttpResponseRedirect('../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    @transaction.atomic
    def form_valid(self, form):

        retoma = models.Retoma.objects.filter(id = self.retoma.id).select_for_update()

        if form.cleaned_data['estado'] == 'Aprobado':

            objetos = models.EntregableRutaObject.objects.filter(ruta=self.ruta, estado='asignado',padre="ruta&estrategia&{0}".format(self.ruta.id))

            if objetos.count() >= retoma[0].bolsas:
                ids = objetos[0:retoma[0].bolsas].values_list('id', flat=True)
                models.EntregableRutaObject.objects.filter(id__in=ids).update(estado='Reportado',soporte="retoma&{0}".format(retoma[0].id))
            else:
                retoma.update(estado_observacion='Pendiente para pago')
                objetos.update(estado='Reportado', soporte="retoma&{0}".format(retoma[0].id))
                #raise ValueError(
                #    'La cantidad de bolsas aprobadas en la retoma es superior a la dispuesta en el ruteo.'
                #)


        models.RegistroRetoma.objects.create(
            retoma=retoma[0],
            usuario=self.request.user,
            delta=json.dumps(
                functions.delta_registro_calificacion_retoma(self.request,form.cleaned_data['estado'], form.cleaned_data['delta']))
        )

        retoma.update(estado = form.cleaned_data['estado'])

        return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.retoma.radicado
        kwargs['breadcrum_active'] = self.componente.nombre

        return super(CalificarRetomaRutaView,self).get_context_data(**kwargs)



#---------------------- ACTIVIDADES SEDE X RUTA ---------------------


class ActividadesSedeRutaListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/sede_ruta/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "ver_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero)
            ],
            "crear_actividad": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.crear".format(self.region.numero)
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_actividades')):
                if self.objeto_ruta.entregable.modelo == 'talleres_fomento_uso':
                    return HttpResponseRedirect('../../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/actividades/{1}/componente/{2}/cargar/{3}/'.format(
            self.region.id,
            self.ruta.id,
            self.componente.id,
            self.objeto_ruta.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions.get('crear_actividad'))

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)
            if modelo != None:
                try:
                    objeto = modelo.objects.get(ruta = self.ruta)
                except:
                    pass
                else:
                    kwargs['objeto'] = objeto
                    kwargs['permiso_crear'] = False
            else:
                pass
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        return super(ActividadesSedeRutaListView,self).get_context_data(**kwargs)


class ActividadesSedeRutaCreateView(CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/sede_ruta/crear.html'
    success_url = "../"

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "crear_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.crear".format(self.region.numero)
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        objeto = None

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                try:
                    objeto = modelo.objects.get(ruta = self.ruta)
                except:
                    pass
            else:
                pass
        else:
            raise NotImplementedError("EL modelo no esta establecido")



        if objeto != None:
            return HttpResponseRedirect('../')

        else:

            if not request.user.is_authenticated:
                return HttpResponseRedirect(self.login_url)
            else:
                if self.ruta.estado == 'Liquidación':
                    return HttpResponseRedirect('../')
                else:
                    if request.user.has_perms(self.permissions.get('crear_actividades')):
                        if request.method.lower() in self.http_method_names:
                            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                        else:
                            handler = self.http_method_not_allowed
                        return handler(request, *args, **kwargs)
                    else:
                        return HttpResponseRedirect('../')

    def get_form_class(self):

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            return self.modelos.get(self.objeto_ruta.entregable.modelo)['formulario']
        else:
            raise NotImplementedError("EL modelo no esta establecido")

    def form_valid(self, form):


        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
        else:
            raise NotImplementedError("EL modelo no esta establecido")

        if modelo != None and registro != None:

            objeto = modelo.objects.create(ruta=self.ruta, fecha=form.cleaned_data['fecha'])
            objeto.file = form.cleaned_data['file']
            objeto.nombre = self.objeto_ruta.entregable.nombre
            objeto.estado = "Nuevo"
            objeto.save()

            self.objeto_ruta.soporte = '{0}&{1}'.format(self.objeto_ruta.entregable.modelo,objeto.id)
            self.objeto_ruta.save()

            registro.objects.create(
                modelo=objeto,
                usuario=self.request.user,
                delta=json.dumps(
                    functions.delta_registro_sede_ruta(self.request, form.cleaned_data['delta'],
                                                       'Creación: {0}'.format(objeto.nombre)))
            )

        return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre


        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
        else:
            raise NotImplementedError("EL modelo no esta establecido")

        kwargs['file_url'] = '<p style="display:inline;">No hay archivos cargados.</p>'



        return super(ActividadesSedeRutaCreateView,self).get_context_data(**kwargs)


class ActividadesSedeRutaUpdateView(UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/sede_ruta/editar.html'
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "editar_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.editar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('editar_actividades')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_object(self, queryset=None):
        return self.soporte

    def get_form_class(self):

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            return self.modelos.get(self.objeto_ruta.entregable.modelo)['formulario']
        else:
            raise NotImplementedError("EL modelo no esta establecido")

    def form_valid(self, form):

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
        else:
            raise NotImplementedError("EL modelo no esta establecido")

        if modelo != None and registro != None:

            try:
                objeto = modelo.objects.get(ruta = self.ruta)
            except:
                raise NotImplementedError("No existe el objeto")

            objeto.file = form.cleaned_data['file']
            objeto.fecha = form.cleaned_data['fecha']
            objeto.nombre = self.objeto_ruta.entregable.nombre
            objeto.estado = "Actualizado"
            objeto.save()

            self.objeto_ruta.soporte = '{0}&{1}'.format(self.objeto_ruta.entregable.modelo,objeto.id)
            self.objeto_ruta.save()

            registro.objects.create(
                modelo=objeto,
                usuario=self.request.user,
                delta=json.dumps(
                    functions.delta_registro_sede_ruta(self.request, form.cleaned_data['delta'],
                                                       'Actualización: {0}'.format(objeto.nombre)))
            )

        return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())

        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre

        kwargs['file_url'] = self.soporte.pretty_print_url_file()

        return super(ActividadesSedeRutaUpdateView,self).get_context_data(**kwargs)


class ActividadesSedeRutaDeleteListView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "eliminar_actividad": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.eliminar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('eliminar_actividad')):
                if self.objeto_ruta.estado == 'Aprobado':
                    return HttpResponseRedirect('../../')

                else:
                    if self.objeto_ruta.entregable.modelo in self.modelos.keys():
                        modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
                        registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
                    else:
                        raise NotImplementedError("EL modelo no esta establecido")

                    if modelo != None and registro != None:
                        objeto = modelo.objects.get(id=self.kwargs['pk_soporte'])

                        self.objeto_ruta.soporte = ''
                        self.objeto_ruta.save()

                        registro.objects.filter(modelo=objeto).delete()
                        objeto.delete()

                    return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')


class ActividadesSedeRutaVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/sede_ruta/ver.html'


    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "ver_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero)
            ],
            "calificar_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.calificar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_actividades')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['soporte'] = self.soporte
        kwargs['objeto_ruta'] = self.objeto_ruta
        kwargs['permiso_calificacion'] = self.request.user.has_perms(self.permissions.get('calificar_actividades')) and self.soporte.estado != 'Aprobado'

        return super(ActividadesSedeRutaVerView,self).get_context_data(**kwargs)


class TrazabilidadSedeRutaVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/sede_ruta/trazabilidad.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "ver_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero)
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_actividades')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def get_items_registros(self):

        lista = []
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])


        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
            registros = registro.objects.filter(modelo = self.soporte).order_by('-creation')
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['registros'] = self.get_items_registros()

        return super(TrazabilidadSedeRutaVerView,self).get_context_data(**kwargs)


class CalificarSedeRutaVerView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/sede_ruta/calificar.html'
    form_class = forms.CalificacionSedeRutaForm
    success_url = "../"

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "calificar_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.calificar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")



        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('calificar_actividades')):
                if self.soporte != None:
                    if self.soporte.estado == 'Aprobado':
                        return HttpResponseRedirect('../')
                    else:
                        if request.method.lower() in self.http_method_names:
                            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                        else:
                            handler = self.http_method_not_allowed
                        return handler(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect('../')
            else:
                return HttpResponseRedirect('../')

    def form_valid(self, form):

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
        else:
            raise NotImplementedError("EL modelo no esta establecido")

        registro.objects.create(
            modelo = self.soporte,
            usuario=self.request.user,
            delta=json.dumps(
                functions.delta_registro_calificacion_sede_ruta(self.request, form.cleaned_data['delta'],
                                                                'Calificación: {0}'.format(
                                                                    form.cleaned_data['estado'])))
        )

        if self.soporte != None:

            self.soporte.estado = form.cleaned_data['estado']
            self.soporte.save()

            if form.cleaned_data['estado'] == 'Aprobado':
                self.objeto_ruta.estado = 'Reportado'
                self.objeto_ruta.soporte = '{0}&{1}'.format(self.objeto_ruta.entregable.modelo, self.soporte.id)
                self.objeto_ruta.save()

            return HttpResponseRedirect('../')

        else:
            return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre

        return super(CalificarSedeRutaVerView,self).get_context_data(**kwargs)



#------------------------- ACTIVIDADES RADICADO -----------------------


class ActividadesComponenteRutaRadicadoListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/radicados/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])

        self.permissions = {
            "ver_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero)
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_actividades')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/actividades/{1}/componente/{2}/radicado/{3}/'.format(
            self.region.id,
            self.ruta.id,
            self.componente.id,
            self.radicado.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.componente.nombre
        kwargs['breadcrum_active'] = self.radicado.numero
        return super(ActividadesComponenteRutaRadicadoListView,self).get_context_data(**kwargs)


class ToogleActividadesComponenteRutaRadicadoListView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.entregable_ruta_object = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_entregable_ruta_object'])


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.is_superuser:

                self.entregable_ruta_object.para_pago = not self.entregable_ruta_object.para_pago
                self.entregable_ruta_object.save()

                return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')


class ActividadesSedeListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/sede/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "ver_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero)
            ],
            "crear_actividad": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.crear".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_actividades')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/actividades/{1}/componente/{2}/radicado/{3}/cargar/{4}/'.format(
            self.region.id,
            self.ruta.id,
            self.componente.id,
            self.radicado.id,
            self.objeto_ruta.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.radicado.numero
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions.get('crear_actividad'))


        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            objetos = modelo.objects.filter(ruta=self.ruta, radicado=self.radicado)
            if objetos.count() > 0:
                if objetos.filter(estado = 'Nuevo').count() > 1:
                    raise NotImplementedError("No puede haber mas de 1 objeto nuevo")
                elif objetos.filter(estado = 'Nuevo').count() == 1:
                    kwargs['permiso_crear'] = False
                else:
                    if objetos.filter(estado='Aprobado').count() > 1:
                        raise NotImplementedError("No puede haber mas de 1 objeto aprobado")
                    elif objetos.filter(estado='Aprobado').count() == 1:
                        kwargs['permiso_crear'] = False
                    else:
                        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions.get('crear_actividad'))
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        return super(ActividadesSedeListView,self).get_context_data(**kwargs)


class ActividadesSedeCreateView(CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/sede/crear.html'
    success_url = "../"

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "crear_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.crear".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }


        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            objetos = modelo.objects.filter(ruta=self.ruta, radicado=self.radicado)
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('crear_actividades')):

                if self.ruta.estado == 'Liquidación':
                    return HttpResponseRedirect('../')
                else:
                    if objetos.count() > 0:
                        if objetos.filter(estado='Nuevo').count() > 1:
                            raise NotImplementedError("No puede haber mas de 1 objeto nuevo")
                        elif objetos.filter(estado='Nuevo').count() == 1:
                            return HttpResponseRedirect('../')
                        else:
                            if objetos.filter(estado='Aprobado').count() > 1:
                                raise NotImplementedError("No puede haber mas de 1 objeto aprobado")
                            elif objetos.filter(estado='Aprobado').count() == 1:
                                return HttpResponseRedirect('../')
                            else:
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
                return HttpResponseRedirect('../')

    def get_form_class(self):

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            return self.modelos.get(self.objeto_ruta.entregable.modelo)['formulario']
        else:
            raise NotImplementedError("EL modelo no esta establecido")

    def form_valid(self, form):

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
        else:
            raise NotImplementedError("EL modelo no esta establecido")

        if modelo != None and registro != None:

            objeto = modelo.objects.create(ruta=self.ruta, fecha=form.cleaned_data['fecha'])
            objeto.radicado = self.radicado
            objeto.file = form.cleaned_data['file']
            objeto.nombre = self.objeto_ruta.entregable.nombre
            objeto.estado = "Nuevo"

            if 'tipo' in form.cleaned_data.keys():
                objeto.tipo = form.cleaned_data['tipo']

            objeto.save()

            self.objeto_ruta.soporte = '{0}&{1}'.format(self.objeto_ruta.entregable.modelo,objeto.id)
            self.objeto_ruta.save()

            registro.objects.create(
                modelo=objeto,
                usuario=self.request.user,
                delta=json.dumps(
                    functions.delta_registro_sede_ruta(self.request, form.cleaned_data['delta'],
                                                       'Creación: {0}'.format(objeto.nombre)))
            )

        return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.radicado.numero
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['file_url'] = '<p style="display:inline;">No hay archivos cargados.</p>'

        return super(ActividadesSedeCreateView,self).get_context_data(**kwargs)


class ActividadesSedeUpdateView(UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/sede/editar.html'
    success_url = "../"

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "editar_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.editar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            self.soporte = modelo.objects.get(id = self.kwargs['pk_soporte'])
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('editar_actividades')):
                if self.soporte.estado == 'Nuevo' or self.soporte.estado == 'Actualizado':
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
                else:
                    return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

    def get_object(self, queryset=None):
        return self.soporte

    def get_form_class(self):

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            return self.modelos.get(self.objeto_ruta.entregable.modelo)['formulario']
        else:
            raise NotImplementedError("EL modelo no esta establecido")

    def form_valid(self, form):

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
        else:
            raise NotImplementedError("EL modelo no esta establecido")

        if modelo != None and registro != None:

            self.soporte.file = form.cleaned_data['file']
            self.soporte.fecha = form.cleaned_data['fecha']
            self.soporte.nombre = self.objeto_ruta.entregable.nombre
            self.soporte.estado = "Actualizado"

            if 'tipo' in form.cleaned_data.keys():
                self.soporte.tipo = form.cleaned_data['tipo']

            self.soporte.save()

            self.objeto_ruta.soporte = '{0}&{1}'.format(self.objeto_ruta.entregable.modelo,self.soporte.id)
            self.objeto_ruta.save()

            registro.objects.create(
                modelo=self.soporte,
                usuario=self.request.user,
                delta=json.dumps(
                    functions.delta_registro_sede_ruta(self.request, form.cleaned_data['delta'],
                                                       'Actualización: {0}'.format(self.soporte.nombre)))
            )

        return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.radicado.numero
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['file_url'] = self.soporte.pretty_print_url_file()

        return super(ActividadesSedeUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk_soporte':self.kwargs['pk_soporte']}


class ActividadesSedeDeleteListView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "eliminar_actividad": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.eliminar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('eliminar_actividad')):
                if self.objeto_ruta.estado == 'Aprobado' or self.objeto_ruta.estado == 'Rechazado':
                    return HttpResponseRedirect('../../')

                else:
                    if self.objeto_ruta.entregable.modelo in self.modelos.keys():
                        modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
                        registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
                    else:
                        raise NotImplementedError("EL modelo no esta establecido")

                    if modelo != None and registro != None:

                        objeto = modelo.objects.get(id=self.kwargs['pk_soporte'])

                        if objeto.estado == 'Nuevo':

                            if objeto.red == None:
                                self.objeto_ruta.soporte = ''
                                self.objeto_ruta.save()

                                registro.objects.filter(modelo=objeto).delete()
                                objeto.delete()
                            return HttpResponseRedirect('../../')
                        else:
                            return HttpResponseRedirect('../../')

                    return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')


class ActividadesSedeVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/sede/ver.html'


    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "ver_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero)
            ],
            "calificar_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.calificar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            if modelo != None:
                self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
            else:
                self.soporte = None
        else:
            raise NotImplementedError("EL modelo no esta establecido")



        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_actividades')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.radicado.numero
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['soporte'] = self.soporte
        kwargs['objeto_ruta'] = self.objeto_ruta
        kwargs['permiso_calificacion'] = self.request.user.has_perms(self.permissions.get('calificar_actividades')) and self.soporte.estado == 'Nuevo'

        return super(ActividadesSedeVerView,self).get_context_data(**kwargs)


class TrazabilidadSedeVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/sede/trazabilidad.html'


    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "ver_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero)
            ],
            "calificar_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.calificar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_actividades')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def get_items_registros(self):

        lista = []

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
            registros = registro.objects.filter(modelo = self.soporte).order_by('-creation')
        else:
            raise NotImplementedError("EL modelo no esta establecido")


        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.radicado.numero
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre
        kwargs['registros'] = self.get_items_registros()

        return super(TrazabilidadSedeVerView,self).get_context_data(**kwargs)


class CalificarSedeVerView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/componentes/actividades/sede/calificar.html'
    form_class = forms.CalificacionSedeRutaForm
    success_url = "../"


    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "ver_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero)
            ],
            "calificar_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.calificar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])
        else:
            raise NotImplementedError("EL modelo no esta establecido")



        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('calificar_actividades')):
                if self.soporte.estado == 'Aprobado' or self.soporte.estado == 'Rechazado':
                    return HttpResponseRedirect('../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def form_valid(self, form):

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            registro = self.modelos.get(self.objeto_ruta.entregable.modelo)['registro']
        else:
            raise NotImplementedError("EL modelo no esta establecido")

        registro.objects.create(
            modelo = self.soporte,
            usuario=self.request.user,
            delta=json.dumps(
                functions.delta_registro_calificacion_sede_ruta(self.request, form.cleaned_data['delta'],
                                                                'Calificación: {0}'.format(
                                                                    form.cleaned_data['estado'])))
        )

        if self.soporte != None:

            self.soporte.estado = form.cleaned_data['estado']
            self.soporte.save()

            if form.cleaned_data['estado'] == 'Aprobado':
                self.objeto_ruta.estado = 'Reportado'
                self.objeto_ruta.soporte = '{0}&{1}'.format(self.objeto_ruta.entregable.modelo, self.soporte.id)
                self.objeto_ruta.save()

            return HttpResponseRedirect('../')

        else:
            return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.radicado.numero
        kwargs['breadcrum_active'] = self.objeto_ruta.entregable.nombre

        return super(CalificarSedeVerView,self).get_context_data(**kwargs)

#----------------------------------- FORMACIÓN ------------------------------------


class FormacionRutaListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/formacion/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])

        self.permissions = {
            "ver_grupos": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero)
            ],
            "crear_grupo": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.crear".format(self.region.numero)
            ]
        }

        actividades_json = json.loads(self.ruta.actividades_json)
        cantidad_formacion = actividades_json['componente_' + str(models.Componentes.objects.get(numero='2').id)]

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_grupos')):
                if cantidad_formacion <= 0:
                    return HttpResponseRedirect('../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/actividades/{1}/formacion/'.format(
            self.region.id,
            self.ruta.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_active'] = self.ruta.nombre
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions.get('crear_grupo'))
        kwargs['cupos'] = models.EntregableRutaObject.objects.filter(ruta = self.ruta, estado = 'asignado', entregable = None).count()
        return super(FormacionRutaListView,self).get_context_data(**kwargs)


class FormacionRutaCreateGroupView(CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/formacion/grupos/crear.html'
    success_url = "../"
    form_class = forms.GrupoForm

    def dispatch(self, request, *args, **kwargs):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])

        self.permissions = {
            "crear_grupos": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.crear".format(self.region.numero)
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('crear_grupos')):
                if self.ruta.estado == 'Liquidación':
                    return HttpResponseRedirect('../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.usuario_creacion = self.request.user
        self.object.usuario_actualizacion = self.request.user
        self.object.ruta = self.ruta
        self.object.save()

        return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_active'] = self.ruta.nombre
        return super(FormacionRutaCreateGroupView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk':self.region.id,'pk_ruta':self.ruta.id}


class FormacionRutaUpdateGroupView(UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/formacion/grupos/editar.html'
    success_url = "../../"
    form_class = forms.GrupoUpdateForm
    pk_url_kwarg = 'pk_grupo'
    model = models.Grupos

    def dispatch(self, request, *args, **kwargs):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])

        self.permissions = {
            "editar_grupos": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.editar".format(self.region.numero)
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('editar_grupos')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.grupo.get_nombre_grupo()
        return super(FormacionRutaUpdateGroupView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk':self.region.id,'pk_ruta':self.ruta.id,'pk_grupo':self.grupo.id}


#--------------------- DOCENTES ---------------------------

class DocentesGrupoRutaListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/formacion/grupos/docentes/lista.html'

    def dispatch(self, request, *args, **kwargs):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])

        self.permissions = {
            "ver_docentes": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.docentes.ver".format(self.region.numero)
            ],
            "agregar_docentes": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.docentes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.docentes.agregar".format(self.region.numero)
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_docentes')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/actividades/{1}/formacion/docentes/{2}/'.format(
            self.region.id,
            self.ruta.id,
            self.grupo.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.grupo.get_nombre_grupo()
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions.get('agregar_docentes'))
        return super(DocentesGrupoRutaListView,self).get_context_data(**kwargs)

class DocentesRetirarRutaListView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/formacion/grupos/docentes/retirar.html'
    form_class = forms.RetirarDocente
    success_url = '../../'

    def dispatch(self, request, *args, **kwargs):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.docente = models.Docentes.objects.get(id=self.kwargs['pk_docente'])

        self.permissions = {
            "retirar_docentes": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.docentes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.docentes.agregar".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.docentes.opciones".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('retirar_docentes')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    @transaction.atomic
    def form_valid(self, form):

        if form.cleaned_data['estado'] == 'Si':
            objetos_docente = models.EntregableRutaObject.objects.select_for_update().filter(
                ruta=self.ruta,
                padre='docente&{0}&{1}'.format(self.ruta.id,self.grupo.id),
                docente = self.docente
            )

            for key in self.modelos.keys():
                modelo = self.modelos[key]['modelo']
                for evidencia in modelo.objects.filter(docentes = self.docente,estado = 'Nuevo'):
                    evidencia.docentes.remove(self.docente)



            valor = objetos_docente.exclude(estado__in = ['Pagado','Reportado']).aggregate(Sum('valor'))['valor__sum']

            if valor == None:
                valor = 0

            objetos_docente.exclude(estado__in=['Pagado', 'Reportado']).update(estado='Cerrado',valor = 0)

            objetos_formacion = models.EntregableRutaObject.objects.select_for_update().filter(
                entregable=None,
                ruta=self.ruta,
                valor=0,
                estado='Pagado',
                padre='docente&{0}'.format(self.ruta.id),
                tipo='Docente',
                orden=2
            )

            if objetos_formacion.count() > 0:
                obj = objetos_formacion.first()
                obj.estado = 'asignado'
                obj.valor = valor
                obj.save()


            self.docente.grupo = None
            self.docente.save()

        else:
            pass

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_active'] = self.docente
        kwargs['docente'] = self.docente
        return super(DocentesRetirarRutaListView,self).get_context_data(**kwargs)

class VerificarDocentesGrupoRutaListView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.docente = models.Docentes.objects.get(id=self.kwargs['pk_docente'])


        if not request.user.is_superuser:
            return HttpResponseRedirect(self.login_url)
        else:
            self.docente.verificar_objetos_formacion_estrategia(self.ruta, self.grupo)
            return HttpResponseRedirect('../../')

class AgregarDocenteGrupoRutaListView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/formacion/grupos/docentes/agregar.html'
    form_class = forms.AgregarDocenteGrupoForm
    success_url = "../"

    def dispatch(self, request, *args, **kwargs):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])

        self.permissions = {
            "agregar_docentes": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.docentes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.docentes.agregar".format(self.region.numero)
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('agregar_docentes')):
                if self.ruta.estado == 'Liquidación':
                    return HttpResponseRedirect('../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    @transaction.atomic
    def form_valid(self, form):

        for id_docente in form.cleaned_data['docentes']:
            objetos_formacion = models.EntregableRutaObject.objects.select_for_update().filter(
                entregable=None,
                ruta=self.ruta,
                padre='docente&{0}'.format(self.ruta.id),
                estado='asignado',
                tipo='Docente'
            )

            docente = models.Docentes.objects.get(id = id_docente)


            objeto_formacion = objetos_formacion.first()

            valor_docente = objeto_formacion.valor.amount

            if self.grupo.estrategia.numero == 1:
                entregables = models.Entregables.objects.filter(momento__estrategia__numero=1, tipo='docente')
            else:
                entregables = models.Entregables.objects.filter(momento__estrategia__numero=2, tipo='docente')

            cantidad = entregables.aggregate(Sum('peso'))['peso__sum']

            if cantidad == None:
                cantidad = 0

            if cantidad > 0:
                valor_entregable = valor_docente / cantidad
            else:
                valor_entregable = 0

            for entregable in entregables:

                q = models.EntregableRutaObject.objects.filter(
                    entregable=entregable,
                    padre='docente&{0}&{1}'.format(self.grupo.ruta.id, self.grupo.id),
                    ruta=self.grupo.ruta,
                    tipo='Docente',
                    docente=docente
                )

                if q.count() == 0:
                    models.EntregableRutaObject.objects.create(
                        entregable=entregable,
                        ruta=self.grupo.ruta,
                        valor=valor_entregable * entregable.peso,
                        estado='asignado',
                        padre='docente&{0}&{1}'.format(
                            self.grupo.ruta.id,
                            self.grupo.id
                        ),
                        tipo='Docente',
                        orden=entregable.orden,
                        docente=docente
                    )



            objeto_formacion.valor = 0
            objeto_formacion.estado = 'Pagado'
            objeto_formacion.save()
            docente.grupo = self.grupo
            docente.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.grupo.get_nombre_grupo()
        kwargs['url_docentes'] = '/rest/v1.0/cpe_2018/rutas/autocomplete/docentes/{0}/{1}/'.format(
            self.grupo.id,
            self.region.id
        )

        return super(AgregarDocenteGrupoRutaListView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk': self.region.id,
            'pk_ruta': self.ruta.id,
            'pk_grupo': self.grupo.id
        }

#--------------------- ACTIVIDADES -------------------------

class DocentesActividadesRutaListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/formacion/grupos/actividades/lista.html'


    def dispatch(self, request, *args, **kwargs):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])

        self.permissions = {
            "ver_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.ver".format(self.region.numero)
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_actividades')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/actividades/{1}/formacion/actividades/{2}/'.format(
            self.region.id,
            self.ruta.id,
            self.grupo.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.grupo.get_nombre_grupo()
        return super(DocentesActividadesRutaListView,self).get_context_data(**kwargs)


class DocentesLiquidacionRutaListView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/formacion/grupos/actividades/liquidacion.html'
    form_class = forms.LiquidacionEvidenciaFormacionForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
        }



        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.is_superuser:
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def form_valid(self, form):

        docentes = []

        file = File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf', 'rb'))

        if self.region.nombre == "Región 2":
            red = models.Red.objects.get(id = "d16ee1d5-0cb0-45a9-99e9-5acbbc309bfe")
        else:
            red = models.Red.objects.get(id = "5e35c570-4a3c-4f90-b479-16c9ba3ee692")


        modelo = self.modelos[self.entregable.modelo]['modelo']
        registro = self.modelos[self.entregable.modelo]['registro']

        objeto = modelo.objects.create(
            grupo=self.grupo,
            estado='Aprobado',
            entregable=self.entregable,
            fecha=Now(),
            red = red
        )

        objeto.file.save('coordinacion.pdf', file)

        for e in models.EntregableRutaObject.objects.filter(ruta=self.ruta, entregable=self.entregable,docente__grupo=self.grupo).exclude(valor=0):

            estado = form.cleaned_data[str(e.id)]

            if estado:
                if e.para_pago == False and e.estado in ["Reportado","Pagado"]:
                    e.para_pago = True
                    e.save()
                elif e.estado == "asignado":
                    docentes.append(e.docente.id)
                    e.estado = 'Reportado'
                    e.soporte = '{0}&{1}'.format(e.entregable.modelo, objeto.id)
                    e.para_pago = True
                    e.save()
                else:
                    pass

        objeto.docentes.add(*docentes)
        objeto.save()

        for obj in modelo.objects.exclude(id=objeto.id).filter(docentes__id__in=docentes,
                                                               entregable=self.entregable,
                                                               estado__in=['Nuevo', 'Actualizado', 'Rechazado',
                                                                           'Solicitud de subsanación']):
            obj.docentes.remove(*docentes)

        for empty in modelo.objects.filter(docentes=None):
            registro.objects.filter(modelo=empty).delete()
            empty.delete()

        #registro.objects.create(
        #    modelo=objeto,
        #    usuario=self.request.user,
        #    delta=json.dumps(
        #        functions.delta_registro_sede_ruta_coordinacion(self.request,
        #                                           'Creación: {0}'.format(self.entregable.nombre)))
        #)






        return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_active'] = self.entregable.nombre

        return super(DocentesLiquidacionRutaListView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk_entregable':self.entregable.id,
            'pk_grupo':self.grupo.id,
            'pk_ruta': self.ruta.id
        }


class DocentesActividadesEntregablesRutaListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/formacion/grupos/actividades/evidencias/lista.html'

    def dispatch(self, request, *args, **kwargs):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "ver_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.ver".format(self.region.numero)
            ],
            "crear_evidencia": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.crear".format(self.region.numero)
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_actividades')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/rutas/{0}/actividades/{1}/formacion/actividades/{2}/evidencias/{3}/'.format(
            self.region.id,
            self.ruta.id,
            self.grupo.id,
            self.entregable.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_active'] = self.entregable.nombre
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions.get('crear_evidencia'))
        return super(DocentesActividadesEntregablesRutaListView,self).get_context_data(**kwargs)


class DocentesActividadesEntregablesRutaCreateView(CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/formacion/grupos/actividades/evidencias/crear.html'
    success_url = "../"

    def dispatch(self, request, *args, **kwargs):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "crear_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.crear".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('crear_actividades')):
                if self.ruta.estado == 'Liquidación':
                    return HttpResponseRedirect('../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def get_form_class(self):

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")

        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            return self.modelos[self.entregable.modelo]['formulario']

    def form_valid(self, form):

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")

        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            registro = self.modelos[self.entregable.modelo]['registro']

            objeto = modelo.objects.create(
                grupo = self.grupo,
                file = form.cleaned_data['file'],
                estado = 'Nuevo',
                entregable = self.entregable,
                fecha = form.cleaned_data['fecha']
            )

            docentes = form.cleaned_data['docentes']

            objeto.docentes.add(*docentes)
            objeto.save()

            for obj in modelo.objects.exclude(id = objeto.id).filter(docentes__id__in = docentes, entregable = self.entregable,estado__in = ['Nuevo','Actualizado','Rechazado','Solicitud de subsanación']):
                obj.docentes.remove(*docentes)

            for empty in modelo.objects.filter(docentes = None):
                registro.objects.filter(modelo = empty).delete()
                empty.delete()

            registro.objects.create(
                modelo = objeto,
                usuario = self.request.user,
                delta = json.dumps(
                    functions.delta_registro_sede_ruta(self.request,form.cleaned_data['delta'], 'Creación: {0}'.format(self.entregable.nombre)))
            )



        return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_active'] = self.entregable.nombre

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")

        else:
            kwargs['file_url'] = '<p style="display:inline;">No hay archivos cargados.</p>'


        return super(DocentesActividadesEntregablesRutaCreateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk': self.region.id,
            'pk_ruta': self.ruta.id,
            'pk_grupo': self.grupo.id,
            'pk_entregable': self.entregable.id
        }


class DocentesActividadesEntregablesRutaUpdateView(UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/formacion/grupos/actividades/evidencias/editar.html'
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "editar_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.editar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('editar_actividades')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_object(self, queryset=None):

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            return modelo.objects.get(id=self.kwargs['pk_objeto'])

    def get_form_class(self):

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            return self.modelos[self.entregable.modelo]['formulario']

    def form_valid(self, form):

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")

        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            registro = self.modelos[self.entregable.modelo]['registro']

            self.object.grupo = self.grupo
            self.object.file = form.cleaned_data['file']
            self.object.fecha = form.cleaned_data['fecha']
            self.object.estado = "Actualizado"
            self.object.save()

            docentes = form.cleaned_data['docentes']

            self.object.docentes.clear()
            self.object.docentes.add(*docentes)
            self.object.save()

            for obj in modelo.objects.exclude(id = self.object.id).filter(docentes__id__in = docentes,entregable = self.entregable,estado__in = ['Nuevo','Actualizado','Rechazado','Solicitud de subsanación']):
                obj.docentes.remove(*docentes)

            for empty in modelo.objects.filter(docentes = None):
                registro.objects.filter(modelo = empty).delete()
                empty.delete()

            registro.objects.create(
                modelo = self.object,
                usuario = self.request.user,
                delta = json.dumps(
                    functions.delta_registro_sede_ruta(self.request,form.cleaned_data['delta'], 'Creación: {0}'.format(self.entregable.nombre)))
            )


        return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_4'] = self.entregable.nombre

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])
            kwargs['file_url'] = objeto.pretty_print_url_file()
            kwargs['breadcrum_active'] = objeto.id

        return super(DocentesActividadesEntregablesRutaUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk': self.region.id,
            'pk_ruta': self.ruta.id,
            'pk_grupo': self.grupo.id,
            'pk_entregable': self.entregable.id,
            'pk_objeto': self.kwargs['pk_objeto']
        }


class DocentesActividadesEntregablesRutaDeleteView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "eliminar_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.eliminar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
        }


        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            registro = self.modelos[self.entregable.modelo]['registro']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])



        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('eliminar_actividades')):
                if objeto.estado == 'Aprobado':
                    return HttpResponseRedirect('../../')

                else:
                    registro.objects.filter(modelo=objeto).delete()
                    objeto.delete()
                    return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')


class DocentesActividadesEntregablesRutaVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/formacion/grupos/actividades/evidencias/ver.html'

    def dispatch(self, request, *args, **kwargs):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "ver_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.ver".format(self.region.numero)
            ],
            "calificar_evidencias": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.calificar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_actividades')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_4'] = self.entregable.nombre


        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])

        kwargs['objeto'] = objeto
        kwargs['breadcrum_active'] = objeto.id
        kwargs['permiso_calificacion'] = self.request.user.has_perms(self.permissions.get('calificar_evidencias')) and objeto.estado != 'Aprobado'

        return super(DocentesActividadesEntregablesRutaVerView,self).get_context_data(**kwargs)


class TrazabilidadDocentesActividadesEntregablesRutaVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/formacion/grupos/actividades/evidencias/trazabilidad.html'

    def dispatch(self, request, *args, **kwargs):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "ver_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.ver".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_actividades')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def get_items_registros(self):

        lista = []

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            registro = self.modelos[self.entregable.modelo]['registro']
            modelo = self.modelos[self.entregable.modelo]['modelo']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])
            registros = registro.objects.filter(modelo = objeto).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_4'] = self.entregable.nombre

        kwargs['registros'] = self.get_items_registros()


        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])

        kwargs['breadcrum_active'] = objeto.id

        return super(TrazabilidadDocentesActividadesEntregablesRutaVerView,self).get_context_data(**kwargs)


class CalificarDocentesActividadesEntregablesRutaView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/rutas/formacion/grupos/actividades/evidencias/calificar.html'
    form_class = forms.CalificacionEvidenciaFormacionForm
    success_url = "../"

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "calificar_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.calificar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
        }


        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('calificar_actividades')):
                if objeto != None:
                    if objeto.estado == 'Aprobado':
                        return HttpResponseRedirect('../')
                    else:
                        if request.method.lower() in self.http_method_names:
                            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                        else:
                            handler = self.http_method_not_allowed
                        return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def form_valid(self, form):

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            registro = self.modelos[self.entregable.modelo]['registro']
            objeto = modelo.objects.get(id=self.kwargs['pk_objeto'])

        registro.objects.create(
            modelo = objeto,
            usuario=self.request.user,
            delta=json.dumps(
                functions.delta_registro_calificacion_sede_ruta(
                    self.request, form.cleaned_data['delta'],
                    'Calificación: {0}'.format(form.cleaned_data['estado']))
            )
        )


        if objeto != None:

            objeto.estado = form.cleaned_data['estado']
            objeto.save()

            if form.cleaned_data['estado'] == 'Aprobado':

                for docente in objeto.docentes.all():
                    try:
                        objeto_ruta = models.EntregableRutaObject.objects.get(
                            entregable = self.entregable,
                            docente = docente,
                            ruta = self.ruta,
                            estado = 'asignado'
                        )
                    except:
                        raise NotImplementedError("No existe el objeto")
                    else:
                        objeto_ruta.estado = 'Reportado'
                        objeto_ruta.soporte = '{0}&{1}'.format(objeto_ruta.entregable.modelo, objeto.id)
                        objeto_ruta.save()

            return HttpResponseRedirect('../')

        else:
            return HttpResponseRedirect('../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "RUTA - {0} - {1}".format(self.ruta.nombre, self.ruta.contrato.contratista.get_full_name())
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.ruta.nombre
        kwargs['breadcrum_3'] = self.grupo.get_nombre_grupo()
        kwargs['breadcrum_4'] = self.entregable.nombre
        kwargs['breadcrum_active'] = str(self.kwargs['pk_objeto'])

        return super(CalificarDocentesActividadesEntregablesRutaView,self).get_context_data(**kwargs)


#----------------------------------------------------------------------------------

#------------------------------------- CORTES -------------------------------------

class CortesOptionsView(TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/cortes/opciones.html'

    def get_items(self):
        items = []

        for region in models.Regiones.objects.all().order_by('numero'):
            if self.request.user.has_perms(self.permissions.get('all')):
                items.append({
                    'sican_categoria': 'Rutas: {0}'.format(region.nombre),
                    'sican_color': region.color,
                    'sican_order': 1,
                    'sican_url': '{0}/'.format(str(region.id)),
                    'sican_name': '{0}'.format(region.nombre),
                    'sican_icon': 'data_usage',
                    'sican_description': 'Asignación, cambio y trazabilidad de las rutas para los contratistas de la {0}.'.format(region.nombre)
                })


        return items

    def dispatch(self, request, *args, **kwargs):

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.cortes.ver"
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
        kwargs['title'] = "CORTES DE PAGO"
        kwargs['items'] = self.get_items()
        return super(CortesOptionsView,self).get_context_data(**kwargs)

class CortesRegionListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/cortes/lista.html'
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.cortes.ver",
        ]
    }


    def get_context_data(self, **kwargs):
        permissions = {
            "crear_corte": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.cortes.ver",
                "usuarios.cpe_2018.cortes.crear",
            ]
        }
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "CORTES DE PAGO - {0}".format(region.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/cortes/{0}/'.format(region.id)
        kwargs['breadcrum_active'] = region.nombre
        kwargs['permiso_crear'] = self.request.user.has_perms(permissions.get('crear_corte'))
        return super(CortesRegionListView,self).get_context_data(**kwargs)

class CortesRegionCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/cortes/crear.html'
    form_class = forms.CortesCreateForm
    success_url = "../"

    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.cortes.ver",
                "usuarios.cpe_2018.cortes.crear",
            ]
        }
        return permissions

    def form_valid(self, form):

        region = models.Regiones.objects.get(id = self.kwargs['pk'])

        corte = models.Cortes.objects.create(
            region = region,
            consecutivo = models.Cortes.objects.filter(region = region).count() + 1,
            usuario_creacion = self.request.user,
            descripcion = form.cleaned_data['descripcion']
        )

        rutas_ids = models.EntregableRutaObject.objects.filter(
            estado = "Reportado",
            ruta__region__id = self.kwargs['pk']).values_list('ruta__id', flat=True).distinct()

        for ruta_id in rutas_ids:
            ruta = models.Rutas.objects.get(id = ruta_id)

            if 'ruta_{0}'.format(ruta.id) in form.cleaned_data.keys():
                if form.cleaned_data['ruta_{0}'.format(ruta.id)]:
                    models.EntregableRutaObject.objects.filter(estado="Reportado",ruta__id = ruta_id).update(
                        estado = "Pagado",
                        corte = corte
                    )

        corte.create_cuentas_cobro(self.request.user)
        corte.create_excel()


        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "NUEVO CORTE DE PAGO"
        kwargs['breadcrum_active'] = region.nombre
        return super(CortesRegionCreateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk':self.kwargs['pk']}

class CortesRegionCuentasCobroView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/cortes/cuentas_cobro/lista.html'
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.cortes.ver",
            "usuarios.cpe_2018.cortes.cuentas_cobro.ver",
        ]
    }


    def get_context_data(self, **kwargs):
        permissions = {
            "crear_cuenta_cobro": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.cortes.ver",
                "usuarios.cpe_2018.cortes.cuentas_cobro.ver",
                "usuarios.cpe_2018.cortes.cuentas_cobro.crear",
            ]
        }
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        corte = models.Cortes.objects.get(id=self.kwargs['pk_corte'])
        kwargs['title'] = "CORTES DE PAGO - {0}".format(region.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/cortes/{0}/ver/{1}/'.format(region.id,corte.id)
        kwargs['breadcrum_1'] = region.nombre
        kwargs['breadcrum_active'] = corte.consecutivo
        kwargs['permiso_crear'] = self.request.user.has_perms(permissions.get('crear_cuenta_cobro'))
        return super(CortesRegionCuentasCobroView,self).get_context_data(**kwargs)

class CuentaCobroUpdateView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/cortes/cuentas_cobro/actualizar.html'
    form_class = forms.CuentaCobroForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.corte = models.Cortes.objects.get(id=self.kwargs['pk_corte'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "cargar_cuentas_cobro": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.cortes.ver",
                "usuarios.cpe_2018.cortes.cuentas_cobro.ver",
                "usuarios.cpe_2018.cortes.cuentas_cobro.editar"
            ]
        }


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('cargar_cuentas_cobro')):
                if self.cuenta_cobro.estado == 'Reportado':
                    return HttpResponseRedirect('../../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def form_valid(self, form):

        cuenta_cobro = models.CuentasCobro.objects.get(id = self.kwargs['pk_cuenta_cobro'])
        cuenta_cobro.data_json = json.dumps({'mes':form.cleaned_data['mes'],'year':form.cleaned_data['year']})
        cuenta_cobro.valores_json = form.cleaned_data['valores']
        cuenta_cobro.save()

        cuenta_cobro.file.delete()
        cuenta_cobro.html.delete()

        cuenta_cobro.create_delta()

        delta_obj = json.loads(cuenta_cobro.delta)
        delta_valores = json.loads(cuenta_cobro.valores_json)


        renders = ''


        if len(delta_valores) > 1:

            for cuenta in delta_valores:
                valor = float(cuenta.get('valor').replace('$ ','').replace(',',''))
                mes = cuenta.get('mes')
                year = cuenta.get('year')
                renders += '<div class="hoja">' + html.render(functions.delta_cuenta_cobro_parcial(cuenta_cobro,valor,mes,year)['ops']) + '</div>'

        else:
            renders = '<div class="hoja">' + html.render(functions.delta_cuenta_cobro_parcial(cuenta_cobro, float(cuenta_cobro.valor.amount), form.cleaned_data['mes'][0], form.cleaned_data['year'])['ops']) + '</div>'


        html_render = BeautifulSoup(renders, "html.parser", from_encoding='utf-8')

        template_no_header = BeautifulSoup(
            open(settings.TEMPLATES[0]['DIRS'][0] + '/pdfkit/certificaciones/no_header/cuenta_cobro.html',
                 'rb'), "html.parser")

        template_no_header_tag = template_no_header.find(class_='inserts')
        template_no_header_tag.insert(1, html_render)


        cuenta_cobro.html.save('cuenta_cobro.html',File(io.BytesIO(template_no_header.prettify(encoding='utf-8'))))

        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

        cuenta_cobro.file.save('cuenta_cobro.pdf',File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf', 'rb')))

        options = {
            'page-size': 'A4',
            'encoding': 'utf-8',
            'margin-top': '2cm',
            'margin-bottom': '2cm',
            'margin-left': '2cm',
            'margin-right': '2cm',
            'dpi': 400
        }

        pdfkit.from_file(cuenta_cobro.html.path, cuenta_cobro.file.path, options, configuration=config)

        if cuenta_cobro.estado != 'Cargado':
            cuenta_cobro.estado = 'Generado'
        cuenta_cobro.save()

        usuario = cuenta_cobro.ruta.contrato.get_user_or_none()

        if usuario != None:

            tasks.send_mail_templated_cuenta_cobro(
                'mail/cpe_2018/cuenta_cobro.tpl',
                {
                    'url_base': 'https://' + self.request.META['HTTP_HOST'],
                    'ruta': cuenta_cobro.ruta.nombre,
                    'nombre': cuenta_cobro.ruta.contrato.contratista.nombres,
                    'nombre_completo': cuenta_cobro.ruta.contrato.contratista.get_full_name(),
                    'valor': '$ {:20,.2f}'.format(cuenta_cobro.valor.amount),
                },
                DEFAULT_FROM_EMAIL,
                [usuario.email,EMAIL_HOST_USER,settings.EMAIL_DIRECCION_FINANCIERA,settings.EMAIL_GERENCIA]
            )

        return HttpResponseRedirect(self.get_success_url())

    def get_cuentas_meses(self):

        cuentas = models.CuentasCobro.objects.filter(ruta = self.cuenta_cobro.ruta).exclude(id = self.cuenta_cobro.id)
        data = {}
        for cuenta_cobro in cuentas:
            delta_valores = json.loads(cuenta_cobro.valores_json)
            if len(delta_valores) > 1:
                for cuenta in delta_valores:
                    valor = float(cuenta.get('valor').replace('$ ', '').replace(',', ''))
                    mes = cuenta.get('mes')
                    year = cuenta.get('year')

                    if year not in data.keys():
                        data[year] = {}

                    if mes not in data[year].keys():
                        data[year][mes] = {'valor':0}

                    data[year][mes]['valor'] += valor


            else:
                if cuenta_cobro.data_json != None:
                    data_json = json.loads(cuenta_cobro.data_json)
                    valor = float(cuenta_cobro.valor.amount)
                    mes = data_json['mes'][0]
                    year = data_json['year']

                    if year not in data.keys():
                        data[year] = {}

                    if mes not in data[year].keys():
                        data[year][mes] = {'valor': 0}

                    data[year][mes]['valor'] += valor

        html = ''

        for year in data.keys():
            html_parte = ''
            for mes in data[year].keys():
                valor = '$ {:20,.2f}'.format(data[year][mes]['valor'])
                html_parte += '<li style="list-style-type:initial;"><p><b>{0}: </b>{1}</p></li>'.format(mes,valor)

            html += '<div class="row"><div class="col s12"><p><b>Año: </b>{0}</p><div style="margin-left:15px;"><ul>{1}</ul></div></div></div>'.format(year,html_parte)

        return html

    def get_context_data(self, **kwargs):

        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        corte = models.Cortes.objects.get(id=self.kwargs['pk_corte'])
        cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        kwargs['title'] = "CUENTA DE COBRO RUTA {0}".format(cuenta_cobro.ruta.nombre)
        kwargs['breadcrum_1'] = region.nombre
        kwargs['breadcrum_2'] = corte.consecutivo
        kwargs['breadcrum_active'] = cuenta_cobro.ruta.nombre
        kwargs['valor'] = '$ {:20,.2f}'.format(cuenta_cobro.valor.amount)
        kwargs['corte'] = '{0}'.format(corte.consecutivo)
        kwargs['contratista'] = cuenta_cobro.ruta.contrato.contratista.get_full_name()
        kwargs['contrato'] = cuenta_cobro.ruta.contrato.nombre
        kwargs['cuentas'] = self.get_cuentas_meses()
        kwargs['inicio'] = cuenta_cobro.ruta.contrato.inicio
        kwargs['fin'] = cuenta_cobro.ruta.contrato.fin

        return super(CuentaCobroUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk':self.kwargs['pk'],
            'pk_corte': self.kwargs['pk_corte'],
            'pk_cuenta_cobro': self.kwargs['pk_cuenta_cobro']
        }


class CuentaCobroFirmaUploadView(UpdateView):

    login_url = settings.LOGIN_URL
    model = models.CuentasCobro
    template_name = 'cpe_2018/cortes/cuentas_cobro/cargar.html'
    form_class = forms.CuentaCobroCargarForm
    success_url = "../../"
    pk_url_kwarg = 'pk_cuenta_cobro'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.corte = models.Cortes.objects.get(id=self.kwargs['pk_corte'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "cargar_cuentas_cobro": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.cortes.ver",
                "usuarios.cpe_2018.cortes.cuentas_cobro.ver",
                "usuarios.cpe_2018.cortes.cuentas_cobro.cargar"
            ]
        }


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('cargar_cuentas_cobro')):
                if self.cuenta_cobro.estado == 'Creado' or self.cuenta_cobro.estado == 'Reportado':
                    return HttpResponseRedirect('../../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def form_valid(self, form):
        self.object = form.save()
        self.object.estado = 'Cargado'
        self.object.save()
        return super(CuentaCobroFirmaUploadView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CUENTA DE COBRO RUTA {0}".format(self.cuenta_cobro.ruta.nombre)
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.corte.consecutivo
        kwargs['breadcrum_active'] = self.cuenta_cobro.ruta.nombre
        kwargs['file_url'] = self.cuenta_cobro.pretty_print_url_file2()
        return super(CuentaCobroFirmaUploadView,self).get_context_data(**kwargs)

class CuentaCobroEstadoFormView(UpdateView):

    login_url = settings.LOGIN_URL
    model = models.CuentasCobro
    template_name = 'cpe_2018/cortes/cuentas_cobro/estado.html'
    form_class = forms.CuentaCobroEstadoForm
    success_url = "../../"
    pk_url_kwarg = 'pk_cuenta_cobro'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.corte = models.Cortes.objects.get(id=self.kwargs['pk_corte'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "estado_cuentas_cobro": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.cortes.ver",
                "usuarios.cpe_2018.cortes.cuentas_cobro.ver",
                "usuarios.cpe_2018.cortes.cuentas_cobro.estado"
            ]
        }


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('estado_cuentas_cobro')):
                if self.cuenta_cobro.estado == 'Generado' and self.cuenta_cobro.estado == 'Creado' and self.cuenta_cobro.estado == 'Reportado':
                    return HttpResponseRedirect('../../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def form_valid(self, form):
        self.object = form.save()
        self.object.fecha_actualizacion = timezone.now()
        self.object.usuario_actualizacion = self.request.user
        self.object.save()

        if self.object.estado == 'Pendiente':

            usuario = self.cuenta_cobro.ruta.contrato.get_user_or_none()

            if usuario != None:
                tasks.send_mail_templated_cuenta_cobro(
                    'mail/cpe_2018/cuenta_cobro_observacion.tpl',
                    {
                        'url_base': 'https://' + self.request.META['HTTP_HOST'],
                        'ruta': self.cuenta_cobro.ruta.nombre,
                        'nombre': self.cuenta_cobro.ruta.contrato.contratista.nombres,
                        'nombre_completo': self.cuenta_cobro.ruta.contrato.contratista.get_full_name(),
                        'valor': '$ {:20,.2f}'.format(self.cuenta_cobro.valor.amount),
                        'observaciones': form.cleaned_data['observaciones']
                    },
                    DEFAULT_FROM_EMAIL,
                    [usuario.email,EMAIL_HOST_USER,settings.EMAIL_DIRECCION_FINANCIERA,settings.EMAIL_GERENCIA]
                )

        return super(CuentaCobroEstadoFormView, self).form_valid(form)


    def get_context_data(self, **kwargs):
        kwargs['title'] = "CUENTA DE COBRO RUTA {0}".format(self.cuenta_cobro.ruta.nombre)
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.corte.consecutivo
        kwargs['breadcrum_active'] = self.cuenta_cobro.ruta.nombre
        return super(CuentaCobroEstadoFormView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

class MisRutasCuentasCobroUploadView(UpdateView):

    login_url = settings.LOGIN_URL
    model = models.CuentasCobro
    template_name = 'cpe_2018/misrutas/cuentas_cobro/cargar.html'
    form_class = forms.CuentaCobroCargarForm
    success_url = "../../"
    pk_url_kwarg = 'pk_cuenta_cobro'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "cargar_cuentas_cobro": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('cargar_cuentas_cobro')):
                if self.cuenta_cobro.estado == 'Creado' or self.cuenta_cobro.estado == 'Reportado':
                    return HttpResponseRedirect('../../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def form_valid(self, form):
        self.object = form.save()
        self.object.estado = 'Cargado'
        self.object.save()

        if self.object.corte == None:
            ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
            liquidacion = ruta.get_liquidacion()
            liquidacion.file2 = form.cleaned_data['file2']
            liquidacion.estado = "Cargada"
            liquidacion.save()

        return super(MisRutasCuentasCobroUploadView, self).form_valid(form)

    def get_context_data(self, **kwargs):

        if self.cuenta_cobro.corte != None:
            consecutivo = self.cuenta_cobro.corte.consecutivo
        else:
            consecutivo = 'Liquidación'

        kwargs['title'] = "CUENTA DE COBRO RUTA {0}".format(self.cuenta_cobro.ruta.nombre)
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = consecutivo
        kwargs['file_url'] = self.cuenta_cobro.pretty_print_url_file2()
        return super(MisRutasCuentasCobroUploadView,self).get_context_data(**kwargs)

#------------------------------------- CORTES -------------------------------------

class RedsOptionsView(TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/red/opciones.html'

    def dispatch(self, request, *args, **kwargs):

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver"
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

    def get_items(self):
        items = []

        for region in models.Regiones.objects.all().order_by('numero'):
            if self.request.user.has_perms(self.permissions.get('all')):
                items.append({
                    'sican_categoria': 'REDs: {0}'.format(region.nombre),
                    'sican_color': region.color,
                    'sican_order': 1,
                    'sican_url': '{0}/'.format(str(region.id)),
                    'sican_name': '{0}'.format(region.nombre),
                    'sican_icon': 'data_usage',
                    'sican_description': 'Consolidación y reporte de REDs de la {0}.'.format(region.nombre)
                })


        return items

    def get_context_data(self, **kwargs):
        kwargs['title'] = "REDs"
        kwargs['items'] = self.get_items()
        return super(RedsOptionsView,self).get_context_data(**kwargs)


class ReporteTableroControlView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    login_url = settings.LOGIN_URL

    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver"
            ]
        }
        return permissions

    def dispatch(self, request, *args, **kwargs):
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Tablero de control acumulado',
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_tablero_control.delay(reporte.id,region.id)

        return HttpResponseRedirect('/reportes/')


class ReporteEstadoRevisionRedView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    login_url = settings.LOGIN_URL

    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver"
            ]
        }
        return permissions

    def dispatch(self, request, *args, **kwargs):
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        red = models.Red.objects.get(id=self.kwargs['pk_red'])
        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Estado revisión RED {0}'.format(red.consecutivo),
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_red_estado_formacion.delay(reporte.id,red.id)

        return HttpResponseRedirect('/reportes/')


class RedsRegionListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/red/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero)
            ],
            "crear": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.red_{0}.crear".format(self.region.numero)
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "REDs - {0}".format(self.region.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/red/{0}/'.format(self.region.id)
        kwargs['breadcrum_active'] = self.region.nombre
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions.get('crear'))
        return super(RedsRegionListView,self).get_context_data(**kwargs)


class RedsRegionCreateView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/red/crear.html'
    model = models.Red
    form_class = forms.RedForm
    success_url = "../"

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.red_{0}.crear".format(self.region.numero)
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
                return HttpResponseRedirect('../')

    def get_cantidades_red(self):

        #----------------------------------------------------- RETOMAS --------------------------------------------------------------


        retomas = models.Retoma.objects.filter(ruta__region = self.region, red = None).aggregate(Sum('bolsas'))['bolsas__sum']


        # --------------------------------------------------- INNOVATIC -------------------------------------------------------------


        asistencias_innovatic = models.ListadoAsistencia.objects.filter(
            grupo__estrategia__numero = 1, entregable__modelo = 'listado_asistencia',  red = None, grupo__ruta__region = self.region
        ).values_list('docentes', flat = True).distinct().count()

        ple_innovatic = models.ProductoFinalPle.objects.filter(
            grupo__estrategia__numero=1, entregable__modelo='producto_final_ple', red=None, grupo__ruta__region=self.region
        ).values_list('docentes', flat=True).distinct().count()


        # ---------------------------------------------------- RURALTIC ------------------------------------------------------------

        asistencias_ruraltic = models.ListadoAsistencia.objects.filter(
            grupo__estrategia__numero=2, entregable__modelo = 'listado_asistencia',  red = None, grupo__ruta__region = self.region
        ).values_list('docentes', flat=True).distinct().count()

        repositorio_ruraltic = models.RepositorioActividades.objects.filter(
            grupo__estrategia__numero=2, entregable__modelo = 'repositorio_actividades', red = None, grupo__ruta__region = self.region
        ).values_list('docentes', flat=True).distinct().count()



        diccionario = {
            'taller_administratic': models.RelatoriaTallerAdministratic.objects.filter(ruta__region = self.region, red = None).count(),
            'taller_contenidos': models.RelatoriaTallerContenidosEducativos.objects.filter(ruta__region = self.region, red = None).count(),
            'taller_raee': models.RelatoriaTallerRAEE.objects.filter(ruta__region = self.region, red = None).count(),
            'taller_apertura': models.RelatoriaTallerApertura.objects.filter(ruta__region = self.region, red = None).count(),
            'documento_legalizacion_terminales': models.DocumentoLegalizacionTerminales.objects.filter(ruta__region=self.region,red=None).count(),
            'documento_legalizacion_terminales_v1': models.DocumentoLegalizacionTerminalesValle1.objects.filter(ruta__region=self.region, red=None).count(),
            'documento_legalizacion_terminales_v2': models.DocumentoLegalizacionTerminalesValle2.objects.filter(ruta__region=self.region, red=None).count(),
            'encuesta_monitoreo': models.EncuestaMonitoreo.objects.filter(ruta__region=self.region,red=None).count(),
            'retoma': retomas if retomas != None else 0,

            'asistencias_innovatic': asistencias_innovatic,
            'ple_innovatic': ple_innovatic,

            'asistencias_ruraltic': asistencias_ruraltic,
            'repositorio_ruraltic': repositorio_ruraltic
        }

        return diccionario

    def form_valid(self, form):

        consecutivo = 1

        if models.Red.objects.filter(region = self.region).count() > 0:
            consecutivo = models.Red.objects.filter(region = self.region).order_by('-creation')[0].consecutivo + 1

        red = models.Red.objects.create(
            region = self.region,
            consecutivo = consecutivo,
            usuario_creacion = self.request.user,
            estrategia = form.cleaned_data['tipo']
        )

        self.asignar_red(red, form.cleaned_data['tipo'])
        red.generar_red()

        return HttpResponseRedirect(self.get_success_url())

    def asignar_red(self, red, tipo):

        if tipo == 'Acceso':

            models.RelatoriaTallerAdministratic.objects.filter(ruta__region=self.region,red=None).update(red = red)
            models.RelatoriaTallerContenidosEducativos.objects.filter(ruta__region=self.region,red=None).update(red = red)
            models.RelatoriaTallerRAEE.objects.filter(ruta__region=self.region, red=None).update(red = red)
            models.RelatoriaTallerApertura.objects.filter(ruta__region=self.region, red=None).update(red = red)
            models.DocumentoLegalizacionTerminales.objects.filter(ruta__region=self.region, red=None).update(red = red)
            models.DocumentoLegalizacionTerminalesValle1.objects.filter(ruta__region=self.region, red=None).update(red=red)
            models.DocumentoLegalizacionTerminalesValle2.objects.filter(ruta__region=self.region, red=None).update(red=red)
            models.EncuestaMonitoreo.objects.filter(ruta__region=self.region, red=None).update(red=red)
            models.Retoma.objects.filter(ruta__region = self.region, red = None).update(red = red)

        elif tipo == 'Formación':

            # --------------------------------------------------- INNOVATIC -------------------------------------------------------------

            asistencias_innovatic = models.ListadoAsistencia.objects.filter(
                grupo__estrategia__numero=1, entregable__modelo='listado_asistencia', red=None,
                grupo__ruta__region=self.region
            ).values_list('docentes', flat=True).update(red = red)

            ple_innovatic = models.ProductoFinalPle.objects.filter(
                grupo__estrategia__numero=1, entregable__modelo='producto_final_ple', red=None,
                grupo__ruta__region=self.region
            ).values_list('docentes', flat=True).update(red = red)

            # ---------------------------------------------------- RURALTIC ------------------------------------------------------------

            asistencias_ruraltic = models.ListadoAsistencia.objects.filter(
                grupo__estrategia__numero=2, entregable__modelo='listado_asistencia', red=None,
                grupo__ruta__region=self.region
            ).values_list('docentes', flat=True).update(red = red)


            repositorio_ruraltic = models.RepositorioActividades.objects.filter(
                grupo__estrategia__numero=2, entregable__modelo='repositorio_actividades', red=None,
                grupo__ruta__region=self.region
            ).values_list('docentes', flat=True).update(red = red)

        else:
            pass

        return None

    def get_context_data(self, **kwargs):
        kwargs['title'] = "REDs - {0}".format(self.region.nombre)
        kwargs['breadcrum_active'] = self.region.nombre
        kwargs['data'] = self.get_cantidades_red()
        return super(RedsRegionCreateView,self).get_context_data(**kwargs)


class RedsRegionInformeView(LoginRequiredMixin,
                        View):

    login_url = settings.LOGIN_URL


    def dispatch(self, request, *args, **kwargs):
        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Informe RED',
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_red_acceso_informacion.delay(reporte.id)

        return HttpResponseRedirect('/reportes/')


class RedsRegionUpdateView(UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/red/actualizar.html'
    model = models.Red
    form_class = forms.RedUpdateForm
    success_url = "../../"
    pk_url_kwarg = 'pk_red'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.red_{0}.actualizar".format(self.region.numero)
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "REDs - {0}".format(self.region.nombre)
        kwargs['breadcrum_active'] = self.region.nombre
        return super(RedsRegionUpdateView,self).get_context_data(**kwargs)


class RedsRegionVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/red/ver.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero)
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "REDs - {0}".format(self.region.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/red/{0}/ver/{1}/'.format(self.region.id,self.red.id)
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_active'] = self.red.consecutivo
        kwargs['red'] = self.red
        return super(RedsRegionVerView,self).get_context_data(**kwargs)


class RedsRegionVerActividadesView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/red/ver_actividades.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero)
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "REDs - {0}".format(self.region.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/red/{0}/ver/{1}/actividades/{2}/'.format(self.region.id,self.red.id,self.entregable.id)
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.red.consecutivo
        kwargs['breadcrum_active'] = self.entregable.nombre
        return super(RedsRegionVerActividadesView,self).get_context_data(**kwargs)


class RedsRegionActividadCalificarView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/red/calificar.html'
    form_class = forms.CalificacionEvidenciaFormacionForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "calificar": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.red_{0}.calificar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE
            },
            'retoma': {
                'modelo': models.Retoma,
                'registro': models.RegistroRetoma
            }
        }


        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('calificar')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    @transaction.atomic
    def form_valid(self, form):

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            registro = self.modelos[self.entregable.modelo]['registro']
            objeto = modelo.objects.get(id=self.kwargs['pk_soporte'])


        if self.entregable.modelo == 'retoma':

            registro.objects.create(
                retoma = objeto,
                usuario=self.request.user,
                delta=json.dumps(
                    functions.delta_registro_calificacion_sede_ruta(
                        self.request, form.cleaned_data['delta'],
                        'Calificación: {0}'.format(form.cleaned_data['estado']))
                )
            )


            if objeto != None:

                objeto.estado = form.cleaned_data['estado']
                objeto.save()

                if form.cleaned_data['estado'] == 'Aprobado':

                    retoma = models.Retoma.objects.filter(id=objeto.id).select_for_update()

                    if form.cleaned_data['estado'] == 'Aprobado':

                        objetos = models.EntregableRutaObject.objects.filter(ruta=retoma[0].ruta, estado='asignado',padre="ruta&estrategia&{0}".format(retoma[0].ruta.id))

                        if objetos.count() >= retoma[0].bolsas:
                            ids = objetos[0:retoma[0].bolsas].values_list('id', flat=True)
                            models.EntregableRutaObject.objects.filter(id__in=ids).update(estado='Reportado',soporte="retoma&{0}".format(retoma[0].id))
                        else:
                            retoma.update(estado_observacion='Pendiente para pago')
                            objetos.update(estado='Reportado',soporte="retoma&{0}".format(retoma[0].id))
                            #raise ValueError(
                            #    'La cantidad de bolsas aprobadas en la retoma es superior a la dispuesta en el ruteo.'
                            #)

                    models.RegistroRetoma.objects.create(
                        retoma=retoma[0],
                        usuario=self.request.user,
                        delta=json.dumps(
                            functions.delta_registro_calificacion_retoma(self.request, form.cleaned_data['estado'],
                                                                         form.cleaned_data['delta']))
                    )

                    retoma.update(estado=form.cleaned_data['estado'])


                return HttpResponseRedirect('../../')

            else:
                return HttpResponseRedirect('../../')

        else:

            registro.objects.create(
                modelo=objeto,
                usuario=self.request.user,
                delta=json.dumps(
                    functions.delta_registro_calificacion_sede_ruta(self.request, form.cleaned_data['delta'],
                                                                    'Calificación: {0}'.format(
                                                                        form.cleaned_data['estado'])))
            )


            if objeto != None:

                objeto.estado = form.cleaned_data['estado']
                objeto.save()

                if form.cleaned_data['estado'] == 'Aprobado':

                    objeto_ruta = models.EntregableRutaObject.objects.filter(ruta = objeto.ruta,estado = "asignado",radicado = objeto.radicado, entregable = self.entregable)[0]

                    objeto_ruta.estado = 'Reportado'
                    objeto_ruta.soporte = '{0}&{1}'.format(objeto_ruta.entregable.modelo, objeto.id)
                    objeto_ruta.save()

                return HttpResponseRedirect('../../')

            else:
                return HttpResponseRedirect('../../')

    def get_items_registros(self):

        lista = []

        if self.entregable.modelo == 'retoma':

            registros = models.RegistroRetoma.objects.filter(retoma = self.soporte).order_by('-creation')

            for registro in registros:
                delta_obj = json.loads(registro.delta)
                lista.append({
                    'propio': True if registro.usuario == self.request.user else False,
                    'fecha': registro.pretty_creation_datetime(),
                    'usuario': registro.usuario.get_full_name_string(),
                    'html': html.render(delta_obj['ops'])
                })

        else:

            if self.entregable.modelo in self.modelos.keys():
                registro = self.modelos.get(self.entregable.modelo)['registro']
                registros = registro.objects.filter(modelo=self.soporte).order_by('-creation')
            else:
                raise NotImplementedError("EL modelo no esta establecido")

            for registro in registros:
                delta_obj = json.loads(registro.delta)
                lista.append({
                    'propio': True if registro.usuario == self.request.user else False,
                    'fecha': registro.pretty_creation_datetime(),
                    'usuario': registro.usuario.get_full_name_string(),
                    'html': html.render(delta_obj['ops'])
                })

        return lista


    def get_context_data(self, **kwargs):

        kwargs['title'] = "REDs - {0}".format(self.region.nombre)
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.red.consecutivo
        kwargs['breadcrum_3'] = self.entregable.nombre
        kwargs['breadcrum_active'] = str(self.kwargs['pk_soporte'])
        kwargs['modelo'] = self.entregable.modelo
        kwargs['soporte'] = self.soporte
        kwargs['entregable'] = self.entregable
        kwargs['registros'] = self.get_items_registros()

        return super(RedsRegionActividadCalificarView,self).get_context_data(**kwargs)




class RedsRegionActividadCalificarActivarView(View):

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "calificar": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.red_{0}.calificar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE
            },
            'retoma': {
                'modelo': models.Retoma,
                'registro': models.RegistroRetoma
            }
        }


        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])


        if not request.user.is_authenticated:
            return HttpResponseRedirect('../')
        else:
            if request.user.is_superuser:
                if self.soporte.estado == 'Rechazado':
                    self.soporte.estado = 'Nuevo'
                    self.soporte.save()
                return HttpResponseRedirect('../')
            else:
                return HttpResponseRedirect('../')




class RedsRegionActividadObservacionesView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/red/observaciones.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "ver_observaciones": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.red_{0}.calificar".format(self.region.numero),
            ]
        }

        self.modelos = {
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE
            },
            'retoma': {
                'modelo': models.Retoma,
                'registro': models.RegistroRetoma
            }
        }

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_observaciones')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def get_items_registros(self):

        lista = []

        if self.entregable.modelo == 'retoma':

            registros = models.RegistroRetoma.objects.filter(retoma = self.soporte).order_by('-creation')

            for registro in registros:
                delta_obj = json.loads(registro.delta)
                lista.append({
                    'propio': True if registro.usuario == self.request.user else False,
                    'fecha': registro.pretty_creation_datetime(),
                    'usuario': registro.usuario.get_full_name_string(),
                    'html': html.render(delta_obj['ops'])
                })

        else:

            if self.entregable.modelo in self.modelos.keys():
                registro = self.modelos.get(self.entregable.modelo)['registro']
                registros = registro.objects.filter(modelo=self.soporte).order_by('-creation')
            else:
                raise NotImplementedError("EL modelo no esta establecido")

            for registro in registros:
                delta_obj = json.loads(registro.delta)
                lista.append({
                    'propio': True if registro.usuario == self.request.user else False,
                    'fecha': registro.pretty_creation_datetime(),
                    'usuario': registro.usuario.get_full_name_string(),
                    'html': html.render(delta_obj['ops'])
                })

        return lista

    def get_context_data(self, **kwargs):

        kwargs['title'] = "REDs - {0}".format(self.region.nombre)
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.red.consecutivo
        kwargs['breadcrum_3'] = self.entregable.nombre
        kwargs['breadcrum_active'] = str(self.kwargs['pk_soporte'])
        kwargs['modelo'] = self.entregable.modelo
        kwargs['soporte'] = self.soporte
        kwargs['entregable'] = self.entregable
        kwargs['registros'] = self.get_items_registros()

        return super(RedsRegionActividadObservacionesView,self).get_context_data(**kwargs)




class RedsRegionVerActividadesEstrategiaView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/red/ver_actividades_formacion.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.estrategia = models.Estrategias.objects.get(id=self.kwargs['pk_estrategia'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero)
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "REDs - {0}".format(self.region.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/red/{0}/ver/{1}/formacion/{2}/'.format(self.region.id,self.red.id,self.estrategia.id)
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.red.consecutivo
        kwargs['breadcrum_active'] = self.estrategia.nombre
        return super(RedsRegionVerActividadesEstrategiaView,self).get_context_data(**kwargs)


class RedsRegionVerActividadesFormacionView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/red/ver_actividades_entregables_formacion.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.estrategia = models.Estrategias.objects.get(id=self.kwargs['pk_estrategia'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero)
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

    def get_context_data(self, **kwargs):
        kwargs['title'] = "REDs - {0}".format(self.region.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/red/{0}/ver/{1}/formacion/{2}/calificar/{3}/'.format(
            self.region.id,
            self.red.id,
            self.estrategia.id,
            self.entregable.id
        )
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.red.consecutivo
        kwargs['breadcrum_3'] = self.estrategia.nombre
        kwargs['breadcrum_active'] = self.entregable.nombre
        return super(RedsRegionVerActividadesFormacionView,self).get_context_data(**kwargs)


class RedsRegionActividadCalificarFormacionView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/red/calificar_formacion.html'
    form_class = forms.CalificacionEvidenciaCpeFormacionForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.estrategia = models.Estrategias.objects.get(id=self.kwargs['pk_estrategia'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "calificar": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.red_{0}.calificar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades
            },
        }


        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('calificar')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    @transaction.atomic
    def form_valid(self, form):

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            registro = self.modelos[self.entregable.modelo]['registro']
            objeto = modelo.objects.get(id=self.kwargs['pk_soporte'])


        retirados = []

        if form.cleaned_data['estado'] == 'Aprobado':

            for docente in objeto.docentes.all():
                estado = form.cleaned_data[str(docente.id)]
                if not estado:
                    objeto.docentes.remove(docente)
                    retirados.append(str(docente.id))

        registro.objects.create(
            modelo=objeto,
            usuario=self.request.user,
            delta=json.dumps(
                functions.delta_registro_calificacion_formacion(
                    self.request, form.cleaned_data['delta'],
                    'Calificación: {0}'.format(form.cleaned_data['estado']),
                    json.dumps(retirados)
                )
            )
        )


        if objeto != None:

            objeto.estado = form.cleaned_data['estado']
            objeto.save()

            if form.cleaned_data['estado'] == 'Aprobado':

                for docente in objeto.docentes.all():
                    try:
                        objeto_ruta = models.EntregableRutaObject.objects.get(
                            entregable = self.entregable,
                            docente = docente,
                            ruta = objeto.grupo.ruta,
                            estado = 'asignado'
                        )
                    except:
                        pass
                        #raise NotImplementedError("No existe el objeto")
                    else:
                        objeto_ruta.estado = 'Reportado'
                        objeto_ruta.soporte = '{0}&{1}'.format(objeto_ruta.entregable.modelo, objeto.id)
                        objeto_ruta.save()

            return HttpResponseRedirect('../../')

        else:
            return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):

        kwargs['title'] = "REDs - {0}".format(self.region.nombre)
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.red.consecutivo
        kwargs['breadcrum_3'] = self.estrategia.nombre
        kwargs['breadcrum_4'] = self.entregable.nombre
        kwargs['breadcrum_active'] = str(self.kwargs['pk_soporte'])
        kwargs['soporte'] = self.soporte
        kwargs['entregable'] = self.entregable

        return super(RedsRegionActividadCalificarFormacionView,self).get_context_data(**kwargs)

    def get_initial(self):
        docentes = []
        for docente in self.soporte.docentes.all():
            docentes.append(str(docente.id))
        return {'ids_docentes': json.dumps(docentes)}


class RedsRegionActividadActivarFormacionView(View):

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.estrategia = models.Estrategias.objects.get(id=self.kwargs['pk_estrategia'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.modelos = {
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle
            }
        }

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])

        if not request.user.is_authenticated:
            return HttpResponseRedirect('../')
        else:
            if request.user.is_superuser:
                if self.soporte.estado == 'Rechazado':
                    self.soporte.estado = 'Nuevo'
                    self.soporte.save()
                return HttpResponseRedirect('../')
            else:
                return HttpResponseRedirect('../')



class RedsRegionActividadObservacionesFormacionView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/red/observaciones_formacion.html'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.estrategia = models.Estrategias.objects.get(id=self.kwargs['pk_estrategia'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "ver_observaciones": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.red_{0}.calificar".format(self.region.numero),
            ]
        }

        self.modelos = {
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle
            }
        }

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")
        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            self.soporte = modelo.objects.get(id=self.kwargs['pk_soporte'])

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('ver_observaciones')):
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../')

    def get_items_registros(self):

        lista = []

        if self.entregable.modelo in self.modelos.keys():
            registro = self.modelos.get(self.entregable.modelo)['registro']
            registros = registro.objects.filter(modelo=self.soporte).order_by('-creation')
        else:
            raise NotImplementedError("EL modelo no esta establecido")

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops'])
            })

        return lista

    def get_context_data(self, **kwargs):

        kwargs['title'] = "REDs - {0}".format(self.region.nombre)
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_2'] = self.red.consecutivo
        kwargs['breadcrum_3'] = self.estrategia.nombre
        kwargs['breadcrum_4'] = self.entregable.nombre
        kwargs['breadcrum_active'] = str(self.kwargs['pk_soporte'])
        kwargs['modelo'] = self.entregable.modelo
        kwargs['soporte'] = self.soporte
        kwargs['entregable'] = self.entregable
        kwargs['registros'] = self.get_items_registros()

        return super(RedsRegionActividadObservacionesFormacionView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#----------------------------------- MIS RUTAS -------------------------------------


class LiquidacionesOptionsView(TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/liquidaciones/opciones.html'

    def get_items(self):
        items = []

        for region in models.Regiones.objects.all().order_by('numero'):
            if self.request.user.has_perm('usuarios.cpe_2018.rutas_{}.ver'.format(region.numero)):
                items.append({
                    'sican_categoria': '{0}'.format(region.nombre),
                    'sican_color': region.color,
                    'sican_order': 1,
                    'sican_url': '{0}/'.format(str(region.id)),
                    'sican_name': '{0}'.format(region.nombre),
                    'sican_icon': 'data_usage',
                    'sican_description': 'Liquidación de rutas para los contratistas de la {0}.'.format(region.nombre)
                })


        return items

    def dispatch(self, request, *args, **kwargs):

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.liquidaciones.ver"
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
        kwargs['title'] = "LIQUIDACIONES"
        kwargs['items'] = self.get_items()
        return super(LiquidacionesOptionsView,self).get_context_data(**kwargs)


class LiquidacionesRutasRegionListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/liquidaciones/lista.html'


    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.liquidaciones.ver",
                "usuarios.cpe_2018.liquidaciones_{0}.ver".format(region.numero)
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "LIQUIDACIONES - {0}".format(region.nombre)
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/liquidaciones/{0}/'.format(region.id)
        kwargs['breadcrum_active'] = region.nombre
        return super(LiquidacionesRutasRegionListView,self).get_context_data(**kwargs)


class LiquidacionRutaRegionView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      FormView):

    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/liquidaciones/generar.html'
    form_class = forms.GenerarLiquidacionForm
    success_url = '../../'


    def get_permission_required(self, request=None):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.liquidaciones.ver",
                "usuarios.cpe_2018.liquidaciones_{0}.ver".format(region.numero),
                "usuarios.cpe_2018.liquidaciones_{0}.generar".format(region.numero)
            ]
        }
        return permissions


    def get_cuentas_meses(self,cuenta_cobro):

        cuentas = models.CuentasCobro.objects.filter(ruta = cuenta_cobro.ruta).exclude(id = cuenta_cobro.id)
        data = {}
        for cuenta_cobro in cuentas:
            delta_valores = json.loads(cuenta_cobro.valores_json)
            if len(delta_valores) > 1:
                for cuenta in delta_valores:
                    valor = float(cuenta.get('valor').replace('$ ', '').replace(',', ''))
                    mes = cuenta.get('mes')
                    year = cuenta.get('year')

                    if year not in data.keys():
                        data[year] = {}

                    if mes not in data[year].keys():
                        data[year][mes] = {'valor':0}

                    data[year][mes]['valor'] += valor


            else:
                if cuenta_cobro.data_json != None:
                    data_json = json.loads(cuenta_cobro.data_json)
                    valor = float(cuenta_cobro.valor.amount)
                    mes = data_json['mes'][0]
                    year = data_json['year']

                    if year not in data.keys():
                        data[year] = {}

                    if mes not in data[year].keys():
                        data[year][mes] = {'valor': 0}

                    data[year][mes]['valor'] += valor

        html = ''

        for year in data.keys():
            html_parte = ''
            for mes in data[year].keys():
                valor = '$ {:20,.2f}'.format(data[year][mes]['valor'])
                html_parte += '<li style="list-style-type:initial;"><p><b>{0}: </b>{1}</p></li>'.format(mes,valor)

            html += '<div class="row"><div class="col s12"><p><b>Año: </b>{0}</p><div style="margin-left:15px;"><ul>{1}</ul></div></div></div>'.format(year,html_parte)

        return html


    def get_context_data(self, **kwargs):
        region = models.Regiones.objects.get(id = self.kwargs['pk'])
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])

        kwargs['title'] = "LIQUIDACIONES - {0} - Ruta: {1}".format(region.nombre,ruta.nombre)
        kwargs['breadcrum_1'] = region.nombre
        kwargs['breadcrum_active'] = ruta.nombre

        cuenta_cobro, creacion = models.CuentasCobro.objects.get_or_create(ruta=ruta, liquidacion=True)
        progreso, valor_reportado, valor_pagado = ruta.progreso_ruta()


        kwargs['valor'] = '$ {:20,.2f}'.format(ruta.get_valor_liquidacion())
        kwargs['contratista'] = cuenta_cobro.ruta.contrato.contratista.get_full_name()
        kwargs['contrato'] = cuenta_cobro.ruta.contrato.nombre
        kwargs['cuentas'] = self.get_cuentas_meses(cuenta_cobro)
        kwargs['inicio'] = cuenta_cobro.ruta.contrato.inicio
        kwargs['fin'] = cuenta_cobro.ruta.contrato.fin


        return super(LiquidacionRutaRegionView,self).get_context_data(**kwargs)


    def form_valid(self, form):

        ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        descuento_anticipo = float(form.cleaned_data['anticipo'])
        otros_descuentos = float(form.cleaned_data['descuentos'])
        fecha = timezone.now()

        progreso, valor_reportado, valor_pagado = ruta.progreso_ruta()

        liquidacion, created = models.Liquidaciones.objects.get_or_create(ruta = ruta)

        liquidacion.estado = "Generada"
        liquidacion.save()

        models.EntregableRutaObject.objects.filter(ruta = ruta, estado = "Reportado", para_pago = True).update(liquidacion = liquidacion)

        valor_ejecutado = liquidacion.ruta.get_valor_ejecutado()
        ejecutado = valor_ejecutado.replace('$','').replace(',','')

        valor_pendiente_descuentos = float(ruta.get_valor_liquidacion()) - descuento_anticipo - otros_descuentos

        valor_cuentas = 0



        cuenta_cobro, creacion = models.CuentasCobro.objects.get_or_create(ruta=ruta, liquidacion=True)





        for cuenta in models.CuentasCobro.objects.filter(ruta = ruta).exclude(corte = None):
            valor_cuentas += float(cuenta.valor)


        if float(ruta.contrato.valor) > float(ejecutado):

            cuenta_cobro.valor = ruta.get_valor_liquidacion()
            cuenta_cobro.save()

            if valor_pendiente_descuentos >= 0:
                saldo_contratista = valor_pendiente_descuentos
                saldo_andes = 0

            else:
                saldo_contratista = 0
                saldo_andes = abs(valor_pendiente_descuentos)

        else:

            valor_p = float(ruta.contrato.valor) - valor_cuentas - descuento_anticipo - otros_descuentos

            cuenta_cobro.valor = valor_p
            cuenta_cobro.save()

            if valor_p >= 0:
                saldo_contratista = valor_p
                saldo_andes = 0

            else:
                saldo_contratista = 0
                saldo_andes = abs(valor_p)





        cuenta_cobro.data_json = json.dumps({'mes': form.cleaned_data['mes'], 'year': form.cleaned_data['year']})
        cuenta_cobro.valores_json = form.cleaned_data['valores']
        cuenta_cobro.save()

        cuenta_cobro.file.delete()
        cuenta_cobro.html.delete()

        cuenta_cobro.create_delta()

        delta_obj = json.loads(cuenta_cobro.delta)
        delta_valores = json.loads(cuenta_cobro.valores_json)

        renders = ''

        if len(delta_valores) > 1:

            for cuenta in delta_valores:
                valor = float(cuenta.get('valor').replace('$ ', '').replace(',', ''))
                mes = cuenta.get('mes')
                year = cuenta.get('year')
                renders += '<div class="hoja">' + html.render(
                    functions.delta_cuenta_cobro_parcial(cuenta_cobro, valor, mes, year)['ops']) + '</div>'

        else:
            renders = '<div class="hoja">' + html.render(
                functions.delta_cuenta_cobro_parcial(cuenta_cobro, float(cuenta_cobro.valor.amount),
                                                     form.cleaned_data['mes'][0], form.cleaned_data['year'])[
                    'ops']) + '</div>'

        html_render = BeautifulSoup(renders, "html.parser", from_encoding='utf-8')

        template_no_header = BeautifulSoup(
            open(settings.TEMPLATES[0]['DIRS'][0] + '/pdfkit/certificaciones/no_header/cuenta_cobro.html',
                 'rb'), "html.parser")

        template_no_header_tag = template_no_header.find(class_='inserts')
        template_no_header_tag.insert(1, html_render)

        cuenta_cobro.html.save('cuenta_cobro.html', File(io.BytesIO(template_no_header.prettify(encoding='utf-8'))))



        if cuenta_cobro.estado != 'Cargado':
            cuenta_cobro.estado = 'Generado'
        cuenta_cobro.save()












        template_header = BeautifulSoup(open(settings.TEMPLATES[0]['DIRS'][0] + '/pdfkit/liquidaciones/liquidacion.html','rb'), "html.parser")


        template_header_tag = template_header.find(class_='codigo_span')
        template_header_tag.insert(1, str(liquidacion.id))

        template_header_tag = template_header.find(class_='contratista_nombre_span_1')
        template_header_tag.insert(1, liquidacion.ruta.contrato.contratista.get_full_name())

        template_header_tag = template_header.find(class_='contratista_cedula_span_1')
        template_header_tag.insert(1, str(liquidacion.ruta.contrato.contratista.cedula))

        template_header_tag = template_header.find(class_='contratista_cargo_span_1')
        template_header_tag.insert(1, str(liquidacion.ruta.contrato.contratista.cargo))

        template_header_tag = template_header.find(class_='contratista_zona_span_1')
        template_header_tag.insert(1, str(liquidacion.ruta.region.nombre))

        template_header_tag = template_header.find(class_='contrato_inicio_span_1')
        template_header_tag.insert(1, liquidacion.ruta.contrato.pretty_print_inicio())

        template_header_tag = template_header.find(class_='contrato_finalizacion_span_1')
        template_header_tag.insert(1, liquidacion.ruta.contrato.pretty_print_fin())

        template_header_tag = template_header.find(class_='contrato_valor_total_span_1')
        template_header_tag.insert(1, liquidacion.ruta.contrato.pretty_print_valor())

        template_header_tag = template_header.find(class_='contrato_valor_ejecutado_span_1')
        template_header_tag.insert(1, liquidacion.ruta.get_valor_ejecutado())

        template_header_tag = template_header.find(class_='contrato_valor_cortes_span_1')
        template_header_tag.insert(1, '$ {:20,.2f}'.format(valor_cuentas))

        template_header_tag = template_header.find(class_='valor_descuento_anticipo_span_1')
        template_header_tag.insert(1,'$ {:20,.2f}'.format(descuento_anticipo))

        template_header_tag = template_header.find(class_='valor_otros_descuentos_span_1')
        template_header_tag.insert(1, '$ {:20,.2f}'.format(otros_descuentos))




        template_header_tag = template_header.find(class_='contratista_nombre_span_2')
        template_header_tag.insert(1, liquidacion.ruta.contrato.contratista.get_full_name().upper())

        template_header_tag = template_header.find(class_='contratista_cedula_span_2')
        template_header_tag.insert(1, str(liquidacion.ruta.contrato.contratista.cedula))

        template_header_tag = template_header.find(class_='contrato_codigo_span_1')
        template_header_tag.insert(1, str(liquidacion.ruta.contrato.nombre))

        template_header_tag = template_header.find(class_='dia_firma_span_1')
        template_header_tag.insert(1, fecha.strftime('%d'))

        template_header_tag = template_header.find(class_='mes_firma_span_1')
        template_header_tag.insert(1, fecha.strftime('%B'))

        template_header_tag = template_header.find(class_='ano_firma_span_1')
        template_header_tag.insert(1, fecha.strftime('%Y'))

        template_header_tag = template_header.find(class_='contratista_nombre_span_3')
        template_header_tag.insert(1, liquidacion.ruta.contrato.contratista.get_full_name().upper())

        template_header_tag = template_header.find(class_='saldo_favor_contratista')
        template_header_tag.insert(1, '$ {:20,.2f}'.format(saldo_contratista))

        template_header_tag = template_header.find(class_='saldo_favor_andes')
        template_header_tag.insert(1, '$ {:20,.2f}'.format(saldo_andes))


        liquidacion.html.save('liquidacion.html', File(io.BytesIO(template_header.prettify(encoding='utf-8'))))

        path_wkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

        liquidacion.file.save('liquidacion.pdf',
                               File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf', 'rb')))

        options = {
            'page-size': 'A4',
            'encoding': 'utf-8',
            'margin-top': '2cm',
            'margin-bottom': '2cm',
            'margin-left': '2cm',
            'margin-right': '2cm',
            'dpi': 400
        }

        pdfkit.from_file([liquidacion.html.path,cuenta_cobro.html.path], liquidacion.file.path, {
            '--header-html': settings.TEMPLATES[0]['DIRS'][0] + '\\pdfkit\\liquidaciones\\header\\header.html',
            '--footer-html': settings.TEMPLATES[0]['DIRS'][0] + '\\pdfkit\\liquidaciones\\footer\\footer.html',
            'page-size': 'A4',
            'encoding': 'utf-8',
            'margin-top': '4cm',
            'margin-bottom': '3cm',
            'margin-left': '2cm',
            'margin-right': '2cm',
            'dpi': 400
        }, configuration=config)



        cuenta_cobro.file.save('cuenta_cobro.pdf',
                               File(open(settings.STATICFILES_DIRS[0] + '/documentos/empty.pdf', 'rb')))

        pdfkit.from_file([liquidacion.html.path, cuenta_cobro.html.path], cuenta_cobro.file.path, {
            '--header-html': settings.TEMPLATES[0]['DIRS'][0] + '\\pdfkit\\liquidaciones\\header\\header.html',
            '--footer-html': settings.TEMPLATES[0]['DIRS'][0] + '\\pdfkit\\liquidaciones\\footer\\footer.html',
            'page-size': 'A4',
            'encoding': 'utf-8',
            'margin-top': '4cm',
            'margin-bottom': '3cm',
            'margin-left': '2cm',
            'margin-right': '2cm',
            'dpi': 400
        }, configuration=config)



        usuario = cuenta_cobro.ruta.contrato.get_user_or_none()


        if usuario != None:
            tasks.send_mail_templated_cuenta_cobro(
                'mail/cpe_2018/cuenta_cobro.tpl',
                {
                    'url_base': 'https://' + self.request.META['HTTP_HOST'],
                    'ruta': cuenta_cobro.ruta.nombre,
                    'nombre': cuenta_cobro.ruta.contrato.contratista.nombres,
                    'nombre_completo': cuenta_cobro.ruta.contrato.contratista.get_full_name(),
                    'valor': '$ {:20,.2f}'.format(cuenta_cobro.valor.amount),
                },
                DEFAULT_FROM_EMAIL,
                [usuario.email, EMAIL_HOST_USER, settings.EMAIL_DIRECCION_FINANCIERA, settings.EMAIL_GERENCIA]
            )

        tasks.build_excel_liquidacion.delay(liquidacion.id,self.request.user.id)


        return super(LiquidacionRutaRegionView,self).form_valid(form)

    def get_initial(self):
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        cuenta, creacion = models.CuentasCobro.objects.get_or_create(ruta=ruta, liquidacion=True)
        return {'pk_cuenta_cobro':cuenta.id}



class LiquidacionEstadoFormView(UpdateView):

    login_url = settings.LOGIN_URL
    model = models.Liquidaciones
    template_name = 'cpe_2018/liquidaciones/estado.html'
    form_class = forms.LiquidacionesEstadoForm
    success_url = "../../"
    pk_url_kwarg = 'pk_liquidacion'

    def dispatch(self, request, *args, **kwargs):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.liquidacion = models.Liquidaciones.objects.get(id=self.kwargs['pk_liquidacion'])

        self.permissions = {
            "estado_cuentas_cobro": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.liquidaciones.ver",
                "usuarios.cpe_2018.liquidaciones_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.liquidaciones_{0}.estado".format(self.region.numero)
            ]
        }


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('estado_cuentas_cobro')):
                if self.liquidacion.estado == 'Generada' or self.liquidacion.estado == 'Pagada':
                    return HttpResponseRedirect('../../')
                else:
                    if request.method.lower() in self.http_method_names:
                        handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                    else:
                        handler = self.http_method_not_allowed
                    return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def form_valid(self, form):
        self.object = form.save()
        self.object.fecha_actualizacion = timezone.now()
        self.object.usuario_actualizacion = self.request.user
        self.object.save()

        if self.object.estado == 'Pendiente':

            usuario = self.liquidacion.ruta.contrato.get_user_or_none()


            if usuario != None:
                tasks.send_mail_templated_cuenta_cobro(
                    'mail/cpe_2018/cuenta_cobro_observacion.tpl',
                    {
                        'url_base': 'https://' + self.request.META['HTTP_HOST'],
                        'ruta': self.liquidacion.ruta.nombre,
                        'nombre': self.liquidacion.ruta.contrato.contratista.nombres,
                        'nombre_completo': self.liquidacion.ruta.contrato.contratista.get_full_name(),
                        'valor': '$ {:20,.2f}'.format(self.liquidacion.valor.amount),
                        'observaciones': form.cleaned_data['observaciones']
                    },
                    DEFAULT_FROM_EMAIL,
                    [usuario.email,EMAIL_HOST_USER,settings.EMAIL_DIRECCION_FINANCIERA,settings.EMAIL_GERENCIA]
                )


        return super(LiquidacionEstadoFormView, self).form_valid(form)


    def get_context_data(self, **kwargs):
        kwargs['title'] = "LIQUIDACIÓN {0}".format(self.liquidacion.ruta.nombre)
        kwargs['breadcrum_1'] = self.region.nombre
        kwargs['breadcrum_active'] = self.liquidacion.ruta.nombre
        return super(LiquidacionEstadoFormView,self).get_context_data(**kwargs)


#----------------------------------------------------------------------------------