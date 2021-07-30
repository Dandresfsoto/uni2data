from django_datatables_view.base_datatable_view import BaseDatatableView
from ofertas import models
from recursos_humanos import models as models_rh
from django.db.models import Q
from dal import autocomplete
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core import serializers
from usuarios.models import User, Titulos, Experiencias

class OfertasListApi(BaseDatatableView):
    model = models.Ofertas
    columns = ['id','vacantes','creation','cargo','tipo_contrato','honorarios','departamentos']
    order_columns = ['id','vacantes','creation','cargo','tipo_contrato','honorarios','departamentos']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q2 = Q(usuario__first_name__icontains=search) | Q(usuario__last_name__icontains=search) | Q(usuario__cedula__icontains=search)
            aplicaciones_ids = models.AplicacionOferta.objects.filter(q2).values_list('oferta__id',flat=True)

            q = Q(cargo__icontains=search) | Q(id__in=aplicaciones_ids)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.ofertas.seleccion.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.cargo)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.cargo)

            return ret

        elif column == 'honorarios':
            return row.pretty_print_valor()

        elif column == 'vacantes':
            ret = ''
            if self.request.user.has_perm('usuarios.ofertas.ver'):
                ret = '<div class="center-align">' \
                      '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver aplicaciones: {1}">' \
                        '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.cargo)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id, row.cargo)

            return ret

        elif column == 'creation':
            return row.pretty_creation_datetime()

        elif column == 'departamentos':
            return '<div class="center-align"><b>' + str(row.get_aplicaciones_count()) + '</b></div>'

        else:
            return super(OfertasListApi, self).render_column(row, column)

