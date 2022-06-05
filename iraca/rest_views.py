from dal import autocomplete
from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils import timezone
from iraca import models
from iraca.models import Milestones, Meetings, Certificates, Types, Households, Resguards, Comunity, Routes
from mobile.models import FormMobile
from recursos_humanos.models import Collects_Account
from usuarios.models import Municipios
from recursos_humanos import models as rh_models
from requests import request


class HogaresListApi(BaseDatatableView):
    model = models.Households
    columns = ['id','document','first_surname','municipality_attention','routes']
    order_columns = ['id','document','first_surname','municipality_attention','routes']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.db.ver"
            ],
            "editar": [
                "usuarios.iraca.ver",
                "usuarios.iraca.db.ver",
                "usuarios.iraca.db.editar",
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(first_name__icontains=search) | Q(second_name__icontains=search) | \
                Q(first_surname__icontains=search) | Q(second_surname__icontains=search) | Q(document__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                      '<a href="edit/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Editar hogar">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'document':

            return '<div class="center-align"><b>' + str(row.document) + '</b></div>'

        elif column == 'first_surname':
            return row.get_full_name()

        elif column == 'municipality_attention':
            return '{0}, {1}'.format(row.municipality_attention.nombre,row.municipality_attention.departamento.nombre)

        elif column == 'routes':
            return row.get_routes()

        else:
            return super(HogaresListApi, self).render_column(row, column)

class MomentsListApi(BaseDatatableView):
    model = models.Moments
    columns = ['id','name','consecutive','type']
    order_columns = ['id','name','consecutive','type']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.entregables.ver"
            ]
        }
        return self.model.objects.filter(type_moment="implementacion")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(name__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="{0}/instruments/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver soportes de la visita: {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.name)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.name)

            return ret

        elif column == 'consecutive':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.get_consecutive())

        elif column == 'type':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.type)


        else:
            return super(MomentsListApi, self).render_column(row, column)

class InstrumentsListApi(BaseDatatableView):
    model = models.Instruments
    columns = ['name','consecutive','model', 'id']
    order_columns = ['name','consecutive','model', 'id']

    def get_initial_queryset(self):
        self.moment = models.Moments.objects.get(pk=self.kwargs['pk_moment'])
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.entregables.ver"
            ]
        }
        return self.model.objects.filter(moment = self.moment)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(name__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="report/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Generar informe: {1}">' \
                      '<i class="material-icons">email</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.name)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">email</i>' \
                       '</div>'.format(row.id,row.name)

            return ret

        elif column == 'consecutive':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.get_consecutive())


        else:
            return super(InstrumentsListApi, self).render_column(row, column)

class FormulationMomentsListApi(BaseDatatableView):
    model = models.Moments
    columns = ['id','name','consecutive','type']
    order_columns = ['id','name','consecutive','type']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.entregables.ver"
            ]
        }
        return self.model.objects.filter(type_moment="formulacion")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(name__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="{0}/instruments/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver soportes de la visita: {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.name)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.name)

            return ret

        elif column == 'consecutive':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.get_consecutive())

        elif column == 'type':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.type)


        else:
            return super(FormulationMomentsListApi, self).render_column(row, column)

class FormulationInstrumentsListApi(BaseDatatableView):
    model = models.Instruments
    columns = ['name','consecutive','model', 'id']
    order_columns = ['name','consecutive','model', 'id']

    def get_initial_queryset(self):
        self.moment = models.Moments.objects.get(pk=self.kwargs['pk_moment'])
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.entregables.ver"
            ]
        }
        return self.model.objects.filter(moment = self.moment)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(name__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="report/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Generar informe: {1}">' \
                      '<i class="material-icons">email</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.name)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">email</i>' \
                       '</div>'.format(row.id,row.name)

            return ret

        elif column == 'consecutive':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.get_consecutive())


        else:
            return super(FormulationInstrumentsListApi, self).render_column(row, column)

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
                      '<a href="estate/{0}/" class="tooltipped" data-position="top" data-delay="50" data-tooltip="Actualizar estado">' \
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

class ImplementationListApi(BaseDatatableView):
    model = models.Routes
    columns = ['id','creation','name','resguard','novelties','progress','regitered_household']
    order_columns = ['id','creation','name','resguard','novelties','progress','regitered_household']

    def get_initial_queryset(self):

        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.rutas.ver",
            ],
            "editar": [
                "usuarios.iraca.ver",
                "usuarios.iraca.rutas.ver",
                "usuarios.iraca.rutas.editar"
            ],
            "ver_hogares": [
                "usuarios.iraca.ver",
                "usuarios.iraca.rutas.ver",
                "usuarios.iraca.rutas.hogares.ver"
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                           '<a href="edit/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar ruta {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.name)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.name)

            return ret

        elif column == 'creation':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="activities/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades de la ruta {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.name)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.name)

            return ret

        elif column == 'resguard':
            return row.get_resguard_name()

        elif column == 'novelties':
            if row.novelties > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(row.novelties)
            else:
                return ''

        elif column == 'progress':

            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-delay="50" ' \
                   'data-tooltip="Progreso general de la ruta">' \
                   '<b>{0}%</b>' \
                   '</a>' \
                   '</div>'.format(row.progress)

        elif column == 'regitered_household':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver_hogares')):
                ret = '<div class="center-align">' \
                           '<a href="household/{0}" class="tooltipped" data-position="left" data-delay="50" data-tooltip="{1} hogares inscritos">' \
                                '<b>{1}</b>' \
                           '</a>' \
                       '</div>'.format(row.id,row.get_household_count())

            else:
                ret = '<div class="center-align">' \
                           '<b>{1}</b>' \
                       '</div>'.format(row.id,row.regitered_household)

            return ret

        else:
            return super(ImplementationListApi, self).render_column(row, column)

class ImplementationActivitiesListApi(BaseDatatableView):
    model = models.Moments
    columns = ['id', 'consecutive', 'name', 'novelty', 'progress']
    order_columns = ['id', 'consecutive', 'name', 'novelty', 'progress']

    def get_initial_queryset(self):
        self.route = models.Routes.objects.get(id = self.kwargs['pk'])

        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver"
            ]
        }
        return self.model.objects.filter(type_moment="implementacion")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(name__icontains=search) | Q(consecutive__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="instruments/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver instrumentos">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'consecutive':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.consecutive)

        elif column == 'novelty':
            novelty = row.get_novelty(self.route)

            if novelty > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novelty)
            else:
                return ''

        elif column == 'progress':

            progress = row.get_progress_moment(self.route)

            progress = '{:20,.2f}%'.format(progress)


            return '<div class="center-align">' \
                   '<a class="" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="{1}">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(progress,progress)





        else:
            return super(ImplementationActivitiesListApi, self).render_column(row, column)

