from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from recursos_humanos import models as rh_models
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from fest_2019 import models, forms
from django.contrib import messages
from django.contrib.messages import get_messages
from fest_2019 import utils
import openpyxl
from fest_2019 import modelos_instrumentos
from django.utils import timezone
from usuarios.models import Municipios, Corregimientos, Veredas
from reportes.models import Reportes
from fest_2019 import tasks
import json
from delta import html
from bs4 import BeautifulSoup
from fest_2019 import functions
from django.core.files import File
import io
import pdfkit
from config.settings.base import DEFAULT_FROM_EMAIL, EMAIL_HOST_USER, EMAIL_DIRECCION_FINANCIERA

# Create your views here.

#------------------------------- SELECCIÓN ----------------------------------------

class Fest2019OptionsView(LoginRequiredMixin,
                          MultiplePermissionsRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/lista.html'
    permissions = {
        "all": [
            "usuarios.fest_2019.ver"
        ]
    }

    def dispatch(self, request, *args, **kwargs):
        items = self.get_items()
        if len(items) == 0:
            return redirect(self.login_url)
        return super(Fest2019OptionsView, self).dispatch(request, *args, **kwargs)

    def get_items(self):
        items = []


        if self.request.user.has_perm('usuarios.fest_2019.entes_territoriales.ver'):
            items.append({
                'sican_categoria': 'Reuniones',
                'sican_color': 'teal darken-4',
                'sican_order': 1,
                'sican_url': 'entes_territoriales/',
                'sican_name': 'Gestión con comunidades',
                'sican_icon': 'assistant',
                'sican_description': 'Registro de información y gestión.'
            })

        if self.request.user.has_perm('usuarios.fest_2019.bd.ver'):
            items.append({
                'sican_categoria': 'Base de datos',
                'sican_color': 'brown darken-4',
                'sican_order': 2,
                'sican_url': 'bd/',
                'sican_name': 'Base de datos',
                'sican_icon': 'data_usage',
                'sican_description': 'Información general de los hogares atendidos en la intervención.'
            })

        if self.request.user.has_perm('usuarios.fest_2019.entregables.ver'):
            items.append({
                'sican_categoria': 'Entregables',
                'sican_color': 'orange darken-4',
                'sican_order': 3,
                'sican_url': 'entregables/',
                'sican_name': 'Entregables',
                'sican_icon': 'view_list',
                'sican_description': 'Estructura de entregables por cada uno de los componentes.'
            })

        if self.request.user.has_perm('usuarios.fest_2019.rutas.ver'):
            items.append({
                'sican_categoria': 'Rutas',
                'sican_color': 'green darken-4',
                'sican_order': 4,
                'sican_url': 'rutas/',
                'sican_name': 'Rutas',
                'sican_icon': 'autorenew',
                'sican_description': 'Asignación, cambio y trazabilidad de las rutas para los profesionales en campo.'
            })

        if self.request.user.has_perm('usuarios.fest_2019.misrutas.ver'):
            items.append({
                'sican_categoria': 'Mis rutas',
                'sican_color': 'blue-grey darken-3',
                'sican_order': 5,
                'sican_url': 'misrutas/',
                'sican_name': 'Mis rutas',
                'sican_icon': 'assignment_ind',
                'sican_description': 'Ruteos, cuentas de cobro e información de pagos.'
            })

        if self.request.user.has_perm('usuarios.fest_2019.permisos.ver'):
            items.append({
                'sican_categoria': 'Permisos',
                'sican_color': 'red darken-3',
                'sican_order': 6,
                'sican_url': 'permisos/',
                'sican_name': 'Permisos',
                'sican_icon': 'apps',
                'sican_description': 'Asignar permisos a usuarios para calificar rutas.'
            })
        if self.request.user.has_perm('usuarios.fest_2019.permisos.ver'):
            items.append({
                'sican_categoria': 'Permisos proyectos',
                'sican_color': 'orange darken-3',
                'sican_order': 7,
                'sican_url': 'permisos_proyectos/',
                'sican_name': 'Permisos proyectos',
                'sican_icon': 'apps',
                'sican_description': 'Asignar permisos a usuarios para calificar proyectos.'
            })
        """
        if self.request.user.has_perm('usuarios.fest_2019.soportes.ver'):
            items.append({
                'sican_categoria': 'Soportes',
                'sican_color': 'teal darken-4',
                'sican_order': 7,
                'sican_url': 'soportes/',
                'sican_name': 'Soportes',
                'sican_icon': 'insert_drive_file',
                'sican_description': 'Consulta de soportes por cédula titular del hogar.'
            })
        """
            
        if self.request.user.has_perm('usuarios.fest_2019.cortes.ver'):
            items.append({
                'sican_categoria': 'Cortes de pago',
                'sican_color': 'pink darken-3',
                'sican_order': 8,
                'sican_url': 'cortes/',
                'sican_name': 'Cortes de pago',
                'sican_icon': 'attach_money',
                'sican_description': 'Cortes de pago y cuentas de cobro'
            })

        if self.request.user.has_perm('usuarios.fest_2019.misproyectos.ver'):
            items.append({
                'sican_categoria': 'Mis proyectos',
                'sican_color': 'blue darken-3',
                'sican_order': 9,
                'sican_url': 'misproyectos/',
                'sican_name': 'Mis proyectos',
                'sican_icon': 'business_center',
                'sican_description': 'Registro de proyectos'
            })

        if self.request.user.has_perm('usuarios.fest_2019.proyectos_local.ver'):
            items.append({
                'sican_categoria': 'Proyectos (Profesionales locales)',
                'sican_color': 'red darken-3',
                'sican_order': 10,
                'sican_url': 'proyectos_local/',
                'sican_name': 'Proyectos (Profesionales locales)',
                'sican_icon': 'business_center',
                'sican_description': 'Primer filtro para la verificación de proyectos'
            })

        if self.request.user.has_perm('usuarios.fest_2019.proyectos_monitoreo.ver'):
            items.append({
                'sican_categoria': 'Proyectos (Monitoreo y Evaluación)',
                'sican_color': 'green darken-3',
                'sican_order': 11,
                'sican_url': 'proyectos_monitoreo/',
                'sican_name': 'Proyectos (Monitoreo y Evaluación)',
                'sican_icon': 'business_center',
                'sican_description': 'Segundo filtro para la verificación de proyectos'
            })

        if self.request.user.has_perm('usuarios.fest_2019.proyectos_especialistas.ver'):
            items.append({
                'sican_categoria': 'Proyectos (Especialistas)',
                'sican_color': 'blue-grey darken-4',
                'sican_order': 11,
                'sican_url': 'proyectos_especialistas/',
                'sican_name': 'Proyectos (Especialistas)',
                'sican_icon': 'business_center',
                'sican_description': 'Filtro final para la verificación de proyectos'
            })

        if self.request.user.has_perm('usuarios.fest_2019.migeoreferenciacion.ver'):
            items.append({
                'sican_categoria': 'Mi georeferenciación',
                'sican_color': 'brown darken-3',
                'sican_order': 12,
                'sican_url': 'migeoreferenciacion/',
                'sican_name': 'Mi georeferenciación',
                'sican_icon': 'map',
                'sican_description': 'Georeferenciación de hogares y proyectos con la app GeoDatabase'
            })

        if self.request.user.has_perm('usuarios.fest_2019.georeferenciacion.ver'):
            items.append({
                'sican_categoria': 'Georeferenciación',
                'sican_color': 'pink darken-3',
                'sican_order': 13,
                'sican_url': 'georeferenciacion/',
                'sican_name': 'Georeferenciación',
                'sican_icon': 'map',
                'sican_description': 'Georeferenciación de hogares y proyectos con la app GeoDatabase'
            })

        """
        if self.request.user.has_perm('usuarios.fest_2019.ruteo.ver'):
            items.append({
                'sican_categoria': 'Ruteo',
                'sican_color': 'orange darken-4',
                'sican_order': 9,
                'sican_url': 'ruteo/',
                'sican_name': 'Ruteo',
                'sican_icon': 'view_list',
                'sican_description': 'Asignación de rutas a los hogares'
            })
        """

        """
        if self.request.user.has_perm('usuarios.fest_2019.mishogares.ver'):
            items.append({
                'sican_categoria': 'Mis hogares',
                'sican_color': 'purple darken-4',
                'sican_order': 10,
                'sican_url': 'mis_hogares/',
                'sican_name': 'Mis hogares',
                'sican_icon': 'home',
                'sican_description': 'Registro de hogares asignados a mis rutas'
            })
        """

        return items

    def get_context_data(self, **kwargs):
        kwargs['title'] = "IRACA"
        kwargs['items'] = self.get_items()
        return super(Fest2019OptionsView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

class MiGeoreferenciacionListView(LoginRequiredMixin,
                           MultiplePermissionsRequiredMixin,
                           TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.migeoreferenciacion.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/migeoreferenciacion/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Mi Georeferenciación"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/migeoreferenciacion/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MiGeoreferenciacionListView,self).get_context_data(**kwargs)



class GeoreferenciacionListView(LoginRequiredMixin,
                           MultiplePermissionsRequiredMixin,
                           TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.georeferenciacion.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/georeferenciacion/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Georeferenciación"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/georeferenciacion/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(GeoreferenciacionListView,self).get_context_data(**kwargs)




class InformeGeoreferenciacionView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.georeferenciacion.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:

            if request.user.has_perms(self.permissions['ver']):
                reporte = Reportes.objects.create(
                    usuario=self.request.user,
                    nombre='Informe de georeferenciación',
                    consecutivo=Reportes.objects.filter(usuario=self.request.user).count() + 1
                )

                tasks.build_informe_georeferenciacion(reporte.id)
                return redirect('/reportes/')
            else:
                return HttpResponseRedirect('../../')



#----------------------------------------------------------------------------------


class MisProyectosListView(LoginRequiredMixin,
                           MultiplePermissionsRequiredMixin,
                           TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.misproyectos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misproyectos/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Mis proyectos"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/misproyectos/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisProyectosListView,self).get_context_data(**kwargs)


class MisProyectosUpdateView(LoginRequiredMixin,
                             MultiplePermissionsRequiredMixin,
                             UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misproyectos/editar.html'
    form_class = forms.FichaProyectoForm
    success_url = "../../"
    model = models.ProyectosApi

    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        if proyecto.json["documento"] != str(self.request.user.cedula) and self.request.user.id not in models.PermisosMisProyectos.objects.all().values_list('user__id', flat=True):
            return HttpResponseRedirect('../../')
        if proyecto.estado not in ['Cargado', 'Rechazo profesional local', 'Rechazo equipo monitoreo','Rechazo equipo especialistas']:
            return HttpResponseRedirect('../../')
        return super(MisProyectosUpdateView, self).dispatch(request, *args, **kwargs)

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misproyectos.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Mis proyectos"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['url_carga_consejos'] = '/rest/v1.0/usuarios/cargar/consejos/'
        kwargs['url_carga_comunidades'] = '/rest/v1.0/usuarios/cargar/comunidades/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisProyectosUpdateView, self).get_context_data(**kwargs)



    def get_initial(self):
        return {'pk':self.kwargs['pk']}


class MisProyectosEstadoView(LoginRequiredMixin,
                             MultiplePermissionsRequiredMixin,
                             FormView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misproyectos/estado.html'
    form_class = forms.EstadoProyectoForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        if proyecto.json["documento"] != str(self.request.user.cedula) and self.request.user.id not in models.PermisosMisProyectos.objects.all().values_list('user__id', flat=True):
            return HttpResponseRedirect('../../')

        if proyecto.estado not in ["Cargado", "Rechazo profesional local","Rechazo equipo monitoreo",'Rechazo equipo especialistas']:
            return HttpResponseRedirect('../../')

        return super(MisProyectosEstadoView, self).dispatch(request, *args, **kwargs)

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misproyectos.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Mis proyectos"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['proyecto'] = proyecto
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisProyectosEstadoView, self).get_context_data(**kwargs)


    def form_valid(self, form):
        models.ProyectosApi.objects.filter(id=self.kwargs['pk']).update(estado = form.cleaned_data['estado'], actualizar_app = False)
        models.ObservacionesProyectosApi.objects.create(
            proyecto=models.ProyectosApi.objects.get(id = self.kwargs['pk']),
            user = self.request.user,
            estado = form.cleaned_data['estado'],
            descripcion = form.cleaned_data['observacion']
        )
        return super(MisProyectosEstadoView, self).form_valid(form)


    def get_initial(self):
        return {'pk': self.kwargs['pk']}



class MisProyectosFlujoUpdateView(LoginRequiredMixin,
                                  MultiplePermissionsRequiredMixin,
                                  UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misproyectos/flujo_caja.html'
    form_class = forms.FlujoCajaForm
    success_url = "../../"
    model = models.ProyectosApi

    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        if proyecto.json["documento"] != str(self.request.user.cedula) and self.request.user.id not in models.PermisosMisProyectos.objects.all().values_list('user__id', flat=True):
            return HttpResponseRedirect('../../')
        if proyecto.estado not in ['Cargado', 'Rechazo profesional local', 'Rechazo equipo monitoreo','Rechazo equipo especialistas']:
            return HttpResponseRedirect('../../')
        return super(MisProyectosFlujoUpdateView, self).dispatch(request, *args, **kwargs)

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misproyectos.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Mis proyectos"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['meses'] = int(proyecto.duracion)
        kwargs['flujo_caja'] = json.dumps(proyecto.flujo_caja)
        kwargs['lineas'] = json.dumps(proyecto.json['data']['lines'])
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisProyectosFlujoUpdateView, self).get_context_data(**kwargs)



    def get_initial(self):
        return {'pk':self.kwargs['pk']}



class MisProyectosIdentificacionUpdateView(LoginRequiredMixin,
                                           MultiplePermissionsRequiredMixin,
                                           UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misproyectos/identificacion.html'
    form_class = forms.IdentificacionProyectosForm
    success_url = "../../"
    model = models.ProyectosApi


    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        if proyecto.json["documento"] != str(self.request.user.cedula) and self.request.user.id not in models.PermisosMisProyectos.objects.all().values_list('user__id', flat=True):
            return HttpResponseRedirect('../../')
        if proyecto.estado not in ['Cargado', 'Rechazo profesional local', 'Rechazo equipo monitoreo','Rechazo equipo especialistas']:
            return HttpResponseRedirect('../../')
        return super(MisProyectosIdentificacionUpdateView, self).dispatch(request, *args, **kwargs)


    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misproyectos.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Mis proyectos"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisProyectosIdentificacionUpdateView, self).get_context_data(**kwargs)



    def get_initial(self):
        return {'pk':self.kwargs['pk']}



class MisProyectosObservacionesView(LoginRequiredMixin,
                                    MultiplePermissionsRequiredMixin,
                                    TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misproyectos/observaciones.html'


    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misproyectos.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Mis proyectos"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['observaciones'] = proyecto.get_observaciones()
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisProyectosObservacionesView, self).get_context_data(**kwargs)





class MisProyectosHogaresView(LoginRequiredMixin,
                           MultiplePermissionsRequiredMixin,
                           TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.misproyectos.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misproyectos/hogares.html'


    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "Mis proyectos"
        kwargs['proyecto'] = proyecto
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisProyectosHogaresView,self).get_context_data(**kwargs)



#----------------------------------------------------------------------------------

class ProyectosLocalListView(LoginRequiredMixin,
                             MultiplePermissionsRequiredMixin,
                             TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.proyectos_local.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_local/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Proyectos (Profesionales locales)"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/proyectos_local/'
        kwargs['nombre_modulo'] = 'Proyectos (Profesionales locales)'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosLocalListView,self).get_context_data(**kwargs)


class ProyectosLocalUpdateView(LoginRequiredMixin,
                                   MultiplePermissionsRequiredMixin,
                                   UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_local/editar.html'
    form_class = forms.FichaProyectoFullForm
    success_url = "../../"
    model = models.ProyectosApi

    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])

        if proyecto.estado not in ['Enviado a revisión por profesional local']:
            return HttpResponseRedirect('../../')
        return super(ProyectosLocalUpdateView, self).dispatch(request, *args, **kwargs)


    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_local.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Profesionales locales)"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['url_carga_consejos'] = '/rest/v1.0/usuarios/cargar/consejos/'
        kwargs['url_carga_comunidades'] = '/rest/v1.0/usuarios/cargar/comunidades/'
        kwargs['nombre_modulo'] = 'Proyectos (Profesionales locales)'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosLocalUpdateView, self).get_context_data(**kwargs)



    def get_initial(self):
        return {'pk':self.kwargs['pk']}


class ProyectosLocalFlujoUpdateView(LoginRequiredMixin,
                                        MultiplePermissionsRequiredMixin,
                                        UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_local/flujo_caja.html'
    form_class = forms.FlujoCajaForm
    success_url = "../../"
    model = models.ProyectosApi

    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])

        if proyecto.estado not in ['Enviado a revisión por profesional local']:
            return HttpResponseRedirect('../../')
        return super(ProyectosLocalFlujoUpdateView, self).dispatch(request, *args, **kwargs)

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_local.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Profesionales locales)"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['meses'] = int(proyecto.duracion)
        kwargs['flujo_caja'] = json.dumps(proyecto.flujo_caja)
        kwargs['lineas'] = json.dumps(proyecto.json['data']['lines'])
        kwargs['nombre_modulo'] = 'Proyectos (Profesionales locales)'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosLocalFlujoUpdateView, self).get_context_data(**kwargs)



    def get_initial(self):
        return {'pk':self.kwargs['pk']}


class ProyectosLocalIdentificacionUpdateView(LoginRequiredMixin,
                                                 MultiplePermissionsRequiredMixin,
                                                 UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_local/identificacion.html'
    form_class = forms.IdentificacionProyectosForm
    success_url = "../../"
    model = models.ProyectosApi

    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])

        if proyecto.estado not in ['Enviado a revisión por profesional local']:
            return HttpResponseRedirect('../../')
        return super(ProyectosLocalIdentificacionUpdateView, self).dispatch(request, *args, **kwargs)

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_local.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Profesionales locales)"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['nombre_modulo'] = 'Proyectos (Profesionales locales)'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosLocalIdentificacionUpdateView, self).get_context_data(**kwargs)



    def get_initial(self):
        return {'pk':self.kwargs['pk']}


