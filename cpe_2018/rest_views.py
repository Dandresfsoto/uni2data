from django_datatables_view.base_datatable_view import BaseDatatableView
from cpe_2018 import models, forms
from recursos_humanos import models as models_rh
from django.db.models import Q
from dal import autocomplete
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from itertools import chain
import json

class RegionesListApi(BaseDatatableView):
    model = models.Regiones
    columns = ['ver','nombre','numero','cantidad_departamentos','cantidad_municipios','cantidad_radicados','cantidad_docentes']
    order_columns = ['ver','nombre','numero','cantidad_departamentos','cantidad_municipios','cantidad_radicados','cantidad_docentes']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.db.ver"
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            try:
                radicado = models.Radicados.objects.get(numero = search)
            except:
                q = Q(nombre__icontains=search) | Q(numero__icontains=search)
            else:
                try:
                    docente = models.Docentes.objects.get(cedula = search)
                except:
                    region_radicado = radicado.municipio.departamento.region
                    q = Q(nombre__icontains=search) | Q(numero__icontains=search) | Q(id = region_radicado.id)
                else:
                    region_docente = docente.municipio.departamento.region
                    region_radicado = radicado.municipio.departamento.region
                    q = Q(nombre__icontains=search) | Q(numero__icontains=search) | Q(id=region_docente.id) | Q(id = region_radicado.id)


            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'ver':

            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="{0}/departamentos/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Departamentos: {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre)

            else:
                ret = '<div class="center-align">' \
                        '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'

            return ret

        elif column == 'numero':
            return '<div class="center-align"><b>' + str(row.numero) + '</b></div>'

        elif column == 'cantidad_departamentos':
            return '<div class="center-align"><b>' + str(row.get_cantidad_departamentos()) + '</b></div>'

        elif column == 'cantidad_municipios':
            return '<div class="center-align"><b>' + str(row.get_cantidad_municipios()) + '</b></div>'

        elif column == 'cantidad_radicados':
            return '<div class="center-align"><b>' + str(row.get_cantidad_radicados()) + '</b></div>'

        elif column == 'cantidad_docentes':
            return '<div class="center-align"><b>' + str(row.get_cantidad_docentes()) + '</b></div>'


        else:
            return super(RegionesListApi, self).render_column(row, column)

class ActualizacionRadicadosListApi(BaseDatatableView):
    model = models.ActualizacionRadicados
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
            return super(ActualizacionRadicadosListApi, self).render_column(row, column)

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

class DepartamentosListApi(BaseDatatableView):
    model = models.Departamentos
    columns = ['ver','nombre','numero','cantidad_municipios','cantidad_radicados','cantidad_docentes']
    order_columns = ['ver','nombre','numero','cantidad_municipios','cantidad_radicados','cantidad_docentes']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.db.ver"
            ]
        }
        return self.model.objects.filter(region__id = self.kwargs['pk'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            try:
                radicado = models.Radicados.objects.get(numero = search)
            except:
                q = Q(nombre__icontains=search) | Q(numero__icontains=search)
            else:
                try:
                    docente = models.Docentes.objects.get(cedula = search)
                except:
                    departamento = radicado.municipio.departamento
                    q = Q(nombre__icontains=search) | Q(numero__icontains=search) | Q(id = departamento.id)
                else:
                    departamento_radicado = radicado.municipio.departamento
                    departamento_docente = docente.municipio.departamento
                    q = Q(nombre__icontains=search) | Q(numero__icontains=search) | Q(id=departamento_radicado.id) | Q(id=departamento_docente.id)


            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'ver':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="{0}/municipios/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Municipios: {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret


        elif column == 'nombre':

            if row.alias_simec == None:
                ret = row.nombre
            else:
                ret = '<div><a class="tooltipped" data-position="top" data-delay="50" data-tooltip="Alias SIMEC: {0}">' \
                          '<b>{1}</b>' \
                          '</a>' \
                          '</div>'.format(row.alias_simec,row.nombre)
            return ret

        elif column == 'numero':

            return '<div class="center-align"><b>' + str(row.numero) + '</b></div>'


        elif column == 'cantidad_municipios':

            return '<div class="center-align"><b>' + str(row.get_cantidad_municipios()) + '</b></div>'


        elif column == 'cantidad_radicados':

            return '<div class="center-align"><b>' + str(row.get_cantidad_radicados()) + '</b></div>'

        elif column == 'cantidad_docentes':

            return '<div class="center-align"><b>' + str(row.get_cantidad_docentes()) + '</b></div>'


        else:
            return super(DepartamentosListApi, self).render_column(row, column)

class MunicipiosListApi(BaseDatatableView):
    model = models.Municipios
    columns = ['ver','longitud','nombre','numero','cantidad_radicados','cantidad_docentes','latitud']
    order_columns = ['ver','longitud','nombre','numero','cantidad_radicados','cantidad_docentes','latitud']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.db.ver"
            ]
        }
        return self.model.objects.filter(departamento__id = self.kwargs['pk_departamento'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            try:
                radicado = models.Radicados.objects.get(numero = search)
            except:
                q = Q(nombre__icontains=search) | Q(numero__icontains=search)
            else:
                try:
                    docente = models.Docentes.objects.get(cedula = search)
                except:
                    municipio = radicado.municipio
                    q = Q(nombre__icontains=search) | Q(numero__icontains=search) | Q(id = municipio.id)
                else:
                    municipio_radicado = radicado.municipio
                    municipio_docente = docente.municipio
                    q = Q(nombre__icontains=search) | Q(numero__icontains=search) | Q(id=municipio_radicado.id) | Q(id=municipio_docente.id)


            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'ver':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="{0}/radicados/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Municipios: {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret


        elif column == 'longitud':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="{0}/docentes/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Docentes: {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.nombre)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id, row.nombre)

            return ret


        elif column == 'nombre':

            if row.alias_simec == None:
                ret = row.nombre
            else:
                ret = '<div><a class="tooltipped" data-position="top" data-delay="50" data-tooltip="Alias SIMEC: {0}">' \
                          '<b>{1}</b>' \
                          '</a>' \
                          '</div>'.format(row.alias_simec,row.nombre)
            return ret

        elif column == 'numero':

            return '<div class="center-align"><b>' + str(row.numero) + '</b></div>'



        elif column == 'cantidad_radicados':

            return '<div class="center-align"><b>' + str(row.get_cantidad_radicados()) + '</b></div>'

        elif column == 'cantidad_docentes':

            return '<div class="center-align"><b>' + str(row.get_cantidad_docentes()) + '</b></div>'

        elif column == 'latitud':

            return '<div class="center-align">' \
                           '<a id="{3}" onclick="mapa({1},{2})" href="#" class="mapa-municipio tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver mapa: {0}">' \
                                '<i class="mapa-municipio material-icons">gps_fixed</i>' \
                           '</a>' \
                       '</div>'.format(row.nombre,row.latitud,row.longitud,str(row.numero))


        else:
            return super(MunicipiosListApi, self).render_column(row, column)

class RadicadosListApi(BaseDatatableView):
    model = models.Radicados
    columns = ['id','numero','dane_sede','nombre_sede','tipologia_sede','estado']
    order_columns = ['id','numero','dane_sede','nombre_sede','tipologia_sede','estado']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.db.ver"
            ]
        }
        return self.model.objects.filter(municipio__id = self.kwargs['pk_municipio'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(numero__icontains=search) | Q(numero__icontains=search) | Q(nombre_ie__icontains=search) | Q(nombre_sede__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.numero)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.numero)

            return ret



        elif column == 'numero':

            return '<div class="center-align"><b>' + str(row.numero) + '</b></div>'

        elif column == 'tipologia_sede':

            return '<div class="center-align">' + row.tipologia_sede + '</div>'




        else:
            return super(RadicadosListApi, self).render_column(row, column)



class RadicadosSoportesListApi(BaseDatatableView):
    model = models.Radicados
    columns = ['id','numero','municipio','dane_sede','nombre_sede','estado']
    order_columns = ['id','numero','municipio','dane_sede','nombre_sede','estado']

    def get_initial_queryset(self):
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.soportes.ver",
                "usuarios.cpe_2018.soportes.soportes_{0}.ver".format(region.numero)
            ]
        }
        return self.model.objects.filter(municipio__departamento__region__id = self.kwargs['pk'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(numero__icontains=search) | Q(numero__icontains=search) | Q(nombre_ie__icontains=search) | \
                Q(nombre_sede__icontains=search) | Q(municipio__nombre__icontains=search) | Q(municipio__departamento__nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver los soportes del radicado {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.numero)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.numero)

            return ret



        elif column == 'numero':

            return '<div class="center-align"><b>' + str(row.numero) + '</b></div>'


        elif column == 'estado':

            return '<div class="center-align"><b style="color:#004c99;">' + str(row.get_progreso()) + '</b></div>'

        elif column == 'municipio':
            return str(row.municipio)


        else:
            return super(RadicadosSoportesListApi, self).render_column(row, column)


class RadicadosVerSoportesListApi(BaseDatatableView):
    model = models.Entregables
    columns = ['id','nombre','numero','tipo','modelo']
    order_columns = ['id','nombre','numero','tipo','modelo']

    def get_initial_queryset(self):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.soportes.ver",
                "usuarios.cpe_2018.soportes.soportes_{0}.ver".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': models.DocumentoLegalizacionTerminales,
            'encuesta_monitoreo': models.EncuestaMonitoreo,
            'relatoria_taller_apertura': models.RelatoriaTallerApertura,
            'relatoria_taller_administratic': models.RelatoriaTallerAdministratic,
            'relatoria_taller_contenidos_educativos': models.RelatoriaTallerContenidosEducativos,
            'relatoria_taller_raee': models.RelatoriaTallerRAEE
        }

        return self.model.objects.filter(modelo__in = self.modelos.keys())


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':

            lista = row.get_estado_radicado(self.radicado.numero,row.modelo)

            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')) and lista[0] != None:
                ret = '<div class="center-align">' \
                      '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver {1}">' \
                      '<i class="material-icons">insert_drive_file</i>' \
                      '</a>' \
                      '</div>'.format(lista[3], row.nombre)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons"></i>' \
                      '</div>'.format(row.id, row.nombre)

            return ret


        elif column == 'numero':
            lista = row.get_estado_radicado(self.radicado.numero, row.modelo)
            return lista[0]

        elif column == 'tipo':
            lista = row.get_estado_radicado(self.radicado.numero, row.modelo)
            return lista[1]

        elif column == 'modelo':
            lista = row.get_estado_radicado(self.radicado.numero, row.modelo)
            return lista[2]

        else:
            return super(RadicadosVerSoportesListApi, self).render_column(row, column)


class DocentesVerSoportesListApi(BaseDatatableView):
    model = models.Entregables
    columns = ['id','numero','nombre','orden','tipo','modelo']
    order_columns = ['id','numero','nombre','orden','tipo','modelo']

    def get_initial_queryset(self):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.docente = models.Docentes.objects.get(id=self.kwargs['pk_docente'])
        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.soportes.ver",
                "usuarios.cpe_2018.soportes.soportes_{0}.ver".format(self.region.numero)
            ]
        }

        return self.model.objects.filter(momento__estrategia = self.docente.estrategia)


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':

            lista = row.get_progreso_docente(self.docente.cedula,row.modelo)

            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')) and lista[0] != None:
                ret = '<div class="center-align">' \
                      '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver {1}">' \
                      '<i class="material-icons">insert_drive_file</i>' \
                      '</a>' \
                      '</div>'.format(lista[3], row.nombre)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons"></i>' \
                      '</div>'.format(row.id, row.nombre)

            return ret

        elif column == 'numero':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.numero)


        elif column == 'orden':
            lista = row.get_progreso_docente(self.docente.cedula, row.modelo)
            return lista[0]

        elif column == 'tipo':
            lista = row.get_progreso_docente(self.docente.cedula, row.modelo)
            return lista[1]

        elif column == 'modelo':
            lista = row.get_progreso_docente(self.docente.cedula, row.modelo)
            return lista[2]

        else:
            return super(DocentesVerSoportesListApi, self).render_column(row, column)


class DocentesSoportesListApi(BaseDatatableView):
    model = models.Docentes
    columns = ['id','cedula','nombre','municipio','estrategia','sede','estado','valor_total']
    order_columns = ['id','cedula','nombre','municipio','estrategia','sede','estado','valor_total']

    def get_initial_queryset(self):
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.soportes.ver",
                "usuarios.cpe_2018.soportes.soportes_{0}.ver".format(region.numero)
            ]
        }
        return self.model.objects.filter(municipio__departamento__region__id = self.kwargs['pk'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(cedula__icontains=search) | Q(nombre__icontains=search) | \
                Q(municipio__nombre__icontains=search) | Q(municipio__departamento__nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver los soportes de {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'valor_total':

            return '<div class="center-align"><b style="color:#004c99;">' + str(row.progreso_actividades()) + '</b></div>'


        elif column == 'municipio':
            return str(row.municipio)

        elif column == 'estrategia':
            return str(row.estrategia)

        else:
            return super(DocentesSoportesListApi, self).render_column(row, column)


class RetomasSoportesListApi(BaseDatatableView):
    model = models.Retoma
    columns = ['id','radicado','municipio','fecha','cpu','bolsas','estado']
    order_columns = ['id','radicado','municipio','fecha','cpu','bolsas','estado']

    def get_initial_queryset(self):
        region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.soportes.ver",
                "usuarios.cpe_2018.soportes.soportes_{0}.ver".format(region.numero)
            ]
        }
        return self.model.objects.filter(municipio__departamento__region__id = self.kwargs['pk'],estado = "Aprobado")


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(municipio__nombre__icontains=search) | Q(municipio__departamento__nombre__icontains=search) | Q(radicado__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver legalización {1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                           '</a>' \
                       '</div>'.format(row.url_file(),row.radicado)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">insert_drive_file</i>' \
                       '</div>'.format(row.url_file(),row.radicado)

            return ret

        elif column == 'bolsas':
            lider = '{0} - C.C.{1}'.format(row.ruta.contrato.contratista.get_full_name(),row.ruta.contrato.contratista.cedula)
            return lider

        elif column == 'estado':
            return '<div class="center-align"><b style="color:#004c99;">' + str('{:20,.2f}'.format(row.get_equipos_calculadora())) + '</b></div>'

        elif column == 'cpu':
            return row.ruta.nombre

        elif column == 'municipio':
            return str(row.municipio)


        else:
            return super(RetomasSoportesListApi, self).render_column(row, column)



class DocentesListApi(BaseDatatableView):
    model = models.Docentes
    columns = ['cedula','nombre','estrategia','sede','telefono','registro','estado']
    order_columns = ['cedula','nombre','estrategia','sede','telefono','registro','estado']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.db.ver"
            ]
        }
        return self.model.objects.filter(municipio__id = self.kwargs['pk_municipio'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(cedula__icontains=search) | Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):
        if column == 'estrategia':
            return str(row.estrategia.nombre)

        else:
            return super(DocentesListApi, self).render_column(row, column)

class ComponentesListApi(BaseDatatableView):
    model = models.Componentes
    columns = ['nombre','numero','cantidad']
    order_columns = ['nombre','numero','cantidad']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(numero__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'nombre':
            ret = '<div class="center-align">' \
                  '<a href="{0}/estrategias/" class="link-sec">' \
                  '<b>{1}</b>' \
                  '</a>' \
                  '</div>'.format(row.id, row.nombre)

            return ret

        elif column == 'numero':
            return '<div class="center-align"><b>' + str(row.numero) + '</b></div>'

        elif column == 'cantidad':
            return '<div class="center-align"><b>' + str(row.cantidad) + '</b></div>'

        else:
            return super(ComponentesListApi, self).render_column(row, column)

class EstrategiasListApi(BaseDatatableView):
    model = models.Estrategias
    columns = ['nombre','numero','cantidad']
    order_columns = ['nombre','numero','cantidad']

    def get_initial_queryset(self):
        return self.model.objects.filter(componente__id = self.kwargs['pk_componente'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(numero__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'nombre':
            ret = '<div class="center-align">' \
                  '<a href="{0}/momentos/" class="link-sec">' \
                  '<b>{1}</b>' \
                  '</a>' \
                  '</div>'.format(row.id, row.nombre)

            return ret

        elif column == 'numero':
            return '<div class="center-align"><b>' + str(row.get_consecutivo()) + '</b></div>'

        elif column == 'cantidad':
            return '<div class="center-align"><b>' + str(row.cantidad) + '</b></div>'

        else:
            return super(EstrategiasListApi, self).render_column(row, column)

class MomentosListApi(BaseDatatableView):
    model = models.Momentos
    columns = ['nombre','numero','cantidad']
    order_columns = ['nombre','numero','cantidad']

    def get_initial_queryset(self):
        return self.model.objects.filter(estrategia__id = self.kwargs['pk_estrategia'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(numero__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'nombre':
            ret = '<div class="center-align">' \
                  '<a href="{0}/entregables/" class="link-sec">' \
                  '<b>{1}</b>' \
                  '</a>' \
                  '</div>'.format(row.id, row.nombre)

            return ret

        elif column == 'numero':
            return '<div class="center-align"><b>' + str(row.get_consecutivo()) + '</b></div>'

        elif column == 'cantidad':
            return '<div class="center-align"><b>' + str(row.cantidad) + '</b></div>'

        else:
            return super(MomentosListApi, self).render_column(row, column)

class EntregablesListApi(BaseDatatableView):
    model = models.Entregables
    columns = ['nombre','numero','tipo','modelo','peso','presupuesto']
    order_columns = ['nombre','numero','tipo','modelo','peso','presupuesto']

    def get_initial_queryset(self):
        return self.model.objects.filter(momento__id = self.kwargs['pk_momento'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(numero__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'nombre':
            return '<div class="center-align"><b>' + str(row.nombre) + '</b></div>'

        elif column == 'numero':
            return '<div class="center-align"><b>' + str(row.get_consecutivo()) + '</b></div>'

        elif column == 'tipo':
            return '<b>' + str(row.tipo) + '</b>'

        elif column == 'modelo':
            return '<b>' + str(row.modelo) + '</b>'

        elif column == 'peso':
            return '<b>' + str(row.peso) + '</b>'

        else:
            return super(EntregablesListApi, self).render_column(row, column)

class RutasRegionListApi(BaseDatatableView):
    model = models.Rutas
    columns = ['id','usuario_creacion','nombre','contrato','update_datetime','estado','actividades_json','usuario_actualizacion']
    order_columns = ['id','usuario_creacion','nombre','contrato','update_datetime','estado','actividades_json','usuario_actualizacion']

    def get_initial_queryset(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])

        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ],
            "editar": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.editar".format(self.region.numero)
            ],
            "ver_privadas": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}_privadas.ver".format(self.region.numero)
            ],
            "editar_privadas": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}_privadas.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.editar".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}_privadas.editar".format(self.region.numero)
            ],
        }

        if self.request.user.has_perms(self.permissions.get('ver_privadas')):
            return self.model.objects.filter(region__id = self.kwargs['pk'])
        else:
            return self.model.objects.filter(region__id=self.kwargs['pk'],visible = True)


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(contrato__contratista__nombres__icontains=search) |\
                Q(contrato__contratista__apellidos__icontains=search) | Q(contrato__contratista__cedula__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):


        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'usuario_creacion':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="actividades/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Gestionar actividades de la ruta {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.nombre)

            return ret

        elif column == 'nombre':
            if row.estado == 'Liquidación':
                return '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{0}">' \
                            '<span class="mapa-ruta material-icons" style="font-size: 1.5rem;color:red;">error</span><span style="font-weight: bold;color: #000;">{1}</span>' \
                       '</a>'.format(row.estado, row.nombre)
            else:
                if row.visible:
                    return '<div class="center-align">' + row.nombre + '</div>'
                else:
                    return '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{0}">' \
                                '<span class="material-icons" style="font-size: 1.5rem;color:red;">compare</span><span style="font-weight: bold;color: #000;">{1}</span>' \
                            '</a>'.format('Contrato privado', row.nombre)

        elif column == 'estado':
            novedad = row.get_novedades_ruta()
            if novedad > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedad)
            else:
                return ''

        elif column == 'actividades_json':
            progreso, valor_reportado, valor_pagado = row.progreso_ruta()
            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(progreso, valor_reportado, valor_pagado)

        elif column == 'contrato':
            return row.contrato.rest_contratista()

        elif column == 'update_datetime':
            return row.contrato.pretty_print_valor()

        elif column == 'usuario_actualizacion':

            render = '''<a id="{1}" onclick="mapa_ruta('{1}')" href="#" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver mapa de la ruta: {0}">''' \
                        '<i class="mapa-ruta material-icons">gps_fixed</i>' \
                     '</a>'.format(row.nombre, str(row.id))

            render += '''<a id="{1}" onclick="trazabilidad('{1}')" href="#" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver trazabilidad de la ruta: {0}">''' \
                            '<i class="mapa-ruta material-icons">assessment</i>' \
                      '</a>'.format(row.nombre, str(row.id))

            render += '''<a href="cuentas_cobro/{0}/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver cuentas de cobro de la ruta {1}">''' \
                      '<i class="material-icons">account_balance_wallet</i>' \
                      '</a>'.format(row.id,row.nombre)



            return '<div class="center-align">' + render + '</div>'


        else:
            return super(RutasRegionListApi, self).render_column(row, column)







class RadicadosRutaListApi(BaseDatatableView):
    model = models.Radicados
    columns = ['id','numero','dane_sede','nombre_sede','tipologia_sede','estado','observaciones','ruta']
    order_columns = ['id','numero','dane_sede','nombre_sede','tipologia_sede','estado','observaciones','ruta']

    def get_initial_queryset(self):
        actividades_radicados_id = models.ActividadesRadicados.objects.filter(ruta__id = self.kwargs['pk_ruta']).values_list('radicado__id',flat=True)
        return self.model.objects.filter(id__in = actividades_radicados_id)


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(numero__icontains=search) | Q(nombre_ie__icontains=search) | Q(nombre_sede__icontains=search) | \
                Q(municipio__departamento__nombre__icontains=search) | Q(municipio__nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        ruta = models.Rutas.objects.get(id = self.kwargs['pk_ruta'])
        region = models.Regiones.objects.get(id=self.kwargs['pk'])

        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.acceso.ver",
                "usuarios.cpe_2018.acceso.rutas.ver",
                "usuarios.cpe_2018.acceso.rutas_{0}.ver".format(region.numero)
            ]
        }

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(permissions.get('all')):
                ret = '<div class="center-align">' \
                           '<a href="actividades/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Editar: {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.numero)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.numero)

            return ret



        elif column == 'numero':

            return '<div class="center-align"><b>' + str(row.numero) + '</b></div>'

        elif column == 'tipologia_sede':

            return '<div class="center-align">' + row.tipologia_sede + '</div>'

        elif column == 'observaciones':
            return '<div class="center-align"><b>' + str(row.get_valor_radicado_ruta(ruta = ruta)).replace('COL','') + '</b></div>'

        elif column == 'ruta':

            render = '''<a id="{1}" onclick="trazabilidad('{1}')" href="#" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver trazabilidad del radicado {0}">''' \
                      '<i class="mapa-ruta material-icons">assessment</i>' \
                      '</a>'.format(row.numero, str(row.id))

            return '<div class="center-align">' + render + '</div>'


        else:
            return super(RadicadosRutaListApi, self).render_column(row, column)

class ActividadesRadicadosRutaListApi(BaseDatatableView):
    model = models.ActividadesRadicados
    columns = ['id','numero','valor','estado','ruta']
    order_columns = ['id','numero','valor','estado','ruta']

    def get_initial_queryset(self):
        return self.model.objects.filter(radicado__id = self.kwargs['pk_radicado']).order_by('numero')



    def render_column(self, row, column):

        ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        region = models.Regiones.objects.get(id=self.kwargs['pk'])

        permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.acceso.ver",
                "usuarios.cpe_2018.acceso.rutas.ver",
                "usuarios.cpe_2018.acceso.rutas_{0}.ver".format(region.numero)
            ]
        }

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(permissions.get('all')):
                ret = '<div class="center-align">' \
                           '<a href="evidencias/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Editar: {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.actividad.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.actividad.nombre)

            return ret

        elif column == 'numero':
            return '<b>{0}. {1}</b>'.format(row.numero,row.actividad.nombre)


        elif column == 'valor':
            return row.pretty_print_valor()

        elif column == 'estado':
            return row.estado

        elif column == 'ruta':

            render = '''<a id="{1}" onclick="trazabilidad('{1}')" href="#" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver trazabilidad de la actividad: {0}">''' \
                      '<i class="mapa-ruta material-icons">assessment</i>' \
                      '</a>'.format(row.actividad.nombre, str(row.id))

            return '<div class="center-align">' + render + '</div>'

        else:
            return super(ActividadesRadicadosRutaListApi, self).render_column(row, column)

class RutasTrazabilidadApiJson(APIView):

    def get(self, request, pk,format=None):

        ruta = models.Rutas.objects.get(id = pk)

        ruta_dict = {
            'region': ruta.region.nombre,
            'nombre': ruta.nombre,
            'estado': ruta.estado
        }

        dict = []

        for trazabilidad in models.TrazabilidadRutas.objects.filter(ruta = ruta).order_by('-creation'):
            dict.append({
                'id': trazabilidad.id,
                'creacion': trazabilidad.pretty_creation_datetime(),
                'usuario': trazabilidad.usuario_creacion.get_full_name_string(),
                'observacion': trazabilidad.observacion
            })

        return Response({'data': dict, 'ruta': ruta_dict},status=status.HTTP_200_OK)

class ContratistaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models_rh.Contratistas.objects.none()

        qs = models_rh.Contratistas.objects.all()

        if self.q:
            q = Q(nombres__icontains = self.q) | Q(apellidos__icontains = self.q) | Q(cedula__icontains = self.q)
            qs = qs.filter(q)

        return qs

class ContratosAutocomplete(autocomplete.Select2QuerySetView):

    def get_results(self, context):

        data = []

        for result in context['object_list']:

            #info = result.get_actividades_info()

            data.append({
                'id': self.get_result_value(result),
                'text': result.get_autocomplete_text(),
            })


        return data

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models_rh.Contratos.objects.none()

        qs = models_rh.Contratos.objects.all()

        if self.q:
            q = Q(nombre__icontains = self.q) | Q(contratista__nombres__icontains = self.q) | \
                Q(contratista__apellidos__icontains = self.q) | Q(contratista__cedula__icontains = self.q)
            qs = qs.filter(q)

        return qs









class RadicadosAutocomplete(autocomplete.Select2QuerySetView):
    def get_results(self, context):

        data = []

        for result in context['object_list']:

            #info = result.get_actividades_info()

            data.append({
                'id': self.get_result_value(result),
                'text': self.get_result_label(result),
                'radicado': result.numero,
                'municipio': result.municipio.nombre,
                'departamento': result.municipio.departamento.nombre,
                'tipologia_sede': result.tipologia_sede,
                'estado': result.estado,
                'ruta': result.get_ruta(),
                'contratista': '',
                'disabled': True if result.ruta != None or result.estado != 'Aprobado' else False,
                'progreso': '',
                'pendientes': ''
            })


        return data

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return models.Radicados.objects.none()

        qs = models.Radicados.objects.filter(municipio__departamento__region__id = self.kwargs['pk']).order_by('numero')

        if self.q:
            q = Q(numero__icontains = self.q) | Q(municipio__departamento__nombre__icontains = self.q) | \
                Q(municipio__nombre__icontains = self.q)
            qs = qs.filter(q)

        return qs

class MunicipiosAutocomplete(autocomplete.Select2QuerySetView):
    paginate_by = 120

    def get_queryset(self):

        qs = models.Municipios.objects.all()

        if self.q:
            q = Q(nombre__icontains = self.q) | Q(departamento__nombre__icontains = self.q)
            qs = qs.filter(q)

        return qs



class MunicipiosAutocompleteRegion(autocomplete.Select2QuerySetView):
    paginate_by = 120

    def get_queryset(self):

        qs = models.Municipios.objects.filter(departamento__region__id = self.kwargs['pk_region'])

        if self.q:
            q = Q(nombre__icontains = self.q) | Q(departamento__nombre__icontains = self.q)
            qs = qs.filter(q)

        return qs





class RutasMapaApiJson(APIView):

    def get(self, request, pk,format=None):
        dict = []

        municipios_id = models.Radicados.objects.filter(ruta__id = pk).values_list('municipio__id',flat=True).distinct()

        for municipio in models.Municipios.objects.filter(id__in = municipios_id):
            dict.append({
                'id': municipio.id,
                'nombre': municipio.nombre,
                'departamento': municipio.departamento.nombre,
                'latitud': municipio.latitud,
                'longitud': municipio.longitud,
                'cantidad': str(models.Radicados.objects.filter(ruta__id = pk).filter(municipio = municipio).count())
            })

        return Response(dict,status=status.HTTP_200_OK)

class RadicadoRutasTrazabilidadApiJson(APIView):


    def get(self, request, pk,pk_ruta,pk_radicado,format=None):

        ruta = models.Rutas.objects.get(id = pk_ruta)
        radicado = models.Radicados.objects.get(id=pk_radicado)

        radicado_dict = {
            'numero': radicado.numero
        }

        dict = []

        for trazabilidad in models.TrazabilidadRadicados.objects.filter(radicado = radicado):
            dict.append({
                'id': trazabilidad.id,
                'creacion': trazabilidad.pretty_creation_datetime(),
                'usuario': trazabilidad.usuario_creacion.get_full_name_string(),
                'observacion': trazabilidad.observacion
            })

        return Response({'data': dict, 'radicado': radicado_dict},status=status.HTTP_200_OK)

class ActividadRadicadoRutasTrazabilidadApiJson(APIView):


    def get(self, request, pk,pk_ruta,pk_radicado,pk_actividad,format=None):

        ruta = models.Rutas.objects.get(id = pk_ruta)
        radicado = models.Radicados.objects.get(id=pk_radicado)
        actividad = models.ActividadesRadicados.objects.get(id=pk_actividad)

        actividad_dict = {
            'nombre': actividad.actividad.nombre
        }

        dict = []

        for trazabilidad in models.TrazabilidadActividadesRadicados.objects.filter(actividad = actividad):
            dict.append({
                'id': trazabilidad.id,
                'creacion': trazabilidad.pretty_creation_datetime(),
                'usuario': trazabilidad.usuario_creacion.get_full_name_string(),
                'observacion': trazabilidad.observacion
            })

        return Response({'data': dict, 'actividad': actividad_dict},status=status.HTTP_200_OK)

class ActividadesRutasTrazabilidadApiJson(APIView):


    def get(self, request, pk,pk_ruta,pk_actividad,pk_actividad_ruta,format=None):

        ruta = models.Rutas.objects.get(id = pk_ruta)
        actividad = models.Componentes.objects.get(id=pk_actividad)
        actividad_ruta = models.ActividadesRuta.objects.get(id = pk_actividad_ruta)

        actividad_dict = {
            'nombre': actividad_ruta.actividad.nombre,
            'numero': actividad_ruta.numero
        }

        dict = []

        for trazabilidad in models.TrazabilidadActividadesRuta.objects.filter(actividad = actividad_ruta):
            dict.append({
                'id': trazabilidad.id,
                'creacion': trazabilidad.pretty_creation_datetime(),
                'usuario': trazabilidad.usuario_creacion.get_full_name_string(),
                'observacion': trazabilidad.observacion
            })

        return Response({'data': dict, 'actividad': actividad_dict},status=status.HTTP_200_OK)








class ActividadesActividadRutaListApi(BaseDatatableView):
    model = models.ActividadesRuta
    columns = ['id','numero','valor','estado','ruta']
    order_columns = ['id','numero','valor','estado','ruta']

    def get_initial_queryset(self):
        return self.model.objects.filter(ruta__id = self.kwargs['pk_ruta'] ,actividad__id = self.kwargs['pk_actividad']).order_by('numero')



    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.acceso.db.editar'):
                ret = '<div class="center-align">' \
                           '<a href="evidencias/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Editar: {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.actividad.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.actividad.nombre)

            return ret

        elif column == 'numero':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.numero)


        elif column == 'valor':
            return row.pretty_print_valor()

        elif column == 'estado':
            return row.estado

        elif column == 'ruta':

            render = '''<a id="{1}" onclick="trazabilidad('{1}')" href="#" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver trazabilidad de la actividad: {0}">''' \
                      '<i class="mapa-ruta material-icons">assessment</i>' \
                      '</a>'.format(row.actividad.nombre, str(row.id))

            return '<div class="center-align">' + render + '</div>'

        else:
            return super(ActividadesActividadRutaListApi, self).render_column(row, column)

























