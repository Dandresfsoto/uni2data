from django_datatables_view.base_datatable_view import BaseDatatableView
from formacion import models
from recursos_humanos import models as models_rh
from django.db.models import Q
from dal import autocomplete
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class RegionesListApi(BaseDatatableView):
    model = models.Regiones
    columns = ['ver','nombre','numero','cantidad_departamentos','cantidad_municipios','cantidad_sedes','color']
    order_columns = ['ver','nombre','numero','cantidad_departamentos','cantidad_municipios','cantidad_sedes','color']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(numero__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'ver':

            return '<div class="center-align">' \
                      '<a href="{0}/departamentos/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Departamentos: {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre)

        elif column == 'numero':
            return '<div class="center-align"><b>' + str(row.numero) + '</b></div>'

        elif column == 'cantidad_departamentos':
            return '<div class="center-align"><b>' + str(row.get_cantidad_departamentos()) + '</b></div>'

        elif column == 'cantidad_municipios':
            return '<div class="center-align"><b>' + str(row.get_cantidad_municipios()) + '</b></div>'

        elif column == 'cantidad_sedes':
            return '<div class="center-align"><b>' + str(row.get_cantidad_sedes()) + '</b></div>'

        elif column == 'color':
            return '<div class="center-align"><b>' + str(row.get_cantidad_formados()) + '</b></div>'


        else:
            return super(RegionesListApi, self).render_column(row, column)

class DepartamentosListApi(BaseDatatableView):
    model = models.Departamentos
    columns = ['ver','nombre','numero','cantidad_municipios','cantidad_sedes','region']
    order_columns = ['ver','nombre','numero','cantidad_municipios','cantidad_sedes','region']

    def get_initial_queryset(self):
        return self.model.objects.filter(region__id = self.kwargs['pk'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(numero__icontains=search)

            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'ver':

            return '<div class="center-align">' \
                      '<a href="{0}/municipios/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Municipios: {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre)



        elif column == 'numero':

            return '<div class="center-align"><b>' + str(row.numero) + '</b></div>'


        elif column == 'cantidad_municipios':

            return '<div class="center-align"><b>' + str(row.get_cantidad_municipios()) + '</b></div>'


        elif column == 'cantidad_sedes':

            return '<div class="center-align"><b>' + str(row.get_cantidad_sedes()) + '</b></div>'

        elif column == 'region':

            return '<div class="center-align"><b>' + str(row.get_cantidad_formados()) + '</b></div>'


        else:
            return super(DepartamentosListApi, self).render_column(row, column)

class MunicipiosListApi(BaseDatatableView):
    model = models.Municipios
    columns = ['ver','nombre','numero','cantidad_sedes','departamento','latitud']
    order_columns = ['ver','nombre','numero','cantidad_sedes','departamento','latitud']

    def get_initial_queryset(self):
        return self.model.objects.filter(departamento__id = self.kwargs['pk_departamento'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(numero__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'ver':

            return '<div class="center-align">' \
                      '<a href="{0}/sedes/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Municipios: {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre)



        elif column == 'numero':

            return '<div class="center-align"><b>' + str(row.numero) + '</b></div>'



        elif column == 'cantidad_sedes':

            return '<div class="center-align"><b>' + str(row.get_cantidad_sedes()) + '</b></div>'

        elif column == 'departamento':

            return '<div class="center-align"><b>' + str(row.get_cantidad_formados()) + '</b></div>'

        elif column == 'latitud':

            return '<div class="center-align">' \
                           '<a id="{3}" onclick="mapa({1},{2})" href="#" class="mapa-municipio tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver mapa: {0}">' \
                                '<i class="mapa-municipio material-icons">gps_fixed</i>' \
                           '</a>' \
                       '</div>'.format(row.nombre,row.latitud,row.longitud,str(row.numero))


        else:
            return super(MunicipiosListApi, self).render_column(row, column)

class SedesListApi(BaseDatatableView):
    model = models.Sedes
    columns = ['id','ver','dane_sede','nombre_sede','dane_ie','nombre_ie','municipio']
    order_columns = ['id','ver','dane_sede','nombre_sede','dane_ie','nombre_ie','municipio']

    def get_initial_queryset(self):
        return self.model.objects.filter(municipio__id = self.kwargs['pk_municipio'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(dane_sede__icontains=search) | Q(nombre_sede__icontains=search) |\
                Q(dane_ie__icontains=search) | Q(nombre_ie__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.formacion.db.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre_sede)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre_sede)

            return ret

        elif column == 'ver':

            return '<div class="center-align">' \
                      '<a href="{0}/formados/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Docentes formados: {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre_sede)

        elif column == 'municipio':

            return '<div class="center-align"><b>' + str(row.get_cantidad_formados()) + '</b></div>'


        else:
            return super(SedesListApi, self).render_column(row, column)

class FormadosListApi(BaseDatatableView):
    model = models.DocentesFormados
    columns = ['id','nombres','apellidos','cedula','vigencia','diplomado']
    order_columns = ['id','nombres','apellidos','cedula','vigencia','diplomado']

    def get_initial_queryset(self):
        return self.model.objects.filter(sede__id = self.kwargs['pk_sede'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombres__icontains=search) | Q(apellidos__icontains=search) |\
                Q(cedula__icontains=search) | Q(vigencia__icontains=search) | Q(diplomado__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.formacion.db.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombres)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombres)

            return ret


        else:
            return super(FormadosListApi, self).render_column(row, column)

class ActualizacionSedesListApi(BaseDatatableView):
    model = models.ActualizacionSedes
    columns = ['creation','usuario_creacion','nuevos','modificados','rechazados','file','result']
    order_columns = ['creation','usuario_creacion','nuevos','modificados','rechazados','file','result']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(id__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'creation':
            return row.pretty_creation_datetime()

        elif column == 'usuario_creacion':

            return row.usuario_creacion.get_full_name_string()

        elif column == 'nuevos':
            return '<div class="center-align"><b>' + str(row.nuevos) + '</b></div>'

        elif column == 'modificados':
            return '<div class="center-align"><b>' + str(row.modificados) + '</b></div>'

        elif column == 'rechazados':
            return '<div class="center-align"><b>' + str(row.rechazados) + '</b></div>'

        elif column == 'file':
            return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Formato cargado">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                    '</a></div>'.format(row.url_file())

        elif column == 'result':
            if row.url_result() != None:
                return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Resultado de la actualización">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a></div>'.format(row.url_result())
            else:
                return ''

        else:
            return super(ActualizacionSedesListApi, self).render_column(row, column)

class ActualizacionDocentesListApi(BaseDatatableView):
    model = models.ActualizacionDocentes
    columns = ['creation','usuario_creacion','nuevos','modificados','rechazados','file','result']
    order_columns = ['creation','usuario_creacion','nuevos','modificados','rechazados','file','result']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(id__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'creation':
            return row.pretty_creation_datetime()

        elif column == 'usuario_creacion':

            return row.usuario_creacion.get_full_name_string()

        elif column == 'nuevos':
            return '<div class="center-align"><b>' + str(row.nuevos) + '</b></div>'

        elif column == 'modificados':
            return '<div class="center-align"><b>' + str(row.modificados) + '</b></div>'

        elif column == 'rechazados':
            return '<div class="center-align"><b>' + str(row.rechazados) + '</b></div>'

        elif column == 'file':
            return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Formato cargado">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                    '</a></div>'.format(row.url_file())

        elif column == 'result':
            if row.url_result() != None:
                return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Resultado de la actualización">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a></div>'.format(row.url_result())
            else:
                return ''

        else:
            return super(ActualizacionDocentesListApi, self).render_column(row, column)

class DiplomadosListApi(BaseDatatableView):
    model = models.Diplomados
    columns = ['id','nombre','niveles','sesiones','actividades']
    order_columns = ['id','nombre','niveles','sesiones','actividades']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.formacion.diplomados.ver'):
                ret = '<div class="center-align">' \
                           '<a href="{0}/niveles/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver niveles del diplomado {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'niveles':
            return '<div class="center-align"><b>' + str(row.get_nivel_count()) + '</b></div>'

        elif column == 'sesiones':
            return '<div class="center-align"><b>' + str(row.get_sesiones_count()) + '</b></div>'

        elif column == 'actividades':
            return '<div class="center-align"><b>' + str(row.get_actividades_count()) + '</b></div>'


        else:
            return super(DiplomadosListApi, self).render_column(row, column)

class NivelesListApi(BaseDatatableView):
    model = models.Niveles
    columns = ['id','nombre','sesiones','actividades']
    order_columns = ['id','nombre','sesiones','actividades']

    def get_initial_queryset(self):
        return self.model.objects.filter(diplomado__id = self.kwargs['pk'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.formacion.diplomados.ver'):
                ret = '<div class="center-align">' \
                           '<a href="{0}/sesiones/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver sesiones de {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'sesiones':
            return '<div class="center-align"><b>' + str(row.get_sesiones_count()) + '</b></div>'

        elif column == 'actividades':
            return '<div class="center-align"><b>' + str(row.get_actividades_count()) + '</b></div>'


        else:
            return super(NivelesListApi, self).render_column(row, column)

class SesionesListApi(BaseDatatableView):
    model = models.Sesiones
    columns = ['id','nombre','actividades']
    order_columns = ['id','nombre','actividades']

    def get_initial_queryset(self):
        return self.model.objects.filter(nivel__id = self.kwargs['pk_nivel'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.formacion.diplomados.ver'):
                ret = '<div class="center-align">' \
                           '<a href="{0}/actividades/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades de la {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret


        elif column == 'actividades':
            return '<div class="center-align"><b>' + str(row.get_actividades_count()) + '</b></div>'


        else:
            return super(SesionesListApi, self).render_column(row, column)

class ActividadesListApi(BaseDatatableView):
    model = models.Actividades
    columns = ['numero','nombre','tipo','file']
    order_columns = ['numero','nombre','tipo','file']

    def get_initial_queryset(self):
        return self.model.objects.filter(sesion__id = self.kwargs['pk_sesion'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(numero__icontains=search) | Q(tipo__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'numero':

            return '<div class="center-align"><b>' + str(row.numero) + '</b></div>'

        elif column == 'file':
            return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Formato">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                    '</a></div>'.format(row.url_file())

        else:
            return super(ActividadesListApi, self).render_column(row, column)