class ProyectosLocalVerificarView(LoginRequiredMixin,
                                  MultiplePermissionsRequiredMixin,
                                  FormView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_local/estado.html'
    form_class = forms.VerificarProyectoForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        departamentos_ids = models.PermisosCuentasDepartamentos.objects.filter(users=self.request.user).values_list('departamento__id', flat=True).distinct()

        try:
            id_departamento_proyecto = proyecto.municipio.departamento.id
        except:
            return HttpResponseRedirect('../../')
        else:

            if id_departamento_proyecto not in departamentos_ids:
                return HttpResponseRedirect('../../')
            if proyecto.estado not in ['Enviado a revisión por profesional local']:
                return HttpResponseRedirect('../../')
            return super(ProyectosLocalVerificarView, self).dispatch(request, *args, **kwargs)


    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_local.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Profesionales locales)"
        kwargs['nombre_modulo'] = 'Proyectos (Profesionales locales)'
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['proyecto'] = proyecto
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosLocalVerificarView, self).get_context_data(**kwargs)


    def form_valid(self, form):
        models.ProyectosApi.objects.filter(id=self.kwargs['pk']).update(estado = form.cleaned_data['estado'])

        if form.cleaned_data['estado'] == "Rechazo profesional local":
            models.ProyectosApi.objects.filter(id=self.kwargs['pk']).update(actualizar_app = True)

        models.ObservacionesProyectosApi.objects.create(
            proyecto=models.ProyectosApi.objects.get(id = self.kwargs['pk']),
            user = self.request.user,
            estado = form.cleaned_data['estado'],
            descripcion = form.cleaned_data['observacion']
        )
        return super(ProyectosLocalVerificarView, self).form_valid(form)


class ProyectosLocalHogaresView(LoginRequiredMixin,
                                MultiplePermissionsRequiredMixin,
                                TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.proyectos_local.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_local/hogares.html'


    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Profesionales locales)"
        kwargs['proyecto'] = proyecto
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosLocalHogaresView,self).get_context_data(**kwargs)


class ProyectosLocalObservacionesView(LoginRequiredMixin,
                                      MultiplePermissionsRequiredMixin,
                                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_local/observaciones.html'


    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_local.ver",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Profesionales locales)"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['observaciones'] = proyecto.get_observaciones()
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosLocalObservacionesView, self).get_context_data(**kwargs)


#----------------------------------------------------------------------------------

class ProyectosMonitoreoListView(LoginRequiredMixin,
                                 MultiplePermissionsRequiredMixin,
                                 TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.proyectos_monitoreo.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_monitoreo/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Proyectos (Monitoreo y Evaluación)"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/proyectos_monitoreo/'
        kwargs['nombre_modulo'] = 'Proyectos (Monitoreo y Evaluación)'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosMonitoreoListView,self).get_context_data(**kwargs)


class ProyectosMonitoreoUpdateView(LoginRequiredMixin,
                                   MultiplePermissionsRequiredMixin,
                                   UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_monitoreo/editar.html'
    form_class = forms.FichaProyectoFullForm
    success_url = "../../"
    model = models.ProyectosApi

    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])

        if proyecto.estado not in ['Vo Bo profesional local', 'Enviado a revisión equipo monitoreo']:
            return HttpResponseRedirect('../../')
        return super(ProyectosMonitoreoUpdateView, self).dispatch(request, *args, **kwargs)


    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_monitoreo.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Monitoreo y Evaluación)"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['url_carga_consejos'] = '/rest/v1.0/usuarios/cargar/consejos/'
        kwargs['url_carga_comunidades'] = '/rest/v1.0/usuarios/cargar/comunidades/'
        kwargs['nombre_modulo'] = 'Proyectos (Monitoreo y Evaluación)'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosMonitoreoUpdateView, self).get_context_data(**kwargs)



    def get_initial(self):
        return {'pk':self.kwargs['pk']}


class ProyectosMonitoreoFlujoUpdateView(LoginRequiredMixin,
                                        MultiplePermissionsRequiredMixin,
                                        UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_monitoreo/flujo_caja.html'
    form_class = forms.FlujoCajaForm
    success_url = "../../"
    model = models.ProyectosApi

    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])

        if proyecto.estado not in ['Vo Bo profesional local', 'Enviado a revisión equipo monitoreo']:
            return HttpResponseRedirect('../../')
        return super(ProyectosMonitoreoFlujoUpdateView, self).dispatch(request, *args, **kwargs)

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_monitoreo.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Monitoreo y Evaluación)"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['meses'] = int(proyecto.duracion)
        kwargs['flujo_caja'] = json.dumps(proyecto.flujo_caja)
        kwargs['lineas'] = json.dumps(proyecto.json['data']['lines'])
        kwargs['nombre_modulo'] = 'Proyectos (Monitoreo y Evaluación)'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosMonitoreoFlujoUpdateView, self).get_context_data(**kwargs)



    def get_initial(self):
        return {'pk':self.kwargs['pk']}


class ProyectosMonitoreoIdentificacionUpdateView(LoginRequiredMixin,
                                                 MultiplePermissionsRequiredMixin,
                                                 UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_monitoreo/identificacion.html'
    form_class = forms.IdentificacionProyectosForm
    success_url = "../../"
    model = models.ProyectosApi

    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])

        if proyecto.estado not in ['Vo Bo profesional local', 'Enviado a revisión equipo monitoreo']:
            return HttpResponseRedirect('../../')
        return super(ProyectosMonitoreoIdentificacionUpdateView, self).dispatch(request, *args, **kwargs)

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_monitoreo.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Monitoreo y Evaluación)"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['nombre_modulo'] = 'Proyectos (Monitoreo y Evaluación)'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosMonitoreoIdentificacionUpdateView, self).get_context_data(**kwargs)



    def get_initial(self):
        return {'pk':self.kwargs['pk']}


class ProyectosMonitoreoObservacionesView(LoginRequiredMixin,
                                          MultiplePermissionsRequiredMixin,
                                          TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_monitoreo/observaciones.html'


    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_monitoreo.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Monitoreo y Evaluación)"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['observaciones'] = proyecto.get_observaciones()
        kwargs['nombre_modulo'] = 'Proyectos (Monitoreo y Evaluación)'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosMonitoreoObservacionesView, self).get_context_data(**kwargs)



class ProyectosMonitoreoEstadoView(LoginRequiredMixin,
                                   MultiplePermissionsRequiredMixin,
                                   FormView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_monitoreo/estado.html'
    form_class = forms.EstadoMonitoreoProyectoForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])

        if proyecto.estado not in ['Vo Bo profesional local','Enviado a revisión equipo monitoreo']:
            return HttpResponseRedirect('../../')
        return super(ProyectosMonitoreoEstadoView, self).dispatch(request, *args, **kwargs)

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_monitoreo.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Monitoreo y Evaluación)"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['nombre_modulo'] = 'Proyectos (Monitoreo y Evaluación)'
        kwargs['proyecto'] = proyecto
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosMonitoreoEstadoView, self).get_context_data(**kwargs)


    def form_valid(self, form):
        models.ProyectosApi.objects.filter(id=self.kwargs['pk']).update(estado = form.cleaned_data['estado'], actualizar_app = False)

        if form.cleaned_data['estado'] == "Rechazo equipo monitoreo":
            models.ProyectosApi.objects.filter(id=self.kwargs['pk']).update(actualizar_app = True)

        models.ObservacionesProyectosApi.objects.create(
            proyecto=models.ProyectosApi.objects.get(id = self.kwargs['pk']),
            user = self.request.user,
            estado = form.cleaned_data['estado'],
            descripcion = form.cleaned_data['observacion']
        )
        return super(ProyectosMonitoreoEstadoView, self).form_valid(form)


    def get_initial(self):
        return {'pk': self.kwargs['pk']}



class ProyectosMonitoreoHogaresView(LoginRequiredMixin,
                                MultiplePermissionsRequiredMixin,
                                TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.proyectos_monitoreo.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_monitoreo/hogares.html'


    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Monitoreo y Evaluación)"
        kwargs['nombre_modulo'] = 'Proyectos (Monitoreo y Evaluación)'
        kwargs['proyecto'] = proyecto
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosMonitoreoHogaresView,self).get_context_data(**kwargs)


#----------------------------------------------------------------------------------

class ProyectosEspecialistasListView(LoginRequiredMixin,
                                 MultiplePermissionsRequiredMixin,
                                 TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.proyectos_especialistas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_especialistas/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Proyectos (Especialistas)"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/proyectos_especialistas/'
        kwargs['nombre_modulo'] = 'Proyectos (Especialistas)'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosEspecialistasListView,self).get_context_data(**kwargs)


class ProyectosEspecialistasUpdateView(LoginRequiredMixin,
                                   MultiplePermissionsRequiredMixin,
                                   UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_especialistas/editar.html'
    form_class = forms.FichaProyectoFullForm
    success_url = "../../"
    model = models.ProyectosApi

    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])

        if proyecto.estado not in ['Vo Bo equipo monitoreo', 'Enviado a revisión especialistas']:
            return HttpResponseRedirect('../../')
        return super(ProyectosEspecialistasUpdateView, self).dispatch(request, *args, **kwargs)


    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_especialistas.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Especialistas)"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['url_carga_consejos'] = '/rest/v1.0/usuarios/cargar/consejos/'
        kwargs['url_carga_comunidades'] = '/rest/v1.0/usuarios/cargar/comunidades/'
        kwargs['nombre_modulo'] = 'Proyectos (Especialistas)'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosEspecialistasUpdateView, self).get_context_data(**kwargs)



    def get_initial(self):
        return {'pk':self.kwargs['pk']}


class ProyectosEspecialistasFlujoUpdateView(LoginRequiredMixin,
                                        MultiplePermissionsRequiredMixin,
                                        UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_especialistas/flujo_caja.html'
    form_class = forms.FlujoCajaForm
    success_url = "../../"
    model = models.ProyectosApi

    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])

        if proyecto.estado not in ['Vo Bo equipo monitoreo', 'Enviado a revisión especialistas']:
            return HttpResponseRedirect('../../')
        return super(ProyectosEspecialistasFlujoUpdateView, self).dispatch(request, *args, **kwargs)

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_especialistas.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Especialistas)"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['meses'] = int(proyecto.duracion)
        kwargs['flujo_caja'] = json.dumps(proyecto.flujo_caja)
        kwargs['lineas'] = json.dumps(proyecto.json['data']['lines'])
        kwargs['nombre_modulo'] = 'Proyectos (Especialistas)'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosEspecialistasFlujoUpdateView, self).get_context_data(**kwargs)



    def get_initial(self):
        return {'pk':self.kwargs['pk']}


class ProyectosEspecialistasIdentificacionUpdateView(LoginRequiredMixin,
                                                 MultiplePermissionsRequiredMixin,
                                                 UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_especialistas/identificacion.html'
    form_class = forms.IdentificacionProyectosForm
    success_url = "../../"
    model = models.ProyectosApi

    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])

        if proyecto.estado not in ['Vo Bo equipo monitoreo', 'Enviado a revisión especialistas']:
            return HttpResponseRedirect('../../')
        return super(ProyectosEspecialistasIdentificacionUpdateView, self).dispatch(request, *args, **kwargs)

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_especialistas.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Especialistas)"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['nombre_modulo'] = 'Proyectos (Especialistas)'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosEspecialistasIdentificacionUpdateView, self).get_context_data(**kwargs)



    def get_initial(self):
        return {'pk':self.kwargs['pk']}


class ProyectosEspecialistasObservacionesView(LoginRequiredMixin,
                                          MultiplePermissionsRequiredMixin,
                                          TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_especialistas/observaciones.html'


    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_especialistas.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Especialistas)"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['observaciones'] = proyecto.get_observaciones()
        kwargs['nombre_modulo'] = 'Proyectos (Especialistas)'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosEspecialistasObservacionesView, self).get_context_data(**kwargs)



