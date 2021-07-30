from django_datatables_view.base_datatable_view import BaseDatatableView
from recursos_humanos import models
from recursos_humanos import models as models_rh
from django.db.models import Q
from dal import autocomplete
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ContratosListApi(BaseDatatableView):
    model = models.Contratos
    columns = ['id','nombre','inicio','fin','valor','estado','file','soporte_liquidacion','fecha_legalizacion']
    order_columns = ['id','nombre','inicio','fin','valor','estado','file','soporte_liquidacion','fecha_legalizacion']

    def get_initial_queryset(self):
        return self.model.objects.filter(contratista__usuario_asociado = self.request.user, visible = True)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if not row.liquidado:
                ret = '<div class="center-align">' \
                           '<a href="soportes/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Soportes del contrato: {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'valor':
            return row.pretty_print_valor()

        elif column == 'file':
            render = ''
            if row.url_file() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Minuta contrato {1}">' \
                                '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                          '</a>'.format(row.url_file(),row.nombre)
            return '<div class="center-align">' + render + '</div>'

        elif column == 'soporte_liquidacion':
            render = ''
            if row.suscrito:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Contrato suscrito">' \
                          '<i class="material-icons" style="font-size: 2rem;">check_circle</i>' \
                          '</a>'
            if row.ejecucion:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Contrato en ejecución">' \
                          '<i class="material-icons" style="font-size: 2rem;">access_time</i>' \
                          '</a>'
            if row.ejecutado:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Contrato ejecutado">' \
                          '<i class="material-icons" style="font-size: 2rem;">assignment_turned_in</i>' \
                          '</a>'
            if row.liquidado:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Contrato liquidado">' \
                          '<i class="material-icons" style="font-size: 2rem;">business_center</i>' \
                          '</a>'
            return '<div class="center-align">' + render + '</div>'

        elif column == 'fecha_legalizacion':
            render = ""

            if row.fecha_legalizacion != None:
                render += '<a class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Contrato legalizado el {0}">' \
                                '<i class="material-icons" style="font-size: 2rem;">check_circle</i>' \
                          '</a>'.format(row.fecha_legalizacion)


            return '<div class="center-align">' + render + '</div>'

        else:
            return super(ContratosListApi, self).render_column(row, column)

class SoportesContratoListApi(BaseDatatableView):
    model = models.SoportesContratos
    columns = ['id','numero','codigo','soporte','contrato','file','estado','observacion']
    order_columns = ['id','numero','codigo','soporte','contrato','file','estado','observacion']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(soporte__nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def get_initial_queryset(self):
        return self.model.objects.filter(contrato__id = self.kwargs['pk'])


    def render_column(self, row, column):

        if column == 'id':
            if row.estado != 'Aprobado':
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar soportes: {1}">' \
                                '<i class="material-icons">cloud_upload</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.soporte.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">cloud_upload</i>' \
                       '</div>'.format(row.id,row.soporte.nombre)

            return ret

        elif column == 'numero':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.numero)


        elif column == 'codigo':
            text = ''

            if row.soporte.requerido:
                text = 'Obligatorio'
            else:
                text = 'Opcional'

            return '<div class="center-align"><b>{0}</b></div>'.format(text)


        elif column == 'soporte':

            return str(row.soporte)

        elif column == 'contrato':
            return row.contrato.nombre


        elif column == 'file':

            try:

                url = row.file.url

            except:

                return ''

            else:

                return '<div class="center-align">' \
 \
                       '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Soporte: {1}">' \
 \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
 \
                       '</a>' \
 \
                       '</div>'.format(url, row.soporte.nombre)

        elif column == 'estado':
            ret = ''
            if row.estado == 'Aprobado':
                ret = '<div class="center-align">' \
                      '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="Soporte aprobado">' \
                      '<i class="material-icons green-text text-darken-2">check_circle</i>' \
                      '</a>' \
                      '</div>'

            elif row.estado == 'Solicitar subsanación':
                ret = '<div class="center-align">' \
                      '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="Solicitud de subsanación">' \
                      '<i class="material-icons red-text text-darken-4">cancel</i>' \
                      '</a>' \
                      '</div>'

            return ret

        elif column == 'observacion':
            ret = ''
            if row.observacion != '' and row.observacion != None:
                ret = '<div class="center-align">' \
                      '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{0}">' \
                      '<i class="material-icons green-text text-darken-2">chat</i>' \
                      '</a>' \
                      '</div>'.format(row.observacion)

            return ret


        else:
            return super(SoportesContratoListApi, self).render_column(row, column)