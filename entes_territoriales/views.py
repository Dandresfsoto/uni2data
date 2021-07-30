import mimetypes

from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from django.shortcuts import redirect
from entes_territoriales import forms
from entes_territoriales import models
from entes_territoriales import tasks
from django.http import HttpResponseRedirect
from usuarios.models import Municipios
from django.views.generic.edit import ModelFormMixin
# Create your views here.
from delta import html
import json
from entes_territoriales import functions
from reportes.models import Reportes

#------------------------------- SELECCIÓN ----------------------------------------

class EntesTerritorialesOptionsView(LoginRequiredMixin,
                          MultiplePermissionsRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'entes_territoriales/lista.html'
    permissions = {
        "all": [
            "usuarios.fest_2019.entes_territoriales.ver"
        ]
    }

    def dispatch(self, request, *args, **kwargs):
        items = self.get_items()
        if len(items) == 0:
            return redirect(self.login_url)
        return super(EntesTerritorialesOptionsView, self).dispatch(request, *args, **kwargs)

    def get_items(self):
        items = []

        if self.request.user.has_perm('usuarios.fest_2019.entes_territoriales.reuniones.ver'):
            items.append({
                'sican_categoria': 'Reuniones',
                'sican_color': 'orange darken-4',
                'sican_order': 1,
                'sican_url': 'reuniones/',
                'sican_name': 'Actas de socialización y concertación',
                'sican_icon': 'data_usage',
                'sican_description': 'Seguimiento y registro de actividades.'
            })


        return items

    def get_context_data(self, **kwargs):
        kwargs['title'] = "GESTIÓN CON COMUNIDADES"
        kwargs['items'] = self.get_items()
        return super(EntesTerritorialesOptionsView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#----------------------------------- REUNIONES ------------------------------------

class ReunionesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entes_territoriales.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'entes_territoriales/reuniones/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTAS DE SOCIALIZACIÓN Y CONCERTACIÓN"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/entes_territoriales/reuniones/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.fest_2019.entes_territoriales.reuniones.crear')
        return super(ReunionesListView,self).get_context_data(**kwargs)



class ReporteReunionesListView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.direccion_financiera.solicitudes_desplazamiento.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../"

    def dispatch(self, request, *args, **kwargs):

        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Estado de hitos',
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_estado_hitos.delay(reporte.id)

        return HttpResponseRedirect('/reportes/')



class ReunionesCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entes_territoriales.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'entes_territoriales/reuniones/crear.html'
    form_class = forms.ReunionesForm
    success_url = "../"

    def form_valid(self, form):

        municipio = Municipios.objects.get(id = str(form.cleaned_data['municipio']))

        models.Reuniones.objects.create(
            usuario_creacion = self.request.user,
            usuario_actualizacion = self.request.user,
            municipio = municipio
        )

        #self.object = form.save(commit=False)

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVA GESTIÓN"
        kwargs['url_autocomplete_municipio'] = '/rest/v1.0/fest_2019/entes_territoriales/reuniones/autocomplete/municipios/'
        return super(ReunionesCreateView,self).get_context_data(**kwargs)


class ReunionesContactosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entes_territoriales.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'entes_territoriales/reuniones/contactos/lista.html'


    def get_context_data(self, **kwargs):
        reunion = models.Reuniones.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "CONTACTOS"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/entes_territoriales/reuniones/{0}/contactos/'.format(str(self.kwargs['pk']))
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.fest_2019.entes_territoriales.reuniones.crear')
        kwargs['breadcrum_active'] = str(reunion.municipio)
        return super(ReunionesContactosListView,self).get_context_data(**kwargs)


class ReunionesContactosCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entes_territoriales.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'entes_territoriales/reuniones/contactos/crear.html'
    form_class = forms.ContactosForm
    success_url = "../"
    model = models.Contactos

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.reunion = models.Reuniones.objects.get(id=self.kwargs['pk'])
        self.object.save()

        registro = models.Registro.objects.create(
            reunion = models.Reuniones.objects.get(id = self.kwargs['pk']),
            usuario = self.request.user,
            delta = json.dumps(functions.delta_contacto(self.object)),
            contacto = self.object
        )

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        reunion = models.Reuniones.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "NUEVO CONTACTO"
        kwargs['breadcrum_active'] = str(reunion.municipio)
        return super(ReunionesContactosCreateView,self).get_context_data(**kwargs)


class ReunionesContactosUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entes_territoriales.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'entes_territoriales/reuniones/contactos/editar.html'
    form_class = forms.ContactosForm
    success_url = "../../"
    model = models.Contactos
    pk_url_kwarg = 'pk_contacto'


    def form_valid(self, form):

        self.object = form.save()

        reunion = models.Reuniones.objects.get(id = self.kwargs['pk'])

        models.Registro.objects.filter(reunion = reunion, contacto=self.object, usuario = self.request.user).update(
            delta = json.dumps(functions.delta_contacto(self.object)),
        )

        return HttpResponseRedirect(self.get_success_url())



    def get_context_data(self, **kwargs):
        reunion = models.Reuniones.objects.get(id=self.kwargs['pk'])
        contacto = models.Contactos.objects.get(id=self.kwargs['pk_contacto'])
        kwargs['title'] = "EDITAR CONTACTO"
        kwargs['breadcrum_active'] = str(reunion.municipio)
        kwargs['breadcrum_active_1'] = contacto.nombres
        return super(ReunionesContactosUpdateView,self).get_context_data(**kwargs)


class ReunionesContactosSoportesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entes_territoriales.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'entes_territoriales/reuniones/contactos/soportes/lista.html'


    def get_context_data(self, **kwargs):
        reunion = models.Reuniones.objects.get(id = self.kwargs['pk'])
        contacto = models.Contactos.objects.get(id=self.kwargs['pk_contacto'])
        kwargs['title'] = "SOPORTES"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/entes_territoriales/reuniones/{0}/contactos/{1}/soportes/'.format(
            str(self.kwargs['pk']),
            str(self.kwargs['pk_contacto'])
        )
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.fest_2019.entes_territoriales.reuniones.crear')
        kwargs['breadcrum_active'] = str(reunion.municipio)
        kwargs['breadcrum_active_1'] = contacto.nombres
        return super(ReunionesContactosSoportesListView,self).get_context_data(**kwargs)


class ReunionesContactosSoportesCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entes_territoriales.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'entes_territoriales/reuniones/contactos/soportes/crear.html'
    form_class = forms.SoportesForm
    success_url = "../"
    model = models.Soportes


    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.contacto = models.Contactos.objects.get(id=self.kwargs['pk_contacto'])
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        reunion = models.Reuniones.objects.get(id=self.kwargs['pk'])
        contacto = models.Contactos.objects.get(id=self.kwargs['pk_contacto'])
        kwargs['title'] = "NUEVO SOPORTE"
        kwargs['breadcrum_active'] = str(reunion.municipio)
        kwargs['breadcrum_active_1'] = contacto.nombres
        kwargs['file_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        return super(ReunionesContactosSoportesCreateView,self).get_context_data(**kwargs)


class ReunionesContactosSoportesUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entes_territoriales.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'entes_territoriales/reuniones/contactos/soportes/actualizar.html'
    form_class = forms.SoportesForm
    success_url = "../../"
    model = models.Soportes
    pk_url_kwarg = 'pk_soporte'



    def get_context_data(self, **kwargs):
        reunion = models.Reuniones.objects.get(id=self.kwargs['pk'])
        contacto = models.Contactos.objects.get(id=self.kwargs['pk_contacto'])
        soporte = models.Soportes.objects.get(id=self.kwargs['pk_soporte'])
        kwargs['title'] = "ACTUALIZAR SOPORTE"
        kwargs['breadcrum_active'] = str(reunion.municipio)
        kwargs['breadcrum_active_1'] = contacto.nombres
        kwargs['breadcrum_active_2'] = soporte.tipo
        kwargs['file_url'] = soporte.pretty_print_url_minuta()
        return super(ReunionesContactosSoportesUpdateView,self).get_context_data(**kwargs)


class ReunionesHitosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entes_territoriales.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'entes_territoriales/reuniones/hitos/lista.html'


    def get_context_data(self, **kwargs):
        reunion = models.Reuniones.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "ACTAS"
        kwargs['url_datatable'] = '/rest/v1.0/fest_2019/entes_territoriales/reuniones/{0}/hitos/'.format(
            str(self.kwargs['pk'])
        )
        kwargs['breadcrum_active'] = str(reunion.municipio)
        kwargs['permiso_hito'] = True
        return super(ReunionesHitosListView,self).get_context_data(**kwargs)


class ReunionesHitosVerView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entes_territoriales.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'entes_territoriales/reuniones/hitos/ver.html'


    def get_context_data(self, **kwargs):
        reunion = models.Reuniones.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "ACTAS"
        kwargs['breadcrum_active'] = str(reunion.municipio)
        kwargs['hito'] = models.Hito.objects.get(id = self.kwargs['pk_hito'])
        return super(ReunionesHitosVerView,self).get_context_data(**kwargs)


class ReunionesHitosEstadoUpdateView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      UpdateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entes_territoriales.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'entes_territoriales/reuniones/hitos/estado.html'
    pk_url_kwarg = 'pk_hito'
    success_url = '../../'
    form_class = forms.HitoEstadoForm
    model = models.Hito


    def get_context_data(self, **kwargs):
        reunion = models.Reuniones.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "ACTAS"
        kwargs['breadcrum_active'] = str(reunion.municipio)
        kwargs['hito'] = models.Hito.objects.get(id = self.kwargs['pk_hito'])
        return super(ReunionesHitosEstadoUpdateView,self).get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save()

        models.Registro.objects.create(
            reunion = models.Reuniones.objects.get(id = self.kwargs['pk']),
            usuario = self.request.user,
            delta = json.dumps(functions.delta_estado(self.object)),
            hito = models.Hito.objects.get(id = self.kwargs['pk_hito'])
        )

        return super().form_valid(form)



class ReunionesHitosCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entes_territoriales.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'entes_territoriales/reuniones/hitos/crear.html'
    form_class = forms.HitoForm
    success_url = "../"

    def form_valid(self, form):

        contenido = json.loads(form.cleaned_data['contenido'])
        tipo = form.cleaned_data['tipo']
        fecha = form.cleaned_data['fecha']
        file = form.cleaned_data['file']
        file2 = form.cleaned_data['file2']
        file3 = form.cleaned_data['file3']
        foto_1 = form.cleaned_data['foto_1']
        foto_2 = form.cleaned_data['foto_2']
        foto_3 = form.cleaned_data['foto_3']
        foto_4 = form.cleaned_data['foto_4']

        hito = models.Hito.objects.create(
            reunion=models.Reuniones.objects.get(id=self.kwargs['pk']),
            tipo = tipo,
            file = file,
            file2 = file2,
            file3 = file3,
            fecha = fecha,
            foto_1 = foto_1,
            foto_2 = foto_2,
            foto_3 = foto_3,
            foto_4 = foto_4,
        )

        registro = models.Registro.objects.create(
            reunion=models.Reuniones.objects.get(id=self.kwargs['pk']),
            usuario=self.request.user,
            delta=form.cleaned_data['contenido'],
            hito = hito
        )

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        reunion = models.Reuniones.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "AÑADIR ACTA"
        kwargs['breadcrum_active'] = str(reunion.municipio)
        kwargs['file_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['file2_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        kwargs['file3_url'] = '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        return super(ReunionesHitosCreateView,self).get_context_data(**kwargs)


class ReunionesHitosUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entes_territoriales.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'entes_territoriales/reuniones/hitos/editar.html'
    form_class = forms.HitoForm
    success_url = "../../"


    def form_valid(self, form):

        tipo = form.cleaned_data['tipo']
        fecha = form.cleaned_data['fecha']
        file = form.cleaned_data['file']
        file2 = form.cleaned_data['file2']
        file3 = form.cleaned_data['file3']
        foto_1 = form.cleaned_data['foto_1']
        foto_2 = form.cleaned_data['foto_2']
        foto_3 = form.cleaned_data['foto_3']
        foto_4 = form.cleaned_data['foto_4']

        hito = models.Hito.objects.get(id=self.kwargs['pk_hito'])
        #registro = models.Registro.objects.filter(hito=hito)

        hito.tipo = tipo
        hito.fecha = fecha

        if file != None:
            hito.file = file

        if file2 != None:
            hito.file2 = file2

        if file3 != None:
            hito.file3 = file3

        if foto_1 != None:
            hito.foto_1 = foto_1

        if foto_2 != None:
            hito.foto_2 = foto_2

        if foto_3 != None:
            hito.foto_3 = foto_3

        if foto_4 != None:
            hito.foto_4 = foto_4

        hito.save()

        models.Registro.objects.create(
            reunion = hito.reunion,
            usuario = self.request.user,
            delta = form.cleaned_data['contenido'],
            hito = hito
        )

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        reunion = models.Reuniones.objects.get(id=self.kwargs['pk'])
        hito = models.Hito.objects.get(id = self.kwargs['pk_hito'])
        kwargs['title'] = "EDITAR ACTA"
        kwargs['breadcrum_active'] = str(reunion.municipio)
        kwargs['breadcrum_active_1'] = str(hito.tipo)
        kwargs['file_url'] = hito.pretty_print_url_file()
        kwargs['file2_url'] = hito.pretty_print_url_file2()
        kwargs['file3_url'] = hito.pretty_print_url_file3()
        kwargs['url_foto'] = '/rest/v1.0/fest_2019/entes_territoriales/reuniones/{0}/hitos/{1}/api_foto'.format(
            reunion.id,
            hito.id
        )
        return super(ReunionesHitosUpdateView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'pk_hito':self.kwargs['pk_hito']}


class ReunionesHitosGestionListView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    permissions = {
        "all": [
            "usuarios.fest_2019.ver",
            "usuarios.fest_2019.entes_territoriales.ver",
            "usuarios.fest_2019.entes_territoriales.reuniones.ver",
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'entes_territoriales/reuniones/hitos/gestion.html'
    form_class = forms.GestionForm

    def get_success_url(self):
        return str(self.request.path)

    def form_valid(self, form):

        contenido = json.loads(form.cleaned_data['contenido'])
        first_insert = contenido['ops'][0]['insert']

        if first_insert != '\n':
            registro = models.Registro.objects.create(
                reunion = models.Reuniones.objects.get(id = self.kwargs['pk']),
                usuario = self.request.user,
                delta = form.cleaned_data['contenido']
            )
        return HttpResponseRedirect(self.get_success_url())

    def get_items_registros(self):

        lista = []
        registros = models.Registro.objects.filter(reunion__id = self.kwargs['pk']).order_by('-creation')

        for registro in registros:
            delta_obj = json.loads(registro.delta)
            lista.append({
                'propio': True if registro.usuario == self.request.user else False,
                'fecha': registro.pretty_creation_datetime(),
                'usuario': registro.usuario.get_full_name_string(),
                'html': html.render(delta_obj['ops']),
                'hito': registro.hito
            })

        return lista

    def get_context_data(self, **kwargs):
        reunion = models.Reuniones.objects.get(id=self.kwargs['pk'])
        registros = self.get_items_registros()
        kwargs['title'] = "GESTIÓN"
        kwargs['registros'] = registros
        kwargs['registros_cantidad'] = len(registros)
        kwargs['breadcrum_active'] = str(reunion.municipio)
        return super(ReunionesHitosGestionListView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------