class ProyectosEspecialistasEstadoView(LoginRequiredMixin,
                                   MultiplePermissionsRequiredMixin,
                                   FormView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_especialistas/estado.html'
    form_class = forms.EstadoEspecialistasProyectoForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])

        if proyecto.estado not in ['Vo Bo equipo monitoreo', 'Enviado a revisión especialistas']:
            return HttpResponseRedirect('../../')
        return super(ProyectosEspecialistasEstadoView, self).dispatch(request, *args, **kwargs)

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.proyectos_especialistas.editar",
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Especialistas)"
        kwargs['breadcrumb_active'] = f"{proyecto.nombre_proyecto}"
        kwargs['nombre_modulo'] = 'Proyectos (Especialistas)'
        kwargs['proyecto'] = proyecto
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosEspecialistasEstadoView, self).get_context_data(**kwargs)


    def form_valid(self, form):
        models.ProyectosApi.objects.filter(id=self.kwargs['pk']).update(estado = form.cleaned_data['estado'], actualizar_app = False)

        if form.cleaned_data['estado'] == "Rechazo equipo especialistas":
            models.ProyectosApi.objects.filter(id=self.kwargs['pk']).update(actualizar_app = True)

        models.ObservacionesProyectosApi.objects.create(
            proyecto=models.ProyectosApi.objects.get(id = self.kwargs['pk']),
            user = self.request.user,
            estado = form.cleaned_data['estado'],
            descripcion = form.cleaned_data['observacion']
        )
        return super(ProyectosEspecialistasEstadoView, self).form_valid(form)


    def get_initial(self):
        return {'pk': self.kwargs['pk']}



class ProyectosEspecialistasHogaresView(LoginRequiredMixin,
                                MultiplePermissionsRequiredMixin,
                                TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.proyectos_especialistas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/proyectos_especialistas/hogares.html'


    def get_context_data(self, **kwargs):
        proyecto = models.ProyectosApi.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "Proyectos (Especialistas)"
        kwargs['nombre_modulo'] = 'Proyectos (Especialistas)'
        kwargs['proyecto'] = proyecto
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(ProyectosEspecialistasHogaresView,self).get_context_data(**kwargs)


#-------------------------------------- BD ----------------------------------------

class HogaresListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.db.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/bd/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "BASE DE DATOS HOGARES"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/bd/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.fest_2019.db.crear')
        return super(HogaresListView,self).get_context_data(**kwargs)




class HogaresCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/bd/crear.html'
    form_class = forms.HogarCreateForm
    success_url = "../"
    models = models.Hogares

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.db.ver",
                "usuarios.fest_2019.db.crear"
            ]
        }
        return permissions

    def form_valid(self, form):
        self.object = form.save()
        message = 'Se creó el hogar: {0}'.format(form.cleaned_data['documento'])
        messages.add_message(self.request, messages.INFO, message)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVO HOGAR"
        return super(HogaresCreateView,self).get_context_data(**kwargs)


class HogaresUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/bd/editar.html'
    form_class = forms.HogarUpdateForm
    success_url = "../../"
    model = models.Hogares

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.db.ver",
                "usuarios.fest_2019.db.editar"
            ]
        }
        return permissions

    def form_valid(self, form):
        self.object = form.save()
        message = 'Se edito el hogar: {0}'.format(self.object.documento)
        messages.add_message(self.request, messages.INFO, message)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "EDITAR HOGAR"
        return super(HogaresUpdateView,self).get_context_data(**kwargs)


    def get_initial(self):
        return {'pk':self.kwargs['pk']}

#----------------------------------------------------------------------------------

#----------------------------------- ENTREGABLES ----------------------------------

class EntregablesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entregables.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/entregables/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Entregables: Componentes"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/entregables/'
        return super(EntregablesListView,self).get_context_data(**kwargs)



class InformeActividadesListView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.entregables.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:

            if request.user.has_perms(self.permissions['ver']):
                reporte = Reportes.objects.create(
                    usuario=self.request.user,
                    nombre='Informe de actividades',
                    consecutivo=Reportes.objects.filter(usuario=self.request.user).count() + 1
                )

                tasks.build_informe_actividades.delay(reporte.id)
                return redirect('/reportes/')
            else:
                return HttpResponseRedirect('../../')



class VisitasListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entregables.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/entregables/visitas/lista.html'


    def get_context_data(self, **kwargs):
        componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        kwargs['title'] = "Entregables: Momentos"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/entregables/{0}/momentos/'.format(componente.id)
        kwargs['breadcrum_active'] = componente.nombre
        return super(VisitasListView,self).get_context_data(**kwargs)


class InstrumentosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entregables.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/entregables/visitas/instrumentos/lista.html'


    def get_context_data(self, **kwargs):
        componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        kwargs['title'] = "Entregables: Instrumentos"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/entregables/{0}/momentos/{1}/instrumentos/'.format(componente.id,momento.id)
        kwargs['breadcrum_1'] = componente.nombre
        kwargs['breadcrum_active'] = momento.nombre
        return super(InstrumentosListView,self).get_context_data(**kwargs)

class InstrumentosInformeListView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.instrumento = models.Instrumentos.objects.get(id=self.kwargs['pk_instrumento'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "ver": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.entregables.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:

            if request.user.has_perms(self.permissions['ver']):
                reporte = Reportes.objects.create(
                    usuario=self.request.user,
                    nombre='Instrumento: {0} - Momento: {1} - Componente: {2}'.format(self.instrumento.nombre,self.momento.nombre,self.componente.nombre),
                    consecutivo=Reportes.objects.filter(usuario=self.request.user).count() + 1
                )

                tasks.build_informe_instrumento.delay(reporte.id, self.instrumento.id)
                return redirect('/reportes/')
            else:
                return HttpResponseRedirect('../../')

#----------------------------------------------------------------------------------

#---------------------------------------- RUTAS -----------------------------------

class RutasListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.rutas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/rutas/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.fest_2019.rutas.crear')
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasListView,self).get_context_data(**kwargs)


class RutasCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/crear.html'
    form_class = forms.RutasCreateForm
    success_url = "../"

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
                "usuarios.fest_2019.rutas.crear"
            ]
        }
        return permissions

    def form_valid(self, form):
        contrato = rh_models.Contratos.objects.get(id=form.cleaned_data['contrato'])


        self.object = models.Rutas.objects.create(
            nombre=form.cleaned_data['nombre'],
            componente=form.cleaned_data['componente'],
            contrato=contrato,
            valor=contrato.valor.amount,
            valor_transporte=utils.autonumeric2float(form.cleaned_data['valor_transporte']),
            valor_otros=utils.autonumeric2float(form.cleaned_data['valor_otros']),
            usuario_creacion=self.request.user,
            usuario_actualizacion=self.request.user,
            tipo_pago = form.cleaned_data['tipo_pago']
        )
        message = 'Se creó la ruta: {0}'.format(form.cleaned_data['nombre'])
        messages.add_message(self.request, messages.INFO, message)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVA RUTA"
        kwargs['url_contratos'] = '/rest/v1.0/fest_2019/rutas/autocomplete/contratos/'
        return super(RutasCreateView,self).get_context_data(**kwargs)


class RutasUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/editar.html'
    form_class = forms.RutasCreateForm
    success_url = "../../"

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
                "usuarios.fest_2019.rutas.editar"
            ]
        }
        return permissions

    def form_valid(self, form):

        contrato = rh_models.Contratos.objects.get(id=form.cleaned_data['contrato'])


        models.Rutas.objects.filter(id = self.kwargs['pk_ruta']).update(
            nombre=form.cleaned_data['nombre'],
            componente=form.cleaned_data['componente'],
            contrato=contrato,
            valor=contrato.valor.amount,
            valor_transporte=utils.autonumeric2float(form.cleaned_data['valor_transporte']),
            valor_otros=utils.autonumeric2float(form.cleaned_data['valor_otros']),
            usuario_actualizacion=self.request.user,
            tipo_pago=form.cleaned_data['tipo_pago']
        )
        message = 'Se actualizo la ruta: {0}'.format(form.cleaned_data['nombre'])
        messages.add_message(self.request, messages.INFO, message)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        kwargs['title'] = "EDITAR RUTA"
        kwargs['url_contratos'] = '/rest/v1.0/fest_2019/rutas/autocomplete/contratos/'
        kwargs['nombre_ruta'] = ruta.nombre
        return super(RutasUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk':self.kwargs['pk_ruta']}


class RutasHogaresListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/hogares/lista.html'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=request.user)
        except:
            self.permiso = None

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
                "usuarios.fest_2019.rutas.hogares.ver",
            ],
            "crear": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
                "usuarios.fest_2019.rutas.hogares.ver",
                "usuarios.fest_2019.rutas.hogares.crear",
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
                    if self.permiso == None:
                        return HttpResponseRedirect('../../')
                    else:
                        ids_ver = self.permiso.rutas_ver.all()
                        if self.ruta in ids_ver:
                            if request.method.lower() in self.http_method_names:
                                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                            else:
                                handler = self.http_method_not_allowed
                            return handler(request, *args, **kwargs)
                        else:
                            return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')


    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id = kwargs['pk_ruta'])
        kwargs['title'] = "Rutas"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/rutas/hogares/{0}/'.format(kwargs['pk_ruta'])
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions['crear'])
        kwargs['breadcrum_active'] = ruta.nombre
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasHogaresListView,self).get_context_data(**kwargs)





class RutaCrearHogarView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/hogares/crear.html'
    form_class = forms.HogarCreateForm
    success_url = "../"
    models = models.Hogares

    def get_permission_required(self, request=None):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
                "usuarios.fest_2019.rutas.hogares.ver",
                "usuarios.fest_2019.rutas.hogares.crear",
            ]
        }
        return permissions

    def form_valid(self, form):
        documento = form.cleaned_data['documento']
        if models.Hogares.objects.filter(documento = documento).count() == 0:
            self.object = form.save()
            self.object.rutas.add(self.ruta)
        else:
            hogar = models.Hogares.objects.get(documento = documento)
            hogar.rutas.add(self.ruta)
        message = 'Se creó el hogar: {0}'.format(form.cleaned_data['documento'])
        messages.add_message(self.request, messages.INFO, message)
        self.ruta.update_hogares_inscritos()
        return HttpResponseRedirect("../")


    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVO HOGAR"
        kwargs['breadcrum_active'] = self.ruta.nombre
        return super(RutaCrearHogarView,self).get_context_data(**kwargs)





class RutasHogaresCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/hogares/cargar.html'
    form_class = forms.RutasHogaresForm
    success_url = "../"

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
                "usuarios.fest_2019.rutas.hogares.ver",
                "usuarios.fest_2019.rutas.hogares.crear"
            ]
        }
        return permissions

    def form_valid(self, form):
        ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        wb = openpyxl.load_workbook(form.cleaned_data['file'])
        ws = wb.get_active_sheet()
        hogares = []
        vinculacion = []

        for file in ws.rows:
            hogares.append(file[0].value)
            if file[1].value == "SI":
                vinculacion.append(file[0].value)

        if str(ruta.componente.consecutivo) == '1':
            objetos_hogares = models.Hogares.objects.filter(ruta_1 = None)
            cantidad_hogares = objetos_hogares.filter(documento__in=hogares).update(ruta_1 = ruta)

        elif str(ruta.componente.consecutivo) == '2':
            objetos_hogares = models.Hogares.objects.filter(ruta_2 = None)
            cantidad_hogares = objetos_hogares.filter(documento__in=hogares).update(ruta_2=ruta)

        elif str(ruta.componente.consecutivo) == '3':
            objetos_hogares = models.Hogares.objects.filter(ruta_3 = None)
            cantidad_hogares = objetos_hogares.filter(documento__in=hogares).update(ruta_3=ruta)

        elif str(ruta.componente.consecutivo) == '4':
            objetos_hogares = models.Hogares.objects.filter(ruta_4 = None)
            cantidad_hogares = objetos_hogares.filter(documento__in=hogares).update(ruta_4=ruta)

        else:
            objetos_hogares = models.Hogares.objects.none()
            cantidad_hogares = 0


        cantidad_vinculacion = models.Hogares.objects.filter(ruta_vinculacion=None,documento__in=vinculacion).update(ruta_vinculacion = ruta)

        ruta.update_hogares_inscritos()


        message = 'Hogares inscritos: {0}, Asignados para vinculación: {1}'.format(cantidad_hogares,cantidad_vinculacion)
        messages.add_message(self.request, messages.INFO, message)

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        kwargs['title'] = "RUTAS"
        kwargs['breadcrum_active'] = ruta.nombre
        return super(RutasHogaresCreateView,self).get_context_data(**kwargs)


class RutasHogaresVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/hogares/ver.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.hogar = models.Hogares.objects.get(id=self.kwargs['pk_hogar'])
        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=request.user)
        except:
            self.permiso = None

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
                "usuarios.fest_2019.rutas.hogares.ver",
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
                    if self.permiso == None:
                        return HttpResponseRedirect('../../')
                    else:
                        ids_ver = self.permiso.rutas_ver.all()
                        if self.ruta in ids_ver:
                            if request.method.lower() in self.http_method_names:
                                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                            else:
                                handler = self.http_method_not_allowed
                            return handler(request, *args, **kwargs)
                        else:
                            return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')


    def get_context_data(self, **kwargs):
        kwargs['hogar'] = self.hogar
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.hogar.documento
        return super(RutasHogaresVerView,self).get_context_data(**kwargs)


class RutasActividadesListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/actividades/lista.html'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=request.user)
        except:
            self.permiso = None

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
            ],
            "valores": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
                "usuarios.fest_2019.rutas.actividades.valores",
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
                    if self.permiso == None:
                        return HttpResponseRedirect('../../')
                    else:
                        ids_ver = self.permiso.rutas_ver.all()
                        if self.ruta in ids_ver:
                            if request.method.lower() in self.http_method_names:
                                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                            else:
                                handler = self.http_method_not_allowed
                            return handler(request, *args, **kwargs)
                        else:
                            return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')


    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id = kwargs['pk_ruta'])
        kwargs['title'] = "Actividades"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/rutas/actividades/{0}/'.format(kwargs['pk_ruta'])
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions['valores'])
        kwargs['breadcrum_active'] = ruta.nombre
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasActividadesListView,self).get_context_data(**kwargs)




class RutasActividadesListObjetosView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/actividades/objetos/lista.html'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])


        if request.user.is_superuser:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('../../')



    def get_context_data(self, **kwargs):

        kwargs['title'] = "Objetos"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/rutas/actividades/{0}/objetos/{1}/'.format(kwargs['pk_ruta'],kwargs['pk_momento'])

        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.momento.nombre

        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasActividadesListObjetosView,self).get_context_data(**kwargs)



class RutasActividadesObjeroCeroView(View):


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.objeto = models.CuposRutaObject.objects.get(id=self.kwargs['pk_cupo'])


        if request.user.is_superuser and self.momento.nombre == 'Visita 1':

            self.objeto.valor = 0
            self.objeto.estado = 'Reportado'
            self.objeto.save()

            return HttpResponseRedirect('../../')
        else:
            return HttpResponseRedirect('../../')










class RutasActividadesValoresView(MultiplePermissionsRequiredMixin,FormView):

    template_name = 'fest_2019/rutas/actividades/valores.html'
    login_url = settings.LOGIN_URL
    form_class = forms.ValoresActividadesForm
    success_url = '../'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
                "usuarios.fest_2019.rutas.actividades.ver",
                "usuarios.fest_2019.rutas.actividades.valores",
            ]
        }

        return super(RutasActividadesValoresView,self).dispatch(request, *args, **kwargs)



    def get_ids_momentos(self):
        data = []

        for momento in models.Momentos.objects.filter(componente=self.ruta.componente):
            data.append('id_valor_' + str(momento.id))

        return json.dumps(data)


    def form_valid(self, form):
        json_data = json.dumps(form.cleaned_data)
        models.Rutas.objects.filter(id = self.ruta.id).update(valores_actividades = json_data)
        return super(RutasActividadesValoresView, self).form_valid(form)



    def get_context_data(self, **kwargs):
        kwargs['title'] = "Valor actividades"
        kwargs['breadcrum_active'] = self.ruta.nombre
        kwargs['ids_momentos'] = self.get_ids_momentos()

        return super(RutasActividadesValoresView, self).get_context_data(**kwargs)




    def get_initial(self):
        return {'pk_ruta':self.kwargs['pk_ruta']}


class RutasActividadesHogaresListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/actividades/hogares/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=request.user)
        except:
            self.permiso = None

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
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
                    if self.permiso == None:
                        return HttpResponseRedirect('../../')
                    else:
                        ids_ver = self.permiso.rutas_ver.all()
                        if self.ruta in ids_ver:
                            if request.method.lower() in self.http_method_names:
                                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                            else:
                                handler = self.http_method_not_allowed
                            return handler(request, *args, **kwargs)
                        else:
                            return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/rutas/actividades/{0}/hogares/{1}/'.format(kwargs['pk_ruta'],kwargs['pk_momento'])
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.momento.nombre
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasActividadesHogaresListView,self).get_context_data(**kwargs)


class RutasInstrumentosHogaresListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/actividades/hogares/instrumentos/lista.html'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=request.user)
        except:
            self.permiso = None

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
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
                    if self.permiso == None:
                        return HttpResponseRedirect('../../')
                    else:
                        ids_ver = self.permiso.rutas_ver.all()
                        if self.ruta in ids_ver:
                            if request.method.lower() in self.http_method_names:
                                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                            else:
                                handler = self.http_method_not_allowed
                            return handler(request, *args, **kwargs)
                        else:
                            return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

    def get_permiso_ruta(self, ruta):
        permiso = False

        if self.request.user.is_superuser:
            permiso = True

        else:
            try:
                obj = models.PermisosCuentasRutas.objects.get(user = self.request.user)
            except:
                pass
            else:
                if ruta.id in obj.rutas_aprobar.all().values_list('id',flat=True):
                    permiso = True
                else:
                    permiso = False

        return permiso

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/rutas/actividades/{0}/instrumentos/{1}/'.format(
            kwargs['pk_ruta'],
            kwargs['pk_momento'],
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.momento.nombre
        kwargs['permiso_aprobar'] = self.get_permiso_ruta(self.ruta)
        kwargs['instrumentos'] = self.ruta.get_instrumentos_list(self.momento)
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasInstrumentosHogaresListView,self).get_context_data(**kwargs)



class RutasInstrumentosFormHogaresListView(CreateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.instrumento = models.Instrumentos.objects.get(id=self.kwargs['pk_instrumento'])

        try:
            self.modelos = modelos_instrumentos.get_modelo(self.instrumento.modelo)
        except:
            return HttpResponseRedirect('../../')

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver"
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
        return self.modelos.get('template')


    def get_form_class(self):
        self.model = self.modelos.get('model')
        return self.modelos.get('form')


    def update_objeto_instrumento(self,id,modelo,creacion):

        instrumento = models.InstrumentosRutaObject.objects.get(id = id)

        if creacion:
            models.InstrumentosRutaObject.objects.filter(id = id).update(
                usuario_creacion=self.request.user
            )

            models.InstrumentosTrazabilidadRutaObject.objects.create(
                instrumento = instrumento,
                user = self.request.user,
                observacion = 'Creación del soporte'
            )

        else:
            models.InstrumentosTrazabilidadRutaObject.objects.create(
                instrumento=instrumento,
                user=self.request.user,
                observacion='Actualización del soporte'
            )

        models.InstrumentosRutaObject.objects.filter(id=id).update(
            modelo = self.instrumento.nombre,
            soporte = modelo.id,
            fecha_actualizacion = timezone.now(),
            usuario_actualizacion = self.request.user,
            consecutivo = self.instrumento.consecutivo,
            nombre = self.instrumento.short_name,
            estado = 'cargado'
        )

        self.ruta.update_novedades()

        return 'Ok'



    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.ruta = self.ruta
        self.object.instrumento = self.instrumento
        self.object.nombre = self.instrumento.short_name
        self.object.save()

        self.object.hogares.clear()

        if self.instrumento.nivel == 'individual':
            self.object.hogares.add(form.cleaned_data['hogares'])

        elif self.instrumento.nivel == 'ruta':
            pass

        else:
            self.object.hogares.add(*form.cleaned_data['hogares'])


        objeto = models.InstrumentosRutaObject.objects.create(ruta=self.ruta, momento=self.momento, instrumento=self.instrumento)
        ids = self.object.hogares.all().values_list('id',flat = True)
        objeto.hogares.add(*ids)
        models.ObservacionesInstrumentoRutaObject.objects.create(instrumento = objeto,usuario_creacion = self.request.user,observacion = "Creación del instrumento")

        self.update_objeto_instrumento(objeto.id, self.object, True)
        objeto.clean_similares()


        return HttpResponseRedirect(self.get_success_url())


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.momento.nombre
        kwargs['breadcrum_active'] = self.instrumento.short_name
        kwargs['ruta_breadcrum'] = 'Rutas'
        kwargs['url_ruta_breadcrum'] = '/fest_2019/rutas/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasInstrumentosFormHogaresListView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk_ruta': self.ruta.id, 'short_name': self.instrumento.short_name, 'pk_instrumento': self.instrumento.pk}


class RutasInstrumentosHogaresDeleteView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.modelos = modelos_instrumentos.get_modelo(self.instrumento_object.instrumento.modelo)

        self.permissions = {
            "eliminar": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver"
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions['eliminar']):
                if self.instrumento_object.estado == 'cargado':
                    self.modelos.get('model').objects.get(id = self.instrumento_object.soporte).delete()
                    models.InstrumentosTrazabilidadRutaObject.objects.filter(instrumento = self.instrumento_object).delete()
                    models.ObservacionesInstrumentoRutaObject.objects.filter(instrumento = self.instrumento_object).delete()
                    self.instrumento_object.delete()
                    self.ruta.update_novedades()
                    return HttpResponseRedirect('../../')
                else:
                    return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')


class AprobarInstrumentoHogaresView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.modelos = modelos_instrumentos.get_modelo(self.instrumento_object.instrumento.modelo)

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=request.user)
        except:
            self.permiso = None

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if request.user.is_superuser:
                    self.instrumento_object.estado = 'aprobado'
                    models.InstrumentosTrazabilidadRutaObject.objects.create(
                        instrumento=self.instrumento_object,
                        user=self.request.user,
                        observacion='Aprobación del soporte'
                    )
                    models.ObservacionesInstrumentoRutaObject.objects.create(
                        usuario_creacion=self.request.user,
                        instrumento=self.instrumento_object,
                        observacion="Soporte aprobado"
                    )
                    self.instrumento_object.save()

                    aprobable = self.ruta.get_aprobable_valor(self.momento)


                    if aprobable['aprobable'] == 'si':
                        cupo = models.CuposRutaObject.objects.create(
                            ruta = self.ruta,
                            momento = self.momento,
                            estado = "Reportado",
                            valor = aprobable['valor']
                        )

                    self.ruta.update_novedades()
                    self.ruta.update_progreso()
                    models.InstrumentosRutaObject.objects.filter(id = self.instrumento_object.id).update(cupo_object = cupo)

                    return HttpResponseRedirect('../../')
                else:
                    if self.permiso == None:
                        return HttpResponseRedirect('../../')
                    else:
                        ids_aprobar= self.permiso.rutas_aprobar.all()
                        if self.ruta in ids_aprobar:
                            self.instrumento_object.estado = 'aprobado'
                            models.InstrumentosTrazabilidadRutaObject.objects.create(
                                instrumento=self.instrumento_object,
                                user=self.request.user,
                                observacion='Aprobación del soporte'
                            )
                            models.ObservacionesInstrumentoRutaObject.objects.create(
                                usuario_creacion = self.request.user,
                                instrumento=self.instrumento_object,
                                observacion = "Soporte aprobado"
                            )
                            self.instrumento_object.save()
                            aprobable = self.ruta.get_aprobable_valor(self.momento)

                            if aprobable['aprobable'] == 'si':
                                cupo = models.CuposRutaObject.objects.create(
                                    ruta=self.ruta,
                                    momento=self.momento,
                                    estado="Reportado",
                                    valor=aprobable['valor']
                                )

                            self.ruta.update_novedades()
                            self.ruta.update_progreso()
                            models.InstrumentosRutaObject.objects.filter(id=self.instrumento_object.id).update(cupo_object=cupo)

                            return HttpResponseRedirect('../../')
                        else:
                            return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')




class RutasInstrumentosVerHogaresView(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])
        self.instrumento = self.instrumento_object.instrumento
        self.modelos = modelos_instrumentos.get_modelo(self.instrumento.modelo)
        self.objeto = self.modelos.get('model').objects.get(id=self.instrumento_object.soporte)

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=request.user)
        except:
            self.permiso = None

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
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
                    if self.permiso == None:
                        return HttpResponseRedirect('../../')
                    else:
                        ids_ver = self.permiso.rutas_ver.all()
                        if self.ruta in ids_ver:
                            if request.method.lower() in self.http_method_names:
                                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                            else:
                                handler = self.http_method_not_allowed
                            return handler(request, *args, **kwargs)
                        else:
                            return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

    def get_template_names(self):
        return self.modelos.get('template_ver')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.momento.nombre
        kwargs['breadcrum_active'] = self.instrumento.short_name
        kwargs['objeto'] = self.objeto
        kwargs['ruta_breadcrum'] = 'Rutas'
        kwargs['url_ruta_breadcrum'] = '/iraca/rutas/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasInstrumentosVerHogaresView,self).get_context_data(**kwargs)




class RutasInstrumentoHogarAprobarView(View):

    login_url = settings.LOGIN_URL

    def aprobar(self,ruta,momento,hogar):

        message = ''

        try:
            cupo = models.CuposRutaObject.objects.get(ruta = ruta,momento=momento,hogar=hogar)
        except:
            try:
                obj = models.CuposRutaObject.objects.filter(ruta=ruta,momento=momento,estado='asignado')[0]
            except:
                message = 'No hay cupos disponibles'
            else:
                obj.hogar = hogar
                obj.estado = 'Reportado'
                obj.save()

                models.InstrumentosRutaObject.objects.filter(ruta = ruta,momento = momento,hogar = hogar).update(estado = 'aprobado')


                for instrumento in models.InstrumentosRutaObject.objects.filter(ruta = ruta,momento = momento,hogar = hogar):
                    models.InstrumentosTrazabilidadRutaObject.objects.create(
                        instrumento=instrumento,
                        user=self.request.user,
                        observacion='Aprobación del soporte'
                    )

                    models.ObservacionesInstrumentoRutaObject.objects.create(
                        usuario_creacion=self.request.user,
                        instrumento=instrumento,
                        observacion="Soporte aprobado"
                    )


                ruta.update_novedades()
                message = 'Se ha aprobado el momento, valor: {0}'.format(str(obj.valor))
        else:
            message = 'Ya se ha pagado anteriormente este momento'

        return message

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.hogar = models.Hogares.objects.get(id=self.kwargs['pk_hogar'])


        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=request.user)
        except:
            self.permiso = None

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if request.user.is_superuser:
                    message = self.aprobar(self.ruta,self.momento,self.hogar)
                    messages.add_message(self.request, messages.INFO, message)
                    return HttpResponseRedirect('../')
                else:
                    if self.permiso == None:
                        return HttpResponseRedirect('../')
                    else:
                        ids_ver = self.permiso.rutas_aprobar.all()
                        if self.ruta in ids_ver:
                            message = self.aprobar(self.ruta,self.momento,self.hogar)
                            messages.add_message(self.request, messages.INFO, message)
                            return HttpResponseRedirect('../')
                        else:
                            return HttpResponseRedirect('../')
            else:
                return HttpResponseRedirect('../')


"""
class RutasInstrumentoHogarRechazarView(View):

    login_url = settings.LOGIN_URL

    def rechazar(self,ruta,momento,hogar):

        message = ''

        try:
            cupo = models.CuposRutaObject.objects.get(ruta = ruta,momento=momento,hogar=hogar)
        except:
            models.InstrumentosRutaObject.objects.filter(ruta=ruta, momento=momento, hogar=hogar).update(estado='rechazado')

            for instrumento in models.InstrumentosRutaObject.objects.filter(ruta=ruta, momento=momento, hogar=hogar):
                models.InstrumentosTrazabilidadRutaObject.objects.create(
                    instrumento=instrumento,
                    user=self.request.user,
                    observacion='Rechazo del soporte'
                )

            ruta.update_novedades()
            message = 'Se han actualizado los instrumentos'
        else:
            if cupo.estado == 'Reportado':
                cupo.hogar = None
                cupo.estado = 'asignado'
                cupo.save()
                models.InstrumentosRutaObject.objects.filter(ruta=ruta, momento=momento, hogar=hogar).update(estado='rechazado')


                for instrumento in models.InstrumentosRutaObject.objects.filter(ruta = ruta,momento = momento,hogar = hogar):
                    models.InstrumentosTrazabilidadRutaObject.objects.create(
                        instrumento=instrumento,
                        user=self.request.user,
                        observacion='Rechazo del soporte'
                    )

                ruta.update_novedades()
                message = 'Reporte eliminado y actualización de instrumentos'
            else:
                message = 'No se puede rechazar el momento'

        return message

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.hogar = models.Hogares.objects.get(id=self.kwargs['pk_hogar'])


        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=request.user)
        except:
            self.permiso = None

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if request.user.is_superuser:
                    message = self.rechazar(self.ruta,self.momento,self.hogar)
                    messages.add_message(self.request, messages.INFO, message)
                    return HttpResponseRedirect('../')
                else:
                    if self.permiso == None:
                        return HttpResponseRedirect('../')
                    else:
                        ids_ver = self.permiso.rutas_aprobar.all()
                        if self.ruta in ids_ver:
                            message = self.rechazar(self.ruta,self.momento,self.hogar)
                            messages.add_message(self.request, messages.INFO, message)
                            return HttpResponseRedirect('../')
                        else:
                            return HttpResponseRedirect('../')
            else:
                return HttpResponseRedirect('../')
"""

class RutasInstrumentoHogarRechazarView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/actividades/hogares/rechazar.html'
    form_class = forms.RutasInstrumentosRechazarForm
    success_url = "../"

    def rechazar(self, ruta, momento, hogar, observacion):

        message = ''

        try:
            cupo = models.CuposRutaObject.objects.get(ruta=ruta, momento=momento, hogar=hogar)
        except:
            models.InstrumentosRutaObject.objects.filter(ruta=ruta, momento=momento, hogar=hogar).update(estado='rechazado')

            for instrumento in models.InstrumentosRutaObject.objects.filter(ruta=ruta, momento=momento, hogar=hogar):
                models.InstrumentosTrazabilidadRutaObject.objects.create(
                    instrumento=instrumento,
                    user=self.request.user,
                    observacion=observacion
                )

                models.ObservacionesInstrumentoRutaObject.objects.create(
                    usuario_creacion=self.request.user,
                    instrumento=instrumento,
                    observacion=observacion
                )

            ruta.update_novedades()
            message = 'Se han actualizado los instrumentos'
        else:
            if cupo.estado == 'Reportado':
                cupo.hogar = None
                cupo.estado = 'asignado'
                cupo.save()
                models.InstrumentosRutaObject.objects.filter(ruta=ruta, momento=momento, hogar=hogar).update(estado='rechazado')

                for instrumento in models.InstrumentosRutaObject.objects.filter(ruta=ruta, momento=momento,
                                                                                hogar=hogar):
                    models.InstrumentosTrazabilidadRutaObject.objects.create(
                        instrumento=instrumento,
                        user=self.request.user,
                        observacion=observacion
                    )

                    models.ObservacionesInstrumentoRutaObject.objects.create(
                        usuario_creacion=self.request.user,
                        instrumento=instrumento,
                        observacion=observacion
                    )

                ruta.update_novedades()
                message = 'Reporte eliminado y actualización de instrumentos'
            else:
                message = 'No se puede rechazar el momento'

        return message

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.hogar = models.Hogares.objects.get(id=self.kwargs['pk_hogar'])

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=request.user)
        except:
            self.permiso = None

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
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
                    if self.permiso == None:
                        return HttpResponseRedirect('../../')
                    else:
                        ids_ver = self.permiso.rutas_ver.all()
                        if self.ruta in ids_ver:
                            if request.method.lower() in self.http_method_names:
                                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                            else:
                                handler = self.http_method_not_allowed
                            return handler(request, *args, **kwargs)
                        else:
                            return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

    def form_valid(self, form):
        message = self.rechazar(self.ruta,self.momento,self.hogar,form.cleaned_data['observacion'])
        messages.add_message(self.request, messages.INFO, message)
        return super(RutasInstrumentoHogarRechazarView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.momento.nombre
        kwargs['breadcrum_active'] = self.hogar.documento

        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasInstrumentoHogarRechazarView, self).get_context_data(**kwargs)


