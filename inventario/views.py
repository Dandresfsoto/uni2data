from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View
from django.shortcuts import render

from inventario import forms
from inventario.models import Productos, CargarProductos


class InventarioOptionsView(LoginRequiredMixin,
                          MultiplePermissionsRequiredMixin,
                          TemplateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'inventario/lista.html'
    permissions = {
        "all": [
            "usuarios.inventario.ver"
        ]
    }

    def dispatch(self, request, *args, **kwargs):
        items = self.get_items()
        if len(items) == 0:
            return redirect(self.login_url)
        return super(InventarioOptionsView, self).dispatch(request, *args, **kwargs)

    def get_items(self):
        items = []

        if self.request.user.has_perm('usuarios.inventario.productos.ver'):
            items.append({
                'sican_categoria': 'Listado de productos',
                'sican_color': 'red darken-4',
                'sican_order': 1,
                'sican_url': 'productos/',
                'sican_name': 'Productos',
                'sican_icon': 'assignment',
                'sican_description': 'Información los productos alojados'
            })
        if self.request.user.has_perm('usuarios.inventario.subir.ver'):
            items.append({
                'sican_categoria': 'Subir productos',
                'sican_color': 'indigo darken-3',
                'sican_order': 2,
                'sican_url': 'subir/',
                'sican_name': 'Cargue de productos',
                'sican_icon': 'archive',
                'sican_description': 'cargar productos'
            })
        return items

    def get_context_data(self, **kwargs):
        kwargs['title'] = "INVENTARIO"
        kwargs['items'] = self.get_items()
        return super(InventarioOptionsView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#-----------------------------PRODUCTOS--------------------------------------------

class ProductosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.inventario.ver",
            "usuarios.inventario.productos.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'inventario/productos/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "PRODUCTOS"
        kwargs['url_datatable'] = '/rest/v1.0/inventario/productos/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.inventario.productos.crear')
        return super(ProductosListView,self).get_context_data(**kwargs)

class ProductosCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'inventario/productos/create.html'
    form_class = forms.ProductForm
    success_url = "../"
    models = Productos

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.inventario.ver",
                "usuarios.inventario.productos.ver",
                "usuarios.inventario.productos.crear"
            ]
        }
        return permissions

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVO PRODUCTO"
        return super(ProductosCreateView,self).get_context_data(**kwargs)

class ProductosEditView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'inventario/productos/edit.html'
    form_class = forms.ProductForm
    success_url = "../../"
    model = Productos

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.inventario.ver",
                "usuarios.inventario.productos.ver",
                "usuarios.inventario.productos.editar"
            ]
        }
        return permissions

    def get_initial(self):
        return {'pk':self.kwargs['pk']}

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "EDITAR PRODUCTO"
        return super(ProductosEditView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#-----------------------------PRODUCTOS--------------------------------------------

class SubirListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.inventario.ver",
            "usuarios.inventario.subir.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'inventario/subir/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "CARGAR PRODUCTOS"
        kwargs['url_datatable'] = '/rest/v1.0/inventario/subir/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.inventario.subir.crear')
        return super(SubirListView,self).get_context_data(**kwargs)

class SubirCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'inventario/subir/create.html'
    form_class = forms.CargueProductosForm
    success_url = "../"
    models = CargarProductos

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.inventario.ver",
                "usuarios.inventario.subir.ver",
                "usuarios.inventario.subir.crear"
            ]
        }
        return permissions

    def form_valid(self, form):
        ordenes = CargarProductos.objects.all().count()
        self.object = form.save(commit=False)
        self.object.consecutivo = ordenes + 1
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVO CARGUE"
        return super(SubirCreateView,self).get_context_data(**kwargs)

class SubirEditView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'inventario/subir/edit.html'
    form_class = forms.CargueProductosForm
    success_url = "../../"
    model = CargarProductos

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.inventario.ver",
                "usuarios.inventario.subir.ver",
                "usuarios.inventario.subir.editar"
            ]
        }
        return permissions

    def get_initial(self):
        return {'pk':self.kwargs['pk']}

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        cargue = CargarProductos.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "EDITAR CARGUE"
        kwargs['respaldo_url'] = cargue.pretty_print_respaldo()
        return super(SubirEditView,self).get_context_data(**kwargs)