class ImplementationHouseholdListApi(BaseDatatableView):
    model = models.ObjectRouteInstrument
    columns = ['creation', 'creacion_user', 'id', 'consecutive', 'name', 'estate', 'route',
               'update_user']
    order_columns = ['creacion', 'creacion_user', 'id', 'consecutivo', 'name', 'estate', 'route',
                     'update_user']

    def get_initial_queryset(self):
        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])


        self.permissions = {
            "ver": [
                "usuarios.iraca_.ver",
                "usuarios.iraca.implementacion.ver"
            ]
        }
        return self.model.objects.filter(route=self.route, moment=self.moment)


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(households__document__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'creation':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                from iraca import utils
                ret = '<div class="center-align">' \
                      '<a href="view/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, utils.pretty_datetime(timezone.localtime(row.update_date)))

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id)

            return ret

        elif column == 'id':
            ret = ''

            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="traceability/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                      '<i class="material-icons">class</i>' \
                      '</a>' \
                      '</div>'.format(row.id, 'Ver la trazabilidad')

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">class</i>' \
                      '</div>'.format(row.id)

            return ret

        elif column == 'consecutive':

            ret = '<div class="center-align">' \
                  '<a href="household/{0}" class="tooltipped" data-position="left" data-delay="50" data-tooltip="Hogares del soporte">' \
                  '<b>{1}</b>' \
                  '</a>' \
                  '</div>'.format(row.id, row.households.all().count())

            return ret

        elif column == 'creacion_user':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):

                if row.estate in ['cargado', 'rechazado']:

                    ret = '<div class="center-align">' \
                          '<a href="edit/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Actualizar el soporte">' \
                          '<i class="material-icons">cloud_upload</i>' \
                          '</a>' \
                          '</div>'.format(row.id)


                else:

                    ret = '<div class="center-align">' \
                          '<i class="material-icons">cloud_upload</i>' \
                          '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">cloud_upload</i>' \
                      '</div>'.format(row.id)

            return ret

        elif column == 'name':
            return row.name

        elif column == 'estate':
            ret = ''
            if row.estate == 'cargado':
                ret = ''
            return row.estate

        elif column == 'route':
            ret = ''

            if self.request.user.is_superuser:

                if row.estate != 'aprobado':
                    ret += '<a style="color:green;" href="approve/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                           '<i class="material-icons">{2}</i>' \
                           '</a>'.format(row.id, 'Aprobar', 'check_box')

                if row.estate != 'rechazado':
                    ret += '<a style="color:red;margin-left:10px;" href="reject/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                           '<i class="material-icons">{2}</i>' \
                           '</a>'.format(row.id, 'Rechazar', 'highlight_off')

            else:
                if self.request.user.has_perms(self.permissions.get('"usuarios.iraca.implementacion.aprobar"')):
                    if row.estate != 'aprobado':
                        ret += '<a style="color:green;" href="aprobar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                               '<i class="material-icons">{2}</i>' \
                               '</a>'.format(row.id, 'Aprobar', 'check_box')

                    if row.estate != 'rechazado':
                        ret += '<a style="color:red;margin-left:10px;" href="reject/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                               '<i class="material-icons">{2}</i>' \
                               '</a>'.format(row.id, 'Rechazar', 'highlight_off')

            return '<div class="center-align">' + ret + '</div>'

        elif column == 'update_user':
            ret = ''

            if self.request.user.is_superuser:
                if row.estate in ['cargado']:

                    ret = '<div class="center-align">' \
                          '<a href="delete/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar soporte">' \
                          '<i class="material-icons">delete</i>' \
                          '</a>' \
                          '</div>'.format(row.id)

                elif row.estate in ['rechazado']:

                    ret = '<div class="center-align">' \
                          '<a href="delete/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar soporte">' \
                          '<i class="material-icons">delete</i>' \
                          '</a>' \
                          '</div>'.format(row.id)
                else:

                    ret = '<div class="center-align">' \
                          '<i class="material-icons">delete</i>' \
                          '</div>'.format(row.id)

                return ret

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">delete</i>' \
                      '</div>'.format(row.id)

                return ret

        else:
            return super(ImplementationHouseholdListApi, self).render_column(row, column)