class DocentesGrupoMisRutasListApi(BaseDatatableView):
    model = models.Docentes
    columns = ['cedula','nombre','municipio','estrategia','sede','telefono','registro','estado']
    order_columns = ['cedula','nombre','municipio','estrategia','sede','telefono','registro','estado']

    def get_initial_queryset(self):
        return self.model.objects.filter(grupo__id = self.kwargs['pk_grupo'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(cedula__icontains=search) | Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):
        if column == 'estrategia':
            return str(row.estrategia.nombre)
        elif column == 'municipio':
            return str(row.municipio)
        else:
            return super(DocentesGrupoMisRutasListApi, self).render_column(row, column)



class ActividadesRutaListApi(BaseDatatableView):
    model = models.Componentes
    columns = ['id','numero','nombre','tipo','cantidad','modelo']
    order_columns = ['id','numero','nombre','tipo','cantidad','modelo']

    def get_initial_queryset(self):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])

        self.permissions = {
            "ver_sedes": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero)
            ],
            "ver_grupos": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero)
            ]
        }

        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(numero__icontains=search) | Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACTIVIDADES
            """

            if row.numero == 1:
                if self.request.user.has_perms(self.permissions.get('ver_sedes')):
                    ret = '<div class="center-align">' \
                               '<a href="componente/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades de acceso">' \
                                    '<i class="material-icons">remove_red_eye</i>' \
                               '</a>' \
                           '</div>'.format(row.id,row.nombre)
                else:
                    ret = '<div class="center-align">' \
                          '<i class="material-icons">remove_red_eye</i>' \
                          '</div>'

            elif row.numero == 2:
                if self.request.user.has_perms(self.permissions.get('ver_grupos')):
                    ret = '<div class="center-align">' \
                          '<a href="formacion/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver grupos de formación">' \
                          '<i class="material-icons">remove_red_eye</i>' \
                          '</a>' \
                          '</div>'.format(row.id, row.nombre)
                else:
                    ret = '<div class="center-align">' \
                          '<i class="material-icons">remove_red_eye</i>' \
                          '</div>'

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'numero':
            """
            NUMERO
            """
            return '<div class="center-align"><b>' + str(row.numero) + '</b></div>'

        elif column == 'tipo':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>' + '$ {:20,.2f}'.format(self.ruta.get_valor_componente(row)) + '</b></div>'

        elif column == 'cantidad':
            """
            NOVEDADES
            """
            novedad = self.ruta.get_novedades_componente(row)
            if novedad > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedad)
            else:
                return ''

        elif column == 'modelo':
            """
            PROGRESO
            """
            progreso, valor_reportado, valor_pagado = self.ruta.progreso_ruta_componente(row)
            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(progreso, valor_reportado, valor_pagado)

        else:
            return super(ActividadesRutaListApi, self).render_column(row, column)



#------------------------------- CUENTAS DE COBRO ----------------------------------


class RutasCuentasCobroListApi(BaseDatatableView):
    model = models.CuentasCobro
    columns = ['corte','creation','valor','estado','file','file2','html']
    order_columns = ['corte','creation','valor','estado','file','file2','html']

    def get_initial_queryset(self):
        return self.model.objects.filter(ruta__id = self.kwargs['pk_ruta'])


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(corte__consecutivo=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        region = models.Regiones.objects.get(id = self.kwargs['pk'])

        permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(region.numero)
            ],
            "cargar_cuentas_cobro": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(region.numero),
                "usuarios.cpe_2018.rutas_{0}.cuentas_cobro.cargar".format(region.numero)
            ]
        }

        if column == 'corte':
            if row.corte != None:
                return '<div class="center-align"><b>' + str(row.corte.consecutivo) + '</b></div>'
            else:
                return 'Liquidación'

        elif column == 'creation':
            return '<div>' + row.pretty_creation_datetime() + '</div>'

        elif column == 'valor':
            return '<div class="center-align"><b>{0}</b></div>'.format('{:20,.2f}'.format(row.valor.amount))

        elif column == 'file':
            if row.url_file() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file(),'Descargar archivo')
            else:
                ret = ''

            return ret

        elif column == 'file2':
            if row.url_file2() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file2(),'Descargar archivo')
            else:
                ret = ''

            return ret


        elif column == 'estado':
            if row.estado == 'Pendiente':
                ret = '<div class="center-align">' \
                            '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<b>{0}</b>' \
                            '</a>' \
                      '</div>'.format(row.estado,row.observaciones)
            else:
                ret = row.estado

            return ret


        elif column == 'html':
            ret = '<div class="center-align">' \
                            '<a href="detalle/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">assignment_turned_in</i>' \
                            '</a>' \
                      '</div>'.format(row.id,'Detalle de las actividades')
            return ret

        else:
            return super(RutasCuentasCobroListApi, self).render_column(row, column)

class RutasCuentasCobroDetalleListApi(BaseDatatableView):
    model = models.Componentes
    columns = ['id','numero','nombre','tipo']
    order_columns = ['id','numero','nombre','tipo']

    def get_initial_queryset(self):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(numero__icontains=search) | Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACTIVIDADES
            """

            if row.numero == 1:
                if self.request.user.has_perms(self.permissions.get('ver')):
                    ret = '<div class="center-align">' \
                               '<a href="componente/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades de acceso">' \
                                    '<i class="material-icons">remove_red_eye</i>' \
                               '</a>' \
                           '</div>'.format(row.id,row.nombre)
                else:
                    ret = '<div class="center-align">' \
                          '<i class="material-icons">remove_red_eye</i>' \
                          '</div>'

            elif row.numero == 2:
                if self.request.user.has_perms(self.permissions.get('ver')):
                    ret = '<div class="center-align">' \
                          '<a href="formacion/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver grupos de formación">' \
                          '<i class="material-icons">remove_red_eye</i>' \
                          '</a>' \
                          '</div>'.format(row.id, row.nombre)
                else:
                    ret = '<div class="center-align">' \
                          '<i class="material-icons">remove_red_eye</i>' \
                          '</div>'

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'numero':
            """
            NUMERO
            """
            return '<div class="center-align"><b>' + str(row.numero) + '</b></div>'

        elif column == 'tipo':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>' + '$ {:20,.2f}'.format(self.ruta.get_valor_componente_corte(row,self.cuenta_cobro.corte)) + '</b></div>'

        else:
            return super(RutasCuentasCobroDetalleListApi, self).render_column(row, column)

class RutasCuentasCobroDetalleComponenteListApi(BaseDatatableView):
    model = models.EntregableRutaObject
    columns = ['id','tipo','entregable','valor','orden']
    order_columns = ['id','tipo','entregable','valor','orden']

    def get_initial_queryset(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        if self.cuenta_cobro.corte != None:
            query = self.model.objects.filter(ruta = self.ruta, corte = self.cuenta_cobro.corte)
        else:
            query = self.model.objects.filter(ruta=self.ruta).exclude(liquidacion = None)

        query_ruta_si_formacion = query.filter(padre='sede&ruta&siformacion&{0}'.format(self.ruta.id))
        query_sede_ruta = query.filter(padre='sede&ruta&{0}'.format(self.ruta.id))
        query_ruta_estrategia = query.filter(padre='ruta&estrategia&{0}'.format(self.ruta.id))
        query_sede = query.filter(entregable__tipo='sede')


        if query_ruta_estrategia.count() > 0:
            id = query_ruta_estrategia[0].id
            query_ruta_estrategia = query_ruta_estrategia.filter(id = id)



        if query_sede.count() > 0:
            ids = query_sede.distinct('padre').values_list('id',flat= True)
            query_sede = query_sede.filter(id__in = ids)



        query = query_ruta_si_formacion | query_sede_ruta | query_ruta_estrategia | query_sede


        return self.model.objects.filter(id__in = query.values_list('id',flat=True))

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)

        if search:

            try:
                radicado = models.Radicados.objects.get(numero=search)
            except:
                q = Q(entregable__nombre__icontains=search) | Q(entregable__momento__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__componente__nombre__icontains=search)
            else:
                q = Q(entregable__nombre__icontains=search) | Q(entregable__momento__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__componente__nombre__icontains=search) | Q(padre = 'sede&{0}'.format(radicado.id))
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACCIONES
            """
            ret = ''

            if row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id) or row.padre == 'sede&ruta&{0}'.format(self.ruta.id):

                if self.request.user.has_perms(self.permissions.get('ver')):
                    ret = '<div class="center-align">' \
                                '<a href="cargar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver archivos">' \
                                    '<i class="material-icons">cloud_upload</i>' \
                                '</a>' \
                          '</div>'.format(row.id)

                else:
                    ret = '<div class="center-align">' \
                                '<i class="material-icons">cloud_upload</i>' \
                          '</div>'

            elif row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):

                if self.request.user.has_perms(self.permissions.get('ver')):
                    ret = '<div class="center-align">' \
                                '<a href="retoma/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver retomas">' \
                                    '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                                '</a>' \
                          '</div>'.format(row.id)

                else:
                    ret = '<div class="center-align">' \
                                '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                          '</div>'

            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    if self.request.user.has_perms(self.permissions.get('ver')):
                        ret = '<div class="center-align">' \
                                    '<a href="radicado/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades Radicado: {1}">' \
                                        '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                                    '</a>' \
                              '</div>'.format(row.get_radicado().id, row.get_radicado().numero)
                    else:
                        ret = '<div class="center-align">' \
                                    '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                              '</div>'
                else:
                    pass

            else:
                raise NotImplementedError("Noesta definida la estrategia")

            return ret

        elif column == 'tipo':
            """
            TIPO
            """
            if row.estado == 'Cerrado':
                return '<div class="center-align">' \
                            '<a class="tooltipped" data-position = "top" data-delay="50" data-tooltip="Liquidación">' \
                                '<span class="material-icons" style="font-size: 1.5rem;color:red;">error</span>' \
                                '<span style="font-weight: bold;color: #000;">{0}</span>' \
                            '</a>' \
                       '</div>'.format(row.tipo)
            else:
                return row.tipo

        elif column == 'entregable':
            """
            NOMBRE
            """
            if row.entregable.tipo == 'sede':
                return 'Radicado: {0}'.format(row.get_radicado().numero)

            else:
                if row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                    return 'Retoma'
                else:
                    return row.entregable.nombre

        elif column == 'valor':
            """
            VALOR MAXIMO
            """
            if row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                return '<div class="center-align"><b>{0}</b></div>'.format(
                    '$ {:20,.2f}'.format(row.ruta.valor_ruta_entregable_estrategia_corte(row.entregable, self.cuenta_cobro.corte))
                )

            elif row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id) or row.padre == 'sede&ruta&{0}'.format(
                    self.ruta.id):
                return '<div class="center-align"><b>{0}</b></div>'.format(row.pretty_print_valor())

            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    return '<div class="center-align"><b>{0}</b></div>'.format(
                        '$ {:20,.2f}'.format(row.get_radicado_valor_corte(self.cuenta_cobro.corte))
                    )
                else:
                    pass

            return ''

        elif column == 'orden':
            """
            MOMENTO
            """
            if row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id):
                name = row.entregable.momento.nombre
                color = '#1a237e'

            elif row.padre == 'sede&ruta&{0}'.format(self.ruta.id):
                name = row.entregable.momento.nombre
                color = '#ffab00'

            elif row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                name = row.entregable.momento.nombre
                color = '#7b1fa2'


            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    name = 'Radicado'
                    color = '#388e3c'

            else:
                name = ''
                color = ''


            return '<div class="center-align">' \
                           '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{0}">' \
                                '<i style = "color:{1};" class="material-icons">{2}</i>' \
                           '</a>' \
                       '</div>'.format(name, color, row.entregable.momento.icon if row.entregable != None else 'accessibility')

        else:
            return super(RutasCuentasCobroDetalleComponenteListApi, self).render_column(row, column)

class RutasCuentasCobroDetalleRetomaListApi(BaseDatatableView):
    model = models.Retoma
    columns = ['ruta','radicado','fecha','red','municipio','bolsas','cedula']
    order_columns = ['ruta','radicado','fecha','red','municipio','bolsas','cedula']

    def get_initial_queryset(self):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        ids = []

        if self.cuenta_cobro.corte != None:
            for entregable in models.EntregableRutaObject.objects.filter(padre = "ruta&estrategia&{0}".format(self.ruta.id), corte = self.cuenta_cobro.corte):
                ids.append(entregable.soporte.replace('retoma&',''))

        else:
            for entregable in models.EntregableRutaObject.objects.filter(padre="ruta&estrategia&{0}".format(self.ruta.id)).exclude(liquidacion = None):
                ids.append(entregable.soporte.replace('retoma&', ''))

        return self.model.objects.filter(ruta__id = self.kwargs['pk_ruta'], id__in = ids).order_by('fecha')

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(municipio__nombre__icontains=search) | Q(municipio__departamento__nombre__icontains=search) | \
                Q(radicado__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'ruta':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('ver')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver retoma del radicado {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.radicado)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.radicado)

            return ret

        elif column == 'red':
            """
            RED
            """
            if row.red == None:
                return ''
            else:
                return '<div class="center-align"><b>RED {0}</b></div>'.format(row.red.consecutivo)

        elif column == 'municipio':
            """
            MUNICIPIO
            """
            return str(row.municipio)

        elif column == 'bolsas':
            """
            CANTIDAD
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><b>{0}</b><span class="nuevo badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas,row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><b>{0}</b><span class="actualizado badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas, row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><b>{0}</b><span class="aprobado badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas, row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><b>{0}</b><span class="rechazado badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas, row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><b>{0}</b><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.bolsas, row.estado)
            else:
                return '<div class="center-align"><b>{0}</b><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.bolsas)

        elif column == 'cedula':
            """
            VALOR
            """
            return '<div class="center-align"><b>{0}</b></div>'.format(self.ruta.get_valor_ruta_estrategia_id(row.id))

        else:
            return super(RutasCuentasCobroDetalleRetomaListApi, self).render_column(row, column)

