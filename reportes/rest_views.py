from django_datatables_view.base_datatable_view import BaseDatatableView
from reportes.models import Reportes
from django.db.models import Q

class ReportesListApi(BaseDatatableView):
    model = Reportes
    columns = ['consecutivo','creation','nombre','file']
    order_columns = ['consecutivo','creation','nombre','file']


    def get_initial_queryset(self):
        return self.model.objects.filter(usuario = self.request.user)


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'consecutivo':
            return '<div class="center-align"><p style="font-weight:bold;">{0}</p></div>'.format(row.consecutivo)

        elif column == 'creation':
            return row.pretty_creation_datetime()

        elif column == 'file':

            if row.url_file() != None:
                return '<div class="center-align">' \
                           '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Reporte: {1}">' \
                                '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                           '</a>' \
                       '</div>'.format(row.url_file(),row.nombre)
            else:
                return ''

        else:
            return super(ReportesListApi, self).render_column(row, column)