class ImplementationTraceabilityListApi(BaseDatatableView):
    model = models.InstrumentTraceabilityRouteObject
    columns = ['creacion','user','observation']
    order_columns = ['creacion','user','observation']

    def get_initial_queryset(self):
        self.route = models.Routes.objects.get(id = self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])


        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementation.ver"
            ]
        }

        if self.request.user.is_superuser:
            return self.model.objects.filter(instrument=self.instrument_object)
        else:
            return self.model.objects.filter(instrument=self.instrument_object)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(observacion__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'creacion':
            return timezone.localtime(row.creacion).strftime('%d de %B del %Y a las %I:%M:%S %p')


        elif column == 'user':
            return row.user.get_full_name()


        else:
            return super(ImplementationTraceabilityListApi, self).render_column(row, column)

class ImplementationHouseholdsListApi(BaseDatatableView):
    model = models.Households
    columns = ['id','document','first_name','municipality_attention']
    order_columns = ['id','document','first_name','municipality_attention']

    def get_initial_queryset(self):
        self.route = models.Routes.objects.get(id = self.kwargs['pk'])

        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver",
                "usuarios.iraca.implementacion.hogares.ver"
            ]
        }

        return self.model.objects.filter(routes = self.route)



    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(first_name__icontains=search) | Q(second_name__icontains=search) | \
                Q(first_surname__icontains=search) | Q(second_surname__icontains=search) | \
                Q(document__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="view/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver información del hogar">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'document':

            return '<div class="center-align"><b>' + str(row.document) + '</b></div>'

        elif column == 'first_name':
            return row.get_full_name()

        elif column == 'municipality_attention':
            return '{0}, {1}'.format(row.municipality_attention.nombre,row.municipality_attention.departamento.nombre)



        else:
            return super(ImplementationHouseholdsListApi, self).render_column(row, column)

class FormulationListApi(BaseDatatableView):
    model = models.Routes
    columns = ['creation','name','resguard','novelties','progress_form','regitered_household']
    order_columns = ['creation','name','resguard','novelties','progress_form','regitered_household']

    def get_initial_queryset(self):

        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.rutas.ver",
            ],
            "editar": [
                "usuarios.iraca.ver",
                "usuarios.iraca.rutas.ver",
                "usuarios.iraca.rutas.editar"
            ],
            "ver_hogares": [
                "usuarios.iraca.ver",
                "usuarios.iraca.rutas.ver",
                "usuarios.iraca.rutas.hogares.ver"
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'creation':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="activities/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades de la ruta {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.name)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.name)

            return ret


        elif column == 'novelties':
            if row.novelties_form > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(row.novelties_form)
            else:
                return ''

        elif column == 'resguard':
            return row.get_resguard_name()

        elif column == 'progress_form':

            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-delay="50" ' \
                   'data-tooltip="Progreso general de la ruta">' \
                   '<b>{0}%</b>' \
                   '</a>' \
                   '</div>'.format(row.progress_form)

        elif column == 'regitered_household':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver_hogares')):
                ret = '<div class="center-align">' \
                           '<a href="household/{0}" class="tooltipped" data-position="left" data-delay="50" data-tooltip="{1} hogares inscritos">' \
                                '<b>{1}</b>' \
                           '</a>' \
                       '</div>'.format(row.id,row.get_household_count())

            else:
                ret = '<div class="center-align">' \
                           '<b>{1}</b>' \
                       '</div>'.format(row.id,row.regitered_household)

            return ret

        else:
            return super(FormulationListApi, self).render_column(row, column)

class FormulationActivitiesListApi(BaseDatatableView):
    model = models.Moments
    columns = ['id', 'consecutive', 'name', 'novelty', 'progress']
    order_columns = ['id', 'consecutive', 'name', 'novelty', 'progress']

    def get_initial_queryset(self):
        self.route = models.Routes.objects.get(id = self.kwargs['pk'])

        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver"
            ]
        }
        return self.model.objects.filter(type_moment="formulacion")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(name__icontains=search) | Q(consecutive__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="instruments/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver instrumentos">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'consecutive':
            return '<div class="center-align"><b>{0}</b></div>'.format(row.consecutive)

        elif column == 'novelty':
            novelty = row.get_novelty(self.route)

            if novelty > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novelty)
            else:
                return ''

        elif column == 'progress':

            progress = row.get_progress_moment(self.route)

            progress = '{:20,.2f}%'.format(progress)


            return '<div class="center-align">' \
                   '<a class="" data-position="left" data-html="true" data-delay="50" ' \
                   'data-tooltip="{1}">' \
                   '<b>{0}</b>' \
                   '</a>' \
                   '</div>'.format(progress,progress)





        else:
            return super(FormulationActivitiesListApi, self).render_column(row, column)

