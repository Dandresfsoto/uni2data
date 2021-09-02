from dal import autocomplete
from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView

from iraca import models
from usuarios.models import Municipios


class MeetingsListApi(BaseDatatableView):
    model = models.Meetings
    columns = ['id','user_update','creation','municipality','update_datetime']
    order_columns = ['id','user_update','creation','municipality','update_datetime']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(municipality__nombre__icontains=search) | Q(municipality__departamento__nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.iraca.reuniones.ver'):
                ret = '<div class="center-align">' \
                      '<a href="{0}/milestones/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver hitos {1}, {2}">' \
                      '<i class="material-icons">flag</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.municipality.nombre, row.municipality.departamento.nombre)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">flag</i>' \
                      '</div>'.format(row.id, row.municipality.nombre, row.municipality.departamento.nombre)

            return ret

        elif column == 'user_update':

            ret = ''
            if self.request.user.has_perm('usuarios.iraca.reuniones.ver'):
                ret = '<div class="center-align">' \
                      '<a href="{0}/contacts/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver contactos en {1}, {2}">' \
                      '<i class="material-icons">contacts</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.municipality.nombre, row.municipality.departamento.nombre)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">contacts</i>' \
                      '</div>'.format(row.id, row.municipality.nombre, row.municipality.departamento.nombre)

            return ret

        elif column == 'creation':
            return str(row.municipality.departamento.nombre)



        elif column == 'municipality':
            return str(row.municipality.nombre)

        else:
            return super(MeetingsListApi, self).render_column(row, column)



