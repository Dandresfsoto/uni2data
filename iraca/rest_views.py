from dal import autocomplete
from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView

from iraca import models
from iraca.models import Milestones, Meetings, Certificates, Types
from usuarios.models import Municipios


class MeetingsListApi(BaseDatatableView):
    model = Meetings
    columns = ['id','user_update','creation','municipality','update_datetime']
    order_columns = ['id','user_update','creation','municipality','update_datetime']

    def get_initial_queryset(self):

        self.certificate = Certificates.objects.get(id = self.kwargs['pk'])

        return self.model.objects.filter(certificate__id = self.kwargs['pk'])

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
                      '<a href="milestones/{0}/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver hitos {1}, {2}">' \
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
                      '<a href="contacts/{0}/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver contactos en {1}, {2}">' \
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

        elif column == 'update_datetime':
            return str(row.creation_user.get_full_name_string())

        else:
            return super(MeetingsListApi, self).render_column(row, column)

class MilestonesListApi(BaseDatatableView):
    model = Milestones
    columns = ['id','meeting','type','creation','file','file2','file3','estate','observation','date']
    order_columns = ['id','meeting','type','creation','file','file2','file3','estate','observation','date']


    def get_initial_queryset(self):
        return self.model.objects.filter(meeting__id = self.kwargs['pk_meeting'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(type__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            meeting = models.Meetings.objects.get(id = self.kwargs['pk_meeting'])
            ret = ''
            if self.request.user.has_perm('usuarios.iraca.actas.hitos.ver'):

                ret = '<div class="center-align">' \
                      '<a href="edit/{0}/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar">' \
                      '<i class="material-icons">edit</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">edit</i>' \
                      '</div>'.format(row.id)

            return ret

        elif column == 'meeting':
            if self.request.user.has_perm('usuarios.iraca.actas.hitos.ver'):

                ret = '<div class="center-align">' \
                      '<a href="view/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id)

            return ret

        elif column == 'observation':
            ret = ''

            if row.observation != '' and row.observation != None:
                ret = '<div class="center-align">' \
                      '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{0}">' \
                      '<i class="material-icons">chat</i>' \
                      '</a>' \
                      '</div>'.format(row.observation)

            return ret

        elif column == 'file':
            if row.url_file() != None:
                return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Acta">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a></div>'.format(row.url_file())
            else:
                return ''

        elif column == 'file2':
            if row.url_file2() != None:
                return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Listado de asistencia">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a></div>'.format(row.url_file2())
            else:
                return ''

        elif column == 'file3':
            if row.url_file3() != None:
                return '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Otro">' \
                           '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                        '</a></div>'.format(row.url_file3())
            else:
                return ''

        elif column == 'creation':
            return row.date.strftime('%d/%m/%Y - %I:%M:%S %p')

        elif column == 'type':
            return row.type.name

        elif column == 'estate':
            if self.request.user.has_perm('usuarios.iraca.actas.hitos.ver'):

                ret = '<div class="center-align">' \
                      '<a href="{0}/estado/" class="tooltipped" data-position="top" data-delay="50" data-tooltip="Actualizar estado">' \
                      '<b>{1}</b>' \
                      '</a>' \
                      '</div>'.format(row.id, row.estate, row.observation)

            else:
                ret = '<div class="center-align">' \
                      '<b>{1}</b>' \
                      '</div>'.format(row.id, row.estate)

            return ret

        elif column == 'date':
            ret = ''
            if self.request.user.has_perm('usuarios.iraca.actas.hitos.eliminar') and row.estate == "Esperando aprobación":
                ret = '<div class="center-align">' \
                           '<a href="delete/{0}/" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar hito">' \
                                '<i class="material-icons">delete</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">delete</i>' \
                       '</div>'.format(row.id)

            return ret

        else:
            return super(MilestonesListApi, self).render_column(row, column)

class ContactsListApi(BaseDatatableView):
    model = models.Contacts
    columns = ['id','name','surname','charge','movil','email','reservation','community','languahe','observation']
    order_columns = ['id','name','surname','charge','movil','email','reservation','community','languahe','observation']


    def get_initial_queryset(self):
        self.meeting = Meetings.objects.get(id=self.kwargs['pk_meeting'])

        return self.model.objects.filter(meting__id = self.kwargs['pk_meeting'])

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(municipality__nombre__icontains=search) | Q(municipality__departamento__nombre__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            meeting = models.Meetings.objects.get(id = self.kwargs['pk_meeting'])
            ret = ''
            if self.request.user.has_perm('usuarios.iraca.actas.contactos.ver'):

                ret = '<div class="center-align">' \
                      '<a href="edit/{0}/" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar">' \
                      '<i class="material-icons">edit</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">edit</i>' \
                      '</div>'.format(row.id)

            return ret

        elif column == 'observation':
            ret = ''

            if row.observation != '':
                ret = '<div class="center-align">' \
                      '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{0}">' \
                      '<i class="material-icons">chat</i>' \
                      '</a>' \
                      '</div>'.format(row.observation)

            return ret

        elif column == 'movil':
            return str(row.movil)


        else:
            return super(ContactsListApi, self).render_column(row, column)

class MunicipiosAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):

        qs = Municipios.objects.all().filter(departamento__codigo=27)

        if self.q:
            q = Q(nombre__icontains = self.q) | Q(departamento__nombre__icontains = self.q)
            qs = qs.filter(q)

        return qs