class FormulationHouseholdListApi(BaseDatatableView):
    model = models.ObjectRouteInstrument
    columns = ['creation', 'creacion_user', 'id', 'consecutive', 'name', 'estate', 'route',
               'update_user']
    order_columns = ['creacion', 'creacion_user', 'id', 'consecutivo', 'name', 'estate', 'route',
                     'update_user']

    def get_initial_queryset(self):
        self.route = models.Routes.objects.get(id=self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])


        self.permissions = {
            "ver": [
                "usuarios.iraca_.ver",
                "usuarios.iraca.implementacion.ver"
            ]
        }
        return self.model.objects.filter(route=self.route, moment=self.moment)


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(households__document__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'creation':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                from iraca import utils
                ret = '<div class="center-align">' \
                      '<a href="view/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="{1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, utils.pretty_datetime(timezone.localtime(row.update_date)))

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id)

            return ret

        elif column == 'id':
            ret = ''

            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="traceability/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                      '<i class="material-icons">class</i>' \
                      '</a>' \
                      '</div>'.format(row.id, 'Ver la trazabilidad')

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">class</i>' \
                      '</div>'.format(row.id)

            return ret

        elif column == 'consecutive':

            ret = '<div class="center-align">' \
                  '<a href="household/{0}" class="tooltipped" data-position="left" data-delay="50" data-tooltip="Hogares del soporte">' \
                  '<b>{1}</b>' \
                  '</a>' \
                  '</div>'.format(row.id, row.households.all().count())

            return ret

        elif column == 'creacion_user':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):

                if row.estate in ['cargado', 'rechazado']:

                    ret = '<div class="center-align">' \
                          '<a href="edit/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Actualizar el soporte">' \
                          '<i class="material-icons">cloud_upload</i>' \
                          '</a>' \
                          '</div>'.format(row.id)


                else:

                    ret = '<div class="center-align">' \
                          '<i class="material-icons">cloud_upload</i>' \
                          '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">cloud_upload</i>' \
                      '</div>'.format(row.id)

            return ret

        elif column == 'name':
            return row.name

        elif column == 'estate':
            ret = ''
            if row.estate == 'cargado':
                ret = ''
            return row.estate

        elif column == 'route':
            ret = ''

            if self.request.user.is_superuser:

                if row.estate != 'aprobado':
                    ret += '<a style="color:green;" href="approve/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                           '<i class="material-icons">{2}</i>' \
                           '</a>'.format(row.id, 'Aprobar', 'check_box')

                if row.estate != 'rechazado':
                    ret += '<a style="color:red;margin-left:10px;" href="reject/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                           '<i class="material-icons">{2}</i>' \
                           '</a>'.format(row.id, 'Rechazar', 'highlight_off')

            else:
                if self.request.user.has_perms(self.permissions.get('"usuarios.iraca.implementacion.aprobar"')):
                    if row.estate != 'aprobado':
                        ret += '<a style="color:green;" href="aprobar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                               '<i class="material-icons">{2}</i>' \
                               '</a>'.format(row.id, 'Aprobar', 'check_box')

                    if row.estate != 'rechazado':
                        ret += '<a style="color:red;margin-left:10px;" href="reject/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                               '<i class="material-icons">{2}</i>' \
                               '</a>'.format(row.id, 'Rechazar', 'highlight_off')

            return '<div class="center-align">' + ret + '</div>'

        elif column == 'update_user':
            ret = ''

            if self.request.user.is_superuser:
                if row.estate in ['cargado']:

                    ret = '<div class="center-align">' \
                          '<a href="delete/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar soporte">' \
                          '<i class="material-icons">delete</i>' \
                          '</a>' \
                          '</div>'.format(row.id)

                elif row.estate in ['rechazado']:

                    ret = '<div class="center-align">' \
                          '<a href="delete/{0}" class="tooltipped delete-table" data-position="top" data-delay="50" data-tooltip="Eliminar soporte">' \
                          '<i class="material-icons">delete</i>' \
                          '</a>' \
                          '</div>'.format(row.id)
                else:

                    ret = '<div class="center-align">' \
                          '<i class="material-icons">delete</i>' \
                          '</div>'.format(row.id)

                return ret

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">delete</i>' \
                      '</div>'.format(row.id)

                return ret

        else:
            return super(FormulationHouseholdListApi, self).render_column(row, column)

class FormulationTraceabilityListApi(BaseDatatableView):
    model = models.InstrumentTraceabilityRouteObject
    columns = ['creacion','user','observation']
    order_columns = ['creacion','user','observation']

    def get_initial_queryset(self):
        self.route = models.Routes.objects.get(id = self.kwargs['pk'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])
        self.instrument_object = models.ObjectRouteInstrument.objects.get(id=self.kwargs['pk_instrument_object'])


        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementation.ver"
            ]
        }

        if self.request.user.is_superuser:
            return self.model.objects.filter(instrument=self.instrument_object)
        else:
            return self.model.objects.filter(instrument=self.instrument_object)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(observacion__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'creacion':
            return timezone.localtime(row.creacion).strftime('%d de %B del %Y a las %I:%M:%S %p')


        elif column == 'user':
            return row.user.get_full_name()


        else:
            return super(FormulationTraceabilityListApi, self).render_column(row, column)

class FormulationHouseholdsListApi(BaseDatatableView):
    model = models.Households
    columns = ['id','document','first_name','municipality_attention']
    order_columns = ['id','document','first_name','municipality_attention']

    def get_initial_queryset(self):
        self.route = models.Routes.objects.get(id = self.kwargs['pk'])

        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.implementacion.ver",
                "usuarios.iraca.implementacion.hogares.ver"
            ]
        }

        return self.model.objects.filter(routes = self.route)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(first_name__icontains=search) | Q(second_name__icontains=search) | \
                Q(first_surname__icontains=search) | Q(second_surname__icontains=search) | \
                Q(document__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="view/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver información del hogar">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'document':

            return '<div class="center-align"><b>' + str(row.document) + '</b></div>'

        elif column == 'first_name':
            return row.get_full_name()

        elif column == 'municipality_attention':
            return '{0}, {1}'.format(row.municipality_attention.nombre,row.municipality_attention.departamento.nombre)



        else:
            return super(FormulationHouseholdsListApi, self).render_column(row, column)

class SupportsHouseholdsListApi(BaseDatatableView):
    model = models.Households
    columns = ['id','document','first_name','municipality_attention']
    order_columns = ['id','document','first_name','municipality_attention']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.soportes.ver"
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(first_name__icontains=search) | Q(second_name__icontains=search) | \
                Q(first_surname__icontains=search) | Q(second_surname__icontains=search) | Q(document__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = '<div class="center-align">' \
                       '<a href="{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver componentes">' \
                            '<i class="material-icons">remove_red_eye</i>' \
                       '</a>' \
                   '</div>'.format(row.id)
            return ret


        elif column == 'document':

            return '<div class="center-align"><b>' + str(row.document) + '</b></div>'

        elif column == 'first_name':
            return row.get_full_name()

        elif column == 'municipality_attention':
            return '{0}, {1}'.format(row.municipality_attention.nombre,row.municipality_attention.departamento.nombre)


        else:
            return super(SupportsHouseholdsListApi, self).render_column(row, column)

class SupportsHouseholdsImplementationMomentsListApi(BaseDatatableView):
    model = models.Moments
    columns = ['id','name','consecutive','novelty']
    order_columns = ['id','name','consecutive','novelty']

    def get_initial_queryset(self):

        self.household = models.Households.objects.get(id = self.kwargs['pk_household'])

        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.support.ver"
            ]
        }
        return self.model.objects.filter(type_moment = "implementacion")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = '<div class="center-align">' \
                       '<a href="instrument/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver instrumentos">' \
                            '<i class="material-icons">remove_red_eye</i>' \
                       '</a>' \
                   '</div>'.format(row.id)
            return ret

        elif column == 'consecutive':
            return '<div class="center-align"><b>' + str(row.get_consecutive()) + '</b></div>'

        else:
            return super(SupportsHouseholdsImplementationMomentsListApi, self).render_column(row, column)

