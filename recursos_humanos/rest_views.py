from django_datatables_view.base_datatable_view import BaseDatatableView
from recursos_humanos.models import Contratistas, Contratos, Soportes, GruposSoportes, SoportesContratos, Certificaciones, Hv, TrazabilidadHv
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import urllib.request
import json
import os
from rest_framework.permissions import AllowAny
from dal import autocomplete

class ContratistasListApi(BaseDatatableView):
    model = Contratistas
    columns = ['id','creation','cedula','nombres','cargo','banco']
    order_columns = ['id','creation','cedula','nombres','cargo','banco']


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
            if self.request.user.has_perm('usuarios.recursos_humanos.contratistas.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar contratista: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombres)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
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


        elif column == 'creation':

            if self.request.user.has_perm('usuarios.recursos_humanos.contratos.ver'):
                ret = '<div class="center-align">' \
                      '<a href="contratos/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver contratos: {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombres)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id, row.nombres)

            return ret




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

            if row.usuario_asociado != None:
                render += '<a class="tooltipped link-sec" data-position="left" data-delay="50" data-tooltip="Usuario: {0}">' \
                            '<i class="material-icons">account_circle</i>' \
                          '</a>'.format(row.usuario_asociado.email)

            return '<div class="center-align">' + render + '</div>'


        else:
            return super(ContratistasListApi, self).render_column(row, column)

class HvListApi(BaseDatatableView):
    model = Hv
    columns = ['id','region','contratista','observacion','consecutivo_cargo','cargo','creation','file','excel','estado']
    order_columns = ['id','region','contratista','observacion','consecutivo_cargo','cargo','creation','file','excel','estado']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(contratista__cedula__icontains=search) | Q(contratista__nombres__icontains=search) \
                | Q(contratista__apellidos__icontains=search) | Q(cargo__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.recursos_humanos.hv.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar hoja de vida: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,str(row.contratista))

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,str(row.contratista))

            return ret

        elif column == 'estado':
            if self.request.user.has_perm('usuarios.recursos_humanos.hv_cpe.editar'):
                return '<a href="{2}/estado/" class="tooltipped" data-position="top" data-delay="50" data-tooltip="Actualizar estado del contratista, Envio {1}">' \
                       '<b>{0}</b>' \
                       '</a>'.format(row.estado,str(row.envio),str(row.id))
            else:
                return '<b>{0}</b>'.format(row.estado,str(row.envio),str(row.id))

        elif column == 'creation':
            return row.pretty_creation_datetime()

        elif column == 'contratista':
            return str(row.contratista)

        elif column == 'observacion':
            return 'Envio {0}'.format(row.envio)

        elif column == 'consecutivo_cargo':
            return '<div class="center-align"><b>{0}</b></div>'.format(str(row.consecutivo_cargo))

        elif column == 'file':

            try:
                url = row.file.url
            except:
                return ''
            else:
                return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Hoja de vida"><i class="material-icons" style="font-size: 2rem;">insert_drive_file</i></a></div>'.format(url)


        elif column == 'excel':

            try:
                url = row.excel.url
            except:
                return ''
            else:
                return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Hoja de vida"><i class="material-icons" style="font-size: 2rem;">insert_drive_file</i></a></div>'.format(url)



        else:
            return super(HvListApi, self).render_column(row, column)