class RutasCuentasCobroDetalleRadicadoListApi(BaseDatatableView):

    model = models.EntregableRutaObject
    columns = ['id','orden','entregable','valor']
    order_columns = ['id','orden','entregable','valor']

    def get_initial_queryset(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id = self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        if self.cuenta_cobro.corte != None:
            query = self.model.objects.filter(ruta = self.ruta, radicado=self.radicado, corte = self.cuenta_cobro.corte)
        else:
            query = self.model.objects.filter(ruta=self.ruta, radicado=self.radicado).exclude(liquidacion = None)

        return self.model.objects.filter(id__in = query.values_list('id',flat=True))

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(entregable__nombre__icontains=search) | Q(entregable__momento__nombre__icontains=search) | \
                Q(entregable__momento__estrategia__nombre__icontains=search) | \
                Q(entregable__momento__estrategia__componente__nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACCIONES
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                      '<a href="cargar/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver soportes">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id)
            else:
                ret = '<div class="center-align">' \
                            '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'

            return ret

        elif column == 'orden':
            """
            MOMENTO
            """
            return '<div class="center-align">' \
                            '<p>{0}</p>' \
                       '</div>'.format(row.entregable.momento.nombre)

        elif column == 'entregable':
            """
            NOMBRE
            """
            return row.entregable.nombre

        elif column == 'valor':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>{0}</b></div>'.format(row.pretty_print_valor())

        else:
            return super(RutasCuentasCobroDetalleRadicadoListApi, self).render_column(row, column)

class ActividadesSedeCuentasCobroListApi(BaseDatatableView):

    columns = ['ver','nombre','estado','red','valor']
    order_columns = ['ver','nombre','estado','red','valor']

    def get_initial_queryset(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            id_soporte = self.objeto_ruta.soporte.split('&')[-1]
            return modelo.objects.filter(id = id_soporte)
        else:
            raise NotImplementedError("EL modelo no esta establecido")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'ver':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'nombre':
            """
            NOMBRE
            """
            return row.nombre

        elif column == 'estado':
            """
            ESTADO
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><span class="actualizado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><span class="aprobado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><span class="rechazado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.estado)
            else:
                return '<div class="center-align"><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.estado)

        elif column == 'red':
            """
            RED
            """
            if row.red == None:
                return ''
            else:
                return '<div class="center-align"><b>RED {0}</b></div>'.format(row.red.consecutivo)

        elif column == 'valor':
            """
            VALOR
            """
            return  '<div class="center-align"><b>{0}</b></div>'.format(self.objeto_ruta.get_valor_si_calificado())

        else:
            return super(ActividadesSedeCuentasCobroListApi, self).render_column(row, column)

class ActividadesSedeRutaCuentaCobroListApi(BaseDatatableView):

    columns = ['ver','nombre','estado','valor']
    order_columns = ['ver','nombre','estado','valor']

    def get_initial_queryset(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            id_soporte = self.objeto_ruta.soporte.split('&')[-1]
            return modelo.objects.filter(id=id_soporte)
        else:
            raise NotImplementedError("EL modelo no esta establecido")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'ver':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'nombre':
            """
            NOMBRE
            """
            return row.nombre

        elif column == 'estado':
            """
            ESTADO
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><span class="actualizado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><span class="aprobado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><span class="rechazado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.estado)
            else:
                return '<div class="center-align"><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.estado)

        elif column == 'valor':
            """
            VALOR
            """
            return  '<div class="center-align"><b>{0}</b></div>'.format(self.objeto_ruta.get_valor_si_calificado())

        else:
            return super(ActividadesSedeRutaCuentaCobroListApi, self).render_column(row, column)

class GruposRutaCuentaCobroListApi(BaseDatatableView):
    model = models.Grupos
    columns = ['creation','numero','ruta']
    order_columns = ['creation','numero','ruta']

    def get_initial_queryset(self):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }
        return self.model.objects.filter(ruta__id = self.kwargs['pk_ruta'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(numero__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'creation':
            """
            ACTIVIDADES
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                           '<a href="actividades/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades del grupo {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.get_nombre_grupo())

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.get_nombre_grupo())

            return ret

        elif column == 'numero':
            """
            NOMBRE
            """
            return '<div class="center-align">' \
                        '<b>{0}</b>' \
                    '</div>'.format(row.get_nombre_grupo())

        elif column == 'ruta':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>$ {:20,.2f}</b></div>'.format(row.get_valor_corte(self.cuenta_cobro.corte))

        else:
            return super(GruposRutaCuentaCobroListApi, self).render_column(row, column)

class ActividadesGrupoCuentaCobroRutaListApi(BaseDatatableView):
    model = models.Entregables
    columns = ['id','orden','momento','nombre','tipo']
    order_columns = ['id','orden','momento','nombre','tipo']

    def get_initial_queryset(self):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        if self.cuenta_cobro.corte != None:
            ids_entregables = models.EntregableRutaObject.objects.filter(ruta = self.ruta, entregable__momento__estrategia = self.grupo.estrategia, corte = self.cuenta_cobro.corte).values_list('entregable__id',flat=True).distinct()
        else:
            ids_entregables = models.EntregableRutaObject.objects.filter(ruta = self.ruta, entregable__momento__estrategia = self.grupo.estrategia).exclude(liquidacion = None).values_list('entregable__id', flat=True).distinct()

        return self.model.objects.filter(id__in = ids_entregables)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)

        if search:
            q = Q(nombre__icontains=search) | Q(momento__nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACCIONES
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                      '<a href="evidencias/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar archivo(s)">' \
                      '<i class="material-icons">cloud_upload</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">cloud_upload</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'orden':
            """
            NUMERO
            """
            return '<div class="center-align"><b>{0}</b></div>'.format(row.orden)

        elif column == 'momento':
            """
            NIVEL
            """
            return '<div class="center-align">{0}</div>'.format(row.momento.nombre)

        elif column == 'tipo':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>$ {:20,.2f}</b></div>'.format(self.grupo.get_valor_maximo_entregable_corte(row,self.cuenta_cobro.corte))

        else:
            return super(ActividadesGrupoCuentaCobroRutaListApi, self).render_column(row, column)

class EvidenciasFormacionRutaCuentaCobroListApi(BaseDatatableView):

    columns = ['ver','docentes','estado','valor']
    order_columns = ['ver','docentes','estado','valor']

    def get_initial_queryset(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
        }

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")

        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']

            if self.cuenta_cobro.corte != None:
                soporte_entregables = models.EntregableRutaObject.objects.filter(ruta=self.ruta,entregable__momento__estrategia=self.grupo.estrategia,entregable=self.entregable,corte=self.cuenta_cobro.corte).values_list('soporte', flat=True).distinct()
            else:
                soporte_entregables = models.EntregableRutaObject.objects.filter(ruta=self.ruta,entregable__momento__estrategia=self.grupo.estrategia,entregable=self.entregable).exclude(liquidacion = None).values_list('soporte', flat=True).distinct()

            ids = []

            for soporte in soporte_entregables:
                ids.append(soporte.split('&')[-1])

            queryset = modelo.objects.filter(id__in = ids)
            return queryset.filter(grupo = self.grupo)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(docentes__nombre__icontains=search) | Q(docentes__cedula__icontains=search)
            qs = qs.filter(q).distinct()
        return qs

    def render_column(self, row, column):

        if column == 'ver':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,self.entregable.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,self.entregable.nombre)

            return ret

        elif column == 'docentes':
            """
            DOCENTES
            """
            ret = ''

            for docente in row.docentes.all():
                ret += '<p><b>{0}</b> - {1}</p>'.format(str(docente.cedula),docente.nombre)

            return '<ul class="collapsible" data-collapsible="accordion">' \
                        '<li>' \
                            '<div class="collapsible-header">' \
                                '<i class="material-icons edit-table">arrow_drop_down_circle</i>' \
                                '{0} Docente(s)' \
                            '</div>' \
                            '<div class="collapsible-body" style="background-color: white;">{1}</div>' \
                        '</li>' \
                   '</ul>'.format(row.docentes.all().count(),ret)

        elif column == 'estado':
            """
            ESTADO
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><span class="actualizado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><span class="aprobado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><span class="rechazado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.estado)
            else:
                return '<div class="center-align"><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.estado)

        elif column == 'valor':
            """
            VALOR
            """
            return  '<div class="center-align"><b>{0}</b></div>'.format(row.get_valor(self.entregable))

        else:
            return super(EvidenciasFormacionRutaCuentaCobroListApi, self).render_column(row, column)



#------------------------------- MIS CUENTAS DE COBRO ----------------------------------

class MisRutasCuentasCobroDetalleListApi(BaseDatatableView):
    model = models.Componentes
    columns = ['id','numero','nombre','tipo']
    order_columns = ['id','numero','nombre','tipo']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(numero__icontains=search) | Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACTIVIDADES
            """

            if row.numero == 1:
                if self.request.user.has_perms(self.permissions.get('ver')):
                    ret = '<div class="center-align">' \
                               '<a href="componente/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades de acceso">' \
                                    '<i class="material-icons">remove_red_eye</i>' \
                               '</a>' \
                           '</div>'.format(row.id,row.nombre)
                else:
                    ret = '<div class="center-align">' \
                          '<i class="material-icons">remove_red_eye</i>' \
                          '</div>'

            elif row.numero == 2:
                if self.request.user.has_perms(self.permissions.get('ver')):
                    ret = '<div class="center-align">' \
                          '<a href="formacion/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver grupos de formación">' \
                          '<i class="material-icons">remove_red_eye</i>' \
                          '</a>' \
                          '</div>'.format(row.id, row.nombre)
                else:
                    ret = '<div class="center-align">' \
                          '<i class="material-icons">remove_red_eye</i>' \
                          '</div>'

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'numero':
            """
            NUMERO
            """
            return '<div class="center-align"><b>' + str(row.numero) + '</b></div>'

        elif column == 'tipo':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>' + '$ {:20,.2f}'.format(self.ruta.get_valor_componente_corte(row,self.cuenta_cobro.corte)) + '</b></div>'

        else:
            return super(MisRutasCuentasCobroDetalleListApi, self).render_column(row, column)



class MisRutasCuentasCobroDetalleComponenteListApi(BaseDatatableView):
    model = models.EntregableRutaObject
    columns = ['id','tipo','entregable','valor','orden']
    order_columns = ['id','tipo','entregable','valor','orden']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        query = self.model.objects.filter(ruta = self.ruta, corte = self.cuenta_cobro.corte)

        query_ruta_si_formacion = query.filter(padre='sede&ruta&siformacion&{0}'.format(self.ruta.id))
        query_sede_ruta = query.filter(padre='sede&ruta&{0}'.format(self.ruta.id))
        query_ruta_estrategia = query.filter(padre='ruta&estrategia&{0}'.format(self.ruta.id))
        query_sede = query.filter(entregable__tipo='sede')


        if query_ruta_estrategia.count() > 0:
            id = query_ruta_estrategia[0].id
            query_ruta_estrategia = query_ruta_estrategia.filter(id = id)



        if query_sede.count() > 0:
            ids = query_sede.distinct('padre').values_list('id',flat= True)
            query_sede = query_sede.filter(id__in = ids)



        query = query_ruta_si_formacion | query_sede_ruta | query_ruta_estrategia | query_sede


        return self.model.objects.filter(id__in = query.values_list('id',flat=True))

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)

        if search:

            try:
                radicado = models.Radicados.objects.get(numero=search)
            except:
                q = Q(entregable__nombre__icontains=search) | Q(entregable__momento__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__componente__nombre__icontains=search)
            else:
                q = Q(entregable__nombre__icontains=search) | Q(entregable__momento__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__componente__nombre__icontains=search) | Q(padre = 'sede&{0}'.format(radicado.id))
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACCIONES
            """
            ret = ''

            if row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id) or row.padre == 'sede&ruta&{0}'.format(self.ruta.id):

                if self.request.user.has_perms(self.permissions.get('ver')):
                    ret = '<div class="center-align">' \
                                '<a href="cargar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver archivos">' \
                                    '<i class="material-icons">cloud_upload</i>' \
                                '</a>' \
                          '</div>'.format(row.id)

                else:
                    ret = '<div class="center-align">' \
                                '<i class="material-icons">cloud_upload</i>' \
                          '</div>'

            elif row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):

                if self.request.user.has_perms(self.permissions.get('ver')):
                    ret = '<div class="center-align">' \
                                '<a href="retoma/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver retomas">' \
                                    '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                                '</a>' \
                          '</div>'.format(row.id)

                else:
                    ret = '<div class="center-align">' \
                                '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                          '</div>'

            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    if self.request.user.has_perms(self.permissions.get('ver')):
                        ret = '<div class="center-align">' \
                                    '<a href="radicado/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades Radicado: {1}">' \
                                        '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                                    '</a>' \
                              '</div>'.format(row.get_radicado().id, row.get_radicado().numero)
                    else:
                        ret = '<div class="center-align">' \
                                    '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                              '</div>'
                else:
                    pass

            else:
                raise NotImplementedError("Noesta definida la estrategia")

            return ret

        elif column == 'tipo':
            """
            TIPO
            """
            if row.estado == 'Cerrado':
                return '<div class="center-align">' \
                            '<a class="tooltipped" data-position = "top" data-delay="50" data-tooltip="Liquidación">' \
                                '<span class="material-icons" style="font-size: 1.5rem;color:red;">error</span>' \
                                '<span style="font-weight: bold;color: #000;">{0}</span>' \
                            '</a>' \
                       '</div>'.format(row.tipo)
            else:
                return row.tipo

        elif column == 'entregable':
            """
            NOMBRE
            """
            if row.entregable.tipo == 'sede':
                return 'Radicado: {0}'.format(row.get_radicado().numero)

            else:
                if row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                    return 'Retoma'
                else:
                    return row.entregable.nombre

        elif column == 'valor':
            """
            VALOR MAXIMO
            """
            if row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                return '<div class="center-align"><b>{0}</b></div>'.format(
                    '$ {:20,.2f}'.format(row.ruta.valor_ruta_entregable_estrategia_corte(row.entregable, self.cuenta_cobro.corte))
                )

            elif row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id) or row.padre == 'sede&ruta&{0}'.format(
                    self.ruta.id):
                return '<div class="center-align"><b>{0}</b></div>'.format(row.pretty_print_valor())

            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    return '<div class="center-align"><b>{0}</b></div>'.format(
                        '$ {:20,.2f}'.format(row.get_radicado_valor_corte(self.cuenta_cobro.corte))
                    )
                else:
                    pass

            return ''

        elif column == 'orden':
            """
            MOMENTO
            """
            if row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id):
                name = row.entregable.momento.nombre
                color = '#1a237e'

            elif row.padre == 'sede&ruta&{0}'.format(self.ruta.id):
                name = row.entregable.momento.nombre
                color = '#ffab00'

            elif row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                name = row.entregable.momento.nombre
                color = '#7b1fa2'


            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    name = 'Radicado'
                    color = '#388e3c'

            else:
                name = ''
                color = ''


            return '<div class="center-align">' \
                           '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{0}">' \
                                '<i style = "color:{1};" class="material-icons">{2}</i>' \
                           '</a>' \
                       '</div>'.format(name, color, row.entregable.momento.icon if row.entregable != None else 'accessibility')

        else:
            return super(MisRutasCuentasCobroDetalleComponenteListApi, self).render_column(row, column)

class MisRutasCuentasCobroDetalleRetomaListApi(BaseDatatableView):
    model = models.Retoma
    columns = ['ruta','radicado','fecha','red','municipio','bolsas','cedula']
    order_columns = ['ruta','radicado','fecha','red','municipio','bolsas','cedula']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        ids = []

        for entregable in models.EntregableRutaObject.objects.filter(padre = "ruta&estrategia&{0}".format(self.ruta.id), corte = self.cuenta_cobro.corte):
            ids.append(entregable.soporte.replace('retoma&',''))

        return self.model.objects.filter(ruta__id = self.kwargs['pk_ruta'], id__in = ids).order_by('fecha')

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(municipio__nombre__icontains=search) | Q(municipio__departamento__nombre__icontains=search) | \
                Q(radicado__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'ruta':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('ver')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver retoma del radicado {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.radicado)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.radicado)

            return ret

        elif column == 'red':
            """
            RED
            """
            if row.red == None:
                return ''
            else:
                return '<div class="center-align"><b>RED {0}</b></div>'.format(row.red.consecutivo)

        elif column == 'municipio':
            """
            MUNICIPIO
            """
            return str(row.municipio)

        elif column == 'bolsas':
            """
            CANTIDAD
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><b>{0}</b><span class="nuevo badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas,row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><b>{0}</b><span class="actualizado badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas, row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><b>{0}</b><span class="aprobado badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas, row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><b>{0}</b><span class="rechazado badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas, row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><b>{0}</b><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.bolsas, row.estado)
            else:
                return '<div class="center-align"><b>{0}</b><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.bolsas)

        elif column == 'cedula':
            """
            VALOR
            """
            return '<div class="center-align"><b>{0}</b></div>'.format(self.ruta.get_valor_ruta_estrategia_id(row.id))

        else:
            return super(MisRutasCuentasCobroDetalleRetomaListApi, self).render_column(row, column)

class MisRutasCuentasCobroDetalleRadicadoListApi(BaseDatatableView):

    model = models.EntregableRutaObject
    columns = ['id','orden','entregable','valor']
    order_columns = ['id','orden','entregable','valor']

    def get_initial_queryset(self):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id = self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        query = self.model.objects.filter(ruta = self.ruta, radicado=self.radicado, corte = self.cuenta_cobro.corte)
        return self.model.objects.filter(id__in = query.values_list('id',flat=True))

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(entregable__nombre__icontains=search) | Q(entregable__momento__nombre__icontains=search) | \
                Q(entregable__momento__estrategia__nombre__icontains=search) | \
                Q(entregable__momento__estrategia__componente__nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACCIONES
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                      '<a href="cargar/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver soportes">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id)
            else:
                ret = '<div class="center-align">' \
                            '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'

            return ret

        elif column == 'orden':
            """
            MOMENTO
            """
            return '<div class="center-align">' \
                            '<p>{0}</p>' \
                       '</div>'.format(row.entregable.momento.nombre)

        elif column == 'entregable':
            """
            NOMBRE
            """
            return row.entregable.nombre

        elif column == 'valor':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>{0}</b></div>'.format(row.pretty_print_valor())

        else:
            return super(MisRutasCuentasCobroDetalleRadicadoListApi, self).render_column(row, column)

class MisActividadesSedeCuentasCobroListApi(BaseDatatableView):

    columns = ['ver','nombre','estado','red','valor']
    order_columns = ['ver','nombre','estado','red','valor']

    def get_initial_queryset(self):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            id_soporte = self.objeto_ruta.soporte.split('&')[-1]
            return modelo.objects.filter(id = id_soporte)
        else:
            raise NotImplementedError("EL modelo no esta establecido")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'ver':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'nombre':
            """
            NOMBRE
            """
            return row.nombre

        elif column == 'estado':
            """
            ESTADO
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><span class="actualizado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><span class="aprobado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><span class="rechazado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.estado)
            else:
                return '<div class="center-align"><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.estado)

        elif column == 'red':
            """
            RED
            """
            if row.red == None:
                return ''
            else:
                return '<div class="center-align"><b>RED {0}</b></div>'.format(row.red.consecutivo)

        elif column == 'valor':
            """
            VALOR
            """
            return  '<div class="center-align"><b>{0}</b></div>'.format(self.objeto_ruta.get_valor_si_calificado())

        else:
            return super(MisActividadesSedeCuentasCobroListApi, self).render_column(row, column)

class MisActividadesSedeRutaCuentaCobroListApi(BaseDatatableView):

    columns = ['ver','nombre','estado','valor']
    order_columns = ['ver','nombre','estado','valor']

    def get_initial_queryset(self):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            id_soporte = self.objeto_ruta.soporte.split('&')[-1]
            return modelo.objects.filter(id=id_soporte)
        else:
            raise NotImplementedError("EL modelo no esta establecido")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'ver':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'nombre':
            """
            NOMBRE
            """
            return row.nombre

        elif column == 'estado':
            """
            ESTADO
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><span class="actualizado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><span class="aprobado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><span class="rechazado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.estado)
            else:
                return '<div class="center-align"><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.estado)

        elif column == 'valor':
            """
            VALOR
            """
            return  '<div class="center-align"><b>{0}</b></div>'.format(self.objeto_ruta.get_valor_si_calificado())

        else:
            return super(MisActividadesSedeRutaCuentaCobroListApi, self).render_column(row, column)

class MisGruposRutaCuentaCobroListApi(BaseDatatableView):
    model = models.Grupos
    columns = ['creation','numero','ruta']
    order_columns = ['creation','numero','ruta']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }
        return self.model.objects.filter(ruta__id = self.kwargs['pk_ruta'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(numero__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'creation':
            """
            ACTIVIDADES
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                           '<a href="actividades/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades del grupo {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.get_nombre_grupo())

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.get_nombre_grupo())

            return ret

        elif column == 'numero':
            """
            NOMBRE
            """
            return '<div class="center-align">' \
                        '<b>{0}</b>' \
                    '</div>'.format(row.get_nombre_grupo())

        elif column == 'ruta':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>$ {:20,.2f}</b></div>'.format(row.get_valor_corte(self.cuenta_cobro.corte))

        else:
            return super(MisGruposRutaCuentaCobroListApi, self).render_column(row, column)

class MisActividadesGrupoCuentaCobroRutaListApi(BaseDatatableView):
    model = models.Entregables
    columns = ['id','orden','momento','nombre','tipo']
    order_columns = ['id','orden','momento','nombre','tipo']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        ids_entregables = models.EntregableRutaObject.objects.filter(ruta = self.ruta, entregable__momento__estrategia = self.grupo.estrategia, corte = self.cuenta_cobro.corte).values_list('entregable__id',flat=True).distinct()

        return self.model.objects.filter(id__in = ids_entregables)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)

        if search:
            q = Q(nombre__icontains=search) | Q(momento__nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACCIONES
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                      '<a href="evidencias/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar archivo(s)">' \
                      '<i class="material-icons">cloud_upload</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">cloud_upload</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'orden':
            """
            NUMERO
            """
            return '<div class="center-align"><b>{0}</b></div>'.format(row.orden)

        elif column == 'momento':
            """
            NIVEL
            """
            return '<div class="center-align">{0}</div>'.format(row.momento.nombre)

        elif column == 'tipo':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>$ {:20,.2f}</b></div>'.format(self.grupo.get_valor_maximo_entregable_corte(row,self.cuenta_cobro.corte))

        else:
            return super(MisActividadesGrupoCuentaCobroRutaListApi, self).render_column(row, column)

class MisEvidenciasFormacionRutaCuentaCobroListApi(BaseDatatableView):

    columns = ['ver','docentes','estado','valor']
    order_columns = ['ver','docentes','estado','valor']

    def get_initial_queryset(self):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.cuenta_cobro = models.CuentasCobro.objects.get(id=self.kwargs['pk_cuenta_cobro'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
        }

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")

        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']

            soporte_entregables = models.EntregableRutaObject.objects.filter(ruta=self.ruta,entregable__momento__estrategia=self.grupo.estrategia,entregable=self.entregable,corte=self.cuenta_cobro.corte).values_list('soporte', flat=True).distinct()

            ids = []

            for soporte in soporte_entregables:
                ids.append(soporte.split('&')[-1])

            queryset = modelo.objects.filter(id__in = ids)
            return queryset.filter(grupo = self.grupo)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(docentes__nombre__icontains=search) | Q(docentes__cedula__icontains=search)
            qs = qs.filter(q).distinct()
        return qs

    def render_column(self, row, column):

        if column == 'ver':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,self.entregable.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,self.entregable.nombre)

            return ret

        elif column == 'docentes':
            """
            DOCENTES
            """
            ret = ''

            for docente in row.docentes.all():
                ret += '<p><b>{0}</b> - {1}</p>'.format(str(docente.cedula),docente.nombre)

            return '<ul class="collapsible" data-collapsible="accordion">' \
                        '<li>' \
                            '<div class="collapsible-header">' \
                                '<i class="material-icons edit-table">arrow_drop_down_circle</i>' \
                                '{0} Docente(s)' \
                            '</div>' \
                            '<div class="collapsible-body" style="background-color: white;">{1}</div>' \
                        '</li>' \
                   '</ul>'.format(row.docentes.all().count(),ret)

        elif column == 'estado':
            """
            ESTADO
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><span class="actualizado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><span class="aprobado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><span class="rechazado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.estado)
            else:
                return '<div class="center-align"><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.estado)

        elif column == 'valor':
            """
            VALOR
            """
            return  '<div class="center-align"><b>{0}</b></div>'.format(row.get_valor(self.entregable))

        else:
            return super(MisEvidenciasFormacionRutaCuentaCobroListApi, self).render_column(row, column)



#------------------------------------ ACCESO --------------------------------------

class ActividadesComponenteRutaListApi(BaseDatatableView):
    model = models.EntregableRutaObject
    columns = ['id','tipo','entregable','estado','valor','orden','padre','para_pago']
    order_columns = ['id','tipo','entregable','estado','valor','orden','padre','para_pago']


    def get_initial_queryset(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero)
            ],
            "retoma": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.ver".format(self.region.numero)
            ]
        }

        query = self.model.objects.filter(ruta = self.ruta)

        query_ruta_si_formacion = query.filter(padre='sede&ruta&siformacion&{0}'.format(self.ruta.id))
        query_sede_ruta = query.filter(padre='sede&ruta&{0}'.format(self.ruta.id))
        query_ruta_estrategia = query.filter(padre='ruta&estrategia&{0}'.format(self.ruta.id))
        query_sede = query.filter(entregable__tipo='sede')


        if query_ruta_estrategia.count() > 0:
            id = query_ruta_estrategia[0].id
            query_ruta_estrategia = query_ruta_estrategia.filter(id = id)



        if query_sede.count() > 0:
            ids = query_sede.distinct('padre').values_list('id',flat= True)
            query_sede = query_sede.filter(id__in = ids)



        query = query_ruta_si_formacion | query_sede_ruta | query_ruta_estrategia | query_sede


        return self.model.objects.filter(id__in = query.values_list('id',flat=True))

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)

        if search:

            try:
                radicado = models.Radicados.objects.get(numero=search)
            except:
                q = Q(entregable__nombre__icontains=search) | Q(entregable__momento__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__componente__nombre__icontains=search)
            else:
                q = Q(entregable__nombre__icontains=search) | Q(entregable__momento__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__componente__nombre__icontains=search) | Q(padre = 'sede&{0}'.format(radicado.id))
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACCIONES
            """
            ret = ''

            if row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id) or row.padre == 'sede&ruta&{0}'.format(self.ruta.id):

                if self.request.user.has_perms(self.permissions.get('actividades')):
                    ret = '<div class="center-align">' \
                                '<a href="cargar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver archivos">' \
                                    '<i class="material-icons">cloud_upload</i>' \
                                '</a>' \
                          '</div>'.format(row.id)

                else:
                    ret = '<div class="center-align">' \
                                '<i class="material-icons">cloud_upload</i>' \
                          '</div>'

            elif row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):

                if self.request.user.has_perms(self.permissions.get('retoma')):
                    ret = '<div class="center-align">' \
                                '<a href="retoma/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver retomas">' \
                                    '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                                '</a>' \
                          '</div>'.format(row.id)

                else:
                    ret = '<div class="center-align">' \
                                '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                          '</div>'

            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    if self.request.user.has_perms(self.permissions.get('actividades')):
                        ret = '<div class="center-align">' \
                                    '<a href="radicado/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades Radicado: {1}">' \
                                        '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                                    '</a>' \
                              '</div>'.format(row.get_radicado().id, row.get_radicado().numero)
                    else:
                        ret = '<div class="center-align">' \
                                    '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                              '</div>'
                else:
                    pass

            else:
                raise NotImplementedError("Noesta definida la estrategia")

            return ret

        elif column == 'tipo':
            """
            TIPO
            """
            if row.estado == 'Cerrado':
                return '<div class="center-align">' \
                            '<a class="tooltipped" data-position = "top" data-delay="50" data-tooltip="Liquidación">' \
                                '<span class="material-icons" style="font-size: 1.5rem;color:red;">error</span>' \
                                '<span style="font-weight: bold;color: #000;">{0}</span>' \
                            '</a>' \
                       '</div>'.format(row.tipo)
            else:
                return row.tipo

        elif column == 'entregable':
            """
            NOMBRE
            """
            if row.entregable.tipo == 'sede':
                return 'Radicado: {0}'.format(row.get_radicado().numero)

            else:
                if row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                    return 'Retoma'
                else:
                    return row.entregable.nombre

        elif column == 'estado':
            """
            NOVEDADES
            """
            if row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id) or row.padre == 'sede&ruta&{0}'.format(self.ruta.id):
                novedad = self.ruta.get_novedades_sede_ruta(row)
                if novedad > 0:
                    return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedad)
                else:
                    return ''


            elif row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                novedades = self.ruta.get_novedades_ruta_estrategia_retoma()
                if novedades > 0:
                    return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedades)
                else:
                    return ''


            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    novedad = self.ruta.get_novedades_sede_radicado(row.get_radicado().id)
                    if novedad > 0:
                        return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedad)
                    else:
                        return ''

            else:
                return ''

        elif column == 'valor':
            """
            VALOR MAXIMO
            """
            if row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id) or row.padre == 'sede&ruta&{0}'.format(self.ruta.id):
                return '<div class="center-align"><b>{0}</b></div>'.format(row.pretty_print_valor())


            elif row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                return '<div class="center-align"><b>{0}</b></div>'.format(
                    '$ {:20,.2f}'.format(row.ruta.valor_ruta_entregable_estrategia(row.entregable))
                )


            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    return '<div class="center-align"><b>{0}</b></div>'.format(
                        '$ {:20,.2f}'.format(row.get_radicado_valor(self.ruta))
                    )
                else:
                    pass

            return ''

        elif column == 'orden':
            """
            MOMENTO
            """
            if row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id):
                name = row.entregable.momento.nombre
                color = '#1a237e'

            elif row.padre == 'sede&ruta&{0}'.format(self.ruta.id):
                name = row.entregable.momento.nombre
                color = '#ffab00'

            elif row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                name = row.entregable.momento.nombre
                color = '#7b1fa2'


            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    name = 'Radicado'
                    color = '#388e3c'

            else:
                name = ''
                color = ''


            return '<div class="center-align">' \
                           '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{0}">' \
                                '<i style = "color:{1};" class="material-icons">{2}</i>' \
                           '</a>' \
                       '</div>'.format(name, color, row.entregable.momento.icon if row.entregable != None else 'accessibility')

        elif column == 'padre':
            """
            PROGRESO
            """
            if row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id):
                progreso, valor_reportado, valor_pagado = row.ruta.progreso_sede_ruta_si_formacion_entregable(row.entregable)
                return '<div class="center-align">' \
                       '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                       'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                       '<b>{0}</b>' \
                       '</a>' \
                       '</div>'.format(progreso, valor_reportado, valor_pagado)

            elif row.padre == 'sede&ruta&{0}'.format(self.ruta.id):
                progreso, valor_reportado, valor_pagado = row.ruta.progreso_sede_ruta_entregable(row.entregable)
                return '<div class="center-align">' \
                       '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                       'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                       '<b>{0}</b>' \
                       '</a>' \
                       '</div>'.format(progreso, valor_reportado, valor_pagado)

            elif row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                progreso, valor_reportado, valor_pagado = row.ruta.progreso_ruta_entregable_estrategia(row.entregable)
                return '<div class="center-align">' \
                        '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                       'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                        '<b>{0}</b>' \
                        '</a>' \
                        '</div>'.format(progreso, valor_reportado, valor_pagado)


            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    progreso, valor_reportado, valor_pagado = row.ruta.progreso_ruta_radicado(row.entregable,row.get_radicado())
                    return '<div class="center-align">' \
                           '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                           'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                           '<b>{0}</b>' \
                           '</a>' \
                           '</div>'.format(progreso, valor_reportado, valor_pagado)
                else:
                    return ''

        elif column == 'para_pago':

            """
            VALIDO
            """

            valido = "No"

            if row.para_pago:
                valido = 'Si'

            if row.padre == 'sede&ruta&{0}'.format(self.ruta.id):

                if row.estado == 'Reportado' or row.estado == 'asignado':

                    return '<div class="center-align">' \
                           '<a href="toogle/{0}" class="tooltipped" data-position="left" data-delay="50" ' \
                           'data-tooltip="Cambiar estado">' \
                           '<b>{1}</b>' \
                           '</a>' \
                           '</div>'.format(row.id, valido)

                else:
                    return '<div class="center-align">' \
                           '<b>{0}</b>' \
                           '</div>'.format(valido)

            else:
                return ''


        else:
            return super(ActividadesComponenteRutaListApi, self).render_column(row, column)

