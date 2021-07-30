from django_datatables_view.base_datatable_view import BaseDatatableView
from direccion_financiera.models import Bancos, Reportes, Pagos, Descuentos, Amortizaciones
from recursos_humanos.models import Contratistas
from django.db.models import Q
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from desplazamiento import models as models_desplazamiento

class BancosListApi(BaseDatatableView):
    model = Bancos
    columns = ['id','codigo','longitud','nombre']
    order_columns = ['id','codigo','longitud','nombre']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(codigo__icontains=search) | Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.direccion_financiera.bancos.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar banco: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret




        else:
            return super(BancosListApi, self).render_column(row, column)

class TercerosListApi(BaseDatatableView):
    model = Contratistas
    columns = ['id', 'celular','cedula', 'nombres', 'cargo', 'banco']
    order_columns = ['id', 'celular', 'cedula', 'nombres', 'cargo', 'banco']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(cedula__icontains=search) | Q(nombres__icontains=search) | \
                Q(apellidos__icontains=search) | Q(cargo__nombre__icontains=search) | \
                Q(email__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.direccion_financiera.terceros.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar tercero: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombres)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombres)

            return ret

        elif column == 'celular':
            ret = ''
            if self.request.user.has_perm('usuarios.direccion_financiera.descuentos.ver'):
                ret = '<div class="center-align">' \
                           '<a href="pagos/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver descuentos: {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombres)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.nombres)

            return ret

        elif column == 'nombres':
            return row.fullname()


        elif column == 'cargo':
            nombre = ''
            try:
                nombre = row.cargo.nombre
            except:
                pass
            return nombre


        elif column == 'banco':
            render = ""

            if row.cuenta != '' and row.cuenta != None and row.banco != None:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{0} cuenta {1} # {2}">' \
                          '<i class="material-icons">monetization_on</i>' \
                          '</a>'.format(row.banco.nombre,row.tipo_cuenta,row.cuenta)

            if row.celular != None and row.celular != '':
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Celular: {0}">' \
                          '<i class="material-icons">phone_android</i>' \
                          '</a>'.format(row.celular)

            if row.email != None and row.email != '':
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Email: {0}">' \
                          '<i class="material-icons">email</i>' \
                          '</a>'.format(row.email)

            if row.birthday != None and row.birthday != '':
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Fecha de nacimiento: {0}">' \
                          '<i class="material-icons">cake</i>' \
                          '</a>'.format(row.birthday)

            return '<div class="center-align">' + render + '</div>'


        else:
            return super(TercerosListApi, self).render_column(row, column)

