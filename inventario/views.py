import openpyxl
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from braces.views import LoginRequiredMixin, MultiplePermissionsRequiredMixin
from django.conf import settings
from django.views.generic import TemplateView, CreateView, UpdateView, FormView, View
from django.shortcuts import render

from inventario import forms
from inventario import tasks
from inventario.models import Productos, CargarProductos, Adiciones, Despachos, Sustracciones, Clientes
from reportes.models import Reportes


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
                'sican_description': 'Cargue de productos'
            })
        if self.request.user.has_perm('usuarios.inventario.despachos.ver'):
            items.append({
                'sican_categoria': 'Despacho',
                'sican_color': 'orange darken-4',
                'sican_order': 3,
                'sican_url': 'despacho/',
                'sican_name': 'Despacho',
                'sican_icon': 'local_shipping',
                'sican_description': 'Despacho de productos'
            })
        if self.request.user.has_perm('usuarios.inventario.clientes.ver'):
            items.append({
                'sican_categoria': 'Clientes',
                'sican_color': 'light-green darken-4',
                'sican_order': 4,
                'sican_url': 'clientes/',
                'sican_name': 'Clientes',
                'sican_icon': 'folder_shared',
                'sican_description': 'listado de clientes'
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
        self.object = form.save(commit=False)
        self.object.valor = float(form.cleaned_data['valor_char'].replace('$ ', '').replace(',', ''))
        self.object.save()
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
        producto = Productos.objects.get(id=self.kwargs['pk'])
        producto.codigo = form.cleaned_data['codigo']
        producto.nombre = form.cleaned_data['nombre']
        producto.valor = float(form.cleaned_data['valor_char'].replace('$ ', '').replace(',', ''))
        producto.stock = form.cleaned_data['stock']
        producto.unidad = form.cleaned_data['unidad']
        producto.impuesto = form.cleaned_data['impuesto']
        producto.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "EDITAR PRODUCTO"
        return super(ProductosEditView,self).get_context_data(**kwargs)

class ProductosAddView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    template_name = 'inventario/productos/edit.html'
    form_class = forms.AddProductForm
    success_url = "../../"

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
        producto = Productos.objects.get(id=self.kwargs['pk'])
        producto.stock += form.cleaned_data['stock']
        producto.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "AGREGAR STOCK"
        return super(ProductosAddView,self).get_context_data(**kwargs)


class ProductosReportView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.inventario.ver",
                "usuarios.inventario.productos.ver",
                "usuarios.inventario.productos.editar"
        ]
    }
    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        products = Productos.objects.all()
        reporte = Reportes.objects.create(
            usuario = self.request.user,
            nombre = 'Reporte de productos',
            consecutivo = Reportes.objects.filter(usuario = self.request.user).count()+1
        )

        tasks.build_list_reports.delay(reporte.id)

        return HttpResponseRedirect('/reportes/')


#----------------------------------------------------------------------------------

#--------------------- CARGUE DE  PRODUCTOS----------------------------------------

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


#----------------------------------------------------------------------------------

#---------------------------- PRODUCTOS ENTRANTES ---------------------------------

class SubirProductosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": ["usuarios.inventario.subir.ver"]
    }
    login_url = settings.LOGIN_URL
    template_name = 'inventario/subir/productos/list.html'


    def get_context_data(self, **kwargs):
        cargue = CargarProductos.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "PRODUCTOS A AGREGAR"
        kwargs['url_datatable'] = '/rest/v1.0/inventario/subir/productos/{0}'.format(cargue.id)
        kwargs['permiso_crear'] = True if cargue.estado == 'Cargando' else False
        kwargs['permiso_finalizar'] = True if cargue.estado == 'Cargando' else False
        kwargs['permiso_cargar'] = True if cargue.estado == 'Cargando' else False
        kwargs['breadcrum_active'] = cargue.consecutivo
        return super(SubirProductosListView,self).get_context_data(**kwargs)

class SubirProductosCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'inventario/subir/productos/create.html'
    form_class = forms.AdicionalForm
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

    def get_initial(self):
        return {'pk':self.kwargs['pk']}

    def form_valid(self, form):
        orden = CargarProductos.objects.get(id=self.kwargs['pk'])
        self.object = form.save(commit=False)
        self.object.cargue = orden
        self.object.producto = Productos.objects.filter(codigo = form.cleaned_data['codigo']).first()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVO CARGUE"
        return super(SubirProductosCreateView,self).get_context_data(**kwargs)


