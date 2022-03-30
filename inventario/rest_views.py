from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from inventario import models



class ProductosListApi(BaseDatatableView):
    model = models.Productos
    columns = ['id','codigo','nombre','valor','stock']
    order_columns = ['id','codigo','nombre','valor','stock']

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
            q = Q(codigo__icontains=search) | Q(nombre__icontains=search)
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
                           '<i class="material-icons">codigo</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'codigo':
            return str(row.codigo)

        elif column == 'valor':
            return '<b>{0}</b>'.format(row.pretty_print_precio())

        elif column == 'stock':
            return '<b style="color:blue">{0}</b>'.format(row.stock)

        else:
            return super(ProductosListApi, self).render_column(row, column)