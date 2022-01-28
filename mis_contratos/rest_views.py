from django_datatables_view.base_datatable_view import BaseDatatableView

from mis_contratos import functions
from recursos_humanos import models
from recursos_humanos import models as models_rh
from django.db.models import Q
from dal import autocomplete
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ContratosListApi(BaseDatatableView):
    model = models.Contratos
    columns = ['id','suscrito','nombre','inicio','fin','valor','estado','file','soporte_liquidacion','fecha_legalizacion']
    order_columns = ['id','suscrito','nombre','inicio','fin','valor','estado','file','soporte_liquidacion','fecha_legalizacion']

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

        if column == 'suscrito':
            ret = '<div class="center-align">' \
                       '<a href="accounts/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Soportes del contrato: {1}">' \
                            '<i class="material-icons" >assignment</i>' \
                       '</a>' \
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

class AccountContractListApi(BaseDatatableView):
    model = models.Collects_Account
    columns = ['id','html','html_2','html_3','delta','user_creation','file5','estate','file','file6','estate_inform','file2','estate_report']
    order_columns = ['id','html','html_2','html_3','delta','user_creation','file5','estate','file','file6','estate_inform','file2','estate_report']

    def get_initial_queryset(self):
        return self.model.objects.filter(contract = self.kwargs['pk']).exclude(value_fees=0).order_by('-cut__consecutive')

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(consecutive__icontains=search) | Q(cut_consecutive__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            if row.liquidacion==False:
                ret = ""
                month = int(row.cut.month) - 1
                month_inform = functions.month_converter(month)

                ret = '<div class="center-align">' \
                      '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{0}" >' \
                      '<b>{1}</b>' \
                      '</a>' \
                      '</div>'.format(row.observaciones_report, month_inform)
                return ret
            else:
                ret = ""
                ret = '<div class="center-align">' \
                      '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="Liquidación" >' \
                      '<b>Liquidación</b>' \
                      '</a>' \
                      '</div>'
                return ret

        elif column == 'html':
            url_file5 = row.url_file5()
            if row.estate == "Generado":
                ret = '<div class="center-align">' \
                      '<a href="upload_ss/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar planilla de seguridad  social {1}">' \
                      '<i class="material-icons">cloud_upload</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.contract.nombre)
            elif row.estate == "Rechazado":
                ret = '<div class="center-align">' \
                      '<a href="upload_ss/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar planilla de seguridad  social {1}">' \
                      '<i class="material-icons">cloud_upload</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.contract.nombre)
            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">cloud_upload</i>' \
                      '</div>'

            return ret

        elif column == 'delta':
            url_file5 = row.url_file5()
            ret = ''
            if url_file5 != None:
                estate = row.estate_report
                if estate == 'Generado':
                    ret = '<div class="center-align">' \
                          '<a href="upload_account/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Generar informe de actividades {1}">' \
                          '<i class="material-icons">cloud_upload</i>' \
                          '</a>' \
                          '</div>'.format(row.id, row.contract.nombre)

                elif estate == 'Cargado':
                    ret = '<div class="center-align">' \
                          '<a href="upload_account/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Generar informe de actividades {1}">' \
                          '<i class="material-icons">cloud_upload</i>' \
                          '</a>' \
                          '</div>'.format(row.id, row.contract.nombre)

                elif estate == 'Rechazado':
                    ret = '<div class="center-align">' \
                          '<a href="upload_account/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Generar informe de actividades {1}">' \
                          '<i class="material-icons">cloud_upload</i>' \
                          '</a>' \
                          '</div>'.format(row.id, row.contract.nombre)

                else:
                    ret = '<div class="center-align">' \
                          '<i class="material-icons">cloud_upload</i>' \
                          '</div>'
            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">cloud_upload</i>' \
                      '</div>'

            return ret

        elif column == 'html_2':
            url_file5 = row.url_file5()
            url_file6 = row.url_file6()
            ret = '<div class="center-align">'
            estate = row.estate_inform
            if url_file5 != None:
                if estate != "Aprobado":
                    if row.estate_inform == "Generado":
                        if url_file6 == None or url_file6=="" or row.delta == "" or row.delta==None:
                            ret = '<div class="center-align">' \
                                  '<a href="upload_activity/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar informe de actividades {1}">' \
                                  '<i class="material-icons">assignment_turned_in</i>' \
                                  '</a>' \
                                  '</div>'.format(row.id, row.contract.nombre)
                        else:
                            ret = '<div class="center-align">' \
                                  '<a href="update_activity/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar informe de actividades {1}">' \
                                  '<i class="material-icons">assignment_turned_in</i>' \
                                  '</a>' \
                                  '</div>'.format(row.id, row.contract.nombre)

                    elif row.estate_inform == "Rechazado":
                        if url_file6 == None or url_file6 == "" or row.delta == "" or row.delta == None:
                            ret = '<div class="center-align">' \
                                  '<a href="upload_activity/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar cuenta de cobro {1}">' \
                                  '<i class="material-icons">assignment_turned_in</i>' \
                                  '</a>' \
                                  '</div>'.format(row.id, row.contract.nombre)
                        else:
                            ret = '<div class="center-align">' \
                                  '<a href="update_activity/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar cuenta de cobro {1}">' \
                                  '<i class="material-icons">assignment_turned_in</i>' \
                                  '</a>' \
                                  '</div>'.format(row.id, row.contract.nombre)

                    else:
                        ret = '<div class="center-align">' \
                              '<i class="material-icons">assignment_turned_in</i>' \
                              '</div>'
                else:
                    ret = '<div class="center-align">' \
                          '<i class="material-icons">assignment_turned_in</i>' \
                          '</div>'
            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">assignment_turned_in</i>' \
                      '</div>'

            return ret

        elif column == 'html_3':
            url_file5 = row.url_file5()
            ret = '<div class="center-align">'
            if url_file5 != None:
                ret = ''
                if row.estate_inform == "Generado":
                    ret = '<div class="center-align">' \
                          '<a href="upload_inform/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar cuenta de cobro {1}">' \
                          '<i class="material-icons">cloud_upload</i>' \
                          '</a>' \
                          '</div>'.format(row.id, row.contract.nombre)

                elif row.estate_inform == "Rechazado":
                    ret = '<div class="center-align">' \
                          '<a href="upload_inform/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar cuenta de cobro {1}">' \
                          '<i class="material-icons">cloud_upload</i>' \
                          '</a>' \
                          '</div>'.format(row.id, row.contract.nombre)

                else:
                    ret = '<div class="center-align">' \
                          '<i class="material-icons">cloud_upload</i>' \
                          '</div>'

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">cloud_upload</i>' \
                      '</div>'

            return ret

        elif column == 'user_creation':
            return row.pretty_print_value_fees()

        elif column == 'file':
            url_file5 = row.url_file5()
            ret = '<div class="center-align">'
            if url_file5 != None:
                url_file = row.url_file()
                url_file2 = row.url_file2()

                ret = '<div class="center-align">'

                if url_file != None:
                    ret += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cuenta de cobro por honorarios">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                           '</a>'.format(url_file)

                if url_file2 != None:
                    ret += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cuenta de cobro por transporte">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                           '</a>'.format(url_file2)

                ret += '</div>'

            return ret

        elif column == 'estate':
            estate = row.estate

            render = ""

            if estate == "Aprobado":
                render += '<a class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Estado {0}">' \
                          '<i class="material-icons" style="font-size: 2rem;">check_circle</i>' \
                          '</a>'.format(row.estate)

            if estate == "Rechazado":
                render += '<a class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Estado: {0} por {1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">block</i>' \
                          '</a>'.format(row.estate, row.observaciones)

            return '<div class="center-align">' + render + '</div>'

        elif column == 'file6':
            url_file5 = row.url_file5()
            ret = '<div class="center-align">'
            if url_file5 != None:
                url_file6 = row.url_file6()

                ret = '<div class="center-align">'

                if url_file6 != None:
                    ret += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Informe de actividades">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                           '</a>'.format(url_file6)

                ret += '</div>'

            return ret

        elif column == 'estate_inform':
            estate = row.estate_inform

            render = ""

            if estate == "Aprobado":
                render += '<a class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Estado {0}">' \
                          '<i class="material-icons" style="font-size: 2rem;">check_circle</i>' \
                          '</a>'.format(row.estate_inform)

            if estate == "Rechazado":
                render += '<a class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Estado: {0} por {1}">' \
                          '<i class="material-icons" style="font-size: 2rem;">block</i>' \
                          '</a>'.format(row.estate_inform, row.observaciones_inform)

            return '<div class="center-align">' + render + '</div>'

        elif column == 'file5':


            url_file5 = row.url_file5()

            ret = '<div class="center-align">'

            if url_file5 != None:
                ret += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Planilla de seguridad social">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                       '</a>'.format(url_file5)

            ret += '</div>'

            return ret

        elif column == 'file2':
            url_file3 = row.url_file3()
            url_file4 = row.url_file4()

            ret = '<div class="center-align">'

            if url_file3 != None:
                ret += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cuenta de cobro por honorarios firmada">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                       '</a>'.format(url_file3)

            if url_file4 != None:
                ret += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Informe de actividades firmado">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                       '</a>'.format(url_file4)


            ret += '</div>'

            return ret

        elif column == 'estate_report':
            ret = ""
            if row.estate_report == 'Rechazado':
                ret = '<div class="center-align">' \
                      '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                      '<b>{0}</b>' \
                      '</a>' \
                      '</div>'.format(row.estate_report, row.observaciones_report)
            else:
                ret = '<div class="center-align">' \
                      '<a class="tooltipped" data-position="top" data-delay="50">' \
                      '<b>{0}</b>' \
                      '</a>' \
                      '</div>'.format(row.estate_report)
            return ret

        else:
            return super(AccountContractListApi, self).render_column(row, column)
