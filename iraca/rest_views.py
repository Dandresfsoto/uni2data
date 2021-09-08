from dal import autocomplete
from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils import timezone
from iraca import models
from iraca.models import Milestones, Meetings, Certificates, Types
from usuarios.models import Municipios


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

        elif column == 'first_name':
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
        return self.model.objects.all()

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
    columns = ['id','creation','name','novelties','progress','regitered_household']
    order_columns = ['id','creation','name','novelties','progress','regitered_household']

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
    columns = ['creation','name','novelties','progress_form','regitered_household']
    order_columns = ['creation','name','novelties','progress_form','regitered_household']

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

class MunicipiosAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):

        qs = Municipios.objects.all().filter(departamento__codigo=27)

        if self.q:
            q = Q(nombre__icontains = self.q) | Q(departamento__nombre__icontains = self.q)
            qs = qs.filter(q)

        return qs