class SupportImplementationHouseholdMomentsListApi(BaseDatatableView):
    model = models.ObjectRouteInstrument
    columns = ['id','route','consecutive']
    order_columns = ['id','route','consecutive']

    def get_initial_queryset(self):

        self.households = models.Households.objects.get(id = self.kwargs['pk_household'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])

        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.soportes.ver"
            ]
        }
        return self.model.objects.filter(households = self.households,moment=self.moment)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(name__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = '<div class="center-align">' \
                       '<a href="view/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver soporte">' \
                            '<i class="material-icons">remove_red_eye</i>' \
                       '</a>' \
                   '</div>'.format(row.id)
            return ret


        elif column == 'route':
            return row.instrument.name


        elif column == 'consecutive':
            return '<div class="center-align"><b>' + str(row.instrument.get_consecutive()) + '</b></div>'


        else:
            return super(SupportImplementationHouseholdMomentsListApi, self).render_column(row, column)

class SupportsFormulationHouseholdsListApi(BaseDatatableView):
    model = models.Households
    columns = ['id','document','first_name','municipality_attention']
    order_columns = ['id','document','first_name','municipality_attention']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.soportes.ver"
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(first_name__icontains=search) | Q(second_name__icontains=search) | \
                Q(first_surname__icontains=search) | Q(second_surname__icontains=search) | Q(document__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = '<div class="center-align">' \
                       '<a href="{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver componentes">' \
                            '<i class="material-icons">remove_red_eye</i>' \
                       '</a>' \
                   '</div>'.format(row.id)
            return ret


        elif column == 'document':

            return '<div class="center-align"><b>' + str(row.document) + '</b></div>'

        elif column == 'first_name':
            return row.get_full_name()

        elif column == 'municipality_attention':
            return '{0}, {1}'.format(row.municipality_attention.nombre,row.municipality_attention.departamento.nombre)


        else:
            return super(SupportsFormulationHouseholdsListApi, self).render_column(row, column)

class SupportsHouseholdsFormulationMomentsListApi(BaseDatatableView):
    model = models.Moments
    columns = ['id','name','consecutive','novelty']
    order_columns = ['id','name','consecutive','novelty']

    def get_initial_queryset(self):

        self.household = models.Households.objects.get(id = self.kwargs['pk_household'])

        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.support.ver"
            ]
        }
        return self.model.objects.filter(type_moment = "formulacion")

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = '<div class="center-align">' \
                       '<a href="instrument/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver instrumentos">' \
                            '<i class="material-icons">remove_red_eye</i>' \
                       '</a>' \
                   '</div>'.format(row.id)
            return ret

        elif column == 'consecutive':
            return '<div class="center-align"><b>' + str(row.get_consecutive()) + '</b></div>'

        else:
            return super(SupportsHouseholdsFormulationMomentsListApi, self).render_column(row, column)

class SupportFormulationHouseholdMomentsListApi(BaseDatatableView):
    model = models.ObjectRouteInstrument
    columns = ['id','route','consecutive']
    order_columns = ['id','route','consecutive']

    def get_initial_queryset(self):

        self.households = models.Households.objects.get(id = self.kwargs['pk_household'])
        self.moment = models.Moments.objects.get(id=self.kwargs['pk_moment'])

        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.soportes.ver"
            ]
        }
        return self.model.objects.filter(households = self.households,moment=self.moment)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(name__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = '<div class="center-align">' \
                       '<a href="view/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver soporte">' \
                            '<i class="material-icons">remove_red_eye</i>' \
                       '</a>' \
                   '</div>'.format(row.id)
            return ret


        elif column == 'route':
            return row.instrument.name


        elif column == 'consecutive':
            return '<div class="center-align"><b>' + str(row.instrument.get_consecutive()) + '</b></div>'


        else:
            return super(SupportFormulationHouseholdMomentsListApi, self).render_column(row, column)

class HouseholdListApi(BaseDatatableView):
    model = models.Households
    columns = ['id','document','first_surname','municipality_attention','routes']
    order_columns = ['id','document','first_surname','municipality_attention','routes']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.vinculacion.ver"
            ],
            "editar": [
                "usuarios.iraca.ver",
                "usuarios.iraca.vinculacion.ver",
                "usuarios.iraca.vinculacion.editar",
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(first_name__icontains=search) | Q(second_name__icontains=search) | \
                Q(first_surname__icontains=search) | Q(second_surname__icontains=search) | Q(document__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Editar hogar">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'document':

            return '<div class="center-align"><b>' + str(row.document) + '</b></div>'

        elif column == 'first_surname':
            return row.get_full_name()

        elif column == 'municipality_attention':
            return '{0}, {1}'.format(row.municipality_attention.nombre,row.municipality_attention.departamento.nombre)

        elif column == 'routes':
            return row.get_routes()

        else:
            return super(HouseholdListApi, self).render_column(row, column)

class BondingListApi(BaseDatatableView):
    model = FormMobile
    columns = ['id','document','data','created_at','updated_at']
    order_columns = ['id','document','data','created_at','updated_at']

    def get_initial_queryset(self):
        household = Households.objects.get(id = self.kwargs['pk_household'])
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.vinculacion.ver"
            ],
            "editar": [
                "usuarios.iraca.ver",
                "usuarios.iraca.vinculacion.ver",
                "usuarios.iraca.vinculacion.editar",
            ]
        }
        return self.model.objects.filter(data__icontains=household.document)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)

        if search:
            q = Q(id__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="view/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Editar hogar">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'document':
            return '<div class="center-align"><b>' + str(row.json_read_document()) + '</b></div>'

        elif column == 'data':
            return '<div class="center-align"><b>' + str(row.json_read_name()) + '</b></div>'

        elif column == 'created_at':
            return timezone.localtime(row.created_at).strftime('%d de %B del %Y a las %I:%M:%S %p')


        elif column == 'updated_at':
            ret = ''
            if self.request.user.has_perm('usuarios.iraca.vinculacion.eliminar'):
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
            return super(BondingListApi, self).render_column(row, column)

class MunicipiosAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):

        qs = Municipios.objects.all().filter(departamento__codigo=27)

        if self.q:
            q = Q(nombre__icontains = self.q) | Q(departamento__nombre__icontains = self.q)
            qs = qs.filter(q)

        return qs

