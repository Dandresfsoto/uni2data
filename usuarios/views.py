from django.views.generic import TemplateView, CreateView, UpdateView, FormView
from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from usuarios import forms, models
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Permission, Group
from django.shortcuts import redirect
from usuarios.models import PaqueteActivacion, CodigoActivacion
from usuarios.tasks import build_file_paquete_activacion
# Create your views here.

#------------------------------- SELECCIÓN ----------------------------------------

class UsuariosoptionsView(LoginRequiredMixin,
                          MultiplePermissionsRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'usuarios/lista.html'
    permissions = {
        "all": ["usuarios.usuarios.ver"]
    }

    def dispatch(self, request, *args, **kwargs):
        items = self.get_items()
        if len(items) == 0:
            return redirect(self.login_url)
        return super(UsuariosoptionsView, self).dispatch(request, *args, **kwargs)

    def get_items(self):
        items = []

        if self.request.user.has_perm('usuarios.usuarios.cuentas.ver'):
            items.append({
                'sican_categoria': 'Cuentas',
                'sican_color': 'orange darken-4',
                'sican_order': 1,
                'sican_url': 'cuentas/',
                'sican_name': 'Cuentas',
                'sican_icon': 'group',
                'sican_description': 'Gestión y creación'
            })

        if self.request.user.has_perm('usuarios.usuarios.roles.ver'):
            items.append({
                'sican_categoria': 'Roles',
                'sican_color': 'green darken-4',
                'sican_order': 2,
                'sican_url': 'roles/',
                'sican_name': 'Roles',
                'sican_icon': 'class',
                'sican_description': 'Perfiles de usuario'
            })

        if self.request.user.has_perm('usuarios.usuarios.permisos.ver'):
            items.append({
                'sican_categoria': 'Permisos',
                'sican_color': 'brown darken-4',
                'sican_order': 3,
                'sican_url': 'permisos/',
                'sican_name': 'Permisos',
                'sican_icon': 'add_box',
                'sican_description': 'Directivas de acceso'
            })

        if self.request.user.has_perm('usuarios.usuarios.codigos.ver'):
            items.append({
                'sican_categoria': 'Codigos',
                'sican_color': 'blue-grey darken-4',
                'sican_order': 4,
                'sican_url': 'codigos/',
                'sican_name': 'Codigos',
                'sican_icon': 'vpn_key',
                'sican_description': 'Claves para la activación de usuarios'
            })

        return items

    def get_context_data(self, **kwargs):
        kwargs['title'] = "usuarios"
        kwargs['items'] = self.get_items()
        return super(UsuariosoptionsView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#----------------------------------- HV -------------------------------------------

class GestionHvView(LoginRequiredMixin,
                    FormView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'usuarios/hv.html'
    form_class = forms.HojaDeVidaForm
    success_url = "../"

    def get_context_data(self, **kwargs):
        kwargs['title'] = "MI HOJA DE VIDA"
        return super(GestionHvView,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'user':self.request.user.id}

#----------------------------------------------------------------------------------
#-------------------------------- CUENTAS -----------------------------------------

class CuentasListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": ["usuarios.usuarios.cuentas.ver"]
    }
    login_url = settings.LOGIN_URL
    template_name = 'usuarios/cuentas/lista.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "cuentas de usuario"
        kwargs['url_datatable'] = '/rest/v1.0/usuarios/cuentas/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.usuarios.cuentas.crear')
        return super(CuentasListView,self).get_context_data(**kwargs)


class CuentasCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.usuarios.cuentas.ver",
            "usuarios.usuarios.cuentas.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'usuarios/cuentas/crear.html'
    form_class = forms.UserForm
    success_url = "../"
    model = models.User

    def get_context_data(self, **kwargs):
        kwargs['title'] = "CREAR USUARIO"
        return super(CuentasCreateView,self).get_context_data(**kwargs)


class CuentasUpdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.usuarios.cuentas.ver",
            "usuarios.usuarios.cuentas.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'usuarios/cuentas/editar.html'
    form_class = forms.UserForm
    success_url = "../../"
    model = models.User


    def get_context_data(self, **kwargs):
        kwargs['title'] = "ACTUALIZAR USUARIO"
        kwargs['breadcrum_active'] = models.User.objects.get(id=self.kwargs['pk']).email
        return super(CuentasUpdateView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#--------------------------------- ROLES ------------------------------------------

class RolesListView(LoginRequiredMixin,
                    MultiplePermissionsRequiredMixin,
                    TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'usuarios/roles/lista.html'
    permissions = {
        "all": ["usuarios.usuarios.roles.ver"]
    }


    def get_context_data(self, **kwargs):
        kwargs['title'] = "roles"
        kwargs['url_datatable'] = '/rest/v1.0/usuarios/roles/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.usuarios.roles.crear')
        return super(RolesListView,self).get_context_data(**kwargs)


class RolesCreateView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      CreateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.usuarios.roles.ver",
            "usuarios.usuarios.roles.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'usuarios/roles/crear.html'
    form_class = forms.GroupForm
    success_url = "../"
    model = Group


    def get_context_data(self, **kwargs):
        kwargs['title'] = "crear rol"
        return super(RolesCreateView,self).get_context_data(**kwargs)

class RolesUpdateView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      UpdateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.usuarios.roles.ver",
            "usuarios.usuarios.roles.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'usuarios/roles/editar.html'
    form_class = forms.GroupForm
    success_url = "../../"
    model = Group

    def get_context_data(self, **kwargs):
        kwargs['title'] = "actualizar rol"
        kwargs['breadcrum_active'] = Group.objects.get(id=self.kwargs['pk']).name
        return super(RolesUpdateView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#------------------------------- PERMISOS -----------------------------------------

class PermisosListView(LoginRequiredMixin,
            TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'usuarios/permisos/lista.html'
    permissions = {
        "all": ["usuarios.usuarios.permisos.ver"]
    }


    def get_context_data(self, **kwargs):
        kwargs['title'] = "permisos"
        kwargs['url_datatable'] = '/rest/v1.0/usuarios/permisos/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.usuarios.permisos.crear')
        return super(PermisosListView,self).get_context_data(**kwargs)

class PermisosCreateView(LoginRequiredMixin,
                        CreateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.usuarios.permisos.ver",
            "usuarios.usuarios.permisos.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'usuarios/permisos/crear.html'
    form_class = forms.PermisoForm
    success_url = "../"
    model = Permission

    def get_context_data(self, **kwargs):
        kwargs['title'] = "crear permiso"
        return super(PermisosCreateView,self).get_context_data(**kwargs)

class PermisosUpdateView(LoginRequiredMixin,
                        UpdateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.usuarios.permisos.ver",
            "usuarios.usuarios.permisos.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'usuarios/permisos/editar.html'
    form_class = forms.PermisoForm
    success_url = "../../"
    model = Permission

    def get_context_data(self, **kwargs):
        kwargs['title'] = "editar permiso"
        kwargs['breadcrum_active'] = Permission.objects.get(id = self.kwargs['pk']).codename
        return super(PermisosUpdateView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#------------------------------- CODIGOS -----------------------------------------

class CodigosListView(LoginRequiredMixin,
            TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'usuarios/codigos/lista.html'
    permissions = {
        "all": ["usuarios.usuarios.codigos.ver"]
    }


    def get_context_data(self, **kwargs):
        kwargs['title'] = "paquetes de códigos"
        kwargs['url_datatable'] = '/rest/v1.0/usuarios/paquetes/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.usuarios.codigos.crear')
        return super(CodigosListView,self).get_context_data(**kwargs)

class CodigosCreateView(LoginRequiredMixin,
                        CreateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.usuarios.codigos.ver",
            "usuarios.usuarios.codigos.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'usuarios/codigos/crear.html'
    form_class = forms.PaqueteCodigoForm
    success_url = "../"
    model = PaqueteActivacion

    def get_context_data(self, **kwargs):
        kwargs['title'] = "crear paquete de códigos"
        return super(CodigosCreateView,self).get_context_data(**kwargs)

    def form_valid(self, form):

        description = form.cleaned_data['description']
        generados = form.cleaned_data['generados']
        permisos = form.cleaned_data['permissions']

        self.object = PaqueteActivacion.objects.create(
            description = description,
            generados = generados,
            usados = 0,
        )
        self.object.permissions.set(permisos)
        self.object.save()


        build_file_paquete_activacion.delay(str(self.object.id),self.request.user.email)

        return HttpResponseRedirect(self.get_success_url())

class CodigosUpdateView(LoginRequiredMixin,
                        UpdateView):
    """
    """
    permissions = {
        "all": [
            "usuarios.usuarios.codigos.ver",
            "usuarios.usuarios.codigos.crear"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'usuarios/codigos/editar.html'
    form_class = forms.PaqueteCodigoUpdateForm
    success_url = "../../"
    model = PaqueteActivacion

    def form_valid(self, form):
        self.object = form.save()
        return super(CodigosUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "crear paquete de códigos"
        return super(CodigosUpdateView,self).get_context_data(**kwargs)


class CodigosShowView(LoginRequiredMixin,
            TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'usuarios/codigos/lista_codigos.html'
    permissions = {
        "all": ["usuarios.usuarios.codigos.ver"]
    }


    def get_context_data(self, **kwargs):
        kwargs['title'] = "paquetes de códigos"
        kwargs['url_datatable'] = '/rest/v1.0/usuarios/paquetes/' + str(kwargs['pk'])
        kwargs['descripcion'] = PaqueteActivacion.objects.get(id=kwargs['pk']).description
        return super(CodigosShowView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------