class SubirProductosEditView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'inventario/subir/productos/edit.html'
    form_class = forms.AdicionalForm
    success_url = "../../"
    model = Adiciones
    pk_url_kwarg = 'pk_adicion'

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
        return {
            'pk': self.kwargs['pk'],
            'pk_adicion':self.kwargs['pk_adicion']
        }

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        cargue = CargarProductos.objects.get(id=self.kwargs['pk'])
        adicion = Adiciones.objects.get(id=self.kwargs['pk_adicion'])
        kwargs['title'] = "EDITAR PRODUCTO"
        return super(SubirProductosEditView,self).get_context_data(**kwargs)

class SubirProductosDeleteView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.inventario.ver",
            "usuarios.inventario.subir.ver",
            "usuarios.inventario.subir.editar"
            "usuarios.inventario.subir.eliminar"
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):
        Adiciones.objects.get(id = self.kwargs['pk_adicion']).delete()

        return HttpResponseRedirect('../../')

class SubirProductosUploadView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.inventario.ver",
            "usuarios.inventario.subir.ver",
            "usuarios.inventario.subir.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../../"

    def dispatch(self, request, *args, **kwargs):

        if self.request.user.has_perms(self.permissions.get('all')):

            cargue = CargarProductos.objects.get(id = self.kwargs['pk'])
            cargue.estado = 'Completo'
            cargue.save()

            for adicion in Adiciones.objects.filter(cargue = cargue.id):
                producto = Productos.objects.get(id=adicion.producto.id)
                producto.stock += adicion.cantidad
                producto.save()

        return HttpResponseRedirect('../../../')

class SubirMasivoProductosUploadView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    template_name = 'inventario/subir/productos/add.html'
    form_class = forms.AdicionalPlusForm
    success_url = "../"

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
        cargue = CargarProductos.objects.get(id=self.kwargs['pk'])
        wb = openpyxl.load_workbook(form.cleaned_data['file'])
        ws = wb.active

        for file in ws.rows:
            if Productos.objects.filter(codigo = file[0].value).count() > 0:
                adicion = Adiciones.objects.create(
                    cargue = cargue,
                    producto = Productos.objects.get(codigo = file[0].value),
                    cantidad = file[1].value,
                )
                adicion.save()

                observacion = file[2].value
                if observacion != None and observacion != "":
                    adicion.observacion = observacion
                    adicion.save()
            elif Productos.objects.filter(nombre = file[4].value).count() > 0:
                adicion = Adiciones.objects.create(
                    cargue = cargue,
                    producto = Productos.objects.get(codigo = file[0].value),
                    cantidad = file[1].value,
                )
                adicion.save()

                observacion = file[2].value
                if observacion != None and observacion != "":
                    adicion.observacion = observacion
                    adicion.save()



        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "AGREGAR PRODUCTOS"
        return super(SubirMasivoProductosUploadView,self).get_context_data(**kwargs)

#----------------------------------------------------------------------------------

#-----------------------------DESPACHO--------------------------------------------

class DespachoListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.inventario.ver",
            "usuarios.inventario.despachos.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'inventario/despacho/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "DESPARCHAR PRODUCTOS"
        kwargs['url_datatable'] = '/rest/v1.0/inventario/despacho/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.inventario.despacho.crear')
        return super(DespachoListView,self).get_context_data(**kwargs)

class DespachoCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'inventario/despacho/create.html'
    form_class = forms.DespachoForm
    success_url = "../"
    models = Despachos

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.inventario.ver",
                "usuarios.inventario.despachos.ver",
                "usuarios.inventario.despachos.crear"
            ]
        }
        return permissions


    def form_valid(self, form):
        despachos = Despachos.objects.all().count()
        cliente = Clientes.objects.filter(documento=form.cleaned_data['documento']).first()
        self.object = form.save(commit=False)
        self.object.cliente = cliente
        self.object.consecutivo = despachos + 1
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVO DESPACHO"
        return super(DespachoCreateView,self).get_context_data(**kwargs)