class ResguardListApi(BaseDatatableView):
    model = models.Routes
    columns = ['id','color','name','municipality']
    order_columns = ['id','color','name','municipality']

    def get_initial_queryset(self):
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.resguardo.ver"
            ],
            "editar": [
                "usuarios.iraca.ver",
                "usuarios.iraca.resguardo.ver",
                "usuarios.iraca.resguardo.editar",
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(name__icontains=search) | Q(municipality__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                      '<a href="edit/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Editar hogar">' \
                      '<i class="material-icons">edit</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'color':
            ret = '<div class="center-align">' \
                  '<a href="comunity/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver comunidades">' \
                  '<i class="material-icons" >store</i>' \
                  '</a>' \
                  '</div>'.format(row.id)
            return ret

        elif column == 'name':
            return row.name

        elif column == 'municipality':
            return '{0}'.format(row.certificate.name)

        else:
            return super(ResguardListApi, self).render_column(row, column)

class ResguardComunityListApi(BaseDatatableView):
    model = models.Comunity
    columns = ['id','name','resguard']
    order_columns = ['id','name','resguard']

    def get_initial_queryset(self):
        resguardo = Resguards.objects.get(id=self.kwargs['pk'])
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.resguardo.ver"
            ],
            "editar": [
                "usuarios.iraca.ver",
                "usuarios.iraca.resguardo.ver",
                "usuarios.iraca.resguardo.editar",
            ]
        }
        return self.model.objects.filter(resguard = resguardo.id)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(name__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                      '<a href="edit/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Editar hogar">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'name':
            return row.name

        elif column == 'resguard':
            return '{0}'.format(row.resguard.name)

        else:
            return super(ResguardComunityListApi, self).render_column(row, column)

class InformListApi(BaseDatatableView):
    model = rh_models.Cuts
    columns = ['id','consecutive','date_creation','name','month','user_update']
    order_columns = ['id','consecutive','date_creation','name','month','user_update']

    def get_initial_queryset(self):

        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.cortes.ver",
                "usuarios.iraca.cuentas_cobro.ver",
            ]
        }
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            account_q = Q(contract__contratista__cedula__icontains=search) | Q(
                contract__contratista__nombres__icontains=search) | Q(
                contract__contratista__apellidos__icontains=search)

            ids = Collects_Account.objects.filter(account_q).values_list('cut__id', flat=True)

            q = Q(name__icontains=search) | Q(consecutive__icontains=search) | Q(id__in=ids)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="view/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver cuentas de cobro corte {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.consecutive)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'

            return ret

        elif column == 'consecutive':
            return '<div class="center-align"><b>' + str(row.consecutive) + '</b></div>'

        elif column == 'date_creation':
            return row.pretty_creation_datetime()

        elif column == 'month':
            return '<div class="center-align"><b>' + str(row.get_cantidad_cuentas_cobro()) + '</b></div>'

        elif column == 'user_update':
            novedad = row.get_novedades_inform()
            if novedad > 0:
                return '<span class="new badge" data-badge-caption="">{0}</span>'.format(novedad)
            else:
                return ''

        else:
            return super(InformListApi, self).render_column(row, column)