class TerceroPagosListApi(BaseDatatableView):
    model = Pagos
    columns = ['reporte', 'creation', 'valor', 'estado', 'id','observacion']
    order_columns = ['reporte', 'creation', 'valor', 'estado', 'id','observacion']

    def get_initial_queryset(self):
        return self.model.objects.filter(tercero__id = self.kwargs['pk'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(observacion__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'reporte':
            return '<div class="center-align">' \
                        '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="Consecutivo: {0}">' \
                            '<p style="font-weight:bold;">{0}</p>' \
                        '</a>' \
                   '</div>'.format(row.reporte.consecutivo.id)

        elif column == 'creation':
            return row.pretty_creation_datetime()

        elif column == 'valor':
            render = '<span>{0}</span>'.format(row.pretty_print_valor())

            if row.reporte.servicio.descontable:
                render += '<span style="margin-left:10px;"><a class="tooltipped edit-table" data-position="left" data-delay="50" data-html="true" data-tooltip="{1}">' \
                          '<i style="font-size:24px;" class="material-icons">donut_small</i>' \
                          '</a></span>'.format(row.id, row.get_amortizacion_html())

            return render

        elif column == 'id':
            return row.descuentos_html()

        elif column == 'observacion':
            render = ""

            if row.tercero.cuenta != '' and row.tercero.cuenta != None and row.tercero.banco != None:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{0} cuenta {1} # {2}">' \
                          '<i class="material-icons">monetization_on</i>' \
                          '</a>'.format(row.tercero.banco.nombre,row.tercero.tipo_cuenta,row.tercero.cuenta)

            if row.usuario_creacion != None:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Usuario: {0}">' \
                          '<i class="material-icons">account_circle</i>' \
                          '</a>'.format(row.usuario_creacion.get_full_name_string())


            if row.observacion != None:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Observacion: {0}">' \
                          '<i class="material-icons">textsms</i>' \
                          '</a>'.format(row.observacion)


            return '<div class="center-align">' + render + '</div>'


        else:
            return super(TerceroPagosListApi, self).render_column(row, column)

class ReportesListApi(BaseDatatableView):
    model = Reportes
    columns = ['consecutivo', 'usuario_actualizacion','usuario_creacion', 'efectivo', 'proyecto','creation', 'nombre',
               'plano', 'valor', 'estado', 'servicio']

    order_columns = ['consecutivo', 'usuario_actualizacion','usuario_creacion', 'efectivo','proyecto','creation', 'nombre',
               'plano', 'valor', 'estado', 'servicio']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:

            pagos_q = Q(tercero__nombres__icontains=search) | Q(tercero__apellidos__icontains=search) | Q(tercero__cedula__icontains=search)

            ids = Pagos.objects.filter(pagos_q).values_list('reporte__id',flat=True)

            q = Q(id__icontains=search) | Q(nombre__icontains=search) | \
                Q(id__in = ids)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'consecutivo':
            ret = ''

            observacion = ''

            if row.observacion != None and row.observacion != '':

                observacion = '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{0}"><i class="material-icons">announcement</i></a>'.format(row.observacion)

            if self.request.user.has_perm('usuarios.direccion_financiera.reportes.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar reporte: {1}">' \
                                '<p style="font-weight:bold;">{2}</p>' \
                           '</a>' \
                           '{3}' \
                      '</div>'.format(row.id,row.nombre,row.consecutivo.id,observacion)

            else:
                ret = '<div class="center-align">' \
                           '<p style="font-weight:bold;">{0}</p>' \
                       '</div>'.format(row.consecutivo.id)

            return ret

        elif column == 'nombre':
            if row.servicio.descontable:
                return '<span class="new badge" data-badge-caption="Descontable"></span>{0}'.format(row.nombre)
            else:
                return row.nombre


        elif column == 'usuario_actualizacion':

            cantidad = Pagos.objects.filter(reporte=row.id).count()

            if self.request.user.has_perm('usuarios.direccion_financiera.reportes.editar'):
                ret = '<div class="center-align">' \
                      '<a href="pagos/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver {1} pago(s): {2}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, cantidad, row.nombre)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id, row.nombre)

            return ret

        elif column == 'usuario_creacion':
            return row.usuario_actualizacion.first_name



        elif column == 'efectivo':

            if row.efectivo:
                tipo = "Efectivo"

            else:
                tipo = "Bancarizado"

            return tipo


        elif column == 'creation':
            return row.pretty_creation_datetime()



        elif column == 'proyecto':
            return row.proyecto.nombre



        elif column == 'plano':

            url_respaldo = row.url_respaldo()
            url_firma = row.url_firma()
            url_file_banco = row.url_file_banco()

            ret = '<div class="center-align">'

            if url_respaldo != None:
                ret += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Archivo de respaldo: {1}">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                       '</a>'.format(url_respaldo, row.nombre)

            if url_firma != None:
                ret += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Formato interno firmado: {1}">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                       '</a>'.format(url_firma, row.nombre)

            if url_file_banco != None:
                ret += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Archivo del banco: {1}">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                       '</a>'.format(url_file_banco, row.nombre)

            ret += '</div>'

            return ret

        elif column == 'valor':
            return row.pretty_print_valor_descuentos()


        elif column == 'servicio':
            ret = ''
            if self.request.user.has_perm('usuarios.direccion_financiera.reportes.eliminar') and row.estado == "Carga de pagos":
                ret = '<div class="center-align">' \
                           '<a href="eliminar/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar reporte: {1}">' \
                                '<i class="material-icons">delete</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">delete</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret


        else:
            return super(ReportesListApi, self).render_column(row, column)

class PagosListApi(BaseDatatableView):
    model = Pagos
    columns = ['id', 'usuario_creacion', 'creation', 'tercero', 'usuario_actualizacion', 'update_datetime', 'valor', 'estado', 'reporte']
    order_columns = ['id', 'usuario_creacion', 'creation', 'tercero', 'usuario_actualizacion', 'update_datetime', 'valor', 'estado', 'reporte']


    def get_initial_queryset(self):

        self.reporte = Reportes.objects.get(id = self.kwargs['pk'])

        return self.model.objects.filter(reporte__id = self.kwargs['pk'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(tercero__cedula__icontains=search) | Q(tercero__nombres__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.direccion_financiera.reportes.editar') and row.estado == "Pago creado":
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar pago: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.observacion)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.observacion)

            return ret

        elif column == 'usuario_creacion':
            return row.usuario_actualizacion.first_name


        elif column == 'creation':
            return row.chart_creation_datetime()

        elif column == 'tercero':
            return row.tercero.fullname()

        elif column == 'usuario_actualizacion':
            return row.tercero.cedula

        elif column == 'update_datetime':

            descuentos = Descuentos.objects.filter(pago__id = row.id)
            amortizaciones = Amortizaciones.objects.filter(pago_descontado__id = row.id)
            render = ""


            if not self.reporte.efectivo:

                if row.tercero.cuenta != '' and row.tercero.cuenta != None and row.tercero.banco != None:
                    render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{0} cuenta {1} # {2}">' \
                              '<i class="material-icons">monetization_on</i>' \
                              '</a>'.format(row.tercero.banco.nombre,row.tercero.tipo_cuenta,row.tercero.cuenta)

            if row.notificado:
                render += '<a class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Pago notificado a {0}">' \
                          '<i style="font-size:24px;" class="material-icons">check_circle</i>' \
                          '</a>'.format(row.tercero.email)

            if descuentos.count() > 0:

                render += '<a class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Descuentos: {0}">' \
                          '<i style="font-size:24px;" class="material-icons">remove_circle</i>' \
                          '</a>'.format(row.pretty_print_valor_solo_descuentos())

            if amortizaciones.count() > 0:

                render += '<a class="tooltipped edit-table" data-position="top" data-delay="50" data-html="true" data-tooltip="{0}">' \
                          '<i style="font-size:24px;" class="material-icons">donut_small</i>' \
                          '</a>'.format(row.pretty_print_valor_solo_amortizaciones())


            if row.reporte.servicio.descontable:
                if row.estado == 'Pago creado':
                    render += '<a class="tooltipped edit-table" data-position="left" data-delay="50" data-html="true" data-tooltip="{0}">' \
                              '<i style="font-size:24px;" class="material-icons">donut_small</i>' \
                              '</a>'.format(row.get_amortizacion_html())
                else:
                    render += '<a href="amortizaciones/{0}/" class="tooltipped edit-table" data-position="left" data-delay="50" data-html="true" data-tooltip="{1}">' \
                              '<i style="font-size:24px;" class="material-icons">donut_small</i>' \
                              '</a>'.format(row.id,row.get_amortizacion_html())


            return '<div class="center-align">' + render + '</div>'

        elif column == 'valor':
            return row.pretty_print_valor_descuentos()

        elif column == 'reporte':
            ret = ''
            if self.request.user.has_perm('usuarios.direccion_financiera.reportes.eliminar') and row.estado == "Pago creado":
                ret = '<div class="center-align">' \
                           '<a href="eliminar/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar pago: {1}">' \
                                '<i class="material-icons">delete</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.tercero.nombres)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">delete</i>' \
                       '</div>'.format(row.id,row.tercero.nombres)

            return ret


        else:
            return super(PagosListApi, self).render_column(row, column)



class AmortizacionesPagosApi(BaseDatatableView):
    model = Amortizaciones
    columns = ['consecutivo','valor','estado','fecha_descontado']
    order_columns = ['consecutivo','valor','estado','fecha_descontado']


    def get_initial_queryset(self):
        return self.model.objects.filter(pago__id = self.kwargs['pk_pago']).order_by('consecutivo')

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(consecutivo__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'consecutivo':
            ret = ''
            if self.request.user.has_perm('usuarios.direccion_financiera.reportes.editar') and not row.disabled and row.estado == 'Pendiente':
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar amortización #{1}">' \
                                '<b># {1}</b>' \
                           '</a>' \
                       '</div>'.format(row.id,row.consecutivo)

            else:
                ret = '<div class="center-align">' \
                           '<b># {1}</b>' \
                       '</div>'.format(row.id,row.consecutivo)

            return ret

        elif column == 'valor':
            return row.pretty_print_valor()

        elif column == 'estado':
            return '{0}'.format(row.get_descripcion_no_id())

        elif column == 'fecha_descontado':
            return row.pretty_update_datetime_datetime()


        else:
            return super(AmortizacionesPagosApi, self).render_column(row, column)



class TercerosListApiJson(APIView):
    """
    """

    def get(self, request, format=None):
        lista = []
        diccionario = {}
        name = request.query_params.get('name')
        pago_query = request.query_params.get('pago')
        reporte_id = request.query_params.get('reporte')

        reporte = Reportes.objects.get(id = reporte_id)

        if name != None:

            q = Q(nombres__icontains = name) | Q(apellidos__icontains = name) | Q(cedula__icontains = name)


            if reporte.efectivo:
                filtro = Contratistas.objects.all()
            else:
                filtro = Contratistas.objects.exclude(banco=None)


            for contratista in filtro.filter(q).exclude(cargo = None):
                lista.append({
                    'name': contratista.fullname() + " - " +str(contratista.cedula)
                })

                diccionario[str(contratista.cedula)] = {
                    'id': str(contratista.id),
                    'tipo_cuenta': contratista.tipo_cuenta,
                    'banco': contratista.get_banco_name(),
                    'cuenta': contratista.cuenta,
                    'descuentos': {}
                }

                for amortizacion in Amortizaciones.objects.filter(pago__tercero__cedula = contratista.cedula).order_by('consecutivo'):

                    if not amortizacion.get_pago_completo():
                        id_pago = str(amortizacion.pago.id)

                        if id_pago not in diccionario[str(contratista.cedula)]['descuentos'].keys():
                            ultimo_descuento = amortizacion.pago.get_fecha_ultimo_descuento()
                            diccionario[str(contratista.cedula)]['descuentos'][id_pago] = {
                                'amortizaciones' : [],
                                'pago': {
                                    'id': str(amortizacion.pago.id),
                                    'reporte': str(amortizacion.pago.reporte.consecutivo),
                                    'cantidad_amortizaciones_pendientes': amortizacion.pago.get_cantidad_amortizaciones_pendientes(),
                                    'fecha_ultimo_descuento': ultimo_descuento if ultimo_descuento != '' else 'No se ha aplicado ningún descuento',
                                    'cuotas': amortizacion.pago.cuotas,
                                    'valor_total': '${:20,.2f}'.format(amortizacion.pago.valor.amount)
                                }
                            }

                        diccionario[str(contratista.cedula)]['descuentos'][id_pago]['amortizaciones'].append({
                            'id': str(amortizacion.id),
                            'id_pago': str(amortizacion.pago.id),
                            'consecutivo': amortizacion.consecutivo,
                            'valor': '${:20,.2f}'.format(amortizacion.valor.amount),
                            'estado': amortizacion.estado,
                            'pago_descontado': amortizacion.get_dict_pago_descontado(),
                            'fecha_descontado': amortizacion.pretty_update_datetime_datetime(),
                            'checked': amortizacion.get_checked(pago_query),
                            'disabled': amortizacion.get_disabled(pago_query),
                            'descripcion': amortizacion.get_descripcion(pago_query)
                        })


        return Response({'lista':lista,'diccionario':diccionario},status=status.HTTP_200_OK)

class PagoApiJson(APIView):
    """
    """

    def get(self, request, pk, format=None):

        pago = Pagos.objects.get(id = pk)
        diccionario = {str(pago.tercero.cedula):{'descuentos':{}}}

        for amortizacion in Amortizaciones.objects.filter(pago__tercero__cedula=pago.tercero.cedula).order_by(
                'consecutivo'):
            if not amortizacion.get_pago_completo():
                id_pago = str(amortizacion.pago.id)

                if id_pago not in diccionario[str(pago.tercero.cedula)]['descuentos'].keys():
                    ultimo_descuento = amortizacion.pago.get_fecha_ultimo_descuento()
                    diccionario[str(pago.tercero.cedula)]['descuentos'][id_pago] = {
                        'amortizaciones': [],
                        'pago': {
                            'id': str(amortizacion.pago.id),
                            'reporte': str(amortizacion.pago.reporte.consecutivo),
                            'cantidad_amortizaciones_pendientes': amortizacion.pago.get_cantidad_amortizaciones_pendientes(),
                            'fecha_ultimo_descuento': ultimo_descuento if ultimo_descuento != '' else 'No se ha aplicado ningún descuento',
                            'cuotas': amortizacion.pago.cuotas,
                            'valor_total': '${:20,.2f}'.format(amortizacion.pago.valor.amount)
                        }
                    }

                diccionario[str(pago.tercero.cedula)]['descuentos'][id_pago]['amortizaciones'].append({
                    'id': str(amortizacion.id),
                    'id_pago': str(amortizacion.pago.id),
                    'consecutivo': amortizacion.consecutivo,
                    'valor': '${:20,.2f}'.format(amortizacion.valor.amount),
                    'estado': amortizacion.estado,
                    'pago_descontado': amortizacion.get_dict_pago_descontado(),
                    'fecha_descontado': amortizacion.pretty_update_datetime_datetime(),
                    'checked': amortizacion.get_checked(pago.id),
                    'disabled': amortizacion.get_disabled(pago.id),
                    'descripcion': amortizacion.get_descripcion(pago.id)
                })


        return Response(diccionario,status=status.HTTP_200_OK)

class PagosDinamicaAPI(APIView):
    """
    """

    def get(self, request, pk, format=None):

        year = request.query_params.get('year')
        meses = request.query_params.get('meses')
        estado = request.query_params.get('estado')
        informacion = request.query_params.get('informacion')

        labels = []
        datasets = []
        label = ''

        pagos = Pagos.objects.filter(tercero__id = pk , creation__year=year).order_by('-creation')

        if estado == '1':
            pagos = pagos.filter(estado = 'Pago creado')
        if estado == '2':
            pagos = pagos.filter(estado='Reportado')
        if estado == '3':
            pagos = pagos.filter(estado='En pagaduria')
        if estado == '4':
            pagos = pagos.filter(estado='Pago exitoso')
        if estado == '5':
            pagos = pagos.filter(estado='Pago rechazado')
        if estado == '6':
            pagos = pagos.filter(estado='Enviado a otro banco')

        if pagos.count() > 0:
            if meses != '0':
                pagos = pagos.filter(creation__month = meses).order_by('-creation')


            if informacion == '0':
                label = 'Pagos y descuentos'
                datasets = [
                    {
                        'label': 'Pagos',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Descuentos',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for pago in pagos:
                    labels.append(pago.chart_creation_datetime())
                    datasets[0]['data'].append(pago.valor.amount.__float__() - pago.descuentos_chart())
                    datasets[1]['data'].append(pago.descuentos_chart())

            elif informacion == '1':
                label = 'Solo pagos'
                datasets = [
                    {
                        'label': 'Pagos',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for pago in pagos:
                    labels.append(pago.chart_creation_datetime())
                    datasets[0]['data'].append(pago.valor.amount.__float__() - pago.descuentos_chart())

            elif informacion == '2':
                label = 'Solo descuentos'
                datasets = [
                    {
                        'label': 'Descuentos',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for pago in pagos:
                    labels.append(pago.chart_creation_datetime())
                    datasets[0]['data'].append(pago.descuentos_chart())


        response = {
            'data':{
                'labels': labels,
                'datasets': datasets
            },
            'options':{
                'title': {
                    'display': True,
                    'text': label
                }
            }
        }

        return Response(response,status=status.HTTP_200_OK)

class ConsultaPagosListApi(BaseDatatableView):
    model = Pagos
    columns = ['id','creation', 'usuario_creacion', 'update_datetime', 'estado', 'valor', 'reporte','observacion']
    order_columns = ['id','creation', 'usuario_creacion', 'update_datetime', 'estado', 'valor', 'reporte','observacion']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(tercero__cedula__icontains=search) | Q(tercero__nombres__icontains=search)
            qs = qs.filter(q)
        return qs


    def get_initial_queryset(self):
        return self.model.objects.filter(publico = True)


    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.direccion_financiera.consulta_pagos.ver'):
                ret = '<div class="center-align">' \
                      '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver todos los pagos de: {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.tercero.id, row.tercero.fullname())

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id, row.row.tercero.fullname())

            return ret

        elif column == 'creation':
            return row.tercero.fullname()


        elif column == 'reporte':

            url_respaldo = row.reporte.url_respaldo()
            url_firma = row.reporte.url_firma()
            url_file_banco = row.reporte.url_file_banco()

            ret = '<div class="center-align">'

            if url_firma != None:
                ret += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Formato interno firmado: {1}">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                       '</a>'.format(url_firma, row.reporte.nombre)

            if url_file_banco != None:
                ret += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Archivo del banco: {1}">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                       '</a>'.format(url_file_banco, row.reporte.nombre)

            return '<div class="center-align">' + ret + '</div>'


        elif column == 'usuario_creacion':
            return row.tercero.cedula


        elif column == 'update_datetime':
            return row.pretty_update_datetime_datetime()


        elif column == 'valor':
            return row.pretty_print_valor_descuentos()


        elif column == 'observacion':

            descuentos = Descuentos.objects.filter(pago__id=row.id)
            render = ""

            if row.tercero.cuenta != '' and row.tercero.cuenta != None and row.tercero.banco != None:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Banco: {0} cuenta {1} # {2}">' \
                          '<i class="material-icons">monetization_on</i>' \
                          '</a>'.format(row.tercero.banco.nombre,row.tercero.tipo_cuenta,row.tercero.cuenta)

            if row.observacion != '':

                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Observación: {0}">' \
                              '<i class="material-icons">message</i>' \
                              '</a>'.format(row.observacion)

            if row.usuario_actualizacion != None:

                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Usuario: {0} - {1}">' \
                              '<i class="material-icons">account_circle</i>' \
                              '</a>'.format(row.usuario_actualizacion.get_full_name_string(),row.usuario_actualizacion.email)

            if row.notificado:
                render += '<a class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Pago notificado a {0}">' \
                          '<i style="font-size:24px;" class="material-icons">check_circle</i>' \
                          '</a>'.format(row.tercero.email)

            if descuentos.count() > 0:

                render += '<a class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Descuento(s) de {0}">' \
                          '<i style="font-size:24px;" class="material-icons">remove_circle</i>' \
                          '</a>'.format(row.solo_descuentos_tooltip())

            return '<div class="center-align">' + render + '</div>'

        else:
            return super(ConsultaPagosListApi, self).render_column(row, column)

class SolicitudesDesplazamientoListApi(BaseDatatableView):
    model = models_desplazamiento.Solicitudes
    columns = ['id','consecutivo','usuario_creacion','creation','valor','nombre','file','estado']
    order_columns = ['id','consecutivo','usuario_creacion','creation','valor','nombre','file','estado']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(consecutivo__icontains=search) | Q(nombre__icontains=search) | Q(estado__icontains=search) | \
                Q(usuario_creacion__first_name__icontains=search) | Q(usuario_creacion__last_name__icontains=search) | \
                Q(usuario_creacion__cedula__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.direccion_financiera.solicitudes_desplazamiento.ver'):
                ret = '<div class="center-align">' \
                      '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver desplazamientos de {1}">' \
                      '<i class="material-icons">edit</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">edit</i>' \
                      '</div>'.format(row.id, row.nombre)

            return ret

        elif column == 'consecutivo':
            return '<div class="center-align"><b>' + str(row.consecutivo) + '</b></div>'

        elif column == 'usuario_creacion':
            return row.get_contratista()


        elif column == 'creation':
            return row.pretty_creation_datetime()

        elif column == 'valor':
            return '<div class="center-align"><b>' + row.pretty_print_valor() + '</b></div>'

        elif column == 'nombre':
            return '<div class="center-align"><b>' + str(row.get_cantidad_desplazamientos()) + '</b></div>'

        elif column == 'file':
            render = ""

            if row.url_file() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Legalización reintegro de transporte">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                          '</a>'.format(row.url_file(), row.nombre)

            if row.url_file2() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Soporte legalización firmado">' \
                          '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                          '</a>'.format(row.url_file2(), row.nombre)

            return '<div class="center-align">' + render + '</div>'



        elif column == 'estado':
            render = ""

            if row.estado != '':
                render += '<a href="{0}/estado" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Actualizado el {2}">' \
                          '{1}' \
                          '</a>'.format(row.id, row.estado, row.pretty_actualizacion_datetime())

            return '<div class="center-align"><b>' + render + '</b></div>'

        else:
            return super(SolicitudesDesplazamientoListApi, self).render_column(row, column)

class DesplazamientosListApi(BaseDatatableView):
    model = models_desplazamiento.Desplazamiento
    columns = ['id','valor_original','creation','origen','destino','fecha','tipo_transporte','estado','solicitud']
    order_columns = ['id','valor_original','creation','origen','destino','fecha','tipo_transporte','estado','solicitud']


    def get_initial_queryset(self):
        return self.model.objects.filter(solicitud = self.kwargs['pk'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(origen__icontains=search) | Q(destino__icontains=search) | Q(estado__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':

            ret = ''
            if self.request.user.has_perm('usuarios.direccion_financiera.solicitudes_desplazamiento.editar'):
                if row.estado == None or row.estado == 'Verificado':
                    ret = '<div class="center-align">' \
                          '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar desplazamiento">' \
                          '<b>{1}</b>' \
                          '</a>' \
                          '</div>'.format(row.id, row.pretty_print_valor())
                else:
                    ret = '<div class="center-align">' \
                          '<p>{1}</p>' \
                          '</div>'.format(row.id, row.pretty_print_valor())
            else:
                ret = '<div class="center-align">' \
                      '<p>{1}</p>' \
                      '</div>'.format(row.id, row.pretty_print_valor())

            return ret

        elif column == 'creation':
            return row.pretty_creation_datetime()



        elif column == 'valor_original':
            return '<div class="center-align"><b>' + row.pretty_print_valor_original() + '</b></div>'


        elif column == 'solicitud':
            ret = ''
            if self.request.user.has_perm('usuarios.direccion_financiera.solicitudes_desplazamiento.eliminar'):
                if row.estado == None or row.estado == 'Verificado':
                    ret = '<div class="center-align">' \
                               '<a href="eliminar/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar desplazamiento">' \
                                    '<i class="material-icons">delete</i>' \
                               '</a>' \
                           '</div>'.format(row.id,row.pretty_print_valor())
                else:
                    ret = '<div class="center-align">' \
                          '<p>{1}</p>' \
                          '</div>'.format(row.id, row.pretty_print_valor())

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">delete</i>' \
                       '</div>'.format(row.id,row.pretty_print_valor())

            return ret


        else:
            return super(DesplazamientosListApi, self).render_column(row, column)