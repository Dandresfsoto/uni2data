from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from rest_framework.views import APIView

from inventario.models import Adiciones, CargarProductos, Productos, Despachos, Sustracciones, Clientes, Proyectos

from rest_framework.response import Response
from rest_framework import status


class ProductosListApi(BaseDatatableView):
    model = Productos
    columns = ['id','codigo','nombre','marca','valor_compra','valor','stock','unidad']
    order_columns = ['id','codigo','nombre','marca','valor_compra','valor','stock','unidad']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.inventario.ver",
                "usuarios.inventario.productos.ver"
            ],
            "editar": [
                "usuarios.inventario.ver",
                "usuarios.inventario.productos.ver",
                "usuarios.inventario.productos.editar",
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(codigo__icontains=search) | Q(nombre__icontains=search) | Q(descripcion__icontains=search) | Q(marca__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):
        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                      '<a href="edit/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Editar producto">' \
                      '<i class="material-icons">edit</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'codigo':
            return str(row.codigo)

        elif column == 'valor':
            return '<b>{0}</b>'.format(row.pretty_print_precio())

        elif column == 'valor_compra':
            return '<b>{0}</b>'.format(row.pretty_print_precio_compra())

        elif column == 'stock':
            return '<b style="color:blue">{0}</b>'.format(row.stock)

        elif column == 'unidad':
            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                      '<a href="add/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Editar producto">' \
                      '<i class="material-icons" style="color:green">add_box</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">add_box</i>' \
                       '</div>'.format(row.id)

            return ret

        else:
            return super(ProductosListApi, self).render_column(row, column)

class SubirListApi(BaseDatatableView):
    model = CargarProductos
    columns = ['id','consecutivo','creacion','observacion','estado','respaldo']
    order_columns = ['id','consecutivo','creacion','observacion','estado','respaldo']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.inventario.ver",
                "usuarios.inventario.subir.ver"
            ],
            "editar": [
                "usuarios.inventario.ver",
                "usuarios.inventario.subir.ver",
                "usuarios.inventario.subir.editar",
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(consecutivo__icontains=search) | Q(observacion__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):
        if column == 'id':
            ret = ''

            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                      '<a href="edit/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar reporte: {1}">' \
                      '<p style="font-weight:bold;">{2}</p>' \
                      '</a>' \
                      '</div>'.format(row.id, row.consecutivo, row.consecutivo)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">codigo</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'consecutivo':


            if self.request.user.has_perm('usuarios.inventario.subir.editar'):
                ret = '<div class="center-align">' \
                      '<a href="productos/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.consecutivo)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id, row.consecutivo)

            return ret

        elif column == 'creacion':
            return str(row.pretty_creation_datetime())

        elif column == 'observacion':
            return str(row.observacion)

        elif column == 'estado':
            if row.estado == "Cargando":
                return '<b style="color:blue">{0}</b>'.format(row.estado)
            else:
                return '<b style="color:green">{0}</b>'.format(row.estado)

        elif column == 'respaldo':

            url_respaldo = row.url_respaldo()

            ret = '<div class="center-align">'

            if url_respaldo != None:
                ret += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Archivo de respaldo: {1}">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                       '</a>'.format(url_respaldo, row.consecutivo)

            ret += '</div>'

            return ret

        else:
            return super(SubirListApi, self).render_column(row, column)

class SubirProductosListApi(BaseDatatableView):
    model = Adiciones
    columns = ['id', 'producto', 'cantidad', 'observacion', 'cargue']
    order_columns = ['id', 'producto', 'cantidad', 'observacion', 'cargue']


    def get_initial_queryset(self):

        self.cargue = CargarProductos.objects.get(id = self.kwargs['pk'])

        return self.model.objects.filter(cargue__id = self.kwargs['pk'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(producto__nombre__icontains=search) | Q(producto__codigo__icontains=search) | Q(observacion__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            cargue = CargarProductos.objects.get(id=self.kwargs['pk'])
            if self.request.user.has_perm('usuarios.inventario.subir.editar') and cargue.estado == "Cargando":
                ret = '<div class="center-align">' \
                           '<a href="edit/{0}/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar producto: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.producto.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.producto.nombre)

            return ret

        elif column == 'producto':
            return str(str(row.producto.codigo) + " - " + str(row.producto.nombre))


        elif column == 'cantidad':
            return str(row.cantidad)

        elif column == 'observacion':
            return row.observacion


        elif column == 'cargue':
            ret = ''
            cargue = CargarProductos.objects.get(id=self.kwargs['pk'])
            if self.request.user.has_perm('usuarios.inventario.subir.eliminar') and cargue.estado == "Cargando":
                ret = '<div class="center-align">' \
                           '<a href="delete/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar pago: {1}">' \
                                '<i class="material-icons">delete</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.producto.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">delete</i>' \
                       '</div>'.format(row.id,row.producto.nombre)

            return ret


        else:
            return super(SubirProductosListApi, self).render_column(row, column)

class DespachoListApi(BaseDatatableView):
    model = Despachos
    columns = ['id','consecutivo','creacion','nombre_cliente','ciudad','estado','respaldo']
    order_columns = ['id','consecutivo','creacion','nombre_cliente','ciudad','estado','respaldo']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.inventario.ver",
                "usuarios.inventario.despacho.ver"
            ],
            "editar": [
                "usuarios.inventario.ver",
                "usuarios.inventario.despacho.ver",
                "usuarios.inventario.despacho.editar",
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(consecutivo__icontains=search) | Q(nombre_cliente__icontains=search) | Q(documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):
        if column == 'id':
            ret = ''

            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                      '<a href="edit/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar reporte: {1}">' \
                      '<p style="font-weight:bold;">{2}</p>' \
                      '</a>' \
                      '</div>'.format(row.id, row.consecutivo, row.consecutivo)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">codigo</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'consecutivo':


            if self.request.user.has_perm('usuarios.inventario.despacho.editar'):
                ret = '<div class="center-align">' \
                      '<a href="productos/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.consecutivo)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id, row.consecutivo)

            return ret

        elif column == 'nombre_cliente':
            return str(row.get_info_cliente())

        elif column == 'creacion':
            return str(row.pretty_fecha_envio_datetime())

        elif column == 'ciudad':
            return str(row.get_info_destino())

        elif column == 'estado':
            if row.estado == "Cargando":
                return '<b style="color:blue">{0}</b>'.format(row.estado)
            else:
                return '<b style="color:green">{0}</b>'.format(row.estado)

        elif column == 'respaldo':

            url_legalizacion = row.url_legalizacion()

            ret = '<div class="center-align">'

            if url_legalizacion != None:
                ret += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Archivo de respaldo: {1}">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                       '</a>'.format(url_legalizacion, row.consecutivo)

            ret += '</div>'

            return ret

        else:
            return super(DespachoListApi, self).render_column(row, column)

class DespachoProductosListApi(BaseDatatableView):
    model = Sustracciones
    columns = ['id', 'producto', 'cantidad', 'observacion','valor_total', 'despacho']
    order_columns = ['id', 'producto', 'cantidad', 'observacion','valor_total','despacho']


    def get_initial_queryset(self):

        self.despacho = Despachos.objects.get(id = self.kwargs['pk'])

        return self.model.objects.filter(despacho__id = self.kwargs['pk'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(producto__nombre__icontains=search) | Q(producto__codigo__icontains=search) | Q(observacion__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            despacho = Despachos.objects.get(id=self.kwargs['pk'])
            if self.request.user.has_perm('usuarios.inventario.subir.editar') and despacho.estado == "Cargando":
                ret = '<div class="center-align">' \
                           '<a href="edit/{0}/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar producto: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.producto.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.producto.nombre)

            return ret

        elif column == 'producto':
            return str(str(row.producto.codigo) + " - " + str(row.producto.nombre))


        elif column == 'cantidad':
            return str(row.cantidad)

        elif column == 'observacion':
            return row.observacion

        elif column == 'valor_total':
            if row.valor_total != None and row.valor_total != "":
                return row.pretty_print_valor_total()
            else:
                return "0"

        elif column == 'despacho':
            ret = ''
            despacho = Despachos.objects.get(id=self.kwargs['pk'])
            if self.request.user.has_perm('usuarios.inventario.subir.eliminar') and despacho.estado == "Cargando":
                ret = '<div class="center-align">' \
                           '<a href="delete/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar pago: {1}">' \
                                '<i class="material-icons">delete</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.producto.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">delete</i>' \
                       '</div>'.format(row.id,row.producto.nombre)

            return ret


        else:
            return super(DespachoProductosListApi, self).render_column(row, column)

class CientesListApi(BaseDatatableView):
    model = Clientes
    columns = ['id','documento','nombre','direccion','telefono']
    order_columns = ['id','documento','nombre','direccion','telefono']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.inventario.ver",
                "usuarios.inventario.clientes.ver"
            ],
            "editar": [
                "usuarios.inventario.ver",
                "usuarios.inventario.clientes.ver",
                "usuarios.inventario.clientes.editar",
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(apellido__icontains=search) | Q(documento__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):
        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                      '<a href="edit/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Editar producto">' \
                      '<i class="material-icons">edit</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'documento':
            return str(row.documento)

        elif column == 'nombre':
            return row.get_nombre_completo()

        elif column == 'direccion':
            return row.direccion


        elif column == 'telefono':
            return row.telefono

        else:
            return super(CientesListApi, self).render_column(row, column)

class ProductosListApiJson(APIView):
    """
    """

    def get(self, request, format=None):
        lista = []
        diccionario = {}
        name = request.query_params.get('name')

        if name != None:

            q = Q(nombre__icontains = name) | Q(codigo__icontains = name)


            filtro = Productos.objects.all()


            for producto in filtro.filter(q).exclude():
                lista.append({
                    'name': str(producto.codigo) + " - " + str(producto.nombre)
                })
                diccionario[str(producto.codigo)] = {
                    'id': str(producto.id),
                    'nombre': producto.nombre,
                    'codigo': str(producto.codigo),
                }

        return Response({'lista':lista,'diccionario':diccionario},status=status.HTTP_200_OK)

class ClientesListApi(APIView):
    """
    """

    def get(self, request, format=None):
        lista = []
        diccionario = {}
        name = request.query_params.get('name')

        if name != None:

            q = Q(nombre__icontains = name) | Q(apellido__icontains = name) | Q(documento__icontains = name)


            filtro = Clientes.objects.all()


            for cliente in filtro.filter(q).exclude():
                lista.append({
                    'name': str(cliente.documento) + " - " + str(cliente.nombre)  + " " + str(cliente.apellido)
                })
                diccionario[str(cliente.documento)] = {
                    'id': str(cliente.id),
                    'nombre': cliente.nombre,
                    'apellido': cliente.apellido,
                    'docuemento': str(cliente.documento),
                }

        return Response({'lista':lista,'diccionario':diccionario},status=status.HTTP_200_OK)

class InsumosListApi(BaseDatatableView):
    model = Productos
    columns = ['codigo','nombre','marca','valor','stock','descripcion']
    order_columns = ['codigo','nombre','marca','valor','descripcion']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.inventario.ver",
                "usuarios.inventario.productos.ver"
            ],
            "editar": [
                "usuarios.inventario.ver",
                "usuarios.inventario.productos.ver",
                "usuarios.inventario.productos.editar",
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(codigo__icontains=search) | Q(nombre__icontains=search) | Q(descripcion__icontains=search) | Q(marca__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):
        if column == 'codigo':
            return '<b>{0}</b>'.format(str(row.codigo))

        elif column == 'valor':
            return '<b>{0}</b>'.format(row.pretty_print_precio())

        elif column == 'stock':
            return '<b style="color:blue">{0}</b>'.format(row.stock)

        elif column == 'descripcion':
            return row.get_descripcion()

        else:
            return super(InsumosListApi, self).render_column(row, column)

class ProyectosListApi(BaseDatatableView):
    model = Proyectos
    columns = ['id','nombre']
    order_columns = ['id','nombre']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.inventario.ver",
                "usuarios.inventario.proyectos.ver"
            ],
            "editar": [
                "usuarios.inventario.ver",
                "usuarios.inventario.proyectos.ver",
                "usuarios.inventario.proyectos.editar",
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):
        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                      '<a href="edit/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Editar producto">' \
                      '<i class="material-icons">edit</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id)

            return ret

        else:
            return super(ProyectosListApi, self).render_column(row, column)