class InformCollectAccountListApi(BaseDatatableView):
    model = rh_models.Collects_Account
    columns = ['id','contract','date_creation','estate_inform','delta','user_creation','data_json','valores_json','file','file5','file3','estate','estate_report','date_update','user_update']
    order_columns = ['id','contract','date_creation','estate_inform','delta','user_creation','data_json','valores_json','file','file5','estate','estate_report','date_update','user_update']

    def get_initial_queryset(self):
        self.cut = rh_models.Cuts.objects.get(id=self.kwargs['pk_cut'])

        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.cortes.ver",
                "usuarios.iraca.cuentas_cobro.ver",
            ],
        }
        return self.model.objects.filter(cut__id = self.kwargs['pk_cut']).order_by('-creation')

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(contract__nombre__icontains=search) | \
                Q(contract__contratista__nombres__icontains=search) | Q(contract__contratista__apellidos__icontains=search)| \
                Q(contract__contratista__cedula__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):
        if column == 'id':
            ret = '<div class="center-align">' \
                       '<a href="view/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver cuentas de cobro corte {1}">' \
                            '<i class="material-icons">remove_red_eye</i>' \
                       '</a>' \
                   '</div>'.format(row.id,row.contract.nombre)

            return ret

        elif column == 'contract':
            return '<div class="center-align"><b>' + str(row.contract.nombre) + '</b></div>'

        elif column == 'date_creation':
            return '{0}'.format(row.contract.contratista)

        elif column == 'estate_inform':
            ret = ""
            if row.estate_inform == 'Rechazado':
                ret = '<div class="center-align">' \
                      '<a class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                      '<b>{0}</b>' \
                      '</a>' \
                      '</div>'.format(row.estate_inform, row.observaciones_inform)
            else:
                ret = '{0}'.format(row.estate_inform)
            return ret

        elif column == 'delta':
            url_file4 = row.url_file4()
            if row.estate_inform == 'Generado' and url_file4 != None:
                return '<span class="new badge" data-badge-caption="">1</span>'
            else:
                return ''

        elif column == 'user_creation':
            return row.pretty_print_value_fees()

        elif column == 'data_json':
            return row.contract.inicio

        elif column == 'valores_json':
            return row.contract.fin

        elif column == 'file':

            url_file6 = row.url_file6()


            ret = '<div class="center-align">'

            if url_file6 != None:
                ret += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cuenta de cobro por honorarios">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                       '</a>'.format(url_file6)

            ret += '</div>'

            return ret

        elif column == 'file5':

            url_file4 = row.url_file4()


            ret = '<div class="center-align">'

            if url_file4 != None:
                ret += '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Cuenta de cobro por honorarios">' \
                       '<i class="material-icons" style="font-size: 2rem;">insert_drive_file</i>' \
                       '</a>'.format(url_file4)

            ret += '</div>'

            return ret

        elif column == 'file3':
            ret = ''
            url_file4 = row.url_file4()
            if row.estate_inform == 'Generado':
                if self.request.user.is_superuser:
                    ret += '<a style="color:green;" href="aprobar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                           '<i class="material-icons">{2}</i>' \
                           '</a>'.format(row.id, 'Aprobar', 'check_box')

                    ret += '<a style="color:red;margin-left:10px;" href="rechazar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                           '<i class="material-icons">{2}</i>' \
                           '</a>'.format(row.id, 'Rechazar', 'highlight_off')
                else:
                    if url_file4 != None or url_file4 == "":
                        ret += '<a style="color:green;" href="aprobar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                               '<i class="material-icons">{2}</i>' \
                               '</a>'.format(row.id, 'Aprobar', 'check_box')

                        ret += '<a style="color:red;margin-left:10px;" href="rechazar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                               '<i class="material-icons">{2}</i>' \
                               '</a>'.format(row.id, 'Rechazar', 'highlight_off')
                    else:
                        ret += '<i class="material-icons">{2}</i>' \
                               '</a>'.format(row.id, 'Aprobar', 'check_box')

                        ret += '<i class="material-icons">{2}</i>' \
                               '</a>'.format(row.id, 'Rechazar', 'highlight_off')

            if row.estate_inform == 'Rechazado':
                ret += '<a style="color:green;" href="aprobar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                       '<i class="material-icons">{2}</i>' \
                       '</a>'.format(row.id, 'Aprobar', 'check_box')

            if row.estate_inform == 'Aprobado':
                ret += '<a style="color:red;margin-left:10px;" href="rechazar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                       '<i class="material-icons">{2}</i>' \
                       '</a>'.format(row.id, 'Rechazar', 'highlight_off')


            return '<div class="center-align">' + ret + '</div>'

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

        elif column == 'date_update':
            ret = ""
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="historial/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver historial">' \
                                '<i class="material-icons">message</i>' \
                           '</a>' \
                       '</div>'.format(row.id)
            return ret

        elif column == 'user_update':
            url_file6 = row.url_file6()
            if url_file6:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">assignment</i>' \
                      '</div>'
            else:
                ret = '<div class="center-align">' \
                      '<a  style="color:green" href="generate/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Generar informe de actividades del contrato {1}">' \
                      '<i class="material-icons">assignment</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.contract.nombre)
            return ret

        else:
            return super(InformCollectAccountListApi, self).render_column(row, column)