class ActividadesRetomaRutaListApi(BaseDatatableView):
    model = models.Retoma
    columns = ['id','ruta','radicado','fecha','red','municipio','bolsas','cedula','perifericos']
    order_columns = ['id','ruta','radicado','fecha','red','municipio','bolsas','cedula','perifericos']

    def get_initial_queryset(self):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "ver_retomas": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.ver".format(self.region.numero)
            ],
            "crear_retoma": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.crear".format(self.region.numero)
            ],
            "editar_retoma": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.editar".format(self.region.numero)
            ],
            "eliminar_retoma": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.retoma.eliminar".format(self.region.numero)
            ]
        }
        return self.model.objects.filter(ruta__id = self.kwargs['pk_ruta']).order_by('fecha')

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(municipio__nombre__icontains=search) | Q(municipio__departamento__nombre__icontains=search) | \
                Q(radicado__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            EDITAR
            """
            if self.request.user.has_perms(self.permissions.get('editar_retoma')):

                if row.estado == 'Nuevo' or row.estado == 'Actualizado':

                    ret = '<div class="center-align">' \
                               '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar retoma del radicado {1}">' \
                                    '<i class="material-icons">edit</i>' \
                               '</a>' \
                           '</div>'.format(row.id,row.radicado)
                else:
                    ret = '<div class="center-align">' \
                          '<i class="material-icons">edit</i>' \
                          '</div>'.format(row.id, row.radicado)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.radicado)

            return ret

        elif column == 'radicado':
            return '<div class="center-align">' \
                       '<a href="verificar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="Verificar retoma">' \
                            '<b>{1}</b>' \
                       '</a>' \
                   '</div>'.format(row.id,row.radicado)


        elif column == 'ruta':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('ver_retomas')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver retoma del radicado {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.radicado)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.radicado)

            return ret

        elif column == 'red':
            """
            RED
            """
            if row.red == None:
                return ''
            else:
                return '<div class="center-align"><b>RED {0}</b></div>'.format(row.red.consecutivo)

        elif column == 'municipio':
            """
            MUNICIPIO
            """
            return str(row.municipio)

        elif column == 'bolsas':
            """
            CANTIDAD
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><b>{0}</b><span class="nuevo badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas,row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><b>{0}</b><span class="actualizado badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas, row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><b>{0}</b><span class="aprobado badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas, row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><b>{0}</b><span class="rechazado badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas, row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><b>{0}</b><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.bolsas, row.estado)
            else:
                return '<div class="center-align"><b>{0}</b><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.bolsas)

        elif column == 'cedula':
            """
            VALOR
            """
            return '<div class="center-align"><b>{0}</b></div>'.format(self.ruta.get_valor_ruta_estrategia_id(row.id))

        elif column == 'perifericos':
            """
            ELIMINAR
            """
            if self.request.user.has_perms(self.permissions.get('eliminar_retoma')) and row.estado == 'Nuevo' and row.red == None:
                ret = '<div class="center-align">' \
                           '<a href="eliminar/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar retoma">' \
                                '<i class="material-icons">delete</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.pretty_print_valor())

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">delete</i>' \
                       '</div>'.format(row.id,row.pretty_print_valor())

            return ret

        else:
            return super(ActividadesRetomaRutaListApi, self).render_column(row, column)

class ActividadesSedeRutaListApi(BaseDatatableView):

    columns = ['id','ver','nombre','estado','valor','file']
    order_columns = ['id','ver','nombre','estado','valor','file']

    def get_initial_queryset(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "ver_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero)
            ],
            "editar_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.editar".format(self.region.numero)
            ],
            "eliminar_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.eliminar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            return modelo.objects.filter(ruta = self.ruta)
        else:
            raise NotImplementedError("EL modelo no esta establecido")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            EDITAR
            """
            if self.request.user.has_perms(self.permissions.get('editar_actividades')) and row.estado != 'Aprobado':

                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'

            return ret

        elif column == 'ver':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('ver_actividades')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'nombre':
            """
            NOMBRE
            """
            return row.nombre

        elif column == 'estado':
            """
            ESTADO
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><span class="actualizado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><span class="aprobado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><span class="rechazado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.estado)
            else:
                return '<div class="center-align"><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.estado)

        elif column == 'valor':
            """
            VALOR
            """
            return  '<div class="center-align"><b>{0}</b></div>'.format(self.objeto_ruta.get_valor_si_calificado())

        elif column == 'file':
            """
            ELIMINAR
            """

            if self.request.user.has_perms(self.permissions.get('eliminar_actividades')) and row.estado != 'Aprobado':
                ret = '<div class="center-align">' \
                           '<a href="eliminar/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar">' \
                                '<i class="material-icons">delete</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">delete</i>' \
                       '</div>'.format(row.id)

            return ret

        else:
            return super(ActividadesSedeRutaListApi, self).render_column(row, column)

class ActividadesComponenteRadicadoRutaListApi(BaseDatatableView):

    model = models.EntregableRutaObject
    columns = ['id','orden','entregable','estado','valor','padre','para_pago']
    order_columns = ['id','orden','entregable','estado','valor','padre','para_pago']

    def get_initial_queryset(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])

        self.permissions = {
            "actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero)
            ]
        }

        query = self.model.objects.filter(ruta = self.ruta, radicado=self.radicado)
        return self.model.objects.filter(id__in = query.values_list('id',flat=True))

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(entregable__nombre__icontains=search) | Q(entregable__momento__nombre__icontains=search) | \
                Q(entregable__momento__estrategia__nombre__icontains=search) | \
                Q(entregable__momento__estrategia__componente__nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACCIONES
            """
            if self.request.user.has_perms(self.permissions.get('actividades')):

                ret = '<div class="center-align">' \
                      '<a href="cargar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar archivo">' \
                      '<i class="material-icons">cloud_upload</i>' \
                      '</a>' \
                      '</div>'.format(row.id)
            else:
                ret = '<div class="center-align">' \
                            '<i class="material-icons">cloud_upload</i>' \
                      '</div>'

            return ret

        elif column == 'orden':
            """
            MOMENTO
            """
            return '<div class="center-align">' \
                            '<p>{0}</p>' \
                       '</div>'.format(row.entregable.momento.nombre)

        elif column == 'entregable':
            """
            NOMBRE
            """
            return row.entregable.nombre

        elif column == 'estado':
            """
            NOVEDADES
            """
            novedades = self.ruta.get_novedades_sede(row, self.radicado)
            if novedades > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedades)
            else:
                return ''

        elif column == 'valor':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>{0}</b></div>'.format(row.pretty_print_valor())

        elif column == 'padre':
            """
            PROGRESO
            """
            progreso, valor_reportado, valor_pagado = row.ruta.progreso_ruta_entregable_radicado(row.entregable, self.radicado)
            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(progreso, valor_reportado, valor_pagado)

        elif column == 'para_pago':

            """
            VALIDO
            """

            valido = "No"

            if row.para_pago:
                valido = 'Si'

            if row.estado == 'Reportado' or row.estado == 'asignado':

                return '<div class="center-align">' \
                       '<a href="toogle/{0}" class="tooltipped" data-position="left" data-delay="50" ' \
                       'data-tooltip="Cambiar estado">' \
                       '<b>{1}</b>' \
                       '</a>' \
                       '</div>'.format(row.id, valido)

            else:
                return '<div class="center-align">' \
                       '<b>{0}</b>' \
                       '</div>'.format(valido)


        else:
            return super(ActividadesComponenteRadicadoRutaListApi, self).render_column(row, column)

class ActividadesSedeListApi(BaseDatatableView):

    columns = ['id','ver','nombre','estado','red','valor','file']
    order_columns = ['id','ver','nombre','estado','red','valor','file']

    def get_initial_queryset(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "ver_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero)
            ],
            "editar_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.editar".format(self.region.numero)
            ],
            "eliminar_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.sedes.actividades.eliminar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']
            return modelo.objects.filter(ruta = self.ruta, radicado = self.radicado)
        else:
            raise NotImplementedError("EL modelo no esta establecido")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            EDITAR
            """
            if self.request.user.has_perms(self.permissions.get('editar_actividades')):
                if row.estado == 'Nuevo' or row.estado == 'Actualizado':

                    ret = '<div class="center-align">' \
                               '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar {1}">' \
                                    '<i class="material-icons">edit</i>' \
                               '</a>' \
                           '</div>'.format(row.id,row.nombre)

                else:
                    ret = '<div class="center-align">' \
                          '<i class="material-icons">edit</i>' \
                          '</div>'

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'

            return ret

        elif column == 'ver':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('ver_actividades')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'nombre':
            """
            NOMBRE
            """
            return row.nombre

        elif column == 'estado':
            """
            ESTADO
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><span class="actualizado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><span class="aprobado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><span class="rechazado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.estado)
            else:
                return '<div class="center-align"><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.estado)

        elif column == 'red':
            """
            RED
            """
            if row.red == None:
                return ''
            else:
                return '<div class="center-align"><b>RED {0}</b></div>'.format(row.red.consecutivo)

        elif column == 'valor':
            """
            VALOR
            """
            return  '<div class="center-align"><b>{0}</b></div>'.format(self.objeto_ruta.get_valor_si_calificado())

        elif column == 'file':
            """
            ELIMINAR
            """

            if self.request.user.has_perms(self.permissions.get('eliminar_actividades')) and row.estado == 'Nuevo' and row.red == None:
                ret = '<div class="center-align">' \
                           '<a href="eliminar/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar">' \
                                '<i class="material-icons">delete</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">delete</i>' \
                       '</div>'.format(row.id)

            return ret

        else:
            return super(ActividadesSedeRutaListApi, self).render_column(row, column)

#----------------------------------------------------------------------------------


#----------------------------------- FORMACIÓN ------------------------------------

class GruposRutaListApi(BaseDatatableView):
    model = models.Grupos
    columns = ['id','creation','usuario_creacion','numero','estrategia','ruta','update_datetime']
    order_columns = ['id','creation','usuario_creacion','numero','estrategia','ruta','update_datetime']

    def get_initial_queryset(self):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.permissions = {
            "editar_grupos": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.editar".format(self.region.numero)
            ],
            "ver_actividades_grupos": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.ver".format(self.region.numero)
            ],
            "ver_docentes": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.docentes.ver".format(self.region.numero)
            ]
        }
        return self.model.objects.filter(ruta__id = self.kwargs['pk_ruta'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(numero__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            EDITAR
            """
            if self.request.user.has_perms(self.permissions.get('editar_grupos')):
                ret = '<div class="center-align">' \
                      '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar el grupo {1}">' \
                      '<i class="material-icons">edit</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.get_nombre_grupo())

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id, row.get_nombre_grupo())
            return ret

        elif column == 'creation':
            """
            ACTIVIDADES
            """
            if self.request.user.has_perms(self.permissions.get('ver_actividades_grupos')):

                ret = '<div class="center-align">' \
                           '<a href="actividades/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades del grupo {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.get_nombre_grupo())

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.get_nombre_grupo())

            return ret

        elif column == 'usuario_creacion':
            """
            DOCENTES
            """
            if self.request.user.has_perms(self.permissions.get('ver_docentes')):

                ret = '<div class="center-align">' \
                           '<a href="docentes/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="Ver el listado de docentes del grupo {1}">' \
                                '<b>{2}</b>' \
                           '</a>' \
                       '</div>'.format(row.id,row.get_nombre_grupo(),row.get_cantidad_docentes())

            else:
                ret = '<div class="center-align">' \
                           '<b>{2}</b>' \
                       '</div>'.format(row.id,row.get_nombre_grupo(),row.get_cantidad_docentes())

            return ret

        elif column == 'numero':
            """
            NOMBRE
            """
            return '<div class="center-align">' \
                        '<b>{0}</b>' \
                    '</div>'.format(row.get_nombre_grupo())

        elif column == 'estrategia':
            """
            NOVEDADES
            """
            novedad = row.get_novedades()
            if novedad > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedad)
            else:
                return ''

        elif column == 'ruta':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>$ {:20,.2f}</b></div>'.format(row.get_valor_maximo())

        elif column == 'update_datetime':
            """
            PROGRESO
            """
            progreso, valor_reportado, valor_pagado = row.get_progreso()
            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(progreso, valor_reportado, valor_pagado)

        else:
            return super(GruposRutaListApi, self).render_column(row, column)

class DocentesGrupoRutaListApi(BaseDatatableView):
    model = models.Docentes
    columns = ['cedula','nombre','municipio','estrategia','actividades','valor_unitario','valor_total','id','sede']
    order_columns = ['cedula','nombre','municipio','estrategia','actividades','valor_unitario','valor_total','id','sede']

    def get_initial_queryset(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])

        ids_docentes = models.EntregableRutaObject.objects.filter(ruta=self.ruta,padre='docente&{0}&{1}'.format(self.ruta.id,self.grupo.id),tipo='Docente').values_list('docente__id',flat = True)

        return self.model.objects.filter(id__in = ids_docentes)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(cedula__icontains=search) | Q(nombre__icontains=search) | Q(municipio__nombre__icontains=search) \
                | Q(municipio__departamento__nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):
        if column == 'estrategia':
            return str(row.estrategia.nombre)
        elif column == 'cedula':

            estado = row.get_estado(self.ruta,self.grupo)

            if self.request.user.is_superuser and estado == 'Activo':
                return '<div class="center-align"><a href="verificar/{1}/"><b>{0}</b></a></div>'.format(row.cedula,row.id)
            else:
                return row.cedula

        elif column == 'municipio':
            return str(row.municipio)
        elif column == 'actividades':
            return '<div class="center-align">{0}</div>'.format(row.get_actividades_docentes(self.ruta, self.grupo))
        elif column == 'valor_unitario':
            return '<div class="center-align"><b>{0}</b></div>'.format('${:20,.2f}'.format(row.get_valor_unitario_docentes(self.ruta, self.grupo)))
        elif column == 'valor_total':
            return '<div class="center-align"><b>{0}</b></div>'.format('${:20,.2f}'.format(row.get_valor_total_docentes(self.ruta, self.grupo)))
        elif column == 'id':
            estado = row.get_estado(self.ruta, self.grupo)
            progreso, valor = row.get_progreso(self.ruta,self.grupo)

            if self.request.user.is_superuser and estado == 'Activo':
                ret = '<div class="center-align">' \
                            '<a href="retirar/{0}/" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{2}">' \
                                '<b>{1}</b>' \
                            '</a>' \
                      '</div>'.format(row.id,progreso,'$ {:20,.2f}'.format(valor))

                return ret
            else:
                return '<div class="center-align"><b>{0}</b></div>'.format(progreso)

        elif column == 'sede':
            return row.get_estado(self.ruta,self.grupo)
        else:
            return super(DocentesGrupoRutaListApi, self).render_column(row, column)

class ActividadesGrupoRutaListApi(BaseDatatableView):
    model = models.Entregables
    columns = ['id','orden','momento','nombre','numero','tipo','modelo','red']
    order_columns = ['id','orden','momento','nombre','numero','tipo','modelo','red']

    def get_initial_queryset(self):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])

        self.permissions = {
            "cargar_actividades": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.ver".format(self.region.numero)
            ]
        }

        return self.model.objects.filter(tipo = 'docente', momento__estrategia = self.grupo.estrategia)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)

        if search:
            q = Q(nombre__icontains=search) | Q(momento__nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACCIONES
            """
            if self.request.user.has_perms(self.permissions.get('cargar_actividades')):

                ret = '<div class="center-align">' \
                      '<a href="evidencias/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar archivo(s)">' \
                      '<i class="material-icons">cloud_upload</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">cloud_upload</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'orden':
            """
            NUMERO
            """
            return '<div class="center-align"><b>{0}</b></div>'.format(row.orden)

        elif column == 'momento':
            """
            NIVEL
            """
            return '<div class="center-align">{0}</div>'.format(row.momento.nombre)

        elif column == 'numero':
            """
            NOVEDADES
            """
            novedad = row.get_novedades_entregable(self.grupo, row)
            if novedad > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedad)
            else:
                return ''

        elif column == 'tipo':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>$ {:20,.2f}</b></div>'.format(self.grupo.get_valor_maximo_entregable(row))

        elif column == 'modelo':
            """
            PROGRESO
            """
            progreso, valor_reportado, valor_pagado = self.grupo.get_progreso_entregable(row)
            return '<div class="center-align">' \
                   '<a href="liquidacion/{3}/" class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(progreso, valor_reportado, valor_pagado, row.id)


        elif column == 'red':
            """
            TRASLADOS
            """
            return '<div class="center-align"><b>{0}</b></div>'.format(row.get_cantidad_translados(self.ruta,self.grupo))


        else:
            return super(ActividadesGrupoRutaListApi, self).render_column(row, column)

class EvidenciasFormacionRutaListApi(BaseDatatableView):

    columns = ['id','ver','docentes','estado','valor','eliminar']
    order_columns = ['id','ver','docentes','estado','valor','eliminar']

    def get_initial_queryset(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "editar_evidencia": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.editar".format(self.region.numero)
            ],
            "ver_evidencia": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.ver".format(self.region.numero)
            ],
            "eliminar_evidencia": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.rutas.ver",
                "usuarios.cpe_2018.rutas_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.ver".format(self.region.numero),
                "usuarios.cpe_2018.rutas_{0}.grupos.actividades.evidencias.eliminar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
        }

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")

        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            queryset = modelo.objects.filter(grupo=self.grupo, entregable=self.entregable)
            return queryset

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(docentes__nombre__icontains=search) | Q(docentes__cedula__icontains=search)
            qs = qs.filter(q).distinct()
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            EDITAR
            """
            if self.request.user.has_perms(self.permissions.get('editar_evidencia')) and row.estado != 'Aprobado' and row.estado != 'Rechazado':

                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,self.entregable.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,self.entregable.nombre)

            return ret

        elif column == 'ver':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('ver_evidencia')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,self.entregable.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,self.entregable.nombre)

            return ret

        elif column == 'docentes':
            """
            DOCENTES
            """
            ret = ''

            for docente in row.docentes.all():
                ret += '<p><b>{0}</b> - {1}</p>'.format(str(docente.cedula),docente.nombre)

            return '<ul class="collapsible" data-collapsible="accordion">' \
                        '<li>' \
                            '<div class="collapsible-header">' \
                                '<i class="material-icons edit-table">arrow_drop_down_circle</i>' \
                                '{0} Docente(s)' \
                            '</div>' \
                            '<div class="collapsible-body" style="background-color: white;">{1}</div>' \
                        '</li>' \
                   '</ul>'.format(row.docentes.all().count(),ret)

        elif column == 'estado':
            """
            ESTADO
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><span class="actualizado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><span class="aprobado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><span class="rechazado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.estado)
            else:
                return '<div class="center-align"><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.estado)

        elif column == 'valor':
            """
            VALOR
            """
            return  '<div class="center-align"><b>{0}</b></div>'.format(row.get_valor(self.entregable))

        elif column == 'eliminar':
            """
            ELIMINAR
            """
            if self.request.user.has_perms(self.permissions.get('eliminar_evidencia')) and row.estado != 'Aprobado' and row.estado != 'Rechazado':
                ret = '<div class="center-align">' \
                           '<a href="eliminar/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar">' \
                                '<i class="material-icons">delete</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">delete</i>' \
                       '</div>'.format(row.id)

            return ret

        else:
            return super(EvidenciasFormacionRutaListApi, self).render_column(row, column)

class DocentesAutocomplete(autocomplete.Select2QuerySetView):

    def get_results(self, context):

        data = []

        for result in context['object_list']:

            estado = False

            if result.grupo != None and result.estado == 'Si':
                estado = True

            data.append({
                'id': self.get_result_value(result),
                'text': '{0} - {1}'.format(result.cedula, result.nombre),
                'disabled': True if result.grupo != None or result.estado != 'Si' else False,
                'nombre': result.nombre,
                'municipio': result.municipio.nombre,
                'departamento': result.municipio.departamento.nombre,
                'cedula': result.cedula,
                'estado': result.estado,
                'grupo': result.get_nombre_grupo()
            })


        return data

    def get_queryset(self):
        grupo = models.Grupos.objects.get(id = self.kwargs['pk_grupo'])
        region = models.Regiones.objects.get(id = self.kwargs['pk_region'])

        if not self.request.user.is_authenticated:
            return models.Docentes.objects.none()

        qs = models.Docentes.objects.filter(estrategia = grupo.estrategia, municipio__departamento__region = region)

        if self.q:
            q = Q(nombre__icontains = self.q) | Q(cedula__icontains = self.q)
            qs = qs.filter(q)

        return qs


#----------------------------------- MIS RUTAS ------------------------------------

class MisRutasListApi(BaseDatatableView):
    model = models.Rutas
    columns = ['usuario_creacion','nombre','contrato','update_datetime','estado','actividades_json','usuario_actualizacion','id']
    order_columns = ['usuario_creacion','nombre','contrato','update_datetime','estado','actividades_json','usuario_actualizacion','id']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }
        return self.model.objects.filter(contrato__contratista__usuario_asociado = self.request.user).exclude(visible = False)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(contrato__contratista__nombres__icontains=search) |\
                Q(contrato__contratista__apellidos__icontains=search) | Q(contrato__contratista__cedula__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'usuario_creacion':
            """
            ACTIVIDADES
            """
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="actividades/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades de la ruta {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'nombre':
            """
            CODIGO
            """
            return '<div class="center-align">' + row.nombre + '</div>'

        elif column == 'contrato':
            """
            CONTRATO
            """
            return row.contrato.nombre

        elif column == 'update_datetime':
            """
            VALOR
            """
            return row.contrato.pretty_print_valor()

        elif column == 'estado':
            """
            NOVEDADES
            """
            novedad = row.get_novedades_ruta()
            if novedad > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedad)
            else:
                return ''

        elif column == 'actividades_json':
            """
            PROGRESO
            """
            progreso, valor_reportado, valor_pagado = row.progreso_ruta()
            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(progreso, valor_reportado, valor_pagado)

        elif column == 'usuario_actualizacion':
            """
            MAPA
            """
            render = '''<a id="{1}" onclick="mapa_ruta('{1}')" href="#" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver mapa de la ruta: {0}">''' \
                        '<i class="mapa-ruta material-icons">gps_fixed</i>' \
                     '</a>'.format(row.nombre, str(row.id))

            return '<div class="center-align">' + render + '</div>'

        elif column == 'id':
            """
            CUENTAS DE COBRO
            """
            render = '''<a href="cuentas_cobro/{1}/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Gestionar cuentas de cobro de la ruta {0}">''' \
                        '<i class="mapa-ruta material-icons">account_balance_wallet</i>' \
                     '</a>'.format(row.nombre, str(row.id))

            return '<div class="center-align">' + render + '</div>'

        else:
            return super(MisRutasListApi, self).render_column(row, column)

class ActividadesMisRutasListApi(BaseDatatableView):
    model = models.Componentes
    columns = ['id','numero','nombre','tipo','cantidad','modelo']
    order_columns = ['id','numero','nombre','tipo','cantidad','modelo']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }
        if self.ruta.visible:
            return self.model.objects.all()
        else:
            return self.model.objects.none()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(numero__icontains=search) | Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACTIVIDADES
            """

            if row.numero == 1:
                if self.request.user.has_perms(self.permissions.get('all')):
                    ret = '<div class="center-align">' \
                               '<a href="componente/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades de acceso">' \
                                    '<i class="material-icons">remove_red_eye</i>' \
                               '</a>' \
                           '</div>'.format(row.id,row.nombre)
                else:
                    ret = '<div class="center-align">' \
                          '<i class="material-icons">remove_red_eye</i>' \
                          '</div>'

            elif row.numero == 2:
                if self.request.user.has_perms(self.permissions.get('all')):
                    ret = '<div class="center-align">' \
                          '<a href="formacion/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver grupos de formación">' \
                          '<i class="material-icons">remove_red_eye</i>' \
                          '</a>' \
                          '</div>'.format(row.id, row.nombre)
                else:
                    ret = '<div class="center-align">' \
                          '<i class="material-icons">remove_red_eye</i>' \
                          '</div>'

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'numero':
            """
            NUMERO
            """
            return '<div class="center-align"><b>' + str(row.numero) + '</b></div>'

        elif column == 'tipo':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>' + '$ {:20,.2f}'.format(self.ruta.get_valor_componente(row)) + '</b></div>'

        elif column == 'cantidad':
            """
            NOVEDADES
            """
            novedad = self.ruta.get_novedades_componente(row)
            if novedad > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedad)
            else:
                return ''

        elif column == 'modelo':
            """
            PROGRESO
            """
            progreso, valor_reportado, valor_pagado = self.ruta.progreso_ruta_componente(row)
            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(progreso, valor_reportado, valor_pagado)

        else:
            return super(ActividadesMisRutasListApi, self).render_column(row, column)