"""
class RutasInstrumentosRechazarHogaresView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.modelos = modelos_instrumentos.get_modelo(self.instrumento_object.instrumento.modelo)

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=request.user)
        except:
            self.permiso = None

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):
                if request.user.is_superuser:
                    self.instrumento_object.estado = 'rechazado'
                    models.InstrumentosTrazabilidadRutaObject.objects.create(
                        instrumento=self.instrumento_object,
                        user=self.request.user,
                        observacion='Rechazo del soporte'
                    )
                    self.instrumento_object.save()
                    return HttpResponseRedirect('../../')
                else:
                    if self.permiso == None:
                        return HttpResponseRedirect('../../')
                    else:
                        ids_ver = self.permiso.rutas_preaprobar.all()
                        if self.ruta in ids_ver:
                            self.instrumento_object.estado = 'rechazado'
                            models.InstrumentosTrazabilidadRutaObject.objects.create(
                                instrumento=self.instrumento_object,
                                user=self.request.user,
                                observacion='Rechazo del soporte'
                            )
                            self.instrumento_object.save()
                            return HttpResponseRedirect('../../')
                        else:
                            return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')
"""

class RutasInstrumentosRechazarHogaresView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/actividades/hogares/instrumentos/rechazar.html'
    form_class = forms.RutasInstrumentosRechazarForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.instrumento = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=request.user)
        except:
            self.permiso = None

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
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
                    if self.permiso == None:
                        return HttpResponseRedirect('../../')
                    else:
                        ids_aprobar = self.permiso.rutas_aprobar.all()
                        if self.ruta in ids_aprobar:
                            if request.method.lower() in self.http_method_names:
                                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                            else:
                                handler = self.http_method_not_allowed
                            return handler(request, *args, **kwargs)
                        else:
                            return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

    def form_valid(self, form):

        if self.instrumento != 'rechazado':
            self.instrumento.estado = 'rechazado'
            models.InstrumentosTrazabilidadRutaObject.objects.create(
                instrumento=self.instrumento,
                user=self.request.user,
                observacion=form.cleaned_data['observacion']
            )
            models.ObservacionesInstrumentoRutaObject.objects.create(
                usuario_creacion=self.request.user,
                instrumento=self.instrumento,
                observacion=form.cleaned_data['observacion']
            )
            self.instrumento.save()

            if self.instrumento.cupo_object != None and self.instrumento.cupo_object != '':
                if self.instrumento.cupo_object.estado == 'Reportado':
                    if self.instrumento.cupo_object.corte == None or self.instrumento.cupo_object.corte == '':
                        cupo_object = self.instrumento.cupo_object
                        self.instrumento.cupo_object = None
                        self.instrumento.save()
                        cupo_object.delete()

        return super(RutasInstrumentosRechazarHogaresView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.momento.nombre
        kwargs['breadcrum_active'] = self.instrumento.instrumento.short_name

        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasInstrumentosRechazarHogaresView, self).get_context_data(**kwargs)


class RutasInstrumentosTrazabilidadHogaresView(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'
    template_name = 'fest_2019/rutas/actividades/hogares/instrumentos/trazabilidad.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])
        self.instrumento = self.instrumento_object.instrumento
        self.modelos = modelos_instrumentos.get_modelo(self.instrumento.modelo)
        self.objeto = self.modelos.get('model').objects.get(id=self.instrumento_object.soporte)

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=request.user)
        except:
            self.permiso = None

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
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
                    if self.permiso == None:
                        return HttpResponseRedirect('../../')
                    else:
                        ids_ver = self.permiso.rutas_ver.all()
                        if self.ruta in ids_ver:
                            if request.method.lower() in self.http_method_names:
                                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                            else:
                                handler = self.http_method_not_allowed
                            return handler(request, *args, **kwargs)
                        else:
                            return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.momento.nombre
        kwargs['breadcrum_active'] = self.instrumento.short_name
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/rutas/actividades/{0}/instrumentos/{1}/trazabilidad/{2}/'.format(
            kwargs['pk_ruta'],
            kwargs['pk_momento'],
            kwargs['pk_instrumento_object']
        )

        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasInstrumentosTrazabilidadHogaresView,self).get_context_data(**kwargs)


class RutasInstrumentosUpdateHogaresListView(UpdateView):
    login_url = settings.LOGIN_URL
    success_url = '../../'

    def get_object(self, queryset=None):
        self.model = self.modelos.get('model')
        return self.model.objects.get(id=self.instrumento_object.soporte)

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])
        self.instrumento = self.instrumento_object.instrumento

        try:
            self.modelos = modelos_instrumentos.get_modelo(self.instrumento.modelo)
        except:
            return HttpResponseRedirect('../../')

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver"
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')) and self.instrumento_object.estado in ['cargado', 'rechazado']:

                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_template_names(self):
        return self.modelos.get('template')

    def get_form_class(self):
        self.model = self.modelos.get('model')
        return self.modelos.get('form')

    def update_objeto_instrumento(self, id, modelo, creacion):

        instrumento = models.InstrumentosRutaObject.objects.get(id=id)

        if creacion:
            models.InstrumentosRutaObject.objects.filter(id=id).update(
                usuario_creacion=self.request.user
            )

            models.InstrumentosTrazabilidadRutaObject.objects.create(
                instrumento=instrumento,
                user=self.request.user,
                observacion='Creación del soporte'
            )

        else:
            models.InstrumentosTrazabilidadRutaObject.objects.create(
                instrumento=instrumento,
                user=self.request.user,
                observacion='Actualización del soporte'
            )

        models.InstrumentosRutaObject.objects.filter(id=id).update(
            modelo=self.instrumento.nombre,
            soporte=modelo.id,
            fecha_actualizacion=timezone.now(),
            usuario_actualizacion=self.request.user,
            consecutivo=self.instrumento.consecutivo,
            nombre=self.instrumento.short_name,
            estado='cargado'
        )

        self.ruta.update_novedades()

        return 'Ok'

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.ruta = self.ruta
        self.object.instrumento = self.instrumento
        self.object.nombre = self.instrumento.short_name
        self.object.save()

        self.object.hogares.clear()
        if self.instrumento.nivel == 'individual':
            self.object.hogares.add(form.cleaned_data['hogares'])

        elif self.instrumento.nivel == 'ruta':
            pass

        else:
            self.object.hogares.add(*form.cleaned_data['hogares'])

        objeto = self.instrumento_object

        ids = self.object.hogares.all().values_list('id', flat=True)
        objeto.hogares.clear()
        objeto.hogares.add(*ids)

        models.ObservacionesInstrumentoRutaObject.objects.create(instrumento=objeto, usuario_creacion=self.request.user,
                                                                 observacion="Actualización del instrumento")

        self.update_objeto_instrumento(objeto.id, self.object, False)
        objeto.clean_similares()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.momento.nombre
        kwargs['breadcrum_active'] = self.instrumento.short_name
        kwargs['ruta_breadcrum'] = 'Rutas'
        kwargs['url_ruta_breadcrum'] = '/fest_2019/rutas/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasInstrumentosUpdateHogaresListView, self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk_ruta': self.ruta.id, 'short_name': self.instrumento.short_name,
                'pk_instrumento': self.instrumento.pk, 'pk_instrumento_object': self.instrumento_object.pk}




#----------------------------------------------------------------------------------

#----------------------------------- CUENTAS DE COBRO -------------------------------------


class RutasCuentasCobroListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.rutas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/cuentas_cobro/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_active'] = models.Rutas.objects.get(id = kwargs['pk_ruta']).nombre
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/rutas/cuentas_cobro/{0}/'.format(kwargs['pk_ruta'])
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasCuentasCobroListView,self).get_context_data(**kwargs)



class RutasCuentasCobroDetalleListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.rutas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/cuentas_cobro/detalle/lista.html'


    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id=kwargs['pk_ruta'])
        cuenta_cobro = models.CuentasCobro.objects.get(id=kwargs['pk_cuenta_cobro'])
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = ruta.nombre
        kwargs['breadcrum_active'] = cuenta_cobro.corte.consecutivo
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/rutas/cuentas_cobro/{0}/detalle/{1}/'.format(ruta.id,cuenta_cobro.id)
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasCuentasCobroDetalleListView,self).get_context_data(**kwargs)


class RutasCuentasCobroDetalleActividadesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.rutas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/cuentas_cobro/detalle/hogares/lista.html'


    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id=kwargs['pk_ruta'])
        cuenta_cobro = models.CuentasCobro.objects.get(id=kwargs['pk_cuenta_cobro'])
        momento = models.Momentos.objects.get(id=kwargs['pk_momento'])
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = cuenta_cobro.corte.consecutivo
        kwargs['breadcrum_active'] = momento.nombre
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/rutas/cuentas_cobro/{0}/detalle/{1}/hogares/{2}/'.format(
            ruta.id,
            cuenta_cobro.id,
            momento.id
        )
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasCuentasCobroDetalleActividadesListView,self).get_context_data(**kwargs)


class RutasCuentasCobroInstrumentosHogaresListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.rutas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/cuentas_cobro/detalle/hogares/instrumentos/lista.html'


    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id=kwargs['pk_ruta'])
        cuenta_cobro = models.CuentasCobro.objects.get(id=kwargs['pk_cuenta_cobro'])
        momento = models.Momentos.objects.get(id=kwargs['pk_momento'])
        hogar = models.Hogares.objects.get(id=kwargs['pk_hogar'])
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = cuenta_cobro.corte.consecutivo
        kwargs['breadcrum_2'] = momento.nombre
        kwargs['breadcrum_active'] = hogar.documento
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/rutas/cuentas_cobro/{0}/detalle/{1}/hogares/{2}/instrumentos/{3}/'.format(
            ruta.id,
            cuenta_cobro.id,
            momento.id,
            hogar.id
        )
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasCuentasCobroInstrumentosHogaresListView,self).get_context_data(**kwargs)


class RutasCuentasCobroInstrumentosVerHogaresView(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.hogar = models.Hogares.objects.get(id=self.kwargs['pk_hogar'])
        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])

        self.instrumento = self.instrumento_object.instrumento
        self.modelos = modelos_instrumentos.get_modelo(self.instrumento.modelo)
        self.objeto = self.modelos.get('model').objects.get(id=self.instrumento_object.soporte)

        try:
            self.permiso = models.PermisosCuentasRutas.objects.get(user=request.user)
        except:
            self.permiso = None

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
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
                    if self.permiso == None:
                        return HttpResponseRedirect('../../')
                    else:
                        ids_ver = self.permiso.rutas_ver.all()
                        if self.ruta in ids_ver:
                            if request.method.lower() in self.http_method_names:
                                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                            else:
                                handler = self.http_method_not_allowed
                            return handler(request, *args, **kwargs)
                        else:
                            return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

    def get_template_names(self):
        return self.modelos.get('template_ver')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = 'Actividades: Corte {0}'.format(self.cuenta_cobro.corte)
        kwargs['breadcrum_2'] = self.momento.nombre
        kwargs['breadcrum_3'] = 'Hogar: {0}'.format(self.hogar.documento)
        kwargs['breadcrum_active'] = self.instrumento.short_name
        kwargs['objeto'] = self.objeto
        kwargs['ruta_breadcrum'] = 'Rutas'
        kwargs['url_ruta_breadcrum'] = '/fest_2019/rutas/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasCuentasCobroInstrumentosVerHogaresView,self).get_context_data(**kwargs)


class RutasCuentasCobroInstrumentosTrazabilidadHogaresView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.rutas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/cuentas_cobro/detalle/hogares/instrumentos/trazabilidad.html'


    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id=kwargs['pk_ruta'])
        cuenta_cobro = models.CuentasCobro.objects.get(id=kwargs['pk_cuenta_cobro'])
        momento = models.Momentos.objects.get(id=kwargs['pk_momento'])
        hogar = models.Hogares.objects.get(id=kwargs['pk_hogar'])
        instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = cuenta_cobro.corte.consecutivo
        kwargs['breadcrum_2'] = momento.nombre
        kwargs['breadcrum_3'] = hogar.documento
        kwargs['breadcrum_active'] = instrumento_object.instrumento.nombre
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/rutas/cuentas_cobro/{0}/detalle/{1}/hogares/{2}/instrumentos/{3}/trazabilidad/{4}'.format(
            ruta.id,
            cuenta_cobro.id,
            momento.id,
            hogar.id,
            instrumento_object.id
        )
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasCuentasCobroInstrumentosTrazabilidadHogaresView,self).get_context_data(**kwargs)

#----------------------------------- MIS RUTAS -------------------------------------


class MisRutasOptionsView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misrutas/lista.html'

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver"
            ]
        }
        return permissions

    def get_context_data(self, **kwargs):
        kwargs['title'] = "MIS RUTAS"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/misrutas/'
        return super(MisRutasOptionsView,self).get_context_data(**kwargs)


class MisRutasHogaresListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misrutas/hogares/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.hogares.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')) and request.user == self.ruta.contrato.contratista.usuario_asociado:
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')


    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id = kwargs['pk_ruta'])
        kwargs['title'] = "Mis rutas"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/misrutas/hogares/{0}/'.format(kwargs['pk_ruta'])
        kwargs['breadcrum_active'] = ruta.nombre
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasHogaresListView,self).get_context_data(**kwargs)



class RutaCrearMisHogaresView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misrutas/hogares/crear.html'
    form_class = forms.HogarCreateForm
    success_url = "../"
    models = models.Hogares

    def get_permission_required(self, request=None):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.hogares.ver",
            ]
        }
        return permissions

    def form_valid(self, form):
        documento = form.cleaned_data['documento']
        if models.Hogares.objects.filter(documento = documento).count() == 0:
            self.object = form.save()
            self.object.rutas.add(self.ruta)
        else:
            hogar = models.Hogares.objects.get(documento = documento)
            hogar.rutas.add(self.ruta)
        message = 'Se creó el hogar: {0}'.format(form.cleaned_data['documento'])
        messages.add_message(self.request, messages.INFO, message)
        self.ruta.update_hogares_inscritos()
        return HttpResponseRedirect("../")

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVO HOGAR"
        kwargs['breadcrum_active'] = self.ruta.nombre
        return super(RutaCrearMisHogaresView,self).get_context_data(**kwargs)



class MisRutasHogaresMiembrosListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misrutas/hogares/miembros/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.hogares.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')) and request.user == self.ruta.contrato.contratista.usuario_asociado:
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')


    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id = kwargs['pk_ruta'])
        hogar = models.Hogares.objects.get(id=kwargs['pk_hogar'])
        kwargs['title'] = "Mis rutas"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/misrutas/hogares/{0}/ver_miembros/{1}/'.format(kwargs['pk_ruta'],kwargs['pk_hogar'])
        kwargs['breadcrum_1'] = ruta.nombre
        kwargs['breadcrum_active'] = hogar.documento
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasHogaresMiembrosListView,self).get_context_data(**kwargs)


class RutasHogaresMiembrosListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/hogares/miembros/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.rutas.ver",
                "usuarios.fest_2019.rutas.hogares.ver",
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
        ruta = models.Rutas.objects.get(id = kwargs['pk_ruta'])
        hogar = models.Hogares.objects.get(id=kwargs['pk_hogar'])
        kwargs['title'] = "Rutas"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/rutas/hogares/{0}/ver_miembros/{1}/'.format(kwargs['pk_ruta'],kwargs['pk_hogar'])
        kwargs['breadcrum_1'] = ruta.nombre
        kwargs['breadcrum_active'] = hogar.documento
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasHogaresMiembrosListView,self).get_context_data(**kwargs)



class MisRutasHogaresVerView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misrutas/hogares/ver.html'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.hogar = models.Hogares.objects.get(id=self.kwargs['pk_hogar'])

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.hogares.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')) and request.user == self.ruta.contrato.contratista.usuario_asociado:
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')


    def get_context_data(self, **kwargs):
        kwargs['hogar'] = self.hogar
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.hogar.documento
        return super(MisRutasHogaresVerView,self).get_context_data(**kwargs)


class MisRutasActividadesListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misrutas/actividades/lista.html'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.actividades.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')) and request.user == self.ruta.contrato.contratista.usuario_asociado:
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Actividades"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/misrutas/actividades/{0}/'.format(kwargs['pk_ruta'])
        kwargs['breadcrum_active'] = self.ruta.nombre
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasActividadesListView,self).get_context_data(**kwargs)


class MisRutasActividadesHogaresListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misrutas/actividades/hogares/lista.html'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.actividades.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')) and request.user == self.ruta.contrato.contratista.usuario_asociado:
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/misrutas/actividades/{0}/hogares/{1}/'.format(kwargs['pk_ruta'],kwargs['pk_momento'])
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.momento.nombre
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasActividadesHogaresListView,self).get_context_data(**kwargs)


class MisRutasInstrumentosHogaresListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misrutas/actividades/instrumentos/lista.html'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.actividades.ver",
            ],
            "crear_instrumentos": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.actividades.ver",
                "usuarios.fest_2019.misrutas.actividades.crear",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')) and request.user == self.ruta.contrato.contratista.usuario_asociado:
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/misrutas/actividades/{0}/instrumentos/{1}/'.format(
            kwargs['pk_ruta'],
            kwargs['pk_momento']
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.momento.nombre
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions['crear_instrumentos'])
        kwargs['instrumentos'] = self.ruta.get_instrumentos_list(self.momento)
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasInstrumentosHogaresListView,self).get_context_data(**kwargs)




class MisRutasInstrumentosHogaresObservacionesListView(TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misrutas/actividades/instrumentos/observaciones/lista.html'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])
        self.instrumento = self.instrumento_object.instrumento

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.actividades.ver",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')) and request.user == self.ruta.contrato.contratista.usuario_asociado:
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/misrutas/actividades/{0}/instrumentos/{1}/observaciones/{2}/'.format(
            kwargs['pk_ruta'],
            kwargs['pk_momento'],
            kwargs['pk_instrumento_object']
        )
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.momento.nombre
        kwargs['breadcrum_active'] = self.instrumento.nombre
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasInstrumentosHogaresObservacionesListView,self).get_context_data(**kwargs)




class MisRutasInstrumentosFormHogaresListView(CreateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.instrumento = models.Instrumentos.objects.get(id=self.kwargs['pk_instrumento'])

        try:
            self.modelos = modelos_instrumentos.get_modelo(self.instrumento.modelo)
        except:
            return HttpResponseRedirect('../../')

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.actividades.ver",
                "usuarios.fest_2019.misrutas.actividades.crear",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')) and request.user == self.ruta.contrato.contratista.usuario_asociado:

                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')


    def get_template_names(self):
        return self.modelos.get('template')


    def get_form_class(self):
        self.model = self.modelos.get('model')
        return self.modelos.get('form')


    def update_objeto_instrumento(self,id,modelo,creacion):

        instrumento = models.InstrumentosRutaObject.objects.get(id = id)

        if creacion:
            models.InstrumentosRutaObject.objects.filter(id = id).update(
                usuario_creacion=self.request.user
            )

            models.InstrumentosTrazabilidadRutaObject.objects.create(
                instrumento = instrumento,
                user = self.request.user,
                observacion = 'Creación del soporte'
            )

        else:
            models.InstrumentosTrazabilidadRutaObject.objects.create(
                instrumento=instrumento,
                user=self.request.user,
                observacion='Actualización del soporte'
            )

        models.InstrumentosRutaObject.objects.filter(id=id).update(
            modelo = self.instrumento.nombre,
            soporte = modelo.id,
            fecha_actualizacion = timezone.now(),
            usuario_actualizacion = self.request.user,
            consecutivo = self.instrumento.consecutivo,
            nombre = self.instrumento.short_name,
            estado = 'cargado'
        )

        self.ruta.update_novedades()

        return 'Ok'



    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.ruta = self.ruta
        self.object.instrumento = self.instrumento
        self.object.nombre = self.instrumento.short_name
        self.object.save()

        self.object.hogares.clear()

        if self.instrumento.nivel == 'individual':
            self.object.hogares.add(form.cleaned_data['hogares'])

        elif self.instrumento.nivel == 'ruta':
            pass

        else:
            self.object.hogares.add(*form.cleaned_data['hogares'])


        objeto = models.InstrumentosRutaObject.objects.create(ruta=self.ruta, momento=self.momento, instrumento=self.instrumento)
        ids = self.object.hogares.all().values_list('id',flat = True)
        objeto.hogares.add(*ids)
        models.ObservacionesInstrumentoRutaObject.objects.create(instrumento = objeto,usuario_creacion = self.request.user,observacion = "Creación del instrumento")

        self.update_objeto_instrumento(objeto.id, self.object, True)
        objeto.clean_similares()


        return HttpResponseRedirect(self.get_success_url())


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.momento.nombre
        kwargs['breadcrum_active'] = self.instrumento.short_name
        kwargs['ruta_breadcrum'] = 'Mis rutas'
        kwargs['url_ruta_breadcrum'] = '/fest_2019/misrutas/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasInstrumentosFormHogaresListView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk_ruta': self.ruta.id, 'short_name': self.instrumento.short_name, 'pk_instrumento': self.instrumento.pk}


class MisRutasInstrumentosUpdateHogaresListView(UpdateView):
    login_url = settings.LOGIN_URL
    success_url = '../../'
    
    
    
    
    def get_object(self, queryset=None):
        self.model = self.modelos.get('model')
        return self.model.objects.get(id = self.instrumento_object.soporte)
    

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])
        self.instrumento = self.instrumento_object.instrumento

        try:
            self.modelos = modelos_instrumentos.get_modelo(self.instrumento.modelo)
        except:
            return HttpResponseRedirect('../../')

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.actividades.ver",
                "usuarios.fest_2019.misrutas.actividades.crear",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(
                    self.permissions.get('all')) and request.user == self.ruta.contrato.contratista.usuario_asociado:

                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')

    def get_template_names(self):
        return self.modelos.get('template')

    def get_form_class(self):
        self.model = self.modelos.get('model')
        return self.modelos.get('form')

    def update_objeto_instrumento(self, id, modelo, creacion):

        instrumento = models.InstrumentosRutaObject.objects.get(id=id)

        if creacion:
            models.InstrumentosRutaObject.objects.filter(id=id).update(
                usuario_creacion=self.request.user
            )

            models.InstrumentosTrazabilidadRutaObject.objects.create(
                instrumento=instrumento,
                user=self.request.user,
                observacion='Creación del soporte'
            )

        else:
            models.InstrumentosTrazabilidadRutaObject.objects.create(
                instrumento=instrumento,
                user=self.request.user,
                observacion='Actualización del soporte'
            )

        models.InstrumentosRutaObject.objects.filter(id=id).update(
            modelo=self.instrumento.nombre,
            soporte=modelo.id,
            fecha_actualizacion=timezone.now(),
            usuario_actualizacion=self.request.user,
            consecutivo=self.instrumento.consecutivo,
            nombre=self.instrumento.short_name,
            estado='cargado'
        )

        self.ruta.update_novedades()

        return 'Ok'

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.ruta = self.ruta
        self.object.instrumento = self.instrumento
        self.object.nombre = self.instrumento.short_name
        self.object.save()

        self.object.hogares.clear()
        if self.instrumento.nivel == 'individual':
            self.object.hogares.add(form.cleaned_data['hogares'])

        elif self.instrumento.nivel == 'ruta':
            pass

        else:
            self.object.hogares.add(*form.cleaned_data['hogares'])

        objeto = self.instrumento_object

        ids = self.object.hogares.all().values_list('id', flat=True)
        objeto.hogares.clear()
        objeto.hogares.add(*ids)

        models.ObservacionesInstrumentoRutaObject.objects.create(instrumento=objeto, usuario_creacion=self.request.user,observacion="Actualización del instrumento")

        self.update_objeto_instrumento(objeto.id, self.object, False)
        objeto.clean_similares()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.momento.nombre
        kwargs['breadcrum_active'] = self.instrumento.short_name
        kwargs['ruta_breadcrum'] = 'Mis rutas'
        kwargs['url_ruta_breadcrum'] = '/fest_2019/misrutas/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasInstrumentosUpdateHogaresListView, self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk_ruta': self.ruta.id, 'short_name': self.instrumento.short_name, 'pk_instrumento': self.instrumento.pk, 'pk_instrumento_object': self.instrumento_object.pk}





class MisRutasInstrumentosVerHogaresView(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])
        self.instrumento = self.instrumento_object.instrumento
        self.modelos = modelos_instrumentos.get_modelo(self.instrumento.modelo)
        self.objeto = self.modelos.get('model').objects.get(id = self.instrumento_object.soporte)

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.actividades.ver"
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')) and request.user == self.ruta.contrato.contratista.usuario_asociado:
                if request.method.lower() in self.http_method_names:
                    handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                else:
                    handler = self.http_method_not_allowed
                return handler(request, *args, **kwargs)
            else:
                return HttpResponseRedirect('../../')


    def get_template_names(self):
        return self.modelos.get('template_ver')



    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_2'] = self.momento.nombre
        kwargs['breadcrum_active'] = self.instrumento.short_name
        kwargs['objeto'] = self.objeto
        kwargs['ruta_breadcrum'] = 'Mis rutas'
        kwargs['url_ruta_breadcrum'] = '/iraca/misrutas/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasInstrumentosVerHogaresView,self).get_context_data(**kwargs)


class MisRutasInstrumentosHogaresDeleteView(View):

    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):

        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.modelos = modelos_instrumentos.get_modelo(self.instrumento_object.instrumento.modelo)

        self.permissions = {
            "eliminar": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
                "usuarios.fest_2019.misrutas.actividades.ver",
                "usuarios.fest_2019.misrutas.actividades.eliminar",
            ]
        }

        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions['eliminar']):
                if self.instrumento_object.estado == 'cargado':
                    self.modelos.get('model').objects.get(id = self.instrumento_object.soporte).delete()
                    models.InstrumentosTrazabilidadRutaObject.objects.filter(instrumento = self.instrumento_object).delete()
                    models.ObservacionesInstrumentoRutaObject.objects.filter(instrumento = self.instrumento_object).delete()
                    self.instrumento_object.delete()
                    self.ruta.update_novedades()
                    return HttpResponseRedirect('../../')
                else:
                    return HttpResponseRedirect('../../')
            else:
                return HttpResponseRedirect('../../')

#----------------------------------------------------------------------------------

#----------------------------------- PERMISOS -------------------------------------


class PermisosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/permisos/lista.html'
    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.permisos.ver"
        ],
        "crear": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.permisos.ver",
            "usuarios.fest_2019.permisos.crear"
        ]
    }


    def get_context_data(self, **kwargs):
        kwargs['title'] = "PERMISOS"
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions['crear'])
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/permisos/'
        return super(PermisosListView,self).get_context_data(**kwargs)


class PermisosCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/permisos/crear.html'
    form_class = forms.PermisosCreateForm
    model = models.PermisosCuentasRutas
    success_url = "../"

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.permisos.ver",
                "usuarios.fest_2019.permisos.crear"
            ]
        }
        return permissions



    def get_context_data(self, **kwargs):
        kwargs['title'] = "PERMISOS"
        kwargs['url_usuarios'] = '/rest/v1.0/fest_2019/permisos/autocomplete/usuarios/'
        kwargs['url_rutas'] = '/rest/v1.0/fest_2019/permisos/autocomplete/rutas/'
        return super(PermisosCreateView,self).get_context_data(**kwargs)


class PermisosUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/permisos/editar.html'
    form_class = forms.PermisosCreateForm
    model = models.PermisosCuentasRutas
    success_url = "../../"

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.permisos.ver",
                "usuarios.fest_2019.permisos.editar"
            ]
        }
        return permissions



    def get_context_data(self, **kwargs):
        kwargs['title'] = "PERMISOS"
        kwargs['url_usuarios'] = '/rest/v1.0/fest_2019/permisos/autocomplete/usuarios/'
        kwargs['url_rutas'] = '/rest/v1.0/fest_2019/permisos/autocomplete/rutas/'
        return super(PermisosUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk':self.kwargs['pk']}

#----------------------------- PERMISOS PROYECTOS ---------------------------------

class PermisosProyectosListView(LoginRequiredMixin,
                                MultiplePermissionsRequiredMixin,
                                TemplateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/permisos_proyectos/lista.html'
    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.permisos.ver"
        ],
        "crear": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.permisos.ver",
            "usuarios.fest_2019.permisos.crear"
        ]
    }


    def get_context_data(self, **kwargs):
        kwargs['title'] = "PERMISOS PROYECTOS"
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions['crear'])
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/permisos_proyectos/'
        return super(PermisosProyectosListView,self).get_context_data(**kwargs)

class PermisosProyectosCreateView(LoginRequiredMixin,
                                  MultiplePermissionsRequiredMixin,
                                  CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/permisos_proyectos/crear.html'
    form_class = forms.PermisosDepartamentosCreateForm
    model = models.PermisosCuentasDepartamentos
    success_url = "../"

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.permisos.ver",
                "usuarios.fest_2019.permisos.crear"
            ]
        }
        return permissions



    def get_context_data(self, **kwargs):
        kwargs['title'] = "PERMISOS PROYECTOS"
        return super(PermisosProyectosCreateView,self).get_context_data(**kwargs)

