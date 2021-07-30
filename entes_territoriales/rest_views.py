from django_datatables_view.base_datatable_view import BaseDatatableView
from entes_territoriales import models
from recursos_humanos import models as models_rh
from django.db.models import Q
from dal import autocomplete
from usuarios.models import Municipios
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ReunionesListApi(BaseDatatableView):
    model = models.Reuniones
    columns = ['id','usuario_actualizacion','creation','municipio','update_datetime']
    order_columns = ['id','usuario_actualizacion','creation','municipio','update_datetime']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(municipio__nombre__icontains=search) | Q(municipio__departamento__nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':

            ret = ''
            if self.request.user.has_perm('usuarios.fest_2019.entes_territoriales.reuniones.ver'):
                ret = '<div class="center-align">' \
                      '<a href="{0}/hitos/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver hitos {1}, {2}">' \
                      '<i class="material-icons">flag</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.municipio.nombre, row.municipio.departamento.nombre)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">flag</i>' \
                      '</div>'.format(row.id, row.municipio.nombre, row.municipio.departamento.nombre)

            return ret

        elif column == 'usuario_actualizacion':

            ret = ''
            if self.request.user.has_perm('usuarios.fest_2019.entes_territoriales.reuniones.ver'):
                ret = '<div class="center-align">' \
                      '<a href="{0}/contactos/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver contactos en {1}, {2}">' \
                      '<i class="material-icons">contacts</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.municipio.nombre, row.municipio.departamento.nombre)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">contacts</i>' \
                      '</div>'.format(row.id, row.municipio.nombre, row.municipio.departamento.nombre)

            return ret



        elif column == 'creation':
            return str(row.municipio.departamento.nombre)


        elif column == 'municipio':
            return str(row.municipio.nombre)

        elif column == 'update_datetime':
            return str(row.pretty_creation_datetime())



        else:
            return super(ReunionesListApi, self).render_column(row, column)

class ReunionesContactosListApi(BaseDatatableView):
    model = models.Contactos
    columns = ['id','reunion','nombres','apellidos','cargo','celular','email','resguardo','comunidad','lenguas','observaciones']
    order_columns = ['id','reunion','nombres','apellidos','cargo','celular','email','resguardo','comunidad','lenguas','observaciones']


    def get_initial_queryset(self):
        return self.model.objects.filter(reunion__id = self.kwargs['pk'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(municipio__nombre__icontains=search) | Q(municipio__departamento__nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            reunion = models.Reuniones.objects.get(id = self.kwargs['pk'])
            ret = ''
            if self.request.user.has_perm('usuarios.fest_2019.entes_territoriales.reuniones.ver'):

                ret = '<div class="center-align">' \
                      '<a href="{0}/editar/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar">' \
                      '<i class="material-icons">edit</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">edit</i>' \
                      '</div>'.format(row.id)

            return ret


        elif column == 'reunion':
            ret = ''
            if self.request.user.has_perm('usuarios.fest_2019.entes_territoriales.reuniones.ver'):

                ret = '<div class="center-align">' \
                      '<a href="{0}/soportes/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Soportes">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id)

            return ret



        elif column == 'observaciones':
            ret = ''

            if row.observaciones != '':
                ret = '<div class="center-align">' \
                      '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{0}">' \
                      '<i class="material-icons">chat</i>' \
                      '</a>' \
                      '</div>'.format(row.observaciones)

            return ret

        elif column == 'celular':
            return str(row.celular)


        else:
            return super(ReunionesContactosListApi, self).render_column(row, column)

class ReunionesHitosListApi(BaseDatatableView):
    model = models.Hito
    columns = ['id','reunion','tipo','creation','file','file2','file3','estado','observacion']
    order_columns = ['id','reunion','tipo','creation','file','file2','file3','estado','observacion']


    def get_initial_queryset(self):
        return self.model.objects.filter(reunion__id = self.kwargs['pk'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(tipo__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            reunion = models.Reuniones.objects.get(id = self.kwargs['pk'])
            ret = ''
            if self.request.user.has_perm('usuarios.fest_2019.entes_territoriales.reuniones.ver'):

                ret = '<div class="center-align">' \
                      '<a href="{0}/editar/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar">' \
                      '<i class="material-icons">edit</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">edit</i>' \
                      '</div>'.format(row.id)

            return ret


        elif column == 'reunion':
            if self.request.user.has_perm('usuarios.fest_2019.entes_territoriales.reuniones.ver'):

                ret = '<div class="center-align">' \
                      '<a href="{0}/ver/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id)

            return ret


        elif column == 'observacion':
            ret = ''

            if row.observacion != '' and row.observacion != None:
                ret = '<div class="center-align">' \
                      '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{0}">' \
                      '<i class="material-icons">chat</i>' \
                      '</a>' \
                      '</div>'.format(row.observacion)

            return ret

        elif column == 'file':
            if row.url_file() != None:
                return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Acta">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a></div>'.format(row.url_file())
            else:
                return ''



        elif column == 'file2':
            if row.url_file() != None:
                return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Listado de asistencia">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a></div>'.format(row.url_file2())
            else:
                return ''




        elif column == 'file3':
            if row.url_file() != None:
                return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Otro">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a></div>'.format(row.url_file3())
            else:
                return ''



        elif column == 'celular':
            return str(row.celular)

        elif column == 'creation':
            return row.pretty_creation_datetime()

        elif column == 'estado':
            if self.request.user.has_perm('usuarios.fest_2019.entes_territoriales.reuniones.aprobar'):

                ret = '<div class="center-align">' \
                      '<a href="{0}/estado/" class="tooltipped" data-position="top" data-delay="50" data-tooltip="Actualizar estado">' \
                      '<b>{1}</b>' \
                      '</a>' \
                      '</div>'.format(row.id, row.estado, row.observacion)

            else:
                ret = '<div class="center-align">' \
                      '<b>{1}</b>' \
                      '</div>'.format(row.id, row.estado)

            return ret


        else:
            return super(ReunionesHitosListApi, self).render_column(row, column)

class ReunionesContactosSoportesListApi(BaseDatatableView):
    model = models.Soportes
    columns = ['id','tipo','file','observaciones']
    order_columns = ['id','tipo','file','observaciones']


    def get_initial_queryset(self):
        return self.model.objects.filter(contacto__id = self.kwargs['pk_contacto'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(tipo__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            reunion = models.Reuniones.objects.get(id = self.kwargs['pk'])
            ret = ''
            if self.request.user.has_perm('usuarios.fest_2019.entes_territoriales.reuniones.ver'):

                ret = '<div class="center-align">' \
                      '<a href="{0}/editar/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar">' \
                      '<i class="material-icons">edit</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">edit</i>' \
                      '</div>'.format(row.id)

            return ret



        elif column == 'observaciones':
            ret = ''

            if row.observaciones != '':
                ret = '<div class="center-align">' \
                      '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{0}">' \
                      '<i class="material-icons">chat</i>' \
                      '</a>' \
                      '</div>'.format(row.observaciones)

            return ret

        elif column == 'celular':
            return str(row.celular)

        elif column == 'file':
            if row.url_file() != None:
                return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Formato cargado">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a></div>'.format(row.url_file())
            else:
                return ''


        else:
            return super(ReunionesContactosSoportesListApi, self).render_column(row, column)

class MunicipiosAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):

        qs = Municipios.objects.all()

        if self.q:
            q = Q(nombre__icontains = self.q) | Q(departamento__nombre__icontains = self.q)
            qs = qs.filter(q)

        return qs

class FotosHitosApi(APIView):
    """
    """

    def delete(self, request, pk, pk_hito, int_foto, format=None):

        response = 'Eliminado'
        status_response = status.HTTP_404_NOT_FOUND
        hito = models.Hito.objects.get(id = pk_hito)

        if int_foto == 1:
            hito.foto_1.delete()
            status_response = status.HTTP_200_OK

        if int_foto == 2:
            hito.foto_2.delete()
            status_response = status.HTTP_200_OK

        if int_foto == 3:
            hito.foto_3.delete()
            status_response = status.HTTP_200_OK

        if int_foto == 4:
            hito.foto_4.delete()
            status_response = status.HTTP_200_OK


        return Response({'response': response}, status=status_response)