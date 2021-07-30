import mimetypes

from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from django.shortcuts import redirect
from formacion import forms
from formacion import models
from formacion import tasks
from django.http import HttpResponseRedirect
from acceso import functions
from django.views.generic.edit import ModelFormMixin
# Create your views here.

#------------------------------- SELECCIÓN ----------------------------------------

class FormacionOptionsView(LoginRequiredMixin,
                          MultiplePermissionsRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/lista.html'
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formacion.ver"
        ]
    }

    def dispatch(self, request, *args, **kwargs):
        items = self.get_items()
        if len(items) == 0:
            return redirect(self.login_url)
        return super(FormacionOptionsView, self).dispatch(request, *args, **kwargs)

    def get_items(self):
        items = []

        if self.request.user.has_perm('usuarios.cpe_2018.formacion.bd.ver'):
            items.append({
                'sican_categoria': 'Base de datos',
                'sican_color': 'pink darken-4',
                'sican_order': 1,
                'sican_url': 'bd/',
                'sican_name': 'Base de datos',
                'sican_icon': 'data_usage',
                'sican_description': 'Sedes educativas en colombia e información de docentes formados '
                                     'en vigencias anteriores'
            })


        if self.request.user.has_perm('usuarios.cpe_2018.formacion.diplomados.ver'):
            items.append({
                'sican_categoria': 'Diplomados',
                'sican_color': 'green darken-4',
                'sican_order': 2,
                'sican_url': 'diplomados/',
                'sican_name': 'Diplomados',
                'sican_icon': 'computer',
                'sican_description': 'Estructura general de los diplomados y de los entregables'
            })

        return items


    def get_context_data(self, **kwargs):
        kwargs['title'] = "FORMACIÓN"
        kwargs['items'] = self.get_items()
        return super(FormacionOptionsView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------
#----------------------------------- REGIONES -------------------------------------

class RegionesSedesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formacion.ver",
            "usuarios.cpe_2018.formacion.bd.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/bd/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "BASE DE DATOS FORMACIÓN"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formacion/bd/'
        kwargs['permiso_actualizar'] = 'usuarios.cpe_2018.formacion.bd.actualizar'
        return super(RegionesSedesListView,self).get_context_data(**kwargs)


class ActualizacionDbListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formacion.ver",
            "usuarios.cpe_2018.formacion.bd.actualizar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/bd/actualizar/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZACIÓN DE SEDES"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formacion/db/sedes/actualizar/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.formacion.db.crear')
        kwargs['link_formato'] = '/static/documentos/actualizacion_sedes.xlsx'
        return super(ActualizacionDbListView,self).get_context_data(**kwargs)


class ActualizacionDbDocentesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formacion.ver",
            "usuarios.cpe_2018.formacion.bd.actualizar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/bd/actualizar_docentes/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZACIÓN DE DOCENTES FORMADOS"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formacion/db/actualizar_docentes/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.formacion.db.crear')
        kwargs['link_formato'] = '/static/documentos/actualizacion_docentes.xlsx'
        return super(ActualizacionDbDocentesListView,self).get_context_data(**kwargs)


class CreateActualizacionDbView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formacion.ver",
            "usuarios.cpe_2018.formacion.bd.actualizar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/bd/actualizar/crear.html'
    form_class = forms.ActualizacionSedesForm
    success_url = "../"

    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZACIÓN DE SEDES"
        return super(CreateActualizacionDbView,self).get_context_data(**kwargs)


    def form_valid(self, form):
        actualizacion = models.ActualizacionSedes.objects.create(
                            usuario_creacion = self.request.user,
                            file = form.cleaned_data['file']
                        )
        tasks.build_resultado_actualizacion_sedes.delay(actualizacion.id)
        return super(CreateActualizacionDbView,self).form_valid(form)


class CreateActualizacionDbDocentesView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formacion.ver",
            "usuarios.cpe_2018.formacion.bd.actualizar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/bd/actualizar_docentes/crear.html'
    form_class = forms.ActualizacionDocentesForm
    success_url = "../"

    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZACIÓN DE DOCENTES FORMADOS"
        return super(CreateActualizacionDbDocentesView,self).get_context_data(**kwargs)


    def form_valid(self, form):
        actualizacion = models.ActualizacionDocentes.objects.create(
                            usuario_creacion = self.request.user,
                            file = form.cleaned_data['file']
                        )
        tasks.build_resultado_actualizacion_docentes(actualizacion.id)
        return super(CreateActualizacionDbDocentesView,self).form_valid(form)


#----------------------------------------------------------------------------------
#--------------------------------- DEPARTAMENTOS ----------------------------------

class DepartamentosSedesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formacion.ver",
            "usuarios.cpe_2018.formacion.bd.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/bd/departamentos/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "departamentos"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formacion/bd/{0}/departamentos/'.format(self.kwargs['pk'])
        kwargs['breadcrum_active'] = models.Regiones.objects.get(id=self.kwargs['pk']).nombre
        return super(DepartamentosSedesListView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------
#----------------------------------- MUNICIPIOS -----------------------------------

class MunicipiosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formacion.ver",
            "usuarios.cpe_2018.formacion.bd.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/bd/departamentos/municipios/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Municipios"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formacion/bd/{0}/departamentos/{1}/municipios/'.format(self.kwargs['pk'],self.kwargs['pk_departamento'])
        kwargs['breadcrum_active'] = models.Regiones.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active_1'] = models.Departamentos.objects.get(id=self.kwargs['pk_departamento']).nombre
        return super(MunicipiosListView,self).get_context_data(**kwargs)


#----------------------------------------------------------------------------------

#-------------------------------------- SEDES -------------------------------------

class SedesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formacion.ver",
            "usuarios.cpe_2018.formacion.bd.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/bd/departamentos/municipios/sedes/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "Sedes"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formacion/bd/{0}/departamentos/{1}/municipios/{2}/sedes/'.format(
            self.kwargs['pk'],
            self.kwargs['pk_departamento'],
            self.kwargs['pk_municipio']
        )
        kwargs['breadcrum_active'] = models.Regiones.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active_1'] = models.Departamentos.objects.get(id=self.kwargs['pk_departamento']).nombre
        kwargs['breadcrum_active_2'] = models.Municipios.objects.get(id=self.kwargs['pk_municipio']).nombre
        kwargs['permiso_crear'] = self.request.user.has_perm("usuarios.cpe_2018.formacion.bd.crear")
        return super(SedesListView,self).get_context_data(**kwargs)


class SedesCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formacion.ver",
            "usuarios.cpe_2018.formacion.bd.ver",
            "usuarios.cpe_2018.formacion.bd.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/bd/departamentos/municipios/sedes/crear.html'
    form_class = forms.SedesForm
    success_url = "../"
    model = models.Sedes

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.municipio = models.Municipios.objects.get(id=self.kwargs['pk_municipio'])
        self.object.save()
        return super(SedesCreateView,self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "AÑADIR SEDE"
        kwargs['breadcrum_active'] = models.Regiones.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active_1'] = models.Departamentos.objects.get(id=self.kwargs['pk_departamento']).nombre
        kwargs['breadcrum_active_2'] = models.Municipios.objects.get(id=self.kwargs['pk_municipio']).nombre
        return super(SedesCreateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk_municipio':self.kwargs['pk_municipio'],'create':True}


class SedesUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formacion.ver",
            "usuarios.cpe_2018.formacion.bd.ver",
            "usuarios.cpe_2018.formacion.bd.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/bd/departamentos/municipios/sedes/editar.html'
    form_class = forms.SedesForm
    success_url = "../../"
    model = models.Sedes
    pk_url_kwarg = 'pk_sede'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZAR SEDE"
        kwargs['breadcrum_active'] = models.Regiones.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active_1'] = models.Departamentos.objects.get(id=self.kwargs['pk_departamento']).nombre
        kwargs['breadcrum_active_2'] = models.Municipios.objects.get(id=self.kwargs['pk_municipio']).nombre
        kwargs['breadcrum_active_3'] = models.Sedes.objects.get(id=self.kwargs['pk_sede']).nombre_sede
        return super(SedesUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk_municipio':self.kwargs['pk_municipio'],'create':False}

#----------------------------------------------------------------------------------
#------------------------------------- FORMADOS -----------------------------------

class FormadosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formacion.ver",
            "usuarios.cpe_2018.formacion.bd.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/bd/departamentos/municipios/sedes/docentes_formados/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "DOCENTES FORMADOS"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formacion/bd/{0}/departamentos/{1}/municipios/{2}/sedes/{3}/formados/'.format(
            self.kwargs['pk'],
            self.kwargs['pk_departamento'],
            self.kwargs['pk_municipio'],
            self.kwargs['pk_sede']
        )
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.cpe_2018.formacion.bd.crear')
        kwargs['breadcrum_active'] = models.Regiones.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active_1'] = models.Departamentos.objects.get(id=self.kwargs['pk_departamento']).nombre
        kwargs['breadcrum_active_2'] = models.Municipios.objects.get(id=self.kwargs['pk_municipio']).nombre
        kwargs['breadcrum_active_3'] = models.Sedes.objects.get(id=self.kwargs['pk_sede']).nombre_sede
        return super(FormadosListView,self).get_context_data(**kwargs)


class FormadosCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formacion.ver",
            "usuarios.cpe_2018.formacion.bd.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/bd/departamentos/municipios/sedes/docentes_formados/crear.html'
    form_class = forms.DocentesFormadosForm
    success_url = "../"
    model = models.DocentesFormados

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.sede = models.Sedes.objects.get(id=self.kwargs['pk_sede'])
        self.object.save()
        return super(FormadosCreateView,self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CREAR DOCENTE FORMADO"
        kwargs['breadcrum_active'] = models.Regiones.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active_1'] = models.Departamentos.objects.get(id=self.kwargs['pk_departamento']).nombre
        kwargs['breadcrum_active_2'] = models.Municipios.objects.get(id=self.kwargs['pk_municipio']).nombre
        kwargs['breadcrum_active_3'] = models.Sedes.objects.get(id=self.kwargs['pk_sede']).nombre_sede
        return super(FormadosCreateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk_sede':self.kwargs['pk_sede'],'create':True}


class FormadosUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    permissions = {
        "all": [
            "usuarios.cpe_2018.ver",
            "usuarios.cpe_2018.formacion.ver",
            "usuarios.cpe_2018.formacion.bd.actualizar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/bd/departamentos/municipios/sedes/docentes_formados/editar.html'
    form_class = forms.DocentesFormadosForm
    success_url = "../../"
    model = models.DocentesFormados
    pk_url_kwarg = 'pk_docente'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZAR SEDE"
        kwargs['breadcrum_active'] = models.Regiones.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active_1'] = models.Departamentos.objects.get(id=self.kwargs['pk_departamento']).nombre
        kwargs['breadcrum_active_2'] = models.Municipios.objects.get(id=self.kwargs['pk_municipio']).nombre
        kwargs['breadcrum_active_3'] = models.Sedes.objects.get(id=self.kwargs['pk_sede']).nombre_sede
        kwargs['breadcrum_active_4'] = models.DocentesFormados.objects.get(id=self.kwargs['pk_docente']).nombres
        return super(FormadosUpdateView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------
#------------------------------------- DIPLOMADOS -----------------------------------

class DiplomadosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.formacion.diplomados.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/diplomados/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "DIPLOMADOS"
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formacion/diplomados/'
        return super(DiplomadosListView,self).get_context_data(**kwargs)

class NivelesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.formacion.diplomados.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/diplomados/niveles/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "NIVELES"
        kwargs['breadcrum_active'] = models.Diplomados.objects.get(id=self.kwargs['pk']).nombre
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formacion/diplomados/{0}/niveles/'.format(self.kwargs['pk'])
        return super(NivelesListView,self).get_context_data(**kwargs)

class SesionesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.formacion.diplomados.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/diplomados/niveles/sesiones/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "SESIONES"
        kwargs['breadcrum_active'] = models.Diplomados.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active_1'] = models.Niveles.objects.get(id=self.kwargs['pk_nivel']).nombre
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formacion/diplomados/{0}/niveles/{1}/sesiones/'.format(
            self.kwargs['pk'],
            self.kwargs['pk_nivel']
        )
        return super(SesionesListView,self).get_context_data(**kwargs)

class ActividadesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.cpe_2018.formacion.diplomados.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'cpe_2018/formacion/diplomados/niveles/sesiones/actividades/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTIVIDADES"
        kwargs['breadcrum_active'] = models.Diplomados.objects.get(id=self.kwargs['pk']).nombre
        kwargs['breadcrum_active_1'] = models.Niveles.objects.get(id=self.kwargs['pk_nivel']).nombre
        kwargs['breadcrum_active_2'] = models.Sesiones.objects.get(id=self.kwargs['pk_sesion']).nombre
        kwargs['url_datatable'] = '/rest/v1.0/cpe_2018/formacion/diplomados/{0}/niveles/{1}/sesiones/{2}/actividades/'.format(
            self.kwargs['pk'],
            self.kwargs['pk_nivel'],
            self.kwargs['pk_sesion']
        )
        return super(ActividadesListView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------