class ActividadesComponenteMisRutasListApi(BaseDatatableView):
    model = models.EntregableRutaObject
    columns = ['id','tipo','entregable','estado','valor','orden','padre']
    order_columns = ['id','tipo','entregable','estado','valor','orden','padre']

    def get_initial_queryset(self):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        query = self.model.objects.filter(ruta = self.ruta)

        query_ruta_si_formacion = query.filter(padre='sede&ruta&siformacion&{0}'.format(self.ruta.id))
        query_sede_ruta = query.filter(padre='sede&ruta&{0}'.format(self.ruta.id))
        query_ruta_estrategia = query.filter(padre='ruta&estrategia&{0}'.format(self.ruta.id))
        query_sede = query.filter(entregable__tipo='sede')


        if query_ruta_estrategia.count() > 0:
            id = query_ruta_estrategia[0].id
            query_ruta_estrategia = query_ruta_estrategia.filter(id = id)



        if query_sede.count() > 0:
            ids = query_sede.distinct('padre').values_list('id',flat= True)
            query_sede = query_sede.filter(id__in = ids)



        query = query_ruta_si_formacion | query_sede_ruta | query_ruta_estrategia | query_sede

        if self.ruta.visible:
            return self.model.objects.filter(id__in = query.values_list('id',flat=True))
        else:
            return self.model.objects.none()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)

        if search:

            try:
                radicado = models.Radicados.objects.get(numero=search)
            except:
                q = Q(entregable__nombre__icontains=search) | Q(entregable__momento__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__componente__nombre__icontains=search)
            else:
                q = Q(entregable__nombre__icontains=search) | Q(entregable__momento__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__nombre__icontains=search) | \
                    Q(entregable__momento__estrategia__componente__nombre__icontains=search) | Q(padre = 'sede&{0}'.format(radicado.id))
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACCIONES
            """
            ret = ''

            if row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id) or row.padre == 'sede&ruta&{0}'.format(self.ruta.id):

                if self.request.user.has_perms(self.permissions.get('all')):
                    ret = '<div class="center-align">' \
                                '<a href="cargar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver archivos">' \
                                    '<i class="material-icons">cloud_upload</i>' \
                                '</a>' \
                          '</div>'.format(row.id)

                else:
                    ret = '<div class="center-align">' \
                                '<i class="material-icons">cloud_upload</i>' \
                          '</div>'

            elif row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):

                if self.request.user.has_perms(self.permissions.get('all')):
                    ret = '<div class="center-align">' \
                                '<a href="retoma/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver retomas">' \
                                    '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                                '</a>' \
                          '</div>'.format(row.id)

                else:
                    ret = '<div class="center-align">' \
                                '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                          '</div>'

            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    if self.request.user.has_perms(self.permissions.get('all')):
                        ret = '<div class="center-align">' \
                                    '<a href="radicado/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades Radicado: {1}">' \
                                        '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                                    '</a>' \
                              '</div>'.format(row.get_radicado().id, row.get_radicado().numero)
                    else:
                        ret = '<div class="center-align">' \
                                    '<i class="material-icons" style="font-size: 2rem;">remove_red_eye</i>' \
                              '</div>'
                else:
                    pass

            else:
                raise NotImplementedError("Noesta definida la estrategia")

            return ret

        elif column == 'entregable':
            """
            NOMBRE
            """
            if row.entregable.tipo == 'sede':
                return 'Radicado: {0}'.format(row.get_radicado().numero)

            else:
                if row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                    return 'Retoma'
                else:
                    return row.entregable.nombre

        elif column == 'estado':
            """
            NOVEDADES
            """
            if row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id) or row.padre == 'sede&ruta&{0}'.format(self.ruta.id):
                novedad = self.ruta.get_novedades_sede_ruta(row)
                if novedad > 0:
                    return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedad)
                else:
                    return ''


            elif row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                novedades = self.ruta.get_novedades_ruta_estrategia_retoma()
                if novedades > 0:
                    return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedades)
                else:
                    return ''


            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    novedad = self.ruta.get_novedades_sede_radicado(row.get_radicado().id)
                    if novedad > 0:
                        return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedad)
                    else:
                        return ''

            else:
                return ''

        elif column == 'valor':
            """
            VALOR MAXIMO
            """
            if row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id) or row.padre == 'sede&ruta&{0}'.format(self.ruta.id):
                return '<div class="center-align"><b>{0}</b></div>'.format(row.pretty_print_valor())


            elif row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                return '<div class="center-align"><b>{0}</b></div>'.format(
                    '$ {:20,.2f}'.format(row.ruta.valor_ruta_entregable_estrategia(row.entregable))
                )


            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    return '<div class="center-align"><b>{0}</b></div>'.format(
                        '$ {:20,.2f}'.format(row.get_radicado_valor(self.ruta))
                    )
                else:
                    pass

            return ''

        elif column == 'orden':
            """
            MOMENTO
            """
            if row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id):
                name = row.entregable.momento.nombre
                color = '#1a237e'

            elif row.padre == 'sede&ruta&{0}'.format(self.ruta.id):
                name = row.entregable.momento.nombre
                color = '#ffab00'

            elif row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                name = row.entregable.momento.nombre
                color = '#7b1fa2'


            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    name = 'Radicado'
                    color = '#388e3c'

            else:
                name = ''
                color = ''


            return '<div class="center-align">' \
                           '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{0}">' \
                                '<i style = "color:{1};" class="material-icons">{2}</i>' \
                           '</a>' \
                       '</div>'.format(name, color, row.entregable.momento.icon if row.entregable != None else 'accessibility')

        elif column == 'padre':
            """
            PROGRESO
            """
            if row.padre == 'sede&ruta&siformacion&{0}'.format(self.ruta.id):
                progreso, valor_reportado, valor_pagado = row.ruta.progreso_sede_ruta_si_formacion_entregable(row.entregable)
                return '<div class="center-align">' \
                       '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                       'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                       '<b>{0}</b>' \
                       '</a>' \
                       '</div>'.format(progreso, valor_reportado, valor_pagado)

            elif row.padre == 'sede&ruta&{0}'.format(self.ruta.id):
                progreso, valor_reportado, valor_pagado = row.ruta.progreso_sede_ruta_entregable(row.entregable)
                return '<div class="center-align">' \
                       '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                       'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                       '<b>{0}</b>' \
                       '</a>' \
                       '</div>'.format(progreso, valor_reportado, valor_pagado)

            elif row.padre == 'ruta&estrategia&{0}'.format(self.ruta.id):
                progreso, valor_reportado, valor_pagado = row.ruta.progreso_ruta_entregable_estrategia(row.entregable)
                return '<div class="center-align">' \
                        '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                       'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                        '<b>{0}</b>' \
                        '</a>' \
                        '</div>'.format(progreso, valor_reportado, valor_pagado)


            elif row.entregable != None:
                if row.entregable.tipo == 'sede':
                    progreso, valor_reportado, valor_pagado = row.ruta.progreso_ruta_radicado(row.entregable,row.get_radicado())
                    return '<div class="center-align">' \
                           '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                           'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                           '<b>{0}</b>' \
                           '</a>' \
                           '</div>'.format(progreso, valor_reportado, valor_pagado)
                else:
                    return ''

        else:
            return super(ActividadesComponenteMisRutasListApi, self).render_column(row, column)

class ActividadesRetomaMisRutasListApi2(BaseDatatableView):
    model = models.Retoma
    columns = ['id','ruta','radicado','fecha','municipio','bolsas','cedula','perifericos']
    order_columns = ['id','ruta','radicado','fecha','municipio','bolsas','cedula','perifericos']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }
        if self.ruta.visible:
            return self.model.objects.filter(ruta__id=self.kwargs['pk_ruta']).order_by('fecha')
        else:
            return self.model.objects.none()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(municipio__nombre__icontains=search) | Q(municipio__departamento__nombre__icontains=search) | \
                Q(radicado__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            EDITAR
            """
            ret = '<div class="center-align">' \
                  '<i class="material-icons">edit</i>' \
                  '</div>'.format(row.id, row.radicado)

            return ret

        elif column == 'ruta':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver retoma del radicado {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.radicado)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.radicado)

            return ret

        elif column == 'municipio':
            """
            MUNICIPIO
            """
            return str(row.municipio)

        elif column == 'bolsas':
            """
            CANTIDAD
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><b>{0}</b><span class="nuevo badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas,row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><b>{0}</b><span class="actualizado badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas, row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><b>{0}</b><span class="aprobado badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas, row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><b>{0}</b><span class="rechazado badge" data-badge-caption="{1}"></span></div>'.format(row.bolsas, row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><b>{0}</b><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.bolsas, row.estado)
            else:
                return '<div class="center-align"><b>{0}</b><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.bolsas)

        elif column == 'cedula':
            """
            VALOR
            """
            return '<div class="center-align"><b>{0}</b></div>'.format(self.ruta.get_valor_ruta_estrategia_id(row.id))

        elif column == 'perifericos':
            """
            ELIMINAR
            """
            ret = '<div class="center-align">' \
                  '<i class="material-icons">delete</i>' \
                  '</div>'.format(row.id, row.pretty_print_valor())

            return ret

        else:
            return super(ActividadesRetomaMisRutasListApi2, self).render_column(row, column)

class ActividadesSedeMisRutasListApi(BaseDatatableView):

    columns = ['id','ver','nombre','estado','valor','file']
    order_columns = ['id','ver','nombre','estado','valor','file']

    def get_initial_queryset(self):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'evento_municipal': {
                'modelo': models.EventoMunicipal,
                'registro': models.RegistroEventoMunicipal,
                'formulario': forms.EventoMunicipalForm
            },
            'evento_institucional': {
                'modelo': models.EventoInstitucional,
                'registro': models.RegistroEventoInstitucional,
                'formulario': forms.EventoInstitucionalForm
            },
            'acta_postulacion': {
                'modelo': models.ActaPostulacion,
                'registro': models.RegistroActaPostulacion,
                'formulario': forms.ActaPostulacionForm
            },
            'base_datos_postulante': {
                'modelo': models.BaseDatosPostulante,
                'registro': models.RegistroBaseDatosPostulante,
                'formulario': forms.BaseDatosPostulanteForm
            },
            'actualizacion_directorio_sedes': {
                'modelo': models.ActualizacionDirectorioSedes,
                'registro': models.RegistroActualizacionDirectorioSedes,
                'formulario': forms.ActualizacionDirectorioSedesForm
            },
            'actualizacion_directorio_municipios': {
                'modelo': models.ActualizacionDirectorioMunicipios,
                'registro': models.RegistroActualizacionDirectorioMunicipios,
                'formulario': forms.ActualizacionDirectorioMunicipiosForm
            },
            'cronograma_talleres': {
                'modelo': models.CronogramaTalleres,
                'registro': models.RegistroCronogramaTalleres,
                'formulario': forms.CronogramaTalleresForm
            },
            'documento_legalizacion': {
                'modelo': models.DocumentoLegalizacion,
                'registro': models.RegistroDocumentoLegalizacion,
                'formulario': forms.DocumentoLegalizacionForm
            },
            'relatoria_graduacion_docentes': {
                'modelo': models.RelatoriaGraduacionDocentes,
                'registro': models.RegistroRelatoriaGraduacionDocentes,
                'formulario': forms.RelatoriaGraduacionDocentesForm
            },
            'talleres_fomento_uso': {
                'modelo': None,
                'registro': None,
                'formulario': None
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']

            if self.ruta.visible:
                return modelo.objects.filter(ruta=self.ruta)
            else:
                return modelo.objects.none()
        else:
            raise NotImplementedError("EL modelo no esta establecido")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            EDITAR
            """
            ret = '<div class="center-align">' \
                  '<i class="material-icons">edit</i>' \
                  '</div>'

            return ret

        elif column == 'ver':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'nombre':
            """
            NOMBRE
            """
            return row.nombre

        elif column == 'estado':
            """
            ESTADO
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><span class="actualizado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><span class="aprobado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><span class="rechazado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.estado)
            else:
                return '<div class="center-align"><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.estado)

        elif column == 'valor':
            """
            VALOR
            """
            return  '<div class="center-align"><b>{0}</b></div>'.format(self.objeto_ruta.get_valor_si_calificado())

        elif column == 'file':
            """
            ELIMINAR
            """

            ret = '<div class="center-align">' \
                  '<i class="material-icons">delete</i>' \
                  '</div>'

            return ret

        else:
            return super(ActividadesSedeMisRutasListApi, self).render_column(row, column)

class ActividadesComponenteRadicadoMisRutasListApi(BaseDatatableView):

    model = models.EntregableRutaObject
    columns = ['id','orden','entregable','estado','valor','padre']
    order_columns = ['id','orden','entregable','estado','valor','padre']

    def get_initial_queryset(self):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        query = self.model.objects.filter(ruta = self.ruta, padre='sede&{0}'.format(self.radicado.id))

        if self.ruta.visible:
            return self.model.objects.filter(id__in=query.values_list('id', flat=True))
        else:
            return self.model.objects.none()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(entregable__nombre__icontains=search) | Q(entregable__momento__nombre__icontains=search) | \
                Q(entregable__momento__estrategia__nombre__icontains=search) | \
                Q(entregable__momento__estrategia__componente__nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACCIONES
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                      '<a href="cargar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar archivo">' \
                      '<i class="material-icons">cloud_upload</i>' \
                      '</a>' \
                      '</div>'.format(row.id)
            else:
                ret = '<div class="center-align">' \
                            '<i class="material-icons">cloud_upload</i>' \
                      '</div>'

            return ret

        elif column == 'orden':
            """
            MOMENTO
            """
            return '<div class="center-align">' \
                            '<p>{0}</p>' \
                       '</div>'.format(row.entregable.momento.nombre)

        elif column == 'entregable':
            """
            NOMBRE
            """
            return row.entregable.nombre

        elif column == 'estado':
            """
            NOVEDADES
            """
            novedades = self.ruta.get_novedades_sede(row, self.radicado)
            if novedades > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedades)
            else:
                return ''

        elif column == 'valor':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>{0}</b></div>'.format(row.pretty_print_valor())

        elif column == 'padre':
            """
            PROGRESO
            """
            progreso, valor_reportado, valor_pagado = row.ruta.progreso_ruta_entregable_radicado(row.entregable, self.radicado)
            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(progreso, valor_reportado, valor_pagado)

        else:
            return super(ActividadesComponenteRadicadoMisRutasListApi, self).render_column(row, column)

class ActividadesRadicadoSedeMisRutasListApi(BaseDatatableView):

    columns = ['id','ver','nombre','estado','valor','file']
    order_columns = ['id','ver','nombre','estado','valor','file']

    def get_initial_queryset(self):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.componente = models.Componentes.objects.get(id=self.kwargs['pk_componente'])
        self.radicado = models.Radicados.objects.get(id=self.kwargs['pk_radicado'])
        self.objeto_ruta = models.EntregableRutaObject.objects.get(id=self.kwargs['pk_objeto'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales,
                'formulario': forms.DocumentoLegalizacionTerminalesForm
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura,
                'formulario': forms.RelatoriaTallerAperturaForm
            },
            'cuenticos_taller_apertura': {
                'modelo': models.CuenticosTallerApertura,
                'registro': models.RegistroCuenticosTallerApertura,
                'formulario': forms.CuenticosTallerAperturaForm
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic,
                'formulario': forms.RelatoriaTallerAdministraticForm
            },
            'infotic_taller_administratic': {
                'modelo': models.InfoticTallerAdministratic,
                'registro': models.RegistroInfoticTallerAdministratic,
                'formulario': forms.InfoticTallerAdministraticForm
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos,
                'formulario': forms.RelatoriaTallerContenidosEducativosForm
            },
            'dibuarte_taller_contenidos_educativos': {
                'modelo': models.DibuarteTallerContenidosEducativos,
                'registro': models.RegistroDibuarteTallerContenidosEducativos,
                'formulario': forms.DibuarteTallerContenidosEducativosForm
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE,
                'formulario': forms.RelatoriaTallerRAEEForm
            },
            'ecoraee_taller_raee': {
                'modelo': models.EcoraeeTallerRAEE,
                'registro': models.RegistroEcoraeeTallerRAEE,
                'formulario': forms.EcoraeeTallerRAEEForm
            },
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo,
                'formulario': forms.EncuestaMonitoreoForm
            }
        }

        if self.objeto_ruta.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.objeto_ruta.entregable.modelo)['modelo']


            if self.ruta.visible:
                return modelo.objects.filter(ruta=self.ruta, radicado=self.radicado)
            else:
                return modelo.objects.none()

        else:
            raise NotImplementedError("EL modelo no esta establecido")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            EDITAR
            """
            ret = '<div class="center-align">' \
                  '<i class="material-icons">edit</i>' \
                  '</div>'

            return ret

        elif column == 'ver':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'nombre':
            """
            NOMBRE
            """
            return row.nombre

        elif column == 'estado':
            """
            ESTADO
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><span class="actualizado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><span class="aprobado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><span class="rechazado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.estado)
            else:
                return '<div class="center-align"><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.estado)

        elif column == 'valor':
            """
            VALOR
            """
            return  '<div class="center-align"><b>{0}</b></div>'.format(self.objeto_ruta.get_valor_si_calificado())

        elif column == 'file':
            """
            ELIMINAR
            """

            ret = '<div class="center-align">' \
                  '<i class="material-icons">delete</i>' \
                  '</div>'.format(row.id)

            return ret

        else:
            return super(ActividadesRadicadoSedeMisRutasListApi, self).render_column(row, column)

class GruposMisRutasListApi(BaseDatatableView):
    model = models.Grupos
    columns = ['id','creation','usuario_creacion','numero','estrategia','ruta','update_datetime']
    order_columns = ['id','creation','usuario_creacion','numero','estrategia','ruta','update_datetime']

    def get_initial_queryset(self):
        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        if self.ruta.visible:
            return self.model.objects.filter(ruta__id=self.kwargs['pk_ruta'])
        else:
            return self.model.objects.none()



    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(numero__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            EDITAR
            """
            ret = '<div class="center-align">' \
                  '<i class="material-icons">edit</i>' \
                  '</div>'.format(row.id, row.get_nombre_grupo())
            return ret

        elif column == 'creation':
            """
            ACTIVIDADES
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                           '<a href="actividades/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades del grupo {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.get_nombre_grupo())

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.get_nombre_grupo())

            return ret

        elif column == 'usuario_creacion':
            """
            DOCENTES
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                           '<a href="docentes/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="Ver el listado de docentes del grupo {1}">' \
                                '<b>{2}</b>' \
                           '</a>' \
                       '</div>'.format(row.id,row.get_nombre_grupo(),row.get_cantidad_docentes())

            else:
                ret = '<div class="center-align">' \
                           '<b>{2}</b>' \
                       '</div>'.format(row.id,row.get_nombre_grupo(),row.get_cantidad_docentes())

            return ret

        elif column == 'numero':
            """
            NOMBRE
            """
            return '<div class="center-align">' \
                        '<b>{0}</b>' \
                    '</div>'.format(row.get_nombre_grupo())

        elif column == 'estrategia':
            """
            NOVEDADES
            """
            novedad = row.get_novedades()
            if novedad > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedad)
            else:
                return ''

        elif column == 'ruta':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>$ {:20,.2f}</b></div>'.format(row.get_valor_maximo())

        elif column == 'update_datetime':
            """
            PROGRESO
            """
            progreso, valor_reportado, valor_pagado = row.get_progreso()
            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(progreso, valor_reportado, valor_pagado)

        else:
            return super(GruposMisRutasListApi, self).render_column(row, column)

class DocentesGrupoMisRutasListApi(BaseDatatableView):
    model = models.Docentes
    columns = ['cedula','nombre','municipio','estrategia','sede','telefono','registro','estado']
    order_columns = ['cedula','nombre','municipio','estrategia','sede','telefono','registro','estado']

    def get_initial_queryset(self):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])

        if self.ruta.visible:
            return self.model.objects.filter(grupo__id=self.kwargs['pk_grupo'])
        else:
            return self.model.objects.none()



    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(cedula__icontains=search) | Q(nombre__icontains=search) | Q(municipio__nombre__icontains=search) \
                | Q(municipio__departamento__nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):
        if column == 'estrategia':
            return str(row.estrategia.nombre)
        elif column == 'municipio':
            return str(row.municipio)
        else:
            return super(DocentesGrupoMisRutasListApi, self).render_column(row, column)

class ActividadesGrupoMisRutasListApi(BaseDatatableView):
    model = models.Entregables
    columns = ['id','orden','momento','nombre','numero','tipo','modelo']
    order_columns = ['id','orden','momento','nombre','numero','tipo','modelo']

    def get_initial_queryset(self):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        if self.ruta.visible:
            return self.model.objects.filter(tipo='docente', momento__estrategia=self.grupo.estrategia)
        else:
            return self.model.objects.none()



    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)

        if search:
            q = Q(nombre__icontains=search) | Q(momento__nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACCIONES
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                      '<a href="evidencias/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar archivo(s)">' \
                      '<i class="material-icons">cloud_upload</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">cloud_upload</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'orden':
            """
            NUMERO
            """
            return '<div class="center-align"><b>{0}</b></div>'.format(row.orden)

        elif column == 'momento':
            """
            MOMENTO
            """
            return row.momento.nombre

        elif column == 'numero':
            """
            NOVEDADES
            """
            novedad = row.get_novedades_entregable(self.grupo, row)
            if novedad > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedad)
            else:
                return ''

        elif column == 'tipo':
            """
            VALOR MAXIMO
            """
            return '<div class="center-align"><b>$ {:20,.2f}</b></div>'.format(self.grupo.get_valor_maximo_entregable(row))

        elif column == 'modelo':
            """
            PROGRESO
            """
            progreso, valor_reportado, valor_pagado = self.grupo.get_progreso_entregable(row)
            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="<p>Proximo corte: {1}</p><p>Reportado: {2}</p>">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(progreso, valor_reportado, valor_pagado)

        else:
            return super(ActividadesGrupoMisRutasListApi, self).render_column(row, column)