class PermisosProyectosUpdateView(LoginRequiredMixin,
                                  MultiplePermissionsRequiredMixin,
                                  UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/permisos_proyectos/editar.html'
    form_class = forms.PermisosDepartamentosUpdateForm
    model = models.PermisosCuentasDepartamentos
    success_url = "../../"

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.permisos.ver",
                "usuarios.fest_2019.permisos.editar"
            ]
        }
        return permissions



    def get_context_data(self, **kwargs):
        kwargs['title'] = "PERMISOS PROYECTOS"
        return super(PermisosProyectosUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk':self.kwargs['pk']}

#----------------------------------- SOPORTES -------------------------------------

class SoportesHogaresListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.soportes.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/soportes/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "SOPORTES"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/soportes/'
        return super(SoportesHogaresListView,self).get_context_data(**kwargs)


class SoportesHogaresComponenteListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.soportes.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/soportes/componentes/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "SOPORTES"
        kwargs['breadcrum_active'] = models.Hogares.objects.get(id = kwargs['pk_hogar']).documento
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/soportes/{0}/'.format(kwargs['pk_hogar'])
        return super(SoportesHogaresComponenteListView,self).get_context_data(**kwargs)


class SoportesHogaresMomentosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.soportes.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/soportes/componentes/momentos/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "SOPORTES"
        kwargs['breadcrum_1'] = models.Hogares.objects.get(id=kwargs['pk_hogar']).documento
        kwargs['breadcrum_active'] = models.Componentes.objects.get(id = kwargs['pk_componente']).nombre
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/soportes/{0}/componente/{1}/'.format(
            kwargs['pk_hogar'],
            kwargs['pk_componente']
        )
        return super(SoportesHogaresMomentosListView,self).get_context_data(**kwargs)


class SoportesHogaresInstrumentosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.soportes.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/soportes/componentes/momentos/instrumentos/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "SOPORTES"
        kwargs['breadcrum_1'] = models.Hogares.objects.get(id=kwargs['pk_hogar']).documento
        kwargs['breadcrum_2'] = models.Componentes.objects.get(id = kwargs['pk_componente']).nombre
        kwargs['breadcrum_active'] = models.Momentos.objects.get(id = kwargs['pk_momento']).nombre
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/soportes/{0}/componente/{1}/instrumento/{2}/'.format(
            kwargs['pk_hogar'],
            kwargs['pk_componente'],
            kwargs['pk_momento']
        )
        return super(SoportesHogaresInstrumentosListView,self).get_context_data(**kwargs)



class SoportesHogaresInstrumentosVerView(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'


    def dispatch(self, request, *args, **kwargs):

        self.hogar = models.Hogares.objects.get(id=self.kwargs['pk_hogar'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])

        self.modelos = modelos_instrumentos.get_modelo(self.instrumento_object.instrumento.modelo)
        self.objeto = self.modelos.get('model').objects.get(id=self.instrumento_object.soporte)


        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.soportes.ver",
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
        return self.modelos.get('template_ver')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = self.hogar.documento
        kwargs['breadcrum_2'] = self.componente.nombre
        kwargs['breadcrum_3'] = self.momento.nombre
        kwargs['breadcrum_active'] = self.instrumento_object.instrumento.short_name
        kwargs['objeto'] = self.objeto
        kwargs['ruta_breadcrum'] = 'Soportes'
        kwargs['url_ruta_breadcrum'] = '/fest_2019/soportes/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(SoportesHogaresInstrumentosVerView,self).get_context_data(**kwargs)


#----------------------------------- CORTES -------------------------------------

class CortesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.cortes.ver"
        ],
        "crear": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.cortes.ver",
            "usuarios.fest_2019.cortes.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/cortes/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "CORTES"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/cortes/'
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions['crear'])
        return super(CortesListView,self).get_context_data(**kwargs)


class CortesCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/cortes/crear.html'
    form_class = forms.CortesCreateForm
    success_url = "../"

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.cortes.ver",
                "usuarios.fest_2019.cortes.crear"
            ]
        }
        return permissions

    def form_valid(self, form):

        corte = models.Cortes.objects.create(
            consecutivo = models.Cortes.objects.all().count() + 1,
            usuario_creacion = self.request.user,
            descripcion = form.cleaned_data['descripcion']
        )

        rutas_ids = models.CuposRutaObject.objects.exclude(momento__tipo = 'vinculacion').filter(estado = "Reportado").values_list('ruta__id', flat=True).distinct()

        for ruta_id in rutas_ids:
            ruta = models.Rutas.objects.get(id = ruta_id)

            if 'ruta_{0}'.format(ruta.id) in form.cleaned_data.keys():
                if form.cleaned_data['ruta_{0}'.format(ruta.id)]:
                    models.CuposRutaObject.objects.exclude(momento__tipo = 'vinculacion').filter(estado="Reportado",ruta__id = ruta_id).update(
                        estado = "Pagado",
                        corte = corte
                    )

        corte.create_cuentas_cobro(self.request.user)

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVO CORTE DE PAGO"
        return super(CortesCreateView,self).get_context_data(**kwargs)


class CortesCuentasCobroView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.cortes.ver",
            "usuarios.fest_2019.cuentas_cobro.ver"
        ],
        "crear_cuenta_cobro": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.cortes.ver",
            "usuarios.fest_2019.cuentas_cobro.ver",
            "usuarios.fest_2019.cuentas_cobro.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/cortes/cuentas_cobro/lista.html'


    def get_context_data(self, **kwargs):
        corte = models.Cortes.objects.get(id=self.kwargs['pk_corte'])
        kwargs['title'] = "CORTES"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/cortes/ver/{0}/'.format(corte.id)
        kwargs['breadcrum_active'] = corte.consecutivo
        kwargs['permiso_crear'] = self.request.user.has_perms(self.permissions.get('crear_cuenta_cobro'))
        return super(CortesCuentasCobroView,self).get_context_data(**kwargs)


class CuentaCobroUpdateView(FormView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/cortes/cuentas_cobro/actualizar.html'
    form_class = forms.CuentaCobroForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        self.corte = models.Cortes.objects.get(id=self.kwargs['pk_corte'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "cargar_cuentas_cobro": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.cortes.ver",
                "usuarios.fest_2019.cortes.cuentas_cobro.ver",
                "usuarios.fest_2019.cortes.cuentas_cobro.editar"
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

        corte = models.Cortes.objects.get(id=self.kwargs['pk_corte'])
        cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        kwargs['title'] = "CUENTA DE COBRO RUTA {0}".format(cuenta_cobro.ruta.nombre)
        kwargs['breadcrum_1'] = corte.consecutivo
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
            'pk_corte': self.kwargs['pk_corte'],
            'pk_cuenta_cobro': self.kwargs['pk_cuenta_cobro']
        }


class CuentaCobroFirmaUploadView(UpdateView):

    login_url = settings.LOGIN_URL
    model = models.CuentasCobro
    template_name = 'fest_2019/cortes/cuentas_cobro/cargar.html'
    form_class = forms.CuentaCobroCargarForm
    success_url = "../../"
    pk_url_kwarg = 'pk_cuenta_cobro'

    def dispatch(self, request, *args, **kwargs):

        self.corte = models.Cortes.objects.get(id=self.kwargs['pk_corte'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "cargar_cuentas_cobro": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.cortes.ver",
                "usuarios.fest_2019.cortes.cuentas_cobro.ver",
                "usuarios.fest_2019.cortes.cuentas_cobro.cargar"
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
        kwargs['breadcrum_1'] = self.corte.consecutivo
        kwargs['breadcrum_active'] = self.cuenta_cobro.ruta.nombre
        kwargs['file_url'] = self.cuenta_cobro.pretty_print_url_file2()
        return super(CuentaCobroFirmaUploadView,self).get_context_data(**kwargs)


class CuentaCobroEstadoFormView(UpdateView):

    login_url = settings.LOGIN_URL
    model = models.CuentasCobro
    template_name = 'fest_2019/cortes/cuentas_cobro/estado.html'
    form_class = forms.CuentaCobroEstadoForm
    success_url = "../../"
    pk_url_kwarg = 'pk_cuenta_cobro'

    def dispatch(self, request, *args, **kwargs):

        self.corte = models.Cortes.objects.get(id=self.kwargs['pk_corte'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "estado_cuentas_cobro": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.cortes.ver",
                "usuarios.fest_2019.cortes.cuentas_cobro.ver",
                "usuarios.fest_2019.cortes.cuentas_cobro.estado"
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
        kwargs['breadcrum_1'] = self.corte.consecutivo
        kwargs['breadcrum_active'] = self.cuenta_cobro.ruta.nombre
        return super(CuentaCobroEstadoFormView,self).get_context_data(**kwargs)



#----------------------------------- MIS CUENTAS DE COBRO ------------------------------------

class MisRutasCuentasCobroListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.misrutas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misrutas/cuentas_cobro/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Mis rutas"
        kwargs['breadcrum_active'] = models.Rutas.objects.get(id = kwargs['pk_ruta']).nombre
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/misrutas/cuentas_cobro/{0}/'.format(kwargs['pk_ruta'])
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasCuentasCobroListView,self).get_context_data(**kwargs)


class MisRutasCuentasCobroDetalleListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.misrutas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misrutas/cuentas_cobro/detalle/lista.html'


    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id=kwargs['pk_ruta'])
        cuenta_cobro = models.CuentasCobro.objects.get(id=kwargs['pk_cuenta_cobro'])
        kwargs['title'] = "Mis rutas"
        kwargs['breadcrum_1'] = ruta.nombre
        kwargs['breadcrum_active'] = cuenta_cobro.corte.consecutivo
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/misrutas/cuentas_cobro/{0}/detalle/{1}/'.format(ruta.id,cuenta_cobro.id)
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasCuentasCobroDetalleListView,self).get_context_data(**kwargs)


class MisRutasCuentasCobroDetalleActividadesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.misrutas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misrutas/cuentas_cobro/detalle/hogares/lista.html'


    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id=kwargs['pk_ruta'])
        cuenta_cobro = models.CuentasCobro.objects.get(id=kwargs['pk_cuenta_cobro'])
        momento = models.Momentos.objects.get(id=kwargs['pk_momento'])
        kwargs['title'] = "Mis rutas"
        kwargs['breadcrum_1'] = cuenta_cobro.corte.consecutivo
        kwargs['breadcrum_active'] = momento.nombre
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/misrutas/cuentas_cobro/{0}/detalle/{1}/hogares/{2}/'.format(
            ruta.id,
            cuenta_cobro.id,
            momento.id
        )
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasCuentasCobroDetalleActividadesListView,self).get_context_data(**kwargs)


class MisRutasCuentasCobroInstrumentosHogaresListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.misrutas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misrutas/cuentas_cobro/detalle/hogares/instrumentos/lista.html'


    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id=kwargs['pk_ruta'])
        cuenta_cobro = models.CuentasCobro.objects.get(id=kwargs['pk_cuenta_cobro'])
        momento = models.Momentos.objects.get(id=kwargs['pk_momento'])
        hogar = models.Hogares.objects.get(id=kwargs['pk_hogar'])
        kwargs['title'] = "Mis rutas"
        kwargs['breadcrum_1'] = cuenta_cobro.corte.consecutivo
        kwargs['breadcrum_2'] = momento.nombre
        kwargs['breadcrum_active'] = hogar.documento
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/misrutas/cuentas_cobro/{0}/detalle/{1}/hogares/{2}/instrumentos/{3}/'.format(
            ruta.id,
            cuenta_cobro.id,
            momento.id,
            hogar.id
        )
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasCuentasCobroInstrumentosHogaresListView,self).get_context_data(**kwargs)


class MisRutasCuentasCobroInstrumentosVerHogaresView(TemplateView):

    login_url = settings.LOGIN_URL
    success_url = '../../'


    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.momento = models.Momentos.objects.get(id=self.kwargs['pk_momento'])
        self.hogar = models.Hogares.objects.get(id=self.kwargs['pk_hogar'])
        self.instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])

        self.instrumento = self.instrumento_object.instrumento
        self.modelos = modelos_instrumentos.get_modelo(self.instrumento.modelo)
        self.objeto = self.modelos.get('model').objects.get(id=self.instrumento_object.soporte)


        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver",
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
        return self.modelos.get('template_ver')

    def get_context_data(self, **kwargs):
        kwargs['title'] = "Mis rutas"
        kwargs['breadcrum_1'] = 'Actividades: Corte {0}'.format(self.cuenta_cobro.corte)
        kwargs['breadcrum_2'] = self.momento.nombre
        kwargs['breadcrum_3'] = 'Hogar: {0}'.format(self.hogar.documento)
        kwargs['breadcrum_active'] = self.instrumento.short_name
        kwargs['objeto'] = self.objeto
        kwargs['ruta_breadcrum'] = 'Mis rutas'
        kwargs['url_ruta_breadcrum'] = '/fest_2019/misrutas/'
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasCuentasCobroInstrumentosVerHogaresView,self).get_context_data(**kwargs)


class MisRutasCuentasCobroInstrumentosTrazabilidadHogaresView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.misrutas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misrutas/cuentas_cobro/detalle/hogares/instrumentos/trazabilidad.html'


    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id=kwargs['pk_ruta'])
        cuenta_cobro = models.CuentasCobro.objects.get(id=kwargs['pk_cuenta_cobro'])
        momento = models.Momentos.objects.get(id=kwargs['pk_momento'])
        hogar = models.Hogares.objects.get(id=kwargs['pk_hogar'])
        instrumento_object = models.InstrumentosRutaObject.objects.get(id=self.kwargs['pk_instrumento_object'])
        kwargs['title'] = "Mis rutas"
        kwargs['breadcrum_1'] = cuenta_cobro.corte.consecutivo
        kwargs['breadcrum_2'] = momento.nombre
        kwargs['breadcrum_3'] = hogar.documento
        kwargs['breadcrum_active'] = instrumento_object.instrumento.nombre
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/misrutas/cuentas_cobro/{0}/detalle/{1}/hogares/{2}/instrumentos/{3}/trazabilidad/{4}'.format(
            ruta.id,
            cuenta_cobro.id,
            momento.id,
            hogar.id,
            instrumento_object.id
        )
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasCuentasCobroInstrumentosTrazabilidadHogaresView,self).get_context_data(**kwargs)


class MisRutasCuentasCobroUploadView(UpdateView):

    login_url = settings.LOGIN_URL
    model = models.CuentasCobro
    template_name = 'fest_2019/misrutas/cuentas_cobro/cargar.html'
    form_class = forms.CuentaCobroCargarForm
    success_url = "../../"
    pk_url_kwarg = 'pk_cuenta_cobro'

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "cargar_cuentas_cobro": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver"
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


