from django_datatables_view.base_datatable_view import BaseDatatableView
from desplazamiento import models
from recursos_humanos import models as models_rh
from django.db.models import Q
from dal import autocomplete
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class SolicitudesDesplazamientoListApi(BaseDatatableView):
    model = models.Solicitudes
    columns = ['consecutivo','usuario_creacion','creation','valor','estado','id','file','file2']
    order_columns = ['consecutivo','usuario_creacion','creation','valor','estado','id','file','file2']


    def get_initial_queryset(self):
        return self.model.objects.filter(usuario_creacion = self.request.user)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(consecutivo__icontains=search) | Q(nombre__icontains=search) | Q(estado__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'consecutivo':

            ret = ''
            if self.request.user.has_perm('usuarios.cpe_2018.solicitudes_desplazamiento.ver') and row.estado == 'Aprobado' and row.file2 == '':
                ret = '<div class="center-align">' \
                      '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar el formato firmado de la solicitud {2}">' \
                      '<b>{1}</b>' \
                      '</a>' \
                      '</div>'.format(row.id, row.consecutivo, row.nombre)

            else:
                ret = '<div class="center-align">' \
                      '<b>{1}</b>' \
                      '</div>'.format(row.id, row.consecutivo)

            return ret

        elif column == 'creation':
            return row.pretty_creation_datetime()

        elif column == 'usuario_creacion':
            if self.request.user.has_perm('usuarios.cpe_2018.solicitudes_desplazamiento.ver'):
                ret = '<div class="center-align">' \
                      '<a href="desplazamientos/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Gestionar desplazamientos de {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id, row.nombre)

            return ret

        elif column == 'valor':
            return '<div class="center-align"><b>' + row.pretty_print_valor() + '</b></div>'

        elif column == 'id':
            return '<div class="center-align"><b>' + str(row.get_cantidad_desplazamientos()) + '</b></div>'

        elif column == 'file':
            render = ""

            if row.url_file() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Formato legalización reintegro de transporte">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                          '</a>'.format(row.url_file(), row.nombre)

            return '<div class="center-align">' + render + '</div>'

        elif column == 'file2':
            render = ""

            if row.url_file2() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Formato firmado">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                          '</a>'.format(row.url_file2(), row.nombre)

            return '<div class="center-align">' + render + '</div>'


        elif column == 'estado':
            render = ""

            if row.estado != '':
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Actualizado por dirección financiera el {2}">' \
                          '{1}' \
                          '</a>'.format(row.id, row.estado, row.pretty_actualizacion_datetime())

            return '<div class="center-align"><b>' + render + '</b></div>'


        else:
            return super(SolicitudesDesplazamientoListApi, self).render_column(row, column)

class DesplazamientosListApi(BaseDatatableView):
    model = models.Desplazamiento
    columns = ['id','creation','origen','destino','fecha','tipo_transporte','estado','solicitud']
    order_columns = ['id','creation','origen','destino','fecha','tipo_transporte','estado','solicitud']


    def get_initial_queryset(self):
        return self.model.objects.filter(solicitud__usuario_creacion = self.request.user,solicitud = self.kwargs['pk'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(origen__icontains=search) | Q(destino__icontains=search) | Q(estado__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':

            ret = ''
            if self.request.user.has_perm('usuarios.cpe_2018.solicitudes_desplazamiento.editar') and row.estado == None:
                ret = '<div class="center-align">' \
                      '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar desplazamiento">' \
                      '<b>{1}</b>' \
                      '</a>' \
                      '</div>'.format(row.id, row.pretty_print_valor())

            else:
                ret = '<div class="center-align">' \
                      '<p>{1}</p>' \
                      '</div>'.format(row.id, row.pretty_print_valor())

            return ret

        elif column == 'creation':
            return row.pretty_creation_datetime()



        elif column == 'valor':
            return '<div class="center-align"><b>' + row.pretty_print_valor() + '</b></div>'


        elif column == 'solicitud':
            ret = ''
            if self.request.user.has_perm('usuarios.cpe_2018.solicitudes_desplazamiento.eliminar') and row.estado == None:
                ret = '<div class="center-align">' \
                           '<a href="eliminar/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar desplazamiento">' \
                                '<i class="material-icons">delete</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.pretty_print_valor())

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">delete</i>' \
                       '</div>'.format(row.id,row.pretty_print_valor())

            return ret


        else:
            return super(DesplazamientosListApi, self).render_column(row, column)