class EvidenciasFormacionMisRutasListApi(BaseDatatableView):

    columns = ['id','ver','docentes','estado','valor','eliminar']
    order_columns = ['id','ver','docentes','estado','valor','eliminar']

    def get_initial_queryset(self):

        self.ruta = models.Rutas.objects.get(id=self.kwargs['pk_ruta'])
        self.grupo = models.Grupos.objects.get(id=self.kwargs['pk_grupo'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }

        self.modelos = {
            'documento_compromiso_inscripcion': {
                'modelo': models.DocumentoCompromisoInscripcion,
                'registro': models.RegistroDocumentoCompromisoInscripcion,
                'formulario': forms.DocumentoCompromisoInscripcionForm
            },
            'instrumento_autoreporte': {
                'modelo': models.InstrumentoAutoreporte,
                'registro': models.RegistroInstrumentoAutoreporte,
                'formulario': forms.InstrumentoAutoreporteForm
            },
            'instrumento_evaluacion': {
                'modelo': models.InstrumentoEvaluacion,
                'registro': models.RegistroInstrumentoEvaluacion,
                'formulario': forms.InstrumentoEvaluacionForm
            },
            'acta_posesion_docente': {
                'modelo': models.ActaPosesionDocente,
                'registro': models.RegistroActaPosesionDocente,
                'formulario': forms.ActaPosesionDocenteForm
            },
            'base_datos_docentes': {
                'modelo': models.BaseDatosDocentes,
                'registro': models.RegistroBaseDatosDocentes,
                'formulario': forms.BaseDatosDocentesForm
            },
            'documento_proyeccion_cronograma': {
                'modelo': models.DocumentoProyeccionCronograma,
                'registro': models.RegistroDocumentoProyeccionCronograma,
                'formulario': forms.DocumentoProyeccionCronogramaForm
            },
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia,
                'formulario': forms.ListadoAsistenciaForm
            },
            'instrumento_estructuracion_ple': {
                'modelo': models.InstrumentoEstructuracionPle,
                'registro': models.RegistroInstrumentoEstructuracionPle,
                'formulario': forms.InstrumentoEstructuracionPleForm
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle,
                'formulario': forms.ProductoFinalPleForm
            },
            'presentacion_apa': {
                'modelo': models.PresentacionApa,
                'registro': models.RegistroPresentacionApa,
                'formulario': forms.PresentacionApaForm
            },
            'instrumento_hagamos_memoria': {
                'modelo': models.InstrumentoHagamosMemoria,
                'registro': models.RegistroInstrumentoHagamosMemoria,
                'formulario': forms.InstrumentoHagamosMemoriaForm
            },
            'presentacion_actividad_pedagogica': {
                'modelo': models.PresentacionActividadPedagogica,
                'registro': models.RegistroPresentacionActividadPedagogica,
                'formulario': forms.PresentacionActividadPedagogicaForm
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades,
                'formulario': forms.RepositorioActividadesForm
            },
            'sistematizacion_experiencia': {
                'modelo': models.SistematizacionExperiencia,
                'registro': models.RegistroSistematizacionExperiencia,
                'formulario': forms.SistematizacionExperienciaForm
            }
        }

        if self.entregable.modelo not in self.modelos.keys():
            raise NotImplementedError("EL modelo no esta establecido")

        else:
            modelo = self.modelos[self.entregable.modelo]['modelo']
            queryset = modelo.objects.filter(grupo=self.grupo, entregable=self.entregable)

            if self.ruta.visible:
                return queryset
            else:
                return modelo.objects.none()



    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(docentes__nombre__icontains=search) | Q(docentes__cedula__icontains=search)
            qs = qs.filter(q).distinct()
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            EDITAR
            """
            ret = '<div class="center-align">' \
                  '<i class="material-icons">edit</i>' \
                  '</div>'.format(row.id, self.entregable.nombre)

            return ret

        elif column == 'ver':
            """
            VER
            """
            if self.request.user.has_perms(self.permissions.get('all')):

                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,self.entregable.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,self.entregable.nombre)

            return ret

        elif column == 'docentes':
            """
            DOCENTES
            """
            ret = ''

            for docente in row.docentes.all():
                ret += '<p><b>{0}</b> - {1}</p>'.format(str(docente.cedula),docente.nombre)

            return '<ul class="collapsible" data-collapsible="accordion">' \
                        '<li>' \
                            '<div class="collapsible-header">' \
                                '<i class="material-icons edit-table">arrow_drop_down_circle</i>' \
                                '{0} Docente(s)' \
                            '</div>' \
                            '<div class="collapsible-body" style="background-color: white;">{1}</div>' \
                        '</li>' \
                   '</ul>'.format(row.docentes.all().count(),ret)

        elif column == 'estado':
            """
            ESTADO
            """
            if row.estado == 'Nuevo':
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><span class="actualizado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><span class="aprobado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><span class="rechazado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.estado)
            else:
                return '<div class="center-align"><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.estado)

        elif column == 'valor':
            """
            VALOR
            """
            return  '<div class="center-align"><b>{0}</b></div>'.format(row.get_valor(self.entregable))

        elif column == 'eliminar':
            """
            ELIMINAR
            """
            ret = '<div class="center-align">' \
                  '<i class="material-icons">delete</i>' \
                  '</div>'.format(row.id)

            return ret

        else:
            return super(EvidenciasFormacionMisRutasListApi, self).render_column(row, column)

#----------------------------------------------------------------------------------

class CortesRegionListApi(BaseDatatableView):
    model = models.Cortes
    columns = ['id','consecutivo','creation','descripcion','corte','usuario_creacion','valor','file']
    order_columns = ['id','consecutivo','creation','descripcion','corte','usuario_creacion','valor','file']

    def get_initial_queryset(self):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])

        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.cortes.ver"
            ]
        }
        return self.model.objects.filter(region__id = self.kwargs['pk'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(descripcion__icontains=search) | Q(consecutivo=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver cuentas de cobro corte {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.consecutivo)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'consecutivo':
            return '<div class="center-align"><b>' + str(row.consecutivo) + '</b></div>'

        elif column == 'creation':
            return row.pretty_creation_datetime()

        elif column == 'corte':
            return '<div class="center-align"><b>' + str(row.get_cantidad_cuentas_cobro()) + '</b></div>'

        elif column == 'usuario_creacion':
            novedad = row.get_novedades()
            if novedad > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedad)
            else:
                return ''

        elif column == 'valor':
            return '<b>${:20,.2f}</b>'.format(row.get_valor())

        elif column == 'file':
            if row.url_file() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file(),'Descargar archivo')
            else:
                ret = ''

            return ret

        else:
            return super(CortesRegionListApi, self).render_column(row, column)

class CortesRegionCuentasCobroListApi(BaseDatatableView):
    model = models.CuentasCobro
    columns = ['id','html','ruta','creation','estado','delta','usuario_creacion','data_json','valores_json','file','file2']
    order_columns = ['id','html','ruta','creation','estado','delta','usuario_creacion','data_json','valores_json','file','file2']

    def get_initial_queryset(self):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.corte = models.Cortes.objects.get(id=self.kwargs['pk_corte'])

        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.cortes.ver"
            ],
            "cuentas_cobro_editar": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.cortes.ver",
                "usuarios.cpe_2018.cortes.cuentas_cobro.ver",
                "usuarios.cpe_2018.cortes.cuentas_cobro.editar"
            ],
            "cuentas_cobro_cargar": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.cortes.ver",
                "usuarios.cpe_2018.cortes.cuentas_cobro.ver",
                "usuarios.cpe_2018.cortes.cuentas_cobro.cargar"
            ],
            "cuentas_cobro_estado": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.cortes.ver",
                "usuarios.cpe_2018.cortes.cuentas_cobro.ver",
                "usuarios.cpe_2018.cortes.cuentas_cobro.estado"
            ]
        }
        return self.model.objects.filter(corte__id = self.kwargs['pk_corte'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(ruta__nombre__icontains=search) | Q(ruta__contrato__nombre__icontains=search) | \
                Q(ruta__contrato__contratista__nombres__icontains=search) | Q(ruta__contrato__contratista__apellidos__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('cuentas_cobro_editar')) and row.estado != 'Reportado':
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Generar cuenta de cobro {1}">' \
                                '<i class="material-icons">build</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.ruta.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">build</i>' \
                       '</div>'

            return ret

        elif column == 'html':
            if self.request.user.has_perms(self.permissions.get('cuentas_cobro_cargar')) and row.estado != 'Creado' and row.estado != 'Reportado':
                ret = '<div class="center-align">' \
                           '<a href="cargar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cargar cuenta de cobro {1}">' \
                                '<i class="material-icons">cloud_upload</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.ruta.nombre)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">cloud_upload</i>' \
                       '</div>'

            return ret

        elif column == 'ruta':
            return '<div class="center-align"><b>' + str(row.ruta.nombre) + '</b></div>'

        elif column == 'creation':
            return '{0} - {1}'.format(row.ruta.contrato.nombre,row.ruta.contrato.contratista)

        elif column == 'estado':

            if self.request.user.is_superuser:

                ret = '<div class="center-align">' \
                            '<a href="estado/{0}/">' \
                                '<span><b>{1}</b></span>' \
                            '</a>' \
                      '</div>'.format(row.id, row.estado)

            elif self.request.user.has_perms(self.permissions.get('cuentas_cobro_estado')) and row.estado != 'Generado' and row.estado != 'Creado' and row.estado != 'Reportado':
                ret = '<div class="center-align">' \
                      '<a href="estado/{0}/">' \
                      '<span><b>{1}</b></span>' \
                      '</a>' \
                      '</div>'.format(row.id, row.estado)

            else:
                ret = '<div class="center-align">' \
                            '<span>{1}</span>' \
                      '</div>'.format(row.id, row.estado)

            return ret

        elif column == 'delta':
            if row.estado == 'Cargado':
                return '<span class="new badge" data-badge-caption="">1</span>'
            elif row.estado =="Reportado":
                return '<div class="center-align">' \
                            '<a class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Reportado por: {0}">' \
                                '<i class="material-icons">verified_user</i>' \
                            '</a>' \
                      '</div>'.format(row.usuario_actualizacion.get_full_name_string())
            else:
                return ''

        elif column == 'usuario_creacion':
            return '<b>${:20,.2f}</b>'.format(row.valor.amount)

        elif column == 'data_json':
            return row.ruta.contrato.inicio

        elif column == 'valores_json':
            return row.ruta.contrato.fin

        elif column == 'file':
            if row.url_file() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file(),'Descargar archivo')
            else:
                ret = ''

            return ret

        elif column == 'file2':
            if row.url_file2() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file2(),'Descargar archivo')
            else:
                ret = ''

            return ret

        else:
            return super(CortesRegionCuentasCobroListApi, self).render_column(row, column)


class MisRutasCuentasCobroListApi(BaseDatatableView):
    model = models.CuentasCobro
    columns = ['id','corte','creation','valor','estado','file','file2','valores_json']
    order_columns = ['id','corte','creation','valor','estado','file','file2','valores_json']

    def get_initial_queryset(self):
        self.permissions = {
            "all": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.misrutas.ver"
            ]
        }
        return self.model.objects.filter(ruta__id = self.kwargs['pk_ruta']).exclude(estado = 'Creado')


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(corte__consecutivo=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):




        if column == 'id':

            if row.corte != None:
                consecutivo = row.corte.consecutivo
            else:
                consecutivo = 'Liquidación'


            if self.request.user.has_perms(self.permissions.get('all')) and row.estado != 'Reportado':
                ret = '<div class="center-align">' \
                           '<a href="cargar/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Cargar cuenta de cobro Corte {1}">' \
                                '<i class="material-icons">cloud_upload</i>' \
                           '</a>' \
                       '</div>'.format(row.id,consecutivo)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">cloud_upload</i>' \
                       '</div>'

            return ret

        if column == 'corte':
            if row.corte != None:
                return '<div class="center-align"><b>' + str(row.corte.consecutivo) + '</b></div>'
            else:
                return 'Liquidación'

        elif column == 'creation':
            return '<div>' + row.pretty_creation_datetime() + '</div>'

        elif column == 'valor':
            return '<div class="center-align"><b>{0}</b></div>'.format('{:20,.2f}'.format(row.valor.amount))

        elif column == 'estado':
            ret = ''

            if row.estado == 'Reportado':
                ret = '<div class="center-align">' \
                            '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="La cuenta de cobro se reporto para pago">' \
                                '<b>{0}</b>' \
                            '</a>' \
                      '</div>'.format(row.estado)

            elif row.estado == 'Cargado':
                ret = '<div class="center-align">' \
                            '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="La cuenta de cobro se encuentra en revisión">' \
                                '<b>{0}</b>' \
                            '</a>' \
                      '</div>'.format(row.estado)

            elif row.estado == 'Generado':
                ret = '<div class="center-align">' \
                            '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="Por favor firma y carga la cuenta de cobro">' \
                                '<b>{0}</b>' \
                            '</a>' \
                      '</div>'.format(row.estado)

            elif row.estado == 'Pendiente':
                ret = '<div class="center-align">' \
                            '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<b>{0}</b>' \
                            '</a>' \
                      '</div>'.format(row.estado,row.observaciones)

            return ret

        elif column == 'file':
            if row.url_file() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file(),'Descargar archivo')
            else:
                ret = ''

            return ret

        elif column == 'file2':
            if row.url_file2() != None:
                ret = '<div class="center-align">' \
                            '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                                '<i class="material-icons">insert_drive_file</i>' \
                            '</a>' \
                      '</div>'.format(row.url_file2(),'Descargar archivo')
            else:
                ret = ''

            return ret

        elif column == 'valores_json':
            ret = '<div class="center-align">' \
                        '<a href="detalle/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{1}">' \
                            '<i class="material-icons">assignment</i>' \
                        '</a>' \
                  '</div>'.format(row.id,'Ver detalle de actividades')

            return ret

        else:
            return super(MisRutasCuentasCobroListApi, self).render_column(row, column)


#------------------------------------- REDS ---------------------------------------

class RedRegionListApi(BaseDatatableView):
    model = models.Red
    columns = ['id','region','consecutivo','estrategia','creation','usuario_creacion','update_datetime','file']
    order_columns = ['id','region','consecutivo','estrategia','creation','usuario_creacion','update_datetime','file']

    def get_initial_queryset(self):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero)
            ],
            "editar": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.red_{0}.editar".format(self.region.numero)
            ]
        }
        return self.model.objects.filter(region = self.region)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(consecutivo=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar RED {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.consecutivo)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'

            return ret

        elif column == 'region':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="ver/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver soportes del RED {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.consecutivo)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'consecutivo':
            return '<div class="center-align"><b>' + str(row.consecutivo) + '</b></div>'

        elif column == 'creation':
            return row.pretty_creation_datetime()

        elif column == 'usuario_creacion':
            return row.usuario_creacion.get_full_name_string()

        elif column == 'update_datetime':
            novedades = row.get_novedades_red()
            if novedades > 0:
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(
                    novedades)
            else:
                return ''

        elif column == 'file':
            ret = ''
            if row.url_file() != None:
                ret += '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Formato generado">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a></div>'.format(row.url_file())
            elif row.url_file2() != None:
                ret += '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Retroalimentación">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a></div>'.format(row.url_file2())

            return ret

        else:
            return super(RedRegionListApi, self).render_column(row, column)


class RedRegionVerApi(BaseDatatableView):

    def get_order_columns(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])

        if self.red.estrategia == 'Acceso':
            order_columns = ['id','nombre','orden','tipo']

        elif self.red.estrategia == 'Formación':
            order_columns = ['id', 'nombre', 'numero', 'cantidad']

        else:
            order_columns = []

        return order_columns

    def get_columns(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])

        if self.red.estrategia == 'Acceso':
            order_columns = ['id','nombre','orden','tipo']

        elif self.red.estrategia == 'Formación':
            order_columns = ['id', 'nombre', 'numero', 'cantidad']

        else:
            order_columns = []

        return order_columns

    def get_initial_queryset(self):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero)
            ]
        }

        if self.red.estrategia == 'Acceso':
            self.model = models.Entregables
            return self.model.objects.filter(red='red_acceso')

        elif self.red.estrategia == 'Formación':
            self.model = models.Estrategias
            return self.model.objects.all().exclude(nombre = 'Prendo & Aprendo')

        else:
            self.model = models.Entregables
            return self.model.objects.filter(red = 'red_acceso')

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if self.model == models.Entregables:

            if column == 'id':
                if self.request.user.has_perms(self.permissions.get('ver')):
                    ret = '<div class="center-align">' \
                                '<a href="actividades/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver soportes">' \
                                    '<i class="material-icons">remove_red_eye</i>' \
                                '</a>' \
                          '</div>'.format(row.id)

                else:
                    ret = '<div class="center-align">' \
                               '<i class="material-icons">remove_red_eye</i>' \
                           '</div>'

                return ret

            elif column == 'nombre':
                return row.nombre

            elif column == 'orden':
                novedades = row.get_cantidad_novedades_red(self.red)
                if novedades > 0:
                    return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(novedades)
                else:
                    return ''

            elif column == 'tipo':
                return '<div class="center-align"><b>' + str(row.get_cantidad_red(self.red)) + '</b></div>'

            else:
                return super(RedRegionVerApi, self).render_column(row, column)

        elif self.model == models.Estrategias:

            if column == 'id':
                if self.request.user.has_perms(self.permissions.get('ver')):
                    ret = '<div class="center-align">' \
                                '<a href="formacion/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver soportes">' \
                                    '<i class="material-icons">remove_red_eye</i>' \
                                '</a>' \
                          '</div>'.format(row.id)

                else:
                    ret = '<div class="center-align">' \
                               '<i class="material-icons">remove_red_eye</i>' \
                           '</div>'

                return ret

            elif column == 'numero':
                novedades = row.get_cantidad_novedades_red(self.red)
                if novedades > 0:
                    return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(novedades)
                else:
                    return ''

            elif column == 'cantidad':
                return '<div class="center-align"><b>' + str(row.get_cantidad_red(self.red)) + '</b></div>'

            else:
                return super(RedRegionVerApi, self).render_column(row, column)

        else:
            return super(RedRegionVerApi, self).render_column(row, column)


class RedRegionVerEntregablesApi(BaseDatatableView):

    def get_order_columns(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        if self.entregable.modelo == 'retoma':
            order_columns = ['id','radicado','fecha','bolsas','estado','municipio']
        else:
            order_columns = ['id', 'nombre', 'red', 'valor', 'ver','file']

        return order_columns

    def get_columns(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])


        if self.entregable.modelo == 'retoma':
            columns = ['id','radicado','fecha','bolsas','estado','municipio']
        else:
            columns = ['id', 'nombre', 'red', 'valor', 'ver','file']

        return columns

    def get_initial_queryset(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "calificar": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.red_{0}.calificar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'encuesta_monitoreo': {
                'modelo': models.EncuestaMonitoreo,
                'registro': models.RegistroEncuestaMonitoreo
            },
            'documento_legalizacion_terminales': {
                'modelo': models.DocumentoLegalizacionTerminales,
                'registro': models.RegistroDocumentoLegalizacionTerminales
            },
            'documento_legalizacion_terminales_v1': {
                'modelo': models.DocumentoLegalizacionTerminalesValle1,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle1,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle1
            },
            'documento_legalizacion_terminales_v2': {
                'modelo': models.DocumentoLegalizacionTerminalesValle2,
                'registro': models.RegistroDocumentoLegalizacionTerminalesValle2,
                'formulario': forms.DocumentoLegalizacionTerminalesFormValle2
            },
            'relatoria_taller_apertura': {
                'modelo': models.RelatoriaTallerApertura,
                'registro': models.RegistroRelatoriaTallerApertura
            },
            'relatoria_taller_administratic': {
                'modelo': models.RelatoriaTallerAdministratic,
                'registro': models.RegistroRelatoriaTallerAdministratic
            },
            'relatoria_taller_contenidos_educativos': {
                'modelo': models.RelatoriaTallerContenidosEducativos,
                'registro': models.RegistroRelatoriaTallerContenidosEducativos
            },
            'relatoria_taller_raee': {
                'modelo': models.RelatoriaTallerRAEE,
                'registro': models.RegistroRelatoriaTallerRAEE
            },
            'retoma': {
                'modelo': models.Retoma,
                'registro': models.RegistroRetoma
            }
        }

        if self.entregable.modelo in self.modelos.keys():
            modelo = self.modelos.get(self.entregable.modelo)['modelo']
            return modelo.objects.filter(red = self.red)
        else:
            raise NotImplementedError("EL modelo no esta establecido")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            if self.entregable.modelo == 'retoma':
                q = Q(radicado__icontains=search)
            else:
                q = Q(radicado__numero__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('calificar')):
                ret = '<div class="center-align">' \
                            '<a href="calificar/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Calificar soporte">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                            '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'radicado':
            return row.radicado

        elif column == 'fecha':
            return row.ruta.contrato.contratista.get_full_name()

        elif column == 'bolsas':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.bolsas)

        elif column == 'estado':
            if row.estado == 'Nuevo':
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><span class="actualizado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><span class="aprobado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><span class="rechazado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.estado)
            else:
                return '<div class="center-align"><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.estado)

        elif column == 'municipio':
            if row.url_file() != None:
                return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver archivo">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a></div>'.format(row.url_file())


        elif column == 'nombre':
            return row.radicado.numero

        elif column == 'red':
            return row.ruta.contrato.contratista.get_full_name()

        elif column == 'valor':
            return '<div class="center-align"><b>{0}</b></div>'.format(1)

        elif column == 'ver':
            if row.estado == 'Nuevo':
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><span class="actualizado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><span class="aprobado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><span class="rechazado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.estado)
            else:
                return '<div class="center-align"><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.estado)

        elif column == 'file':
            if row.url_file() != None:
                return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver archivo">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a></div>'.format(row.url_file())

        else:
            return super(RedRegionVerEntregablesApi, self).render_column(row, column)


class RedsRegionVerActividadesEstrategiaApi(BaseDatatableView):
    model = models.Entregables
    columns = ['id','orden','momento','nombre','estado','modelo']
    order_columns = ['id','orden','momento','nombre','estado','modelo']

    def get_initial_queryset(self):
        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.estrategia = models.Estrategias.objects.get(id=self.kwargs['pk_estrategia'])

        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero)
            ]
        }

        return self.model.objects.filter(tipo = 'docente', momento__estrategia = self.estrategia, modelo__in = ['listado_asistencia','producto_final_ple','repositorio_actividades'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)

        if search:
            q = Q(nombre__icontains=search) | Q(momento__nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            """
            ACCIONES
            """
            if self.request.user.has_perms(self.permissions.get('ver')):

                ret = '<div class="center-align">' \
                      '<a href="calificar/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver soportes">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'orden':
            """
            NUMERO
            """
            return '<div class="center-align"><b>{0}</b></div>'.format(row.orden)

        elif column == 'momento':
            """
            NIVEL
            """
            return '<div class="center-align">{0}</div>'.format(row.momento.nombre)

        elif column == 'estado':
            novedades = row.get_cantidad_novedades_formacion_red(self.red,self.estrategia)
            if novedades > 0:
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(novedades)
            else:
                return ''

        elif column == 'modelo':
            novedades = row.get_cantidad_formacion_red(self.red,self.estrategia)
            if novedades > 0:
                return '<div class="center-align"><b>{0}</b></div>'.format(novedades)
            else:
                return ''

        else:
            return super(RedsRegionVerActividadesEstrategiaApi, self).render_column(row, column)


class RedRegionVerEntregablesFormacionApi(BaseDatatableView):

    def get_order_columns(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.estrategia = models.Estrategias.objects.get(id=self.kwargs['pk_estrategia'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        order_columns = ['id', 'grupo', 'red', 'valor', 'ver','file']

        return order_columns

    def get_columns(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.estrategia = models.Estrategias.objects.get(id=self.kwargs['pk_estrategia'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        columns = ['id', 'grupo', 'red', 'valor', 'ver','file']

        return columns

    def get_initial_queryset(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])
        self.red = models.Red.objects.get(id=self.kwargs['pk_red'])
        self.estrategia = models.Estrategias.objects.get(id=self.kwargs['pk_estrategia'])
        self.entregable = models.Entregables.objects.get(id=self.kwargs['pk_entregable'])

        self.permissions = {
            "calificar": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.red.ver",
                "usuarios.cpe_2018.red_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.red_{0}.calificar".format(self.region.numero)
            ]
        }

        self.modelos = {
            'listado_asistencia': {
                'modelo': models.ListadoAsistencia,
                'registro': models.RegistroListadoAsistencia
            },
            'producto_final_ple': {
                'modelo': models.ProductoFinalPle,
                'registro': models.RegistroProductoFinalPle
            },
            'repositorio_actividades': {
                'modelo': models.RepositorioActividades,
                'registro': models.RegistroRepositorioActividades
            },
        }

        if self.entregable.modelo in self.modelos.keys():
            self.modelo = self.modelos.get(self.entregable.modelo)['modelo']
            modelo = self.modelos.get(self.entregable.modelo)['modelo']
            return modelo.objects.filter(red = self.red, entregable = self.entregable)
        else:
            raise NotImplementedError("EL modelo no esta establecido")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            if self.entregable.modelo == 'retoma':
                q = Q(radicado__icontains=search)
            else:
                q = Q(radicado__numero__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('calificar')):
                ret = '<div class="center-align">' \
                            '<a href="calificar/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Calificar soporte">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                            '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'grupo':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.grupo.get_nombre_grupo())

        elif column == 'red':
            return row.grupo.ruta.contrato.contratista.get_full_name()

        elif column == 'valor':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.docentes.all().count())

        elif column == 'ver':
            if row.estado == 'Nuevo':
                return '<div class="center-align"><span class="nuevo badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Actualizado':
                return '<div class="center-align"><span class="actualizado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Aprobado':
                return '<div class="center-align"><span class="aprobado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Rechazado':
                return '<div class="center-align"><span class="rechazado badge" data-badge-caption="{0}"></span></div>'.format(row.estado)
            elif row.estado == 'Solicitud de subsanación':
                return '<div class="center-align"><span class="subsanacion badge" data-badge-caption="Subsanación"></span></div>'.format(row.estado)
            else:
                return '<div class="center-align"><span class="new badge" data-badge-caption="Nuevo"></span></div>'.format(row.estado)

        elif column == 'file':
            if row.url_file() != None:
                return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver archivo">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a></div>'.format(row.url_file())

        else:
            return super(RedRegionVerEntregablesFormacionApi, self).render_column(row, column)

#----------------------------------------------------------------------------------

class InformesMatriculaAPI(APIView):
    """
    """


    def get(self, request, pk, format=None):


        labels = []
        datasets = []
        label = ''

        informe = request.query_params.get('informe')
        municipios = json.loads(request.query_params.get('municipios'))

        region = models.Regiones.objects.get(id = pk)



        if informe == '0' or informe == "null":

            if len(municipios) == 0:

                label = 'Conformación de grupos'
                datasets = [
                    {
                        'label': 'Grupos conformados',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for departamento in models.Departamentos.objects.filter(region = region).order_by('nombre'):
                    labels.append(departamento.nombre)
                    cantidad = models.Docentes.objects.filter(municipio__departamento=departamento).exclude(grupo__ruta=None).values_list('grupo', flat=True).distinct().count()
                    datasets[0]['data'].append(cantidad)

            else:

                label = 'Conformación de grupos (municipios)'
                datasets = [
                    {
                        'label': 'Grupos conformados',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for municipio in models.Municipios.objects.filter(departamento__region = region).filter(id__in = municipios).order_by('nombre'):
                    labels.append(municipio.nombre)
                    cantidad = models.Docentes.objects.filter(municipio = municipio).exclude(grupo__ruta=None).values_list('grupo', flat=True).distinct().count()
                    datasets[0]['data'].append(cantidad)



        elif informe == '1':

            if len(municipios) == 0:

                label = 'Docentes inscritos y matriculados'
                datasets = [
                    {
                        'label': 'Matriculados',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Pendientes',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for departamento in models.Departamentos.objects.filter(region=region).order_by('nombre'):
                    labels.append(departamento.nombre)

                    matriculados = models.Docentes.objects.filter(municipio__departamento=departamento,estado__in = ["Si","si"]).exclude(grupo__ruta = None).count()
                    pendientes = models.Docentes.objects.filter(municipio__departamento=departamento,estado__in = ["Si","si"]).count() - matriculados

                    datasets[0]['data'].append(matriculados)
                    datasets[1]['data'].append(pendientes)


            else:

                label = 'Docentes inscritos y matriculados (municipios)'
                datasets = [
                    {
                        'label': 'Matriculados',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Pendientes',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for municipio in models.Municipios.objects.filter(departamento__region = region).filter(id__in = municipios).order_by('nombre'):
                    labels.append(municipio.nombre)

                    matriculados = models.Docentes.objects.filter(municipio = municipio,estado__in=["Si", "si"]).exclude(grupo__ruta=None).count()
                    pendientes = models.Docentes.objects.filter(municipio = municipio,estado__in=["Si", "si"]).count() - matriculados

                    datasets[0]['data'].append(matriculados)
                    datasets[1]['data'].append(pendientes)





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

class InformesSedesAPI(APIView):
    """
    """


    def get(self, request, pk, format=None):


        labels = []
        datasets = []
        label = ''
        modelo = None

        informe = request.query_params.get('informe')
        municipios = json.loads(request.query_params.get('municipios'))

        region = models.Regiones.objects.get(id = pk)



        if informe == '0':
            modelo = models.RelatoriaTallerApertura
            label = "Taller de Apertura"
        elif informe == '1':
            modelo = models.RelatoriaTallerAdministratic
            label = "Taller AdministraTIC"
        elif informe == '2':
            modelo = models.RelatoriaTallerContenidosEducativos
            label = "Taller de Contenidos"
        elif informe == '3':
            modelo = models.RelatoriaTallerRAEE
            label = "Taller RAEE"
        elif informe == '4':
            modelo = models.DocumentoLegalizacionTerminales
            label = "Legalización estudiantes"
        elif informe == '5':
            modelo = models.EncuestaMonitoreo
            label = "Encuesta de monitoreo"


        if len(municipios) == 0:

            datasets = [
                {
                    'label': 'Aprobados',
                    'backgroundColor': "rgba(0,200,83,0.5)",
                    'borderColor': "rgba(0,200,83,1)",
                    'borderWidth': '2',
                    'data': []
                },
                {
                    'label': 'Rechazados',
                    'backgroundColor': "rgba(255,0,0,0.5)",
                    'borderColor': "rgba(255,0,0,1)",
                    'borderWidth': '2',
                    'data': []
                },
                {
                    'label': 'Total',
                    'backgroundColor': "rgba(0,0,255,0.5)",
                    'borderColor': "rgba(0,0,255,1)",
                    'borderWidth': '2',
                    'data': []
                }
            ]

            for departamento in models.Departamentos.objects.filter(region=region).order_by('nombre'):
                labels.append(departamento.nombre)

                radicados = models.Radicados.objects.filter(municipio__departamento=departamento)
                relatorias = modelo.objects.filter(radicado__in = radicados, estado = "Aprobado")

                ids_aprobados = relatorias.values_list('radicado__id',flat = True)

                rechazos = modelo.objects.filter(radicado__in = radicados, estado = "Rechazado").exclude(radicado__id__in = ids_aprobados)


                datasets[0]['data'].append(relatorias.count())
                datasets[1]['data'].append(rechazos.count())
                datasets[2]['data'].append(radicados.count())


        else:

            datasets = [
                {
                    'label': 'Aprobados',
                    'backgroundColor': "rgba(0,200,83,0.5)",
                    'borderColor': "rgba(0,200,83,1)",
                    'borderWidth': '2',
                    'data': []
                },
                {
                    'label': 'Rechazados',
                    'backgroundColor': "rgba(255,0,0,0.5)",
                    'borderColor': "rgba(255,0,0,1)",
                    'borderWidth': '2',
                    'data': []
                },
                {
                    'label': 'Total',
                    'backgroundColor': "rgba(0,0,255,0.5)",
                    'borderColor': "rgba(0,0,255,1)",
                    'borderWidth': '2',
                    'data': []
                }
            ]

            for municipio in models.Municipios.objects.filter(departamento__region = region).filter(id__in = municipios).order_by('nombre'):
                labels.append(municipio.nombre)

                radicados = models.Radicados.objects.filter(municipio=municipio)
                relatorias = modelo.objects.filter(radicado__in=radicados,estado="Aprobado")

                ids_aprobados = relatorias.values_list('radicado__id', flat=True)

                rechazos = modelo.objects.filter(radicado__in=radicados, estado="Rechazado").exclude(radicado__id__in=ids_aprobados)

                datasets[0]['data'].append(relatorias.count())
                datasets[1]['data'].append(rechazos.count())
                datasets[2]['data'].append(radicados.count())



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

class InformesRetomaAPI(APIView):
    """
    """


    def get(self, request, pk, format=None):

        labels = []
        datasets = []
        label = ''

        informe = request.query_params.get('informe')
        municipios = json.loads(request.query_params.get('municipios'))

        region = models.Regiones.objects.get(id = pk)



        if informe == '0' or informe == "null":

            if len(municipios) == 0:

                label = 'Equipos retomados'
                datasets = [
                    {
                        'label': 'Equipos',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]


                for departamento in models.Departamentos.objects.filter(region = region).order_by('nombre'):
                    labels.append(departamento.nombre)


                    retomas = models.Retoma.objects.filter(municipio__departamento=departamento, estado = "Aprobado")

                    cpu = retomas.aggregate(Sum('cpu'))['cpu__sum']

                    if cpu == None:
                        cpu = 0

                    trc = retomas.aggregate(Sum('trc'))['trc__sum']

                    if trc == None:
                        trc = 0

                    lcd = retomas.aggregate(Sum('lcd'))['lcd__sum']

                    if lcd == None:
                        lcd = 0

                    portatil = retomas.aggregate(Sum('portatil'))['portatil__sum']

                    if portatil == None:
                        portatil = 0

                    impresora = retomas.aggregate(Sum('impresora'))['impresora__sum']

                    if impresora == None:
                        impresora = 0

                    tableta = retomas.aggregate(Sum('tableta'))['tableta__sum']

                    if tableta == None:
                        tableta = 0

                    equipos = float(cpu) * 0.5 + float(trc) * 0.5 + float(lcd) * 0.5 + float(portatil) * 0.1 + float(impresora) * 0.5 + float(tableta) * 0.033


                    datasets[0]['data'].append(equipos)


            else:

                label = 'Equipos retomados'
                datasets = [
                    {
                        'label': 'Equipos',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for municipio in models.Municipios.objects.filter(departamento__region = region).filter(id__in = municipios).order_by('nombre'):
                    labels.append(municipio.nombre)
                    retomas = models.Retoma.objects.filter(municipio=municipio, estado="Aprobado")

                    cpu = retomas.aggregate(Sum('cpu'))['cpu__sum']

                    if cpu == None:
                        cpu = 0

                    trc = retomas.aggregate(Sum('trc'))['trc__sum']

                    if trc == None:
                        trc = 0

                    lcd = retomas.aggregate(Sum('lcd'))['lcd__sum']

                    if lcd == None:
                        lcd = 0

                    portatil = retomas.aggregate(Sum('portatil'))['portatil__sum']

                    if portatil == None:
                        portatil = 0

                    impresora = retomas.aggregate(Sum('impresora'))['impresora__sum']

                    if impresora == None:
                        impresora = 0

                    tableta = retomas.aggregate(Sum('tableta'))['tableta__sum']

                    if tableta == None:
                        tableta = 0

                    equipos = float(cpu) * 0.5 + float(trc) * 0.5 + float(lcd) * 0.5 + float(portatil) * 0.1 + float(
                        impresora) * 0.5 + float(tableta) * 0.033

                    datasets[0]['data'].append(equipos)



        elif informe == '1':

            if len(municipios) == 0:

                label = 'Bolsas empacadas'
                datasets = [
                    {
                        'label': 'Bolsas',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]


                for departamento in models.Departamentos.objects.filter(region = region).order_by('nombre'):
                    labels.append(departamento.nombre)


                    retomas = models.Retoma.objects.filter(municipio__departamento=departamento, estado = "Aprobado")

                    bolsas = retomas.aggregate(Sum('bolsas'))['bolsas__sum']

                    datasets[0]['data'].append(bolsas)


            else:

                label = 'Bolsas empacadas'
                datasets = [
                    {
                        'label': 'Bolsas',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for municipio in models.Municipios.objects.filter(departamento__region = region).filter(id__in = municipios).order_by('nombre'):
                    labels.append(municipio.nombre)
                    retomas = models.Retoma.objects.filter(municipio=municipio, estado="Aprobado")

                    bolsas = retomas.aggregate(Sum('bolsas'))['bolsas__sum']

                    datasets[0]['data'].append(bolsas)

        elif informe == '2':

            if len(municipios) == 0:

                label = 'Cantidad de CPU'
                datasets = [
                    {
                        'label': 'CPU',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]


                for departamento in models.Departamentos.objects.filter(region = region).order_by('nombre'):
                    labels.append(departamento.nombre)


                    retomas = models.Retoma.objects.filter(municipio__departamento=departamento, estado = "Aprobado")

                    cpu = retomas.aggregate(Sum('cpu'))['cpu__sum']

                    if cpu == None:
                        cpu = 0


                    datasets[0]['data'].append(cpu)


            else:

                label = 'Cantidad de CPU'
                datasets = [
                    {
                        'label': 'CPU',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for municipio in models.Municipios.objects.filter(departamento__region = region).filter(id__in = municipios).order_by('nombre'):
                    labels.append(municipio.nombre)
                    retomas = models.Retoma.objects.filter(municipio=municipio, estado="Aprobado")

                    cpu = retomas.aggregate(Sum('cpu'))['cpu__sum']

                    if cpu == None:
                        cpu = 0


                    datasets[0]['data'].append(cpu)

        elif informe == '3':

            if len(municipios) == 0:

                label = 'Cantidad de CRT'
                datasets = [
                    {
                        'label': 'CRT',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for departamento in models.Departamentos.objects.filter(region=region).order_by('nombre'):
                    labels.append(departamento.nombre)

                    retomas = models.Retoma.objects.filter(municipio__departamento=departamento, estado="Aprobado")


                    trc = retomas.aggregate(Sum('trc'))['trc__sum']

                    if trc == None:
                        trc = 0



                    datasets[0]['data'].append(trc)


            else:

                label = 'Cantidad de CRT'
                datasets = [
                    {
                        'label': 'CRT',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for municipio in models.Municipios.objects.filter(departamento__region=region).filter(
                        id__in=municipios).order_by('nombre'):
                    labels.append(municipio.nombre)
                    retomas = models.Retoma.objects.filter(municipio=municipio, estado="Aprobado")


                    trc = retomas.aggregate(Sum('trc'))['trc__sum']

                    if trc == None:
                        trc = 0



                    datasets[0]['data'].append(trc)

        elif informe == '4':

            if len(municipios) == 0:

                label = 'Cantidad de LCD'
                datasets = [
                    {
                        'label': 'LCD',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for departamento in models.Departamentos.objects.filter(region=region).order_by('nombre'):
                    labels.append(departamento.nombre)

                    retomas = models.Retoma.objects.filter(municipio__departamento=departamento, estado="Aprobado")



                    lcd = retomas.aggregate(Sum('lcd'))['lcd__sum']

                    if lcd == None:
                        lcd = 0



                    datasets[0]['data'].append(lcd)


            else:

                label = 'Cantidad de LCD'
                datasets = [
                    {
                        'label': 'LCD',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for municipio in models.Municipios.objects.filter(departamento__region=region).filter(
                        id__in=municipios).order_by('nombre'):
                    labels.append(municipio.nombre)
                    retomas = models.Retoma.objects.filter(municipio=municipio, estado="Aprobado")



                    lcd = retomas.aggregate(Sum('lcd'))['lcd__sum']

                    if lcd == None:
                        lcd = 0



                    datasets[0]['data'].append(lcd)

        elif informe == '5':

            if len(municipios) == 0:

                label = 'Cantidad de Portatiles'
                datasets = [
                    {
                        'label': 'Portatiles',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for departamento in models.Departamentos.objects.filter(region=region).order_by('nombre'):
                    labels.append(departamento.nombre)

                    retomas = models.Retoma.objects.filter(municipio__departamento=departamento, estado="Aprobado")



                    portatil = retomas.aggregate(Sum('portatil'))['portatil__sum']

                    if portatil == None:
                        portatil = 0



                    datasets[0]['data'].append(portatil)


            else:

                label = 'Cantidad de Portatiles'
                datasets = [
                    {
                        'label': 'Portatiles',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for municipio in models.Municipios.objects.filter(departamento__region=region).filter(
                        id__in=municipios).order_by('nombre'):
                    labels.append(municipio.nombre)
                    retomas = models.Retoma.objects.filter(municipio=municipio, estado="Aprobado")



                    portatil = retomas.aggregate(Sum('portatil'))['portatil__sum']

                    if portatil == None:
                        portatil = 0



                    datasets[0]['data'].append(portatil)

        elif informe == '6':

            if len(municipios) == 0:

                label = 'Cantidad de Impresoras'
                datasets = [
                    {
                        'label': 'Impresoras',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for departamento in models.Departamentos.objects.filter(region=region).order_by('nombre'):
                    labels.append(departamento.nombre)

                    retomas = models.Retoma.objects.filter(municipio__departamento=departamento, estado="Aprobado")



                    impresora = retomas.aggregate(Sum('impresora'))['impresora__sum']

                    if impresora == None:
                        impresora = 0



                    datasets[0]['data'].append(impresora)


            else:

                label = 'Cantidad de Impresoras'
                datasets = [
                    {
                        'label': 'Impresoras',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for municipio in models.Municipios.objects.filter(departamento__region=region).filter(
                        id__in=municipios).order_by('nombre'):
                    labels.append(municipio.nombre)
                    retomas = models.Retoma.objects.filter(municipio=municipio, estado="Aprobado")



                    impresora = retomas.aggregate(Sum('impresora'))['impresora__sum']

                    if impresora == None:
                        impresora = 0



                    datasets[0]['data'].append(impresora)

        elif informe == '7':

            if len(municipios) == 0:

                label = 'Cantidad de Tabletas'
                datasets = [
                    {
                        'label': 'Tabletas',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for departamento in models.Departamentos.objects.filter(region=region).order_by('nombre'):
                    labels.append(departamento.nombre)

                    retomas = models.Retoma.objects.filter(municipio__departamento=departamento, estado="Aprobado")



                    tableta = retomas.aggregate(Sum('tableta'))['tableta__sum']

                    if tableta == None:
                        tableta = 0



                    datasets[0]['data'].append(tableta)


            else:

                label = 'Cantidad de Tabletas'
                datasets = [
                    {
                        'label': 'Tabletas',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                for municipio in models.Municipios.objects.filter(departamento__region=region).filter(
                        id__in=municipios).order_by('nombre'):
                    labels.append(municipio.nombre)
                    retomas = models.Retoma.objects.filter(municipio=municipio, estado="Aprobado")


                    tableta = retomas.aggregate(Sum('tableta'))['tableta__sum']

                    if tableta == None:
                        tableta = 0


                    datasets[0]['data'].append(tableta)



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

class InformesFormacionAPI(APIView):
    """
    """


    def get(self, request, pk, format=None):

        labels = []
        datasets = []
        label = ''

        informe = request.query_params.get('informe')
        municipios = json.loads(request.query_params.get('municipios'))

        region = models.Regiones.objects.get(id = pk)



        if informe == '0' or informe == "null":

            if len(municipios) == 0:

                label = 'Autoreportes aprobados'
                datasets = [
                    {
                        'label': 'Autoreporte de entrada',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Autoreporte de salida',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                autoreporte_entrada = models.InstrumentoAutoreporte.objects.filter(
                    docentes__municipio__departamento__region = region,
                    docentes__estrategia__nombre__in=["InnovaTIC","RuralTIC"],
                    estado__in = ['Aprobado'],
                    entregable__numero__in = [5,12]
                ).values_list('docentes',flat=True).distinct().count()

                autoreporte_salida = models.InstrumentoAutoreporte.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre__in=["InnovaTIC","RuralTIC"],
                    estado__in=['Aprobado'],
                    entregable__numero__in=[40, 57]
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [autoreporte_entrada]
                datasets[1]['data'] = [autoreporte_salida]


            else:

                label = 'Autoreportes aprobados'
                datasets = [
                    {
                        'label': 'Autoreporte de entrada',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Autoreporte de salida',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                autoreporte_entrada = models.InstrumentoAutoreporte.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre__in=["InnovaTIC","RuralTIC"],
                    docentes__municipio__id__in = municipios,
                    estado__in=['Aprobado'],
                    entregable__numero__in=[5, 12]
                ).values_list('docentes', flat=True).distinct().count()

                autoreporte_salida = models.InstrumentoAutoreporte.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre__in=["InnovaTIC","RuralTIC"],
                    docentes__municipio__id__in=municipios,
                    estado__in=['Aprobado'],
                    entregable__numero__in=[40, 57]
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [autoreporte_entrada]
                datasets[1]['data'] = [autoreporte_salida]

        elif informe == '1':

            if len(municipios) == 0:

                label = 'Autoreportes aprobados InnovaTIC'
                datasets = [
                    {
                        'label': 'Autoreporte de entrada',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Autoreporte de salida',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                autoreporte_entrada = models.InstrumentoAutoreporte.objects.filter(
                    docentes__municipio__departamento__region = region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in = ['Aprobado'],
                    entregable__numero__in = [5,12]
                ).values_list('docentes',flat=True).distinct().count()

                autoreporte_salida = models.InstrumentoAutoreporte.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[40, 57]
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [autoreporte_entrada]
                datasets[1]['data'] = [autoreporte_salida]


            else:

                label = 'Autoreportes aprobados InnovaTIC'
                datasets = [
                    {
                        'label': 'Autoreporte de entrada',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Autoreporte de salida',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                autoreporte_entrada = models.InstrumentoAutoreporte.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    docentes__municipio__id__in = municipios,
                    estado__in=['Aprobado'],
                    entregable__numero__in=[5, 12]
                ).values_list('docentes', flat=True).distinct().count()

                autoreporte_salida = models.InstrumentoAutoreporte.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    docentes__municipio__id__in=municipios,
                    estado__in=['Aprobado'],
                    entregable__numero__in=[40, 57]
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [autoreporte_entrada]
                datasets[1]['data'] = [autoreporte_salida]

        elif informe == '2':

            if len(municipios) == 0:

                label = 'Autoreportes aprobados RuralTIC'
                datasets = [
                    {
                        'label': 'Autoreporte de entrada',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Autoreporte de salida',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                autoreporte_entrada = models.InstrumentoAutoreporte.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[5, 12]
                ).values_list('docentes', flat=True).distinct().count()

                autoreporte_salida = models.InstrumentoAutoreporte.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[40, 57]
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [autoreporte_entrada]
                datasets[1]['data'] = [autoreporte_salida]

            else:

                label = 'Autoreportes aprobados RuralTIC'
                datasets = [
                    {
                        'label': 'Autoreporte de entrada',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Autoreporte de salida',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                autoreporte_entrada = models.InstrumentoAutoreporte.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in = municipios,
                    entregable__numero__in=[5, 12]
                ).values_list('docentes', flat=True).distinct().count()

                autoreporte_salida = models.InstrumentoAutoreporte.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[40, 57]
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [autoreporte_entrada]
                datasets[1]['data'] = [autoreporte_salida]

        elif informe == '3':

            if len(municipios) == 0:

                label = 'Pruebas'
                datasets = [
                    {
                        'label': 'Prueba N1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                n1 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[13]
                ).values_list('docentes', flat=True).distinct().count()

                n2 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[21]
                ).values_list('docentes', flat=True).distinct().count()

                n3 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[29]
                ).values_list('docentes', flat=True).distinct().count()

                n4 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[39]
                ).values_list('docentes', flat=True).distinct().count()




                n1_ = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[18]
                ).values_list('docentes', flat=True).distinct().count()

                n2_ = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[31]
                ).values_list('docentes', flat=True).distinct().count()

                n3_ = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[51]
                ).values_list('docentes', flat=True).distinct().count()

                n4_ = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[56]
                ).values_list('docentes', flat=True).distinct().count()



                datasets[0]['data'] = [n1 + n1_]
                datasets[1]['data'] = [n2 + n2_]
                datasets[2]['data'] = [n3 + n3_]
                datasets[3]['data'] = [n4 + n4_]


            else:

                label = 'Pruebas'
                datasets = [
                    {
                        'label': 'Prueba N1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                n1 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[13]
                ).values_list('docentes', flat=True).distinct().count()

                n2 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[21]
                ).values_list('docentes', flat=True).distinct().count()

                n3 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[29]
                ).values_list('docentes', flat=True).distinct().count()

                n4 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[39]
                ).values_list('docentes', flat=True).distinct().count()



                n1_ = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[18]
                ).values_list('docentes', flat=True).distinct().count()

                n2_ = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[31]
                ).values_list('docentes', flat=True).distinct().count()

                n3_ = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[51]
                ).values_list('docentes', flat=True).distinct().count()

                n4_ = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[56]
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [n1 + n1_]
                datasets[1]['data'] = [n2 + n2_]
                datasets[2]['data'] = [n3 + n3_]
                datasets[3]['data'] = [n4 + n4_]

        elif informe == '4':

            if len(municipios) == 0:

                label = 'Pruebas InnovaTIC'
                datasets = [
                    {
                        'label': 'Prueba N1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                n1 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[13]
                ).values_list('docentes', flat=True).distinct().count()

                n2 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[21]
                ).values_list('docentes', flat=True).distinct().count()

                n3 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[29]
                ).values_list('docentes', flat=True).distinct().count()

                n4 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[39]
                ).values_list('docentes', flat=True).distinct().count()



                datasets[0]['data'] = [n1]
                datasets[1]['data'] = [n2]
                datasets[2]['data'] = [n3]
                datasets[3]['data'] = [n4]


            else:

                label = 'Pruebas InnovaTIC'
                datasets = [
                    {
                        'label': 'Prueba N1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                n1 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[13]
                ).values_list('docentes', flat=True).distinct().count()

                n2 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[21]
                ).values_list('docentes', flat=True).distinct().count()

                n3 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[29]
                ).values_list('docentes', flat=True).distinct().count()

                n4 = models.InstrumentoEvaluacion.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[39]
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [n1]
                datasets[1]['data'] = [n2]
                datasets[2]['data'] = [n3]
                datasets[3]['data'] = [n4]

        elif informe == '5':

            if len(municipios) == 0:

                label = 'Pruebas RuralTIC'
                datasets = [
                    {
                        'label': 'Prueba N1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                n1 = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[18]
                ).values_list('docentes', flat=True).distinct().count()

                n2 = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[31]
                ).values_list('docentes', flat=True).distinct().count()

                n3 = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[51]
                ).values_list('docentes', flat=True).distinct().count()

                n4 = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[56]
                ).values_list('docentes', flat=True).distinct().count()



                datasets[0]['data'] = [n1]
                datasets[1]['data'] = [n2]
                datasets[2]['data'] = [n3]
                datasets[3]['data'] = [n4]


            else:

                label = 'Pruebas RuralTIC'
                datasets = [
                    {
                        'label': 'Prueba N1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'Prueba N4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                n1 = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[18]
                ).values_list('docentes', flat=True).distinct().count()

                n2 = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[31]
                ).values_list('docentes', flat=True).distinct().count()

                n3 = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[51]
                ).values_list('docentes', flat=True).distinct().count()

                n4 = models.InstrumentoHagamosMemoria.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    docentes__municipio__id__in=municipios,
                    entregable__numero__in=[56]
                ).values_list('docentes', flat=True).distinct().count()


                datasets[0]['data'] = [n1]
                datasets[1]['data'] = [n2]
                datasets[2]['data'] = [n3]
                datasets[3]['data'] = [n4]

        elif informe == '6':

            if len(municipios) == 0:

                label = 'Productos finales'
                datasets = [
                    {
                        'label': 'InnovaTIC',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'RuralTIC',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                ple = models.ProductoFinalPle.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[30]
                ).values_list('docentes', flat=True).distinct().count()

                apas = models.RepositorioActividades.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[50]
                ).values_list('docentes', flat=True).distinct().count()



                datasets[0]['data'] = [ple]
                datasets[1]['data'] = [apas]



            else:

                label = 'Productos finales'
                datasets = [
                    {
                        'label': 'InnovaTIC',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'RuralTIC',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                ple = models.ProductoFinalPle.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[30],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                apas = models.RepositorioActividades.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[50],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [ple]
                datasets[1]['data'] = [apas]

        elif informe == '7':

            if len(municipios) == 0:

                label = 'Asistencias N1 InnovaTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S5',
                        'backgroundColor': "rgba(255,83,13,0.5)",
                        'borderColor': "rgba(255,83,13,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S6',
                        'backgroundColor': "rgba(232,174,6,0.5)",
                        'borderColor': "rgba(232,174,6,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S7',
                        'backgroundColor': "rgba(255,8,109,0.5)",
                        'borderColor': "rgba(255,8,109,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S8',
                        'backgroundColor': "rgba(65,91,118,0.5)",
                        'borderColor': "rgba(65,91,118,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S9',
                        'backgroundColor': "rgba(245,155,142,0.5)",
                        'borderColor': "rgba(245,155,142,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[3]
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[4]
                ).values_list('docentes', flat=True).distinct().count()

                s3 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[5]
                ).values_list('docentes', flat=True).distinct().count()

                s4 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[6]
                ).values_list('docentes', flat=True).distinct().count()

                s5 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[7]
                ).values_list('docentes', flat=True).distinct().count()

                s6 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[8]
                ).values_list('docentes', flat=True).distinct().count()

                s7 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[9]
                ).values_list('docentes', flat=True).distinct().count()

                s8 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[10]
                ).values_list('docentes', flat=True).distinct().count()

                s9 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[11]
                ).values_list('docentes', flat=True).distinct().count()




                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]
                datasets[2]['data'] = [s3]
                datasets[3]['data'] = [s4]
                datasets[4]['data'] = [s5]
                datasets[5]['data'] = [s6]
                datasets[6]['data'] = [s7]
                datasets[7]['data'] = [s8]
                datasets[8]['data'] = [s9]


            else:

                label = 'Asistencias N1 InnovaTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S5',
                        'backgroundColor': "rgba(255,83,13,0.5)",
                        'borderColor': "rgba(255,83,13,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S6',
                        'backgroundColor': "rgba(232,174,6,0.5)",
                        'borderColor': "rgba(232,174,6,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S7',
                        'backgroundColor': "rgba(255,8,109,0.5)",
                        'borderColor': "rgba(255,8,109,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S8',
                        'backgroundColor': "rgba(65,91,118,0.5)",
                        'borderColor': "rgba(65,91,118,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S9',
                        'backgroundColor': "rgba(245,155,142,0.5)",
                        'borderColor': "rgba(245,155,142,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[3],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[4],
                docentes__municipio__id__in = municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s3 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[5],
                docentes__municipio__id__in = municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s4 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[6],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s5 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[7],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s6 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[8],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s7 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[9],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s8 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[10],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s9 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[11],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]
                datasets[2]['data'] = [s3]
                datasets[3]['data'] = [s4]
                datasets[4]['data'] = [s5]
                datasets[5]['data'] = [s6]
                datasets[6]['data'] = [s7]
                datasets[7]['data'] = [s8]
                datasets[8]['data'] = [s9]

        elif informe == '8':

            if len(municipios) == 0:

                label = 'Asistencias N2 InnovaTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S5',
                        'backgroundColor': "rgba(255,83,13,0.5)",
                        'borderColor': "rgba(255,83,13,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[15]
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[16]
                ).values_list('docentes', flat=True).distinct().count()

                s3 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[17]
                ).values_list('docentes', flat=True).distinct().count()

                s4 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[18]
                ).values_list('docentes', flat=True).distinct().count()

                s5 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[19]
                ).values_list('docentes', flat=True).distinct().count()






                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]
                datasets[2]['data'] = [s3]
                datasets[3]['data'] = [s4]
                datasets[4]['data'] = [s5]



            else:

                label = 'Asistencias N2 InnovaTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S5',
                        'backgroundColor': "rgba(255,83,13,0.5)",
                        'borderColor': "rgba(255,83,13,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[15],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[16],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s3 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[17],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s4 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[18],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s5 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[19],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]
                datasets[2]['data'] = [s3]
                datasets[3]['data'] = [s4]
                datasets[4]['data'] = [s5]

        elif informe == '9':

            if len(municipios) == 0:

                label = 'Asistencias N3 InnovaTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S5',
                        'backgroundColor': "rgba(255,83,13,0.5)",
                        'borderColor': "rgba(255,83,13,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S6',
                        'backgroundColor': "rgba(232,174,6,0.5)",
                        'borderColor': "rgba(232,174,6,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[23]
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[24]
                ).values_list('docentes', flat=True).distinct().count()

                s3 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[25]
                ).values_list('docentes', flat=True).distinct().count()

                s4 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[26]
                ).values_list('docentes', flat=True).distinct().count()

                s5 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[27]
                ).values_list('docentes', flat=True).distinct().count()

                s6 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[28]
                ).values_list('docentes', flat=True).distinct().count()






                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]
                datasets[2]['data'] = [s3]
                datasets[3]['data'] = [s4]
                datasets[4]['data'] = [s5]
                datasets[5]['data'] = [s6]


            else:

                label = 'Asistencias N3 InnovaTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S5',
                        'backgroundColor': "rgba(255,83,13,0.5)",
                        'borderColor': "rgba(255,83,13,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S6',
                        'backgroundColor': "rgba(232,174,6,0.5)",
                        'borderColor': "rgba(232,174,6,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[23],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[24],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s3 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[25],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s4 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[26],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s5 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[27],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s6 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[28],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]
                datasets[2]['data'] = [s3]
                datasets[3]['data'] = [s4]
                datasets[4]['data'] = [s5]
                datasets[5]['data'] = [s6]

        elif informe == '10':

            if len(municipios) == 0:

                label = 'Asistencias N4 InnovaTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S5',
                        'backgroundColor': "rgba(255,83,13,0.5)",
                        'borderColor': "rgba(255,83,13,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S6',
                        'backgroundColor': "rgba(232,174,6,0.5)",
                        'borderColor': "rgba(232,174,6,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S7',
                        'backgroundColor': "rgba(255,8,109,0.5)",
                        'borderColor': "rgba(255,8,109,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[32]
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[33]
                ).values_list('docentes', flat=True).distinct().count()

                s3 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[34]
                ).values_list('docentes', flat=True).distinct().count()

                s4 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[35]
                ).values_list('docentes', flat=True).distinct().count()

                s5 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[36]
                ).values_list('docentes', flat=True).distinct().count()

                s6 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[37]
                ).values_list('docentes', flat=True).distinct().count()

                s7 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[38]
                ).values_list('docentes', flat=True).distinct().count()






                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]
                datasets[2]['data'] = [s3]
                datasets[3]['data'] = [s4]
                datasets[4]['data'] = [s5]
                datasets[5]['data'] = [s6]
                datasets[6]['data'] = [s7]


            else:

                label = 'Asistencias N4 InnovaTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S5',
                        'backgroundColor': "rgba(255,83,13,0.5)",
                        'borderColor': "rgba(255,83,13,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S6',
                        'backgroundColor': "rgba(232,174,6,0.5)",
                        'borderColor': "rgba(232,174,6,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S7',
                        'backgroundColor': "rgba(255,8,109,0.5)",
                        'borderColor': "rgba(255,8,109,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[32],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[33],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s3 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[34],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s4 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[35],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s5 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[36],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s6 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[37],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s7 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="InnovaTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[38],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]
                datasets[2]['data'] = [s3]
                datasets[3]['data'] = [s4]
                datasets[4]['data'] = [s5]
                datasets[5]['data'] = [s6]
                datasets[6]['data'] = [s7]

        elif informe == '11':

            if len(municipios) == 0:

                label = 'Asistencias N1 RuralTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[3]
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[4]
                ).values_list('docentes', flat=True).distinct().count()


                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]



            else:

                label = 'Asistencias N1 RuralTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[3],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[4],
                docentes__municipio__id__in = municipios,
                ).values_list('docentes', flat=True).distinct().count()



                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]

        elif informe == '12':

            if len(municipios) == 0:

                label = 'Asistencias N2 RuralTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S5',
                        'backgroundColor': "rgba(255,83,13,0.5)",
                        'borderColor': "rgba(255,83,13,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S6',
                        'backgroundColor': "rgba(232,174,6,0.5)",
                        'borderColor': "rgba(232,174,6,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S7',
                        'backgroundColor': "rgba(255,8,109,0.5)",
                        'borderColor': "rgba(255,8,109,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S8',
                        'backgroundColor': "rgba(65,91,118,0.5)",
                        'borderColor': "rgba(65,91,118,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S9',
                        'backgroundColor': "rgba(245,155,142,0.5)",
                        'borderColor': "rgba(245,155,142,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S10',
                        'backgroundColor': "rgba(116,73,65,0.5)",
                        'borderColor': "rgba(116,73,65,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[7]
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[8]
                ).values_list('docentes', flat=True).distinct().count()

                s3 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[9]
                ).values_list('docentes', flat=True).distinct().count()

                s4 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[10]
                ).values_list('docentes', flat=True).distinct().count()

                s5 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[11]
                ).values_list('docentes', flat=True).distinct().count()

                s6 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[12]
                ).values_list('docentes', flat=True).distinct().count()

                s7 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[13]
                ).values_list('docentes', flat=True).distinct().count()

                s8 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[14]
                ).values_list('docentes', flat=True).distinct().count()

                s9 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[15]
                ).values_list('docentes', flat=True).distinct().count()

                s10 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[16]
                ).values_list('docentes', flat=True).distinct().count()






                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]
                datasets[2]['data'] = [s3]
                datasets[3]['data'] = [s4]
                datasets[4]['data'] = [s5]
                datasets[5]['data'] = [s6]
                datasets[6]['data'] = [s7]
                datasets[7]['data'] = [s8]
                datasets[8]['data'] = [s9]
                datasets[9]['data'] = [s10]



            else:

                label = 'Asistencias N2 RuralTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S5',
                        'backgroundColor': "rgba(255,83,13,0.5)",
                        'borderColor': "rgba(255,83,13,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S6',
                        'backgroundColor': "rgba(232,174,6,0.5)",
                        'borderColor': "rgba(232,174,6,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S7',
                        'backgroundColor': "rgba(255,8,109,0.5)",
                        'borderColor': "rgba(255,8,109,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S8',
                        'backgroundColor': "rgba(65,91,118,0.5)",
                        'borderColor': "rgba(65,91,118,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S9',
                        'backgroundColor': "rgba(245,155,142,0.5)",
                        'borderColor': "rgba(245,155,142,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S10',
                        'backgroundColor': "rgba(116,73,65,0.5)",
                        'borderColor': "rgba(116,73,65,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[7],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[8],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s3 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[9],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s4 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[10],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s5 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[11],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s6 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[12],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s7 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[13],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s8 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[14],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s9 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[15],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s10 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[16],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]
                datasets[2]['data'] = [s3]
                datasets[3]['data'] = [s4]
                datasets[4]['data'] = [s5]
                datasets[5]['data'] = [s6]
                datasets[6]['data'] = [s7]
                datasets[7]['data'] = [s8]
                datasets[8]['data'] = [s9]
                datasets[9]['data'] = [s10]

        elif informe == '13':

            if len(municipios) == 0:

                label = 'Asistencias N3 RuralTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S5',
                        'backgroundColor': "rgba(255,83,13,0.5)",
                        'borderColor': "rgba(255,83,13,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S6',
                        'backgroundColor': "rgba(232,174,6,0.5)",
                        'borderColor': "rgba(232,174,6,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S7',
                        'backgroundColor': "rgba(255,8,109,0.5)",
                        'borderColor': "rgba(255,8,109,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S8',
                        'backgroundColor': "rgba(65,91,118,0.5)",
                        'borderColor': "rgba(65,91,118,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S9',
                        'backgroundColor': "rgba(245,155,142,0.5)",
                        'borderColor': "rgba(245,155,142,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S10',
                        'backgroundColor': "rgba(116,73,65,0.5)",
                        'borderColor': "rgba(116,73,65,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[20]
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[21]
                ).values_list('docentes', flat=True).distinct().count()

                s3 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[22]
                ).values_list('docentes', flat=True).distinct().count()

                s4 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[23]
                ).values_list('docentes', flat=True).distinct().count()

                s5 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[24]
                ).values_list('docentes', flat=True).distinct().count()

                s6 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[25]
                ).values_list('docentes', flat=True).distinct().count()

                s7 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[26]
                ).values_list('docentes', flat=True).distinct().count()

                s8 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[27]
                ).values_list('docentes', flat=True).distinct().count()

                s9 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[28]
                ).values_list('docentes', flat=True).distinct().count()

                s10 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[29]
                ).values_list('docentes', flat=True).distinct().count()






                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]
                datasets[2]['data'] = [s3]
                datasets[3]['data'] = [s4]
                datasets[4]['data'] = [s5]
                datasets[5]['data'] = [s6]
                datasets[6]['data'] = [s7]
                datasets[7]['data'] = [s8]
                datasets[8]['data'] = [s9]
                datasets[9]['data'] = [s10]



            else:

                label = 'Asistencias N3 RuralTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S5',
                        'backgroundColor': "rgba(255,83,13,0.5)",
                        'borderColor': "rgba(255,83,13,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S6',
                        'backgroundColor': "rgba(232,174,6,0.5)",
                        'borderColor': "rgba(232,174,6,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S7',
                        'backgroundColor': "rgba(255,8,109,0.5)",
                        'borderColor': "rgba(255,8,109,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S8',
                        'backgroundColor': "rgba(65,91,118,0.5)",
                        'borderColor': "rgba(65,91,118,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S9',
                        'backgroundColor': "rgba(245,155,142,0.5)",
                        'borderColor': "rgba(245,155,142,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S10',
                        'backgroundColor': "rgba(116,73,65,0.5)",
                        'borderColor': "rgba(116,73,65,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[20],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[21],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s3 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[22],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s4 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[23],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s5 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[24],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s6 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[25],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s7 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[26],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s8 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[27],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s9 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[28],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s10 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[29],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]
                datasets[2]['data'] = [s3]
                datasets[3]['data'] = [s4]
                datasets[4]['data'] = [s5]
                datasets[5]['data'] = [s6]
                datasets[6]['data'] = [s7]
                datasets[7]['data'] = [s8]
                datasets[8]['data'] = [s9]
                datasets[9]['data'] = [s10]

        elif informe == '14':

            if len(municipios) == 0:

                label = 'Asistencias N4 RuralTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S5',
                        'backgroundColor': "rgba(255,83,13,0.5)",
                        'borderColor': "rgba(255,83,13,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S6',
                        'backgroundColor': "rgba(232,174,6,0.5)",
                        'borderColor': "rgba(232,174,6,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S7',
                        'backgroundColor': "rgba(255,8,109,0.5)",
                        'borderColor': "rgba(255,8,109,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S8',
                        'backgroundColor': "rgba(65,91,118,0.5)",
                        'borderColor': "rgba(65,91,118,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S9',
                        'backgroundColor': "rgba(245,155,142,0.5)",
                        'borderColor': "rgba(245,155,142,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S10',
                        'backgroundColor': "rgba(116,73,65,0.5)",
                        'borderColor': "rgba(116,73,65,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S11',
                        'backgroundColor': "rgba(172,206,216,0.5)",
                        'borderColor': "rgba(172,206,216,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S12',
                        'backgroundColor': "rgba(161,112,13,0.5)",
                        'borderColor': "rgba(161,112,13,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S13',
                        'backgroundColor': "rgba(43,119,237,0.5)",
                        'borderColor': "rgba(43,119,237,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S14',
                        'backgroundColor': "rgba(59,1,0,0.5)",
                        'borderColor': "rgba(59,1,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S15',
                        'backgroundColor': "rgba(245,233,185,0.5)",
                        'borderColor': "rgba(245,233,185,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S16',
                        'backgroundColor': "rgba(87,191,125,0.5)",
                        'borderColor': "rgba(87,191,125,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[33]
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[34]
                ).values_list('docentes', flat=True).distinct().count()

                s3 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[35]
                ).values_list('docentes', flat=True).distinct().count()

                s4 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[36]
                ).values_list('docentes', flat=True).distinct().count()

                s5 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[37]
                ).values_list('docentes', flat=True).distinct().count()

                s6 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[38]
                ).values_list('docentes', flat=True).distinct().count()

                s7 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[39]
                ).values_list('docentes', flat=True).distinct().count()

                s8 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[40]
                ).values_list('docentes', flat=True).distinct().count()

                s9 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[41]
                ).values_list('docentes', flat=True).distinct().count()

                s10 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[42]
                ).values_list('docentes', flat=True).distinct().count()

                s11 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[43]
                ).values_list('docentes', flat=True).distinct().count()

                s12 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[44]
                ).values_list('docentes', flat=True).distinct().count()

                s13 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[45]
                ).values_list('docentes', flat=True).distinct().count()

                s14 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[46]
                ).values_list('docentes', flat=True).distinct().count()

                s15 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[47]
                ).values_list('docentes', flat=True).distinct().count()

                s16 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[48]
                ).values_list('docentes', flat=True).distinct().count()






                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]
                datasets[2]['data'] = [s3]
                datasets[3]['data'] = [s4]
                datasets[4]['data'] = [s5]
                datasets[5]['data'] = [s6]
                datasets[6]['data'] = [s7]
                datasets[7]['data'] = [s8]
                datasets[8]['data'] = [s9]
                datasets[9]['data'] = [s10]
                datasets[10]['data'] = [s11]
                datasets[11]['data'] = [s12]
                datasets[12]['data'] = [s13]
                datasets[13]['data'] = [s14]
                datasets[14]['data'] = [s15]
                datasets[15]['data'] = [s16]



            else:

                label = 'Asistencias N4 RuralTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S3',
                        'backgroundColor': "rgba(255,0,0,0.5)",
                        'borderColor': "rgba(255,0,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S4',
                        'backgroundColor': "rgba(195,0,255,0.5)",
                        'borderColor': "rgba(195,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S5',
                        'backgroundColor': "rgba(255,83,13,0.5)",
                        'borderColor': "rgba(255,83,13,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S6',
                        'backgroundColor': "rgba(232,174,6,0.5)",
                        'borderColor': "rgba(232,174,6,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S7',
                        'backgroundColor': "rgba(255,8,109,0.5)",
                        'borderColor': "rgba(255,8,109,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S8',
                        'backgroundColor': "rgba(65,91,118,0.5)",
                        'borderColor': "rgba(65,91,118,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S9',
                        'backgroundColor': "rgba(245,155,142,0.5)",
                        'borderColor': "rgba(245,155,142,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S10',
                        'backgroundColor': "rgba(116,73,65,0.5)",
                        'borderColor': "rgba(116,73,65,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S11',
                        'backgroundColor': "rgba(172,206,216,0.5)",
                        'borderColor': "rgba(172,206,216,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S12',
                        'backgroundColor': "rgba(161,112,13,0.5)",
                        'borderColor': "rgba(161,112,13,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S13',
                        'backgroundColor': "rgba(43,119,237,0.5)",
                        'borderColor': "rgba(43,119,237,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S14',
                        'backgroundColor': "rgba(59,1,0,0.5)",
                        'borderColor': "rgba(59,1,0,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S15',
                        'backgroundColor': "rgba(245,233,185,0.5)",
                        'borderColor': "rgba(245,233,185,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S16',
                        'backgroundColor': "rgba(87,191,125,0.5)",
                        'borderColor': "rgba(87,191,125,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[33],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[34],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s3 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[35],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s4 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[36],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s5 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[37],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s6 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[38],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s7 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[39],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s8 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[40],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s9 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[41],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s10 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[42],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s11 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[43],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s12 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[44],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s13 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[45],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s14 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[46],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s15 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[47],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s16 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[48],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]
                datasets[2]['data'] = [s3]
                datasets[3]['data'] = [s4]
                datasets[4]['data'] = [s5]
                datasets[5]['data'] = [s6]
                datasets[6]['data'] = [s7]
                datasets[7]['data'] = [s8]
                datasets[8]['data'] = [s9]
                datasets[9]['data'] = [s10]
                datasets[10]['data'] = [s11]
                datasets[11]['data'] = [s12]
                datasets[12]['data'] = [s13]
                datasets[13]['data'] = [s14]
                datasets[14]['data'] = [s15]
                datasets[15]['data'] = [s16]
        
        elif informe == '15':

            if len(municipios) == 0:

                label = 'Asistencias N5 RuralTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[53]
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[54]
                ).values_list('docentes', flat=True).distinct().count()



                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]




            else:

                label = 'Asistencias N5 RuralTIC'
                datasets = [
                    {
                        'label': 'S1',
                        'backgroundColor': "rgba(0,200,83,0.5)",
                        'borderColor': "rgba(0,200,83,1)",
                        'borderWidth': '2',
                        'data': []
                    },
                    {
                        'label': 'S2',
                        'backgroundColor': "rgba(0,0,255,0.5)",
                        'borderColor': "rgba(0,0,255,1)",
                        'borderWidth': '2',
                        'data': []
                    }
                ]

                s1 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[53],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                s2 = models.ListadoAsistencia.objects.filter(
                    docentes__municipio__departamento__region=region,
                    docentes__estrategia__nombre="RuralTIC",
                    estado__in=['Aprobado'],
                    entregable__numero__in=[54],
                    docentes__municipio__id__in=municipios,
                ).values_list('docentes', flat=True).distinct().count()

                datasets[0]['data'] = [s1]
                datasets[1]['data'] = [s2]








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



class LiquidacionRutasRegionListApi(BaseDatatableView):
    model = models.Rutas
    columns = ['id','nombre','contrato','valor','estado','actividades_json','usuario_actualizacion','region','file']
    order_columns = ['id','nombre','contrato','valor','estado','actividades_json','usuario_actualizacion','region','file']

    def get_initial_queryset(self):

        self.region = models.Regiones.objects.get(id=self.kwargs['pk'])

        self.permissions = {
            "ver": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.liquidaciones.ver",
                "usuarios.cpe_2018.liquidaciones_{0}.ver".format(self.region.numero)
            ],
            "editar": [
                "usuarios.cpe_2018.ver",
                "usuarios.cpe_2018.liquidaciones.ver",
                "usuarios.cpe_2018.liquidaciones_{0}.ver".format(self.region.numero),
                "usuarios.cpe_2018.liquidaciones_{0}.editar".format(self.region.numero)
            ]
        }

        return self.model.objects.filter(region__id=self.kwargs['pk'], visible=True)


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(contrato__contratista__nombres__icontains=search) |\
                Q(contrato__contratista__apellidos__icontains=search) | Q(contrato__contratista__cedula__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):


        if column == 'id':
            liquidacion = row.get_liquidacion()
            ret = ''

            if liquidacion != None:

                if self.request.user.has_perms(self.permissions.get('editar')) and liquidacion.estado in ["","Generada"]:
                    ret = '<div class="center-align">' \
                               '<a href="generar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Generar liquidación ruta {1}">' \
                                    '<i class="material-icons">edit</i>' \
                               '</a>' \
                           '</div>'.format(row.id,row.nombre)

                else:
                    ret = '<div class="center-align">' \
                          '<i class="material-icons">edit</i>' \
                          '</div>'.format(row.id, row.nombre)

            else:
                if self.request.user.has_perms(self.permissions.get('editar')):
                    ret = '<div class="center-align">' \
                               '<a href="generar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Generar liquidación ruta {1}">' \
                                    '<i class="material-icons">edit</i>' \
                               '</a>' \
                           '</div>'.format(row.id,row.nombre)

                else:
                    ret = '<div class="center-align">' \
                          '<i class="material-icons">edit</i>' \
                          '</div>'.format(row.id, row.nombre)

            return ret


        elif column == 'nombre':
            if row.estado == 'Liquidación':
                return '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{0}">' \
                            '<span class="mapa-ruta material-icons" style="font-size: 1.5rem;color:red;">error</span><span style="font-weight: bold;color: #000;">{1}</span>' \
                       '</a>'.format(row.estado, row.nombre)
            else:
                if row.visible:
                    return '<div class="center-align">' + row.nombre + '</div>'
                else:
                    return '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{0}">' \
                                '<span class="material-icons" style="font-size: 1.5rem;color:red;">compare</span><span style="font-weight: bold;color: #000;">{1}</span>' \
                            '</a>'.format('Contrato privado', row.nombre)


        elif column == 'contrato':
            return row.contrato.rest_contratista()


        elif column == 'valor':
            return row.contrato.pretty_print_valor()


        elif column == 'estado':
            liquidacion = row.get_liquidacion()

            if liquidacion != None:
                if liquidacion.estado != None:
                    return '<a href="estado/{1}/"><div class="center-align"><b>{0}</b></div></a>'.format(liquidacion.estado,liquidacion.id)
                else:
                    return liquidacion.estado
            else:
                return ''


        elif column == 'actividades_json':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.get_valor_ejecutado())


        elif column == 'usuario_actualizacion':
            liquidacion = row.get_liquidacion()

            if liquidacion != None:

                if liquidacion.url_file() != "":

                    return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Formato cargado">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                           '</a></div>'.format(liquidacion.url_file())

                else:
                    return ''
            else:
                return ''

        elif column == 'region':
            liquidacion = row.get_liquidacion()

            if liquidacion != None:

                if liquidacion.url_file2() != "" and liquidacion.url_file2() != None:

                    return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Formato cargado">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                           '</a></div>'.format(liquidacion.url_file2())

                else:
                    return ''
            else:
                return ''


        elif column == 'file':
            liquidacion = row.get_liquidacion()

            if liquidacion != None:

                if liquidacion.url_file3() != "" and liquidacion.url_file3() != None:

                    return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Formato cargado">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                           '</a></div>'.format(liquidacion.url_file3())

                else:
                    return ''
            else:
                return ''



        else:
            return super(LiquidacionRutasRegionListApi, self).render_column(row, column)