class MisRutasHogaresAgregarMiembroListView(FormView):

    login_url = settings.LOGIN_URL
    model = models.CuentasCobro
    template_name = 'fest_2019/misrutas/hogares/miembros.html'
    form_class = forms.CaracterizacionInicialForm
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.hogar = models.Hogares.objects.get(id=self.kwargs['pk_hogar'])

        self.permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.misrutas.ver"
            ]
        }


        if not request.user.is_authenticated:
            return HttpResponseRedirect(self.login_url)
        else:
            if request.user.has_perms(self.permissions.get('all')):

                if str(self.ruta.componente.consecutivo) == '1':
                    if self.hogar.ruta_1 == self.ruta:
                        if request.method.lower() in self.http_method_names:
                            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                        else:
                            handler = self.http_method_not_allowed
                        return handler(request, *args, **kwargs)
                    else:
                        return HttpResponseRedirect('../../')
                elif str(self.ruta.componente.consecutivo) == '2':
                    if self.hogar.ruta_2 == self.ruta:
                        if request.method.lower() in self.http_method_names:
                            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                        else:
                            handler = self.http_method_not_allowed
                        return handler(request, *args, **kwargs)
                    else:
                        return HttpResponseRedirect('../../')
                elif str(self.ruta.componente.consecutivo) == '3':
                    if self.hogar.ruta_3 == self.ruta:
                        if request.method.lower() in self.http_method_names:
                            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                        else:
                            handler = self.http_method_not_allowed
                        return handler(request, *args, **kwargs)
                    else:
                        return HttpResponseRedirect('../../')
                elif str(self.ruta.componente.consecutivo) == '4':
                    if self.hogar.ruta_4 == self.ruta:
                        if request.method.lower() in self.http_method_names:
                            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
                        else:
                            handler = self.http_method_not_allowed
                        return handler(request, *args, **kwargs)
                    else:
                        return HttpResponseRedirect('../../')
                else:
                    return HttpResponseRedirect('../../')


            else:
                return HttpResponseRedirect('../../')


    def form_valid(self, form):

        modelo, creacion_modelo = models.MiembroNucleoHogar.objects.get_or_create(hogar=self.hogar,numero_documento=form.cleaned_data['numero_documento'])


        try:
            municipio_nacimiento = Municipios.objects.get(id = form.cleaned_data['municipio_nacimiento'])
        except:
            municipio_nacimiento = None


        try:
            municipio_expedicion = Municipios.objects.get(id=form.cleaned_data['municipio_expedicion'])
        except:
            municipio_expedicion = None


        modelo.tipo_documento = form.cleaned_data['tipo_documento']
        modelo.numero_documento = form.cleaned_data['numero_documento']
        modelo.primer_apellido = form.cleaned_data['primer_apellido']
        modelo.segundo_apellido = form.cleaned_data['segundo_apellido']
        modelo.primer_nombre = form.cleaned_data['primer_nombre']
        modelo.segundo_nombre =form.cleaned_data['segundo_nombre']
        modelo.celular_1 = form.cleaned_data['celular_1']
        modelo.celular_2 = form.cleaned_data['celular_2']
        modelo.correo_electronico = form.cleaned_data['correo_electronico']
        modelo.departamento_nacimiento = form.cleaned_data['departamento_nacimiento']
        modelo.municipio_nacimiento = municipio_nacimiento
        modelo.fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
        modelo.departamento_expedicion = form.cleaned_data['departamento_expedicion']
        modelo.municipio_expedicion = municipio_expedicion
        modelo.fecha_expedicion = form.cleaned_data['fecha_expedicion']
        modelo.longitud = form.cleaned_data['longitud']
        modelo.latitud = form.cleaned_data['latitud']
        modelo.precision = form.cleaned_data['precision']
        modelo.altitud = form.cleaned_data['altitud']
        modelo.sexo = form.cleaned_data['sexo']
        modelo.tiene_libreta = form.cleaned_data['tiene_libreta']
        modelo.numero_libreta = form.cleaned_data['numero_libreta']
        modelo.identidad_genero = form.cleaned_data['identidad_genero']
        modelo.condicion_sexual = form.cleaned_data['condicion_sexual']
        modelo.estado_civil = form.cleaned_data['estado_civil']
        modelo.etnia = form.cleaned_data['etnia']
        modelo.pueblo_indigena = form.cleaned_data['pueblo_indigena']
        modelo.resguardo_indigena = form.cleaned_data['resguardo_indigena']
        modelo.comunidad_indigena = form.cleaned_data['comunidad_indigena']
        modelo.lengua_nativa_indigena = form.cleaned_data['lengua_nativa_indigena']
        modelo.cual_lengua_indigena = form.cleaned_data['cual_lengua_indigena']
        modelo.consejo_afro = form.cleaned_data['consejo_afro']
        modelo.comunidad_afro = form.cleaned_data['comunidad_afro']
        modelo.lengua_nativa_afro = form.cleaned_data['lengua_nativa_afro']
        modelo.cual_lengua_afro = form.cleaned_data['cual_lengua_afro']
        modelo.discapacidad = form.cleaned_data['discapacidad']
        modelo.registro_discapacidad = form.cleaned_data['registro_discapacidad']
        modelo.categoria_discapacidad.set(form.cleaned_data['categoria_discapacidad'])
        modelo.dificultades_permanentes.set(form.cleaned_data['dificultades_permanentes'])
        modelo.utiliza_actualmente.set(form.cleaned_data['utiliza_actualmente'])
        modelo.rehabilitacion.set(form.cleaned_data['rehabilitacion'])
        modelo.tiene_cuidador = form.cleaned_data['tiene_cuidador']
        modelo.cuidador = form.cleaned_data['cuidador']
        modelo.parentezco = form.cleaned_data['parentezco']
        modelo.es_jefe = form.cleaned_data['es_jefe']
        modelo.nivel_escolaridad = form.cleaned_data['nivel_escolaridad']
        modelo.grado_titulo = form.cleaned_data['grado_titulo']
        modelo.sabe_leer = form.cleaned_data['sabe_leer']
        modelo.sabe_sumar_restar = form.cleaned_data['sabe_sumar_restar']
        modelo.actualmente_estudia = form.cleaned_data['actualmente_estudia']
        modelo.recibe_alimentos = form.cleaned_data['recibe_alimentos']
        modelo.razon_no_estudia = form.cleaned_data['razon_no_estudia']
        modelo.razon_no_estudia_otra = form.cleaned_data['razon_no_estudia_otra']
        modelo.regimen_seguridad_social = form.cleaned_data['regimen_seguridad_social']
        modelo.save()

        return super(MisRutasHogaresAgregarMiembroListView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTAS"
        kwargs['breadcrum_1'] = self.ruta.nombre
        kwargs['breadcrum_active'] = self.hogar.documento
        return super(MisRutasHogaresAgregarMiembroListView,self).get_context_data(**kwargs)


class MisRutasHogaresMiembrosVerView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.misrutas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/misrutas/hogares/miembros/ver.html'


    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id=kwargs['pk_ruta'])
        hogar = models.Hogares.objects.get(id=kwargs['pk_hogar'])
        miembro = models.MiembroNucleoHogar.objects.get(id=self.kwargs['pk_miembro'])
        kwargs['title'] = "Mis rutas"
        kwargs['breadcrum_1'] = ruta.nombre
        kwargs['breadcrum_2'] = hogar.documento
        kwargs['breadcrum_active'] = miembro.numero_documento
        kwargs['objeto'] = miembro
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(MisRutasHogaresMiembrosVerView,self).get_context_data(**kwargs)


class RutasHogaresMiembrosVerView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.rutas.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/rutas/hogares/miembros/ver.html'


    def get_context_data(self, **kwargs):
        ruta = models.Rutas.objects.get(id=kwargs['pk_ruta'])
        hogar = models.Hogares.objects.get(id=kwargs['pk_hogar'])
        miembro = models.MiembroNucleoHogar.objects.get(id=self.kwargs['pk_miembro'])
        kwargs['title'] = "Rutas"
        kwargs['breadcrum_1'] = ruta.nombre
        kwargs['breadcrum_2'] = hogar.documento
        kwargs['breadcrum_active'] = miembro.numero_documento
        kwargs['objeto'] = miembro
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(RutasHogaresMiembrosVerView,self).get_context_data(**kwargs)


#-------------------------------------- RUTEO ----------------------------------------

class RuteoHogaresListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.ruteo.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/ruteo/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTEO DE HOGARES"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/ruteo/'
        return super(RuteoHogaresListView,self).get_context_data(**kwargs)


class RuteoHogaresComponentesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.ruteo.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/ruteo/componentes/lista.html'


    def dispatch(self, request, *args, **kwargs):
        self.hogar = models.Hogares.objects.get(id = kwargs['pk'])
        return super(RuteoHogaresComponentesListView, self).dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTEO DE HOGARES"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/ruteo/{0}/componentes/'.format(self.hogar.id)
        kwargs['breadcrum_active'] = self.hogar.documento
        return super(RuteoHogaresComponentesListView,self).get_context_data(**kwargs)


class RuteoHogaresComponentesCambiarView(LoginRequiredMixin,
                                         MultiplePermissionsRequiredMixin,
                                         FormView):
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/ruteo/componentes/actualizar.html'
    form_class = forms.CambioRutaComponenteForm
    success_url = "../../../"
    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.ruteo.ver"
        ]
    }

    def dispatch(self, request, *args, **kwargs):
        self.hogar = models.Hogares.objects.get(id = kwargs['pk'])
        self.componente = models.Componentes.objects.get(id = kwargs['pk_componente'])


        if self.componente.consecutivo == 1:
            if self.hogar.ruta_1 != None:
                self.ruta = self.hogar.ruta_1.id
            else:
                self.ruta = ''

        elif self.componente.consecutivo == 2:
            if self.hogar.ruta_2 != None:
                self.ruta = self.hogar.ruta_2.id
            else:
                self.ruta = ''

        elif self.componente.consecutivo == 3:
            if self.hogar.ruta_3 != None:
                self.ruta = self.hogar.ruta_3.id
            else:
                self.ruta = ''

        elif self.componente.consecutivo == 4:
            if self.hogar.ruta_4 != None:
                self.ruta = self.hogar.ruta_4.id
            else:
                self.ruta = ''

        else:
            self.ruta = ''

        return super(RuteoHogaresComponentesCambiarView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        if form.cleaned_data['ruta'] == None:
            if self.componente.consecutivo == 1:

                ruta = self.hogar.ruta_1

                self.hogar.ruta_1 = None
                self.hogar.save()

            elif self.componente.consecutivo == 2:

                ruta = self.hogar.ruta_2

                self.hogar.ruta_2 = None
                self.hogar.save()


            elif self.componente.consecutivo == 3:

                ruta = self.hogar.ruta_3

                self.hogar.ruta_3 = None
                self.hogar.save()


            elif self.componente.consecutivo == 4:

                ruta = self.hogar.ruta_4

                self.hogar.ruta_4 = None
                self.hogar.save()

            else:
                ruta = None

            if ruta != None:
                ruta.update_hogares_inscritos()
                if models.CuposRutaObject.objects.filter(hogar = self.hogar,translado = False,momento__componente = self.componente).count() > 0:
                    models.CuposRutaObject.objects.filter(hogar = self.hogar,translado = False,momento__componente = self.componente).update(translado = True)
                    ruta.actualizar_objetos()

        else:
            ruta = form.cleaned_data['ruta']
            update = ruta.translado(self.hogar,self.componente)
            ruta.update_hogares_inscritos()
            if update:
                ruta.actualizar_objetos()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTEO DE HOGARES"
        kwargs['breadcrum_1'] = self.hogar.documento
        kwargs['breadcrum_active'] = self.componente.nombre

        if self.ruta == '':
            kwargs['url_rutas'] = '/rest/v1.0/fest_2019/ruteo/autocomplete/rutas/{0}/'.format(self.componente.id)
        else:
            kwargs['url_rutas'] = '/rest/v1.0/fest_2019/ruteo/autocomplete/rutas/{0}/{1}/'.format(self.componente.id,self.ruta)
        return super(RuteoHogaresComponentesCambiarView, self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk': self.kwargs['pk'],
            'pk_componente': self.kwargs['pk_componente']
        }




class RuteoHogaresComponentesVinculacionView(LoginRequiredMixin,
                                         MultiplePermissionsRequiredMixin,
                                         FormView):
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/ruteo/actualizar.html'
    form_class = forms.CambioRutaVinculacionForm
    success_url = "../../../"
    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.ruteo.ver"
        ]
    }

    def dispatch(self, request, *args, **kwargs):
        self.hogar = models.Hogares.objects.get(id = kwargs['pk'])


        if self.hogar.ruta_vinculacion != None:
            self.ruta = self.hogar.ruta_vinculacion.id
        else:
            self.ruta = ''

        return super(RuteoHogaresComponentesVinculacionView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        if form.cleaned_data['ruta'] == None:

            ruta = self.hogar.ruta_vinculacion

            self.hogar.ruta_vinculacion = None
            self.hogar.save()


            if ruta != None:
                ruta.update_hogares_inscritos()
                if models.CuposRutaObject.objects.filter(hogar = self.hogar,momento__tipo='vinculacion').count() > 0:
                    models.CuposRutaObject.objects.filter(hogar = self.hogar,momento__tipo='vinculacion').update(translado = True)
                    ruta.actualizar_objetos()

        else:
            ruta = form.cleaned_data['ruta']
            update = ruta.translado_vinculacion(self.hogar)
            ruta.update_hogares_inscritos()
            if update:
                ruta.actualizar_objetos()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTEO DE HOGARES"
        kwargs['breadcrum_active'] = self.hogar.documento

        if self.ruta == '':
            kwargs['url_rutas'] = '/rest/v1.0/fest_2019/ruteo/autocomplete/vinculacion/rutas/'
        else:
            kwargs['url_rutas'] = '/rest/v1.0/fest_2019/ruteo/autocomplete/vinculacion/rutas/{0}'.format(self.ruta)
        return super(RuteoHogaresComponentesVinculacionView, self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk': self.kwargs['pk']
        }





class RuteoHogaresMomentosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.ruteo.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/ruteo/componentes/momentos/lista.html'


    def dispatch(self, request, *args, **kwargs):
        self.hogar = models.Hogares.objects.get(id = kwargs['pk'])
        self.componente = models.Componentes.objects.get(id=kwargs['pk_componente'])
        return super(RuteoHogaresMomentosListView, self).dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        kwargs['title'] = "RUTEO DE HOGARES"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/ruteo/{0}/componentes/{1}/momentos/'.format(self.hogar.id,self.componente.id)
        kwargs['breadcrum_1'] = self.hogar.documento
        kwargs['breadcrum_active'] = self.componente.nombre
        return super(RuteoHogaresMomentosListView,self).get_context_data(**kwargs)



class RuteoHogaresReporteListadoView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.ruteo.ver"
        ]
    }
    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Reporte de ruteo FEST 2019',
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_ruteo.delay(reporte.id)

        return HttpResponseRedirect('/reportes/')




#----------------------------------------------------------------------------------

#-------------------------------------- BD ----------------------------------------

class DirectorioListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.directorio.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/directorio/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "DIRECTORIO DE CONTACTOS"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/directorio/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.fest_2019.directorio.crear')
        return super(DirectorioListView,self).get_context_data(**kwargs)




class DirectorioCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/directorio/crear.html'
    form_class = forms.ContactoCreateForm
    success_url = "../"
    models = models.Contactos

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.directorio.ver",
                "usuarios.fest_2019.directorio.crear"
            ]
        }
        return permissions

    def form_valid(self, form):
        self.object = form.save()
        message = 'Se creó el contacto: {0}'.format(form.cleaned_data['nombres'])
        messages.add_message(self.request, messages.INFO, message)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVO CONTACTO"
        return super(DirectorioCreateView,self).get_context_data(**kwargs)


class DirectorioUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'fest_2019/directorio/editar.html'
    form_class = forms.ContactoCreateForm
    success_url = "../../"
    model = models.Contactos

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.fest_2019.ver",
                "usuarios.fest_2019.directorio.ver",
                "usuarios.fest_2019.directorio.editar"
            ]
        }
        return permissions

    def form_valid(self, form):
        self.object = form.save()
        message = 'Se edito el contacto: {0}'.format(self.object.nombres)
        messages.add_message(self.request, messages.INFO, message)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "EDITAR CONTACTO"
        return super(DirectorioUpdateView,self).get_context_data(**kwargs)


    def get_initial(self):
        return {'pk':self.kwargs['pk']}