class ContratosListApi(BaseDatatableView):
    model = Contratos
    columns = ['id','liquidado','nombre','inicio','fin','valor','file','estado','fecha_legalizacion']
    order_columns = ['id','liquidado','nombre','inicio','fin','valor','file','estado','fecha_legalizacion']

    def get_initial_queryset(self):
        if self.request.user.is_superuser:
            return self.model.objects.filter(contratista = Contratistas.objects.get(id = self.kwargs['pk']))
        else:
            return self.model.objects.filter(contratista = Contratistas.objects.get(id = self.kwargs['pk']), visible = True)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            if self.request.user.has_perm('usuarios.recursos_humanos.contratos.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar contratista: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'liquidado':

            if self.request.user.has_perm('usuarios.recursos_humanos.soportes.ver'):
                ret = '<div class="center-align">' \
                      '<a href="soportes/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver soportes del contrato {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id, row.nombre)

            return ret

        elif column == 'valor':
            return row.pretty_print_valor()


        elif column == 'file':
            render = ""

            if row.url_file() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Minuta contrato {1}">' \
                                '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                          '</a>'.format(row.url_file(),row.nombre)

            if row.url_soporte_liquidacion() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Liquidación contrato {1}">' \
                            '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a>'.format(row.url_soporte_liquidacion(),row.nombre)

            if row.url_soporte_renuncia() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Soporte de renuncia contrato {1}">' \
                                '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                            '</a>'.format(row.url_soporte_renuncia(),row.nombre)


            return '<div class="center-align">' + render + '</div>'


        elif column == 'fecha_legalizacion':
            render = ""

            if row.fecha_legalizacion != None:
                render += '<a class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Contrato legalizado el {0}">' \
                                '<i class="material-icons" style="font-size: 2rem;">check_circle</i>' \
                          '</a>'.format(row.fecha_legalizacion)

            if not row.visible:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Contrato privado">' \
                                '<i class="material-icons" style="font-size: 2rem;">announcement</i>' \
                          '</a>'.format(row.fecha_legalizacion)


            return '<div class="center-align">' + render + '</div>'


        else:
            return super(ContratosListApi, self).render_column(row, column)

class ContratosEstadoListApi(BaseDatatableView):
    model = Contratos
    columns = ['id','liquidado','creation','contratista','nombre','valor','file','estado','fecha_legalizacion']
    order_columns = ['id','liquidado','creation','contratista','nombre','valor','file','estado','fecha_legalizacion']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(contratista__nombres__icontains=search) | \
                Q(contratista__apellidos__icontains=search) | Q(contratista__cedula__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):
        if column == 'id':
            if self.request.user.has_perm('usuarios.recursos_humanos.contratos.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar contratista: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'liquidado':

            if self.request.user.has_perm('usuarios.recursos_humanos.soportes.ver'):
                ret = '<div class="center-align">' \
                      '<a href="soportes/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver soportes del contrato {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id, row.nombre)

            return ret

        elif column == 'creation':
            return row.pretty_creation_datetime()

        elif column == 'contratista':
            return row.contratista.get_full_name_cedula()

        elif column == 'valor':
            return row.pretty_print_valor()

        elif column == 'estado':
            return '<div class="center-align"><b>' + str(row.cantidad_soportes()) + '</b></div>'


        elif column == 'file':
            render = ""

            if row.url_file() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Minuta contrato {1}">' \
                                '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                          '</a>'.format(row.url_file(),row.nombre)

            if row.url_soporte_liquidacion() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Liquidación contrato {1}">' \
                            '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a>'.format(row.url_soporte_liquidacion(),row.nombre)

            if row.url_soporte_renuncia() != None:
                render += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Soporte de renuncia contrato {1}">' \
                                '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                            '</a>'.format(row.url_soporte_renuncia(),row.nombre)


            return '<div class="center-align">' + render + '</div>'

        elif column == 'fecha_legalizacion':
            render = ""

            if row.fecha_legalizacion != None:
                render += '<a class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Contrato legalizado el {0}">' \
                                '<i class="material-icons" style="font-size: 2rem;">check_circle</i>' \
                          '</a>'.format(row.fecha_legalizacion)


            return '<div class="center-align">' + render + '</div>'

        else:
            return super(ContratosEstadoListApi, self).render_column(row, column)

class SoportesListApi(BaseDatatableView):
    model = Soportes
    columns = ['id','numero','nombre','descripcion','requerido']
    order_columns = ['id','numero','nombre','descripcion','requerido']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(descripcion__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perm('usuarios.recursos_humanos.soportes.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar soporte: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'numero':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.numero)


        elif column == 'requerido':

            if row.requerido:
                return 'Requerido'
            else:
                return 'Opcional'

        else:
            return super(SoportesListApi, self).render_column(row, column)

class GrupoSoportesListApi(BaseDatatableView):
    model = GruposSoportes
    columns = ['id','nombre','soportes']
    order_columns = ['id','nombre','soportes']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perm('usuarios.recursos_humanos.soportes.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar grupo: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'soportes':
            ret = ''

            for soporte in row.soportes.all().order_by('numero'):
                ret += '<p>{0}. {1}</p>'.format(soporte.numero,soporte.nombre)

            return ret

        else:
            return super(GrupoSoportesListApi, self).render_column(row, column)

class SoportesContratoListApi(BaseDatatableView):
    model = SoportesContratos
    columns = ['id','numero','codigo','soporte','contrato','file','estado','observacion']
    order_columns = ['id','numero','codigo','soporte','contrato','file','estado','observacion']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(soporte__nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def get_initial_queryset(self):
        return self.model.objects.filter(contrato__id = self.kwargs['pk_soporte'])


    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perm('usuarios.recursos_humanos.soportes.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar soportes: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.soporte.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
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

class CertificacionesListApi(BaseDatatableView):
    model = Certificaciones
    columns = ['id','creation','update','pdf','html_template','usuario_actualizacion']
    order_columns = ['id','creation','update','pdf','html_template','usuario_actualizacion']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(contratista__cedula__icontains=search) | Q(contratista__nombres__icontains=search) | \
                Q(contratista__apellidos__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.recursos_humanos.certificaciones.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar certificación: {1}">' \
                                '<p><b>{0}</b></p>' \
                           '</a>' \
                       '</div>'.format(row.id,row.contratista.fullname())

            else:
                ret = '<div class="center-align">' \
                           '<p>{0}</p>' \
                       '</div>'.format(row.id,row.contratista.fullname())

            return ret

        elif column == 'creation':
            return row.contratista.fullname()

        elif column == 'update':
            return row.contratista.cedula

        elif column == 'pdf':
            if row.url_pdf() == None:
                return ''
            else:
                return '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Certificación: {1}">' \
                                '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                       '</a>' \
                       '</div>'.format(row.url_pdf(), str(row.codigo))

        elif column == 'html_template':
            return '<div class="center-align">' \
                        '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Url certificación: {1}">' \
                            '<i class="material-icons" style="font-size: 2rem;">link</i>' \
                   '</a>' \
                   '</div>'.format('/certificaciones/'+str(row.codigo), str(row.codigo))

        elif column == 'usuario_actualizacion':
            render = ""

            if row.usuario_actualizacion != None:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Usuario: {0}">' \
                          '<i class="material-icons">account_circle</i>' \
                          '</a>'.format(row.usuario_actualizacion.get_full_name_string())

            if row.update != None:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Fecha de actualización: {0}">' \
                          '<i class="material-icons">av_timer</i>' \
                          '</a>'.format(row.pretty_update_datetime())

            return '<div class="center-align">' + render + '</div>'

        else:
            return super(CertificacionesListApi, self).render_column(row, column)

class CertificacionesCedulaApi(APIView):
    permission_classes = (AllowAny,)
    """
    """

    def get(self, request, format=None):
        certificaciones_list = []
        cedula = request.query_params.get('cedula')
        captcha = request.query_params.get('captcha')
        contratista_name = ''

        secret = os.getenv('SICAN_SECRET_CAPTCHA')

        req = json.loads(urllib.request.urlopen("https://www.google.com/recaptcha/api/siteverify?secret={0}&response={1}".format(secret,captcha)).read())

        if req['success']:
            if cedula != None:

                try:
                    contratista = Contratistas.objects.get(cedula=cedula)
                except:
                    pass
                else:
                    contratista_name = contratista.fullname()
                    for certificacion in Certificaciones.objects.filter(contratista = contratista):
                        certificaciones_list.append({
                            'codigo': str(certificacion.codigo),
                            'pdf': certificacion.url_pdf(),
                            'url': '/certificaciones/' + str(certificacion.codigo),
                            'fecha': certificacion.pretty_update_datetime()
                        })

            return Response({'certificaciones':certificaciones_list,'contratista':contratista_name,'cedula':cedula},status=status.HTTP_200_OK)
        else:
            return Response({'certificaciones': certificaciones_list,'contratista':contratista_name,'cedula':cedula}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ContratistaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Contratistas.objects.none()

        qs = Contratistas.objects.all()

        if self.q:
            q = Q(nombres__icontains = self.q) | Q(apellidos__icontains = self.q) | Q(cedula__icontains = self.q)
            qs = qs.filter(q)

        return qs

class HvTrazabilidadApiJson(APIView):
    """
    """

    def get(self, request, pk,format=None):

        hv = Hv.objects.get(id = pk)


        dict = []

        for trazabilidad in TrazabilidadHv.objects.filter(hv = hv).order_by('-creation'):
            dict.append({
                'id': trazabilidad.id,
                'creacion': trazabilidad.pretty_creation_datetime(),
                'usuario': trazabilidad.usuario_creacion.get_full_name_string(),
                'observacion': trazabilidad.observacion
            })

        return Response({'data': dict},status=status.HTTP_200_OK)