class OfertasAplicacionesListApi(BaseDatatableView):
    model = models.AplicacionOferta
    columns = ['id','aplica','oferta','creation','municipios','cualificacion_perfil','cualificacion_experiencia','cualificacion_seleccion','usuario']
    order_columns = ['id','aplica','oferta','creation','municipios','cualificacion_perfil','cualificacion_experiencia','cualificacion_seleccion','usuario']

    def get_initial_queryset(self):
        return self.model.objects.filter(oferta__id = self.kwargs['pk'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(usuario__first_name__icontains=search)| Q(usuario__last_name__icontains=search)| \
                Q(usuario__cedula__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.ofertas.seleccion.editar'):
                ret = '<div class="center-align">' \
                           '<a href="cualificar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cualificar oferta">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.cargo)

            return ret

        elif column == 'aplica':
            return row.usuario.get_full_name_string()

        elif column == 'oferta':
            return row.usuario.cedula

        elif column == 'creation':
            return row.pretty_creation_datetime()

        elif column == 'municipios':
            return row.get_municipios_string()


        elif column == 'cualificacion_perfil':
            ret = ''
            if row.cualificacion_perfil == 'Cumple con el perfil':
                ret = '<div class="center-align">' \
                           '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="Cumple con el perfil">' \
                                '<i class="material-icons green-text text-darken-2">check_circle</i>' \
                           '</a>' \
                       '</div>'

            elif row.cualificacion_perfil == 'No cumple con el perfil':
                ret = '<div class="center-align">' \
                           '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="No cumple con el perfil">' \
                                '<i class="material-icons red-text text-darken-4">cancel</i>' \
                           '</a>' \
                       '</div>'

            return ret


        elif column == 'cualificacion_experiencia':
            ret = ''
            if row.cualificacion_experiencia == 'Cumple con la experiencia':
                ret = '<div class="center-align">' \
                           '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="Cumple con la experiencia">' \
                                '<i class="material-icons green-text text-darken-2">check_circle</i>' \
                           '</a>' \
                       '</div>'

            elif row.cualificacion_experiencia == 'No cumple con la experiencia':
                ret = '<div class="center-align">' \
                           '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="No cumple con la experiencia">' \
                                '<i class="material-icons red-text text-darken-4">cancel</i>' \
                           '</a>' \
                       '</div>'

            return ret


        elif column == 'cualificacion_seleccion':
            ret = ''
            if row.cualificacion_seleccion == 'No seleccionado':
                ret = '<div class="center-align">' \
                           '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="Aplicación no seleccionada">' \
                                '<i class="material-icons green-text text-darken-2">cancel</i>' \
                           '</a>' \
                       '</div>'

            elif row.cualificacion_seleccion == 'Preseleccionado':
                ret = '<div class="center-align">' \
                           '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="Preseleccionado">' \
                                '<i class="material-icons orange-text text-darken-4">access_time</i>' \
                           '</a>' \
                       '</div>'

            elif row.cualificacion_seleccion == 'Seleccionado':
                ret = '<div class="center-align">' \
                           '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="Seleccionado">' \
                                '<i class="material-icons red-text text-darken-4">check_circle</i>' \
                           '</a>' \
                       '</div>'

            elif row.cualificacion_seleccion == 'Pendiente':
                ret = '<div class="center-align">' \
                           '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="Pendiente">' \
                                '<i class="material-icons red-text text-darken-4">hourglass_full</i>' \
                           '</a>' \
                       '</div>'

            return ret



        elif column == 'usuario':

            ret = ''

            ret += '<a href="{0}" target="_blank" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Hoja de vida">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                    '</a>'.format(row.usuario.url_hv())

            ret += '<a id="{0}" onclick="resumen(\'{0}\')" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver resumen de la aplicación">' \
                        '<i class="material-icons">pageview</i>' \
                      '</a>'.format(str(row.id))

            return '<div class="center-align">' + ret + '</div>'

        else:
            return super(OfertasAplicacionesListApi, self).render_column(row, column)

class ResumenAplicacionOferta(APIView):
    """
    """

    def get(self, request, pk,format=None):

        response = {
            'usuario': {},
            'titulos': [],
            'experiencias': [],
            'aplicacion': {}
        }
        status_response = None

        data = request.query_params

        id = data.get('id')
        aplicacion = models.AplicacionOferta.objects.get(id = id)
        usuario = aplicacion.usuario

        response['usuario'] = {
            'photo': usuario.url_photo(),
            'fullname': usuario.get_full_name_string().upper(),
            'cedula': usuario.cedula,
            'edad': usuario.calculate_age(),
            'sexo': usuario.sexo.lower(),
            'lugar_nacimiento': str(usuario.lugar_nacimiento),
            'lugar_expedicion': str(usuario.lugar_expedicion),
            'lugar_residencia': str(usuario.lugar_residencia),

            'email': usuario.email,
            'direccion': usuario.direccion,
            'celular': str(usuario.celular),
            'tipo_sangre': usuario.tipo_sangre,
            'birthday': str(usuario.birthday),

            'nivel_educacion_basica': usuario.nivel_educacion_basica,
            'grado_educacion_basica': usuario.grado_educacion_basica,
            'hv': usuario.url_hv()
        }

        response['aplicacion'] = {
            'id': str(aplicacion.id),
            'creation': aplicacion.pretty_creation_datetime(),
            'municipios': aplicacion.get_municipios_string(),
            'observacion': aplicacion.observacion
        }

        for titulo in Titulos.objects.filter(usuario = usuario).order_by('-creation'):
            response['titulos'].append({
                'modalidad': titulo.modalidad,
                'semestres': titulo.semestres,
                'graduado': titulo.graduado,
                'nombre': titulo.nombre,
                'fecha_terminacion': titulo.fecha_terminacion,
                'numero_tarjeta': titulo.numero_tarjeta,
                'fecha_expedicion': titulo.fecha_expedicion,
            })


        for experiencia in Experiencias.objects.filter(usuario = usuario).order_by('-creation'):
            response['experiencias'].append({
                'nombre_empresa': experiencia.nombre_empresa,
                'tipo_empresa': experiencia.tipo_empresa,
                'email_empresa': experiencia.email_empresa,
                'telefono_empresa': experiencia.telefono_empresa,
                'cargo': experiencia.cargo,
                'dependencia': experiencia.dependencia,
                'direccion': experiencia.direccion,
                'meses': experiencia.get_duracion_meses(),
                'fecha_ingreso': experiencia.fecha_ingreso,
                'fecha_retiro': experiencia.fecha_retiro,
                'municipio': str(experiencia.municipio)
            })


        status_response = status.HTTP_200_OK



        return Response(response,status=status_response)