class DespachoEditView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'inventario/despacho/edit.html'
    form_class = forms.DespachoForm
    success_url = "../../"
    model = Despachos
    pk_url_kwarg = 'pk_despacho'

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.inventario.ver",
                "usuarios.inventario.despachos.ver",
                "usuarios.inventario.despachos.editar"
            ]
        }
        return permissions

    def get_initial(self):
        return {'pk_despacho':self.kwargs['pk_despacho']}

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        despacho = Despachos.objects.get(id=self.kwargs['pk_despacho'])
        kwargs['title'] = "EDITAR DESPACHO"
        kwargs['respaldo_url'] = despacho.pretty_print_respaldo()
        kwargs['legalizacion_url'] = despacho.pretty_print_legalizacion()
        return super(DespachoEditView,self).get_context_data(**kwargs)

class DespachoProductosListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):
    """
    """
    permissions = {
        "all": ["usuarios.inventario.despacho.ver"]
    }
    login_url = settings.LOGIN_URL
    template_name = 'inventario/despacho/productos/list.html'


    def get_context_data(self, **kwargs):
        despacho = Despachos.objects.get(id=self.kwargs['pk'])
        kwargs['title'] = "PRODUCTOS A DESPACHAR"
        kwargs['url_datatable'] = '/rest/v1.0/inventario/despacho/productos/{0}'.format(despacho.id)
        kwargs['permiso_crear'] = True if despacho.estado == 'Cargando' else False
        kwargs['permiso_finalizar'] = True if despacho.estado == 'Cargando' else False
        kwargs['breadcrum_active'] = despacho.consecutivo
        kwargs['respaldo'] = despacho.url_respaldo()
        return super(DespachoProductosListView,self).get_context_data(**kwargs)

class DespachoProductosCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'inventario/despacho/productos/create.html'
    form_class = forms.SustraccionForm
    success_url = "../"
    models = Sustracciones

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.inventario.ver",
                "usuarios.inventario.despacho.ver",
                "usuarios.inventario.despacho.crear"
            ]
        }
        return permissions

    def get_initial(self):
        return {'pk':self.kwargs['pk']}

    def form_valid(self, form):
        despacho = Despachos.objects.get(id=self.kwargs['pk'])
        producto = Productos.objects.filter(codigo = form.cleaned_data['codigo']).first()
        self.object = form.save(commit=False)
        self.object.despacho = despacho
        self.object.producto = producto
        self.object.valor_total = float(producto.valor) * float(form.cleaned_data['cantidad'])
        self.object.save()

        despacho.respaldo.delete(save=True)

        tasks.build_remision.delay(str(despacho.id))
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVO CARGUE"
        return super(DespachoProductosCreateView,self).get_context_data(**kwargs)

class DespachoProductosEditView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'inventario/despacho/productos/edit.html'
    form_class = forms.SustraccionForm
    success_url = "../../"
    model = Sustracciones
    pk_url_kwarg = 'pk_sustracion'

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.inventario.ver",
                "usuarios.inventario.despacho.ver",
                "usuarios.inventario.despacho.editar"
            ]
        }
        return permissions

    def get_initial(self):
        return {
            'pk': self.kwargs['pk'],
            'pk_sustracion':self.kwargs['pk_sustracion']
        }

    def form_valid(self, form):
        despacho = Despachos.objects.get(id=self.kwargs['pk'])
        sustraccion = Sustracciones.objects.get(id=self.kwargs['pk_sustracion'])
        self.object.valor_total = float(sustraccion.producto.valor) * float(form.cleaned_data['cantidad'])
        self.object = form.save()
        despacho.respaldo.delete(save=True)

        tasks.build_remision.delay(str(despacho.id))
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        despacho = Despachos.objects.get(id=self.kwargs['pk'])
        sustraccion = Sustracciones.objects.get(id=self.kwargs['pk_sustracion'])
        kwargs['title'] = "EDITAR PRODUCTO"
        return super(DespachoProductosEditView,self).get_context_data(**kwargs)

class DespachoProductosDeleteView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.inventario.ver",
            "usuarios.inventario.despachos.ver",
            "usuarios.inventario.despachos.editar"
            "usuarios.inventario.despachos.eliminar"
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../"

    def dispatch(self, request, *args, **kwargs):
        despacho = Despachos.objects.get(id=self.kwargs['pk'])
        Sustracciones.objects.get(id = self.kwargs['pk_sustracion']).delete()

        tasks.build_remision.delay(str(despacho.id))
        return HttpResponseRedirect(self.get_success_url())