class LiquidacionesListApi(BaseDatatableView):
    model = rh_models.Liquidations
    columns = ['id','contrato','valor_ejecutado','estado_informe','valor','file','estado','mes','año','file2','estado_seguridad']
    order_columns = ['id','contrato','valor_ejecutado','estado_informe','valor','file','estado','mes','año','file2','estado_seguridad']

    def get_initial_queryset(self):
        return self.model.objects.all()

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search) | Q(contratista__nombres__icontains=search) | \
                Q(contratista__apellidos__icontains=search) | Q(contratista__cedula__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):
        if column == 'id':
            ret = '<div class="center-align">' \
                       '<a href="ver/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar liquidacion: {1}">' \
                            '<i class="material-icons">remove_red_eye</i>' \
                       '</a>' \
                   '</div>'.format(row.id, row.contrato.nombre)
            return ret

        elif column == 'contrato':
            return row.contrato.nombre

        elif column == 'valor_ejecutado':
            return row.contrato.contratista.get_full_name_cedula()

        elif column == 'estado_informe':
            return row.contrato.get_cargo()

        elif column == 'valor':
            valor = str(row.valor).replace('COL', '')
            return valor


        elif column == 'estado':
            if row.estado_informe != None:
                return '<a><div class="center-align"><b>{0}</b></div></a>'.format(row.estado_informe)
            else:
                return row.estado_informe

        elif column == 'file':
            if row.url_file3() != None:
                ret = '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                      '<i class="material-icons">insert_drive_file</i>' \
                      '</a></div>'.format(row.url_file3(), 'Descargar archivo')
            else:
                ret = ''
            return ret

        elif column == 'mes':
            if row.url_file() != None:
                ret = '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                      '<i class="material-icons">insert_drive_file</i>' \
                      '</a></div>'.format(row.url_file(), 'Descargar archivo')
            else:
                ret = ''
            return ret

        elif column == 'año':
            if row.url_file2() != None:
                ret = '<div class="center-align"><a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="{1}">' \
                      '<i class="material-icons">insert_drive_file</i>' \
                      '</a></div>'.format(row.url_file2(), 'Descargar archivo')
            else:
                ret = ''
            return ret

        elif column == 'file2':
            ret = ""
            if row.estado_informe == 'Generada':
                ret += '<a style="color:green;" href="aprobar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                       '<i class="material-icons">{2}</i>' \
                       '</a>'.format(row.id, 'Aprobar', 'check_box')

                ret += '<a style="color:red;margin-left:10px;" href="rechazar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                       '<i class="material-icons">{2}</i>' \
                       '</a>'.format(row.id, 'Rechazar', 'highlight_off')

            elif row.estado_informe == 'Rechazado':
                ret += '<a style="color:green;" href="aprobar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                       '<i class="material-icons">{2}</i>' \
                       '</a>'.format(row.id, 'Aprobar', 'check_box')

            elif row.estado_informe == 'Aprobado':
                ret += '<a style="color:red;margin-left:10px;" href="rechazar/{0}" class="tooltipped" data-position="top" data-delay="50" data-tooltip="{1}">' \
                       '<i class="material-icons">{2}</i>' \
                       '</a>'.format(row.id, 'Rechazar', 'highlight_off')

            return ret

        if column == 'estado_seguridad':
            ret = '<div class="center-align">' \
                       '<a href="historial/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar liquidacion: {1}">' \
                            '<i class="material-icons">history</i>' \
                       '</a>' \
                   '</div>'.format(row.id,row.contrato.nombre)
            return ret
        else:
            return super(LiquidacionesListApi, self).render_column(row, column)

class IndividualMunicipioComunidadListApi(BaseDatatableView):
    model = models.Routes
    columns = ['id','creation','comunity','progress_form','regitered_household']
    order_columns = ['id','creation','comunity','progress_form','regitered_household']

    def get_initial_queryset(self):
        resguardo = Resguards.objects.get(id=self.kwargs['pk_resguardo'])
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.individual.ver",
            ],
            "editar": [
                "usuarios.iraca.ver",
                "usuarios.iraca.individual.ver",
                "usuarios.iraca.individual.editar"
            ],
            "ver_hogares": [
                "usuarios.iraca.ver",
                "usuarios.iraca.individual.ver",
                "usuarios.iraca.individual.hogares.ver"
            ]
        }
        return self.model.objects.filter(comunity__resguard_id=resguardo.id)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(nombre__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('editar')):
                ret = '<div class="center-align">' \
                           '<a href="edit/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades de la ruta {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.name)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.name)

            return ret

        elif column == 'creation':
            ret = ''
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                           '<a href="activities/{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver actividades de la ruta {1}">' \
                                '<i class="material-icons">remove_red_eye</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.name)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id,row.name)

            return ret

        elif column == 'comunity':
            return row.get_comunity_name()

        elif column == 'progress_form':

            return '<div class="center-align">' \
                   '<a class="tooltipped" data-position="left" data-delay="50" ' \
                   'data-tooltip="Progreso general de la ruta">' \
                   '<b>{0}%</b>' \
                   '</a>' \
                   '</div>'.format(row.progress_form)

        elif column == 'regitered_household':
            ret = '<div class="center-align">' \
                       '<b>{1}</b>' \
                   '</div>'.format(row.id,row.regitered_household)
            return ret

        else:
            return super(IndividualMunicipioComunidadListApi, self).render_column(row, column)

class IndividualMunicipioComunidadHogaresListApi(BaseDatatableView):
    model = models.Households
    columns = ['id','document','first_surname','municipality_attention','routes']
    order_columns = ['id','document','first_surname','municipality_attention','routes']

    def get_initial_queryset(self):
        ruta = models.Routes.objects.get(id=self.kwargs['pk_ruta'])
        self.permissions = {
            "ver": [
                "usuarios.iraca.ver",
                "usuarios.iraca.individual.ver"
            ],
            "editar": [
                "usuarios.iraca.ver",
                "usuarios.iraca.individual.ver",
                "usuarios.iraca.individual.editar",
            ]
        }
        return self.model.objects.filter(routes=ruta)

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(first_name__icontains=search) | Q(second_name__icontains=search) | \
                Q(first_surname__icontains=search) | Q(second_surname__icontains=search) | Q(document__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):


        if column == 'id':
            if self.request.user.has_perms(self.permissions.get('ver')):
                ret = '<div class="center-align">' \
                      '<a href="edit/{0}/" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Editar hogar">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">remove_red_eye</i>' \
                       '</div>'.format(row.id)

            return ret

        elif column == 'document':

            return '<div class="center-align"><b>' + str(row.document) + '</b></div>'

        elif column == 'first_surname':
            return row.get_full_name()

        elif column == 'municipality_attention':
            return '{0}, {1}'.format(row.municipality_attention.nombre,row.municipality_attention.departamento.nombre)

        elif column == 'routes':
            return row.get_routes()

        else:
            return super(IndividualMunicipioComunidadHogaresListApi, self).render_column(row, column)