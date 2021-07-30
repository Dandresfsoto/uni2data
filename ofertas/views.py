import mimetypes

from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from django.shortcuts import redirect
from ofertas import forms
from ofertas import models
from ofertas import tasks
from django.http import HttpResponseRedirect
# Create your views here.
from usuarios.models import Titulos, Experiencias
from reportes.models import Reportes
from django.contrib import messages
from django.contrib.messages import get_messages

#------------------------------- SELECCIÓN ----------------------------------------

class OfertasListView(LoginRequiredMixin,
                          MultiplePermissionsRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'ofertas/lista.html'
    permissions = {
        "all": ["usuarios.ofertas.seleccion.ver"]
    }

    def get_context_data(self, **kwargs):
        kwargs['title'] = "OFERTAS"
        kwargs['url_datatable'] = '/rest/v1.0/ofertas/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.ofertas.crear')
        return super(OfertasListView,self).get_context_data(**kwargs)

class OfertaAplicacionesListView(LoginRequiredMixin,
                          MultiplePermissionsRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'ofertas/lista_aplicaciones.html'
    permissions = {
        "all": ["usuarios.ofertas.seleccion.ver"]
    }

    def get_context_data(self, **kwargs):
        oferta = models.Ofertas.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "OFERTAS"
        kwargs['url_datatable'] = '/rest/v1.0/ofertas/ver/{0}/'.format(str(oferta.id))
        kwargs['url_resumen_aplicacion'] = '/rest/v1.0/ofertas/resumen/{0}/'.format(str(oferta.id))
        kwargs['breadcrum_active'] = oferta.cargo
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.ofertas.seleccion.ver')
        return super(OfertaAplicacionesListView,self).get_context_data(**kwargs)

class OfertasCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.ofertas.seleccion.ver",
            "usuarios.ofertas.seleccion.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'ofertas/crear.html'
    form_class = forms.OfertasForm
    success_url = "../"
    model = models.Ofertas

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.honorarios = float(form.cleaned_data['honorarios'].replace('$ ','').replace(',',''))
        self.object.save()
        return super(OfertasCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CREAR OFERTA"
        return super(OfertasCreateView,self).get_context_data(**kwargs)

class OfertasUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.ofertas.seleccion.ver",
            "usuarios.ofertas.seleccion.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'ofertas/crear.html'
    form_class = forms.OfertasForm
    success_url = "../../"
    model = models.Ofertas

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.honorarios = float(form.cleaned_data['honorarios'].replace('$ ','').replace(',',''))
        self.object.save()
        return super(OfertasUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZAR OFERTA"
        return super(OfertasUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk':self.kwargs['pk']}

class OfertasPublicListView(LoginRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'ofertas/aplicar.html'

    def get_context_data(self, **kwargs):
        kwargs['title'] = "APLICAR A OFERTAS"
        kwargs['ofertas'] = models.Ofertas.objects.filter(estado=True).order_by('-creation')
        storage = get_messages(self.request)
        for message in storage:
            kwargs['success'] = message
        return super(OfertasPublicListView,self).get_context_data(**kwargs)

class OfertasAplicarCreateView(LoginRequiredMixin,
                          FormView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'ofertas/aplicar_oferta.html'
    form_class = forms.CreateAplicacion
    success_url = '../'

    def dispatch(self, request, *args, **kwargs):

        usuario = request.user

        if usuario.formulario_completo_ofertas:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/perfil/')

    def form_valid(self, form):
        oferta = models.Ofertas.objects.get(id = self.kwargs['pk'])
        aplicacion, created = models.AplicacionOferta.objects.get_or_create(oferta = oferta,usuario = self.request.user)


        aplicacion.municipios.add(*form.cleaned_data['municipios'])
        aplicacion.observacion = form.cleaned_data['observacion']
        aplicacion.save()

        message = 'Aplicaste a la oferta {0}'.format(oferta.cargo)

        messages.add_message(self.request, messages.INFO, message)

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        oferta = models.Ofertas.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "APLICAR A OFERTA"
        kwargs['breadcrum_active'] = oferta.cargo
        kwargs['oferta'] = oferta
        return super(OfertasAplicarCreateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk':self.kwargs['pk'],'usuario_id':self.request.user.id}

class CualificarOfertaView(LoginRequiredMixin,
                           MultiplePermissionsRequiredMixin,
                           UpdateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'ofertas/cualificacion_oferta.html'
    form_class = forms.CualificacionAplicacion
    success_url = '../../'
    pk_url_kwarg = 'pk_aplicacion'
    model = models.AplicacionOferta
    permissions = {
        "all": [
            "usuarios.ofertas.seleccion.ver",
            "usuarios.ofertas.seleccion.editar"
        ]
    }


    def get_aplicacion_data(self, aplicacion):

        response = {
            'usuario': {},
            'titulos': [],
            'experiencias': [],
            'aplicacion': {}
        }

        usuario = aplicacion.usuario

        response['usuario'] = {
            'photo': usuario.url_photo(),
            'fullname': usuario.get_full_name_string().upper(),
            'cedula': usuario.cedula,
            'edad': usuario.calculate_age(),
            'sexo': usuario.sexo.lower(),
            'lugar_nacimiento': str(usuario.lugar_nacimiento),
            'lugar_expedicion': str(usuario.lugar_expedicion),
            'lugar_residencia': str(usuario.lugar_residencia),

            'email': usuario.email,
            'direccion': usuario.direccion,
            'celular': str(usuario.celular),
            'tipo_sangre': usuario.tipo_sangre,
            'birthday': str(usuario.birthday),

            'nivel_educacion_basica': usuario.nivel_educacion_basica,
            'grado_educacion_basica': usuario.grado_educacion_basica,
            'hv': usuario.url_hv()
        }

        response['aplicacion'] = {
            'id': str(aplicacion.id),
            'creation': aplicacion.pretty_creation_datetime(),
            'municipios': aplicacion.get_municipios_string(),
            'observacion': aplicacion.observacion
        }

        for titulo in Titulos.objects.filter(usuario = usuario).order_by('-creation'):
            response['titulos'].append({
                'modalidad': titulo.modalidad,
                'semestres': titulo.semestres,
                'graduado': titulo.graduado,
                'nombre': titulo.nombre,
                'fecha_terminacion': titulo.fecha_terminacion,
                'numero_tarjeta': titulo.numero_tarjeta,
                'fecha_expedicion': titulo.fecha_expedicion,
            })


        for experiencia in Experiencias.objects.filter(usuario = usuario).order_by('-creation'):
            response['experiencias'].append({
                'nombre_empresa': experiencia.nombre_empresa,
                'tipo_empresa': experiencia.tipo_empresa,
                'email_empresa': experiencia.email_empresa,
                'telefono_empresa': experiencia.telefono_empresa,
                'cargo': experiencia.cargo,
                'dependencia': experiencia.dependencia,
                'direccion': experiencia.direccion,
                'meses': experiencia.get_duracion_meses(),
                'fecha_ingreso': experiencia.fecha_ingreso,
                'fecha_retiro': experiencia.fecha_retiro,
                'municipio': str(experiencia.municipio)
            })

        return response

    def get_context_data(self, **kwargs):
        aplicacion = models.AplicacionOferta.objects.get(id = self.kwargs['pk_aplicacion'])
        oferta = models.Ofertas.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "CUALIFICAR APLICACIÓN"
        kwargs['breadcrum_active'] = oferta.cargo
        kwargs['oferta'] = oferta
        kwargs['aplicacion'] = aplicacion
        kwargs['usuario'] = self.get_aplicacion_data(aplicacion)
        return super(CualificarOfertaView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {
            'pk':self.kwargs['pk'],
            'pk_aplicacion': self.kwargs['pk_aplicacion']
        }

class ReporteOfertaAplicacionesListView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.ofertas.seleccion.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):
        oferta = models.Ofertas.objects.get(id = self.kwargs['pk'])
        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Estado de aplicaciones a la oferta: {0}'.format(oferta.cargo),
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_estado_aplicacion_oferta.delay(reporte.id, oferta.id)

        return HttpResponseRedirect('/reportes/')

#----------------------------------------------------------------------------------