class DespachoProductosUploadView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        View):

    permissions = {
        "all": [
            "usuarios.inventario.ver",
            "usuarios.inventario.despachos.ver",
            "usuarios.inventario.despachos.editar"
        ]
    }
    login_url = settings.LOGIN_URL
    success_url = "../../../"

    def dispatch(self, request, *args, **kwargs):

        if self.request.user.has_perms(self.permissions.get('all')):

            despacho = Despachos.objects.get(id = self.kwargs['pk'])
            despacho.estado = 'Completo'
            despacho.save()

            for sustraccion in Sustracciones.objects.filter(despacho = despacho.id):
                producto = Productos.objects.get(id=sustraccion.producto.id)
                producto.stock -= sustraccion.cantidad
                producto.save()

        return HttpResponseRedirect('../../../')

class DespachoMasivoProductosUploadView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        FormView):

    login_url = settings.LOGIN_URL
    template_name = 'inventario/despacho/productos/add.html'
    form_class = forms.SustraccionPlusForm
    success_url = "../"

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.inventario.ver",
                "usuarios.inventario.despacho.ver",
                "usuarios.inventario.despacho.editar"
            ]
        }
        return permissions

    def get_initial(self):
        return {'pk':self.kwargs['pk']}

    def form_valid(self, form):
        despacho = Despachos.objects.get(id=self.kwargs['pk'])
        wb = openpyxl.load_workbook(form.cleaned_data['file'])
        ws = wb.active

        for file in ws.rows:
            if Productos.objects.filter(codigo = file[0].value).count() > 0:
                sustraccion = Sustracciones.objects.create(
                    despacho = despacho,
                    producto = Productos.objects.get(codigo = file[0].value),
                    cantidad = file[1].value,
                )
                sustraccion.save()

                observacion = file[2].value
                if observacion != None and observacion != "":
                    sustraccion.observacion = observacion
                    sustraccion.save()
            elif Productos.objects.filter(nombre = file[4].value).count() > 0:
                sustraccion = Sustracciones.objects.create(
                    despacho = despacho,
                    producto = Productos.objects.get(codigo = file[0].value),
                    cantidad = file[1].value,
                )
                sustraccion.save()

                observacion = file[2].value
                if observacion != None and observacion != "":
                    sustraccion.observacion = observacion
                    sustraccion.save()

        tasks.build_remision.delay(str(despacho.id))
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['title'] = "AGREGAR PRODUCTOS"
        return super(DespachoMasivoProductosUploadView,self).get_context_data(**kwargs)
#----------------------------------------------------------------------------------

#-----------------------------PRODUCTOS--------------------------------------------

class ClientesListView(LoginRequiredMixin,
                      MultiplePermissionsRequiredMixin,
                      TemplateView):

    permissions = {
        "all": [
            "usuarios.inventario.ver",
            "usuarios.inventario.clientes.ver"
        ]
    }
    login_url = settings.LOGIN_URL
    template_name = 'inventario/clientes/list.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "CLIENTES"
        kwargs['url_datatable'] = '/rest/v1.0/inventario/clientes/'
        kwargs['permiso_crear'] = self.request.user.has_perm('usuarios.inventario.clientes.crear')
        return super(ClientesListView,self).get_context_data(**kwargs)

class ClientesCreateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        CreateView):

    login_url = settings.LOGIN_URL
    template_name = 'inventario/clientes/create.html'
    form_class = forms.ClienteForm
    success_url = "../"
    models = Clientes

    def get_permission_required(self, request=None):
        permissions = {
            "all": [
                "usuarios.inventario.ver",
                "usuarios.inventario.clientes.ver",
                "usuarios.inventario.clientes.crear"
            ]
        }
        return permissions

    def form_valid(self, form):
        self.object = form.save()
        self.object.save()
        return super(ClientesCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "NUEVO CLIENTE"
        return super(ClientesCreateView,self).get_context_data(**kwargs)

class ClientesupdateView(LoginRequiredMixin,
                        MultiplePermissionsRequiredMixin,
                        UpdateView):

    login_url = settings.LOGIN_URL
    template_name = 'inventario/clientes/edit.html'
    form_class = forms.ClienteForm
    success_url = "../../"
    model = Clientes

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
        self.object.save()
        return super(ClientesupdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "EDITAR CLIENTE"
        return super(ClientesupdateView,self).get_context_data(**kwargs)