from rest_framework.views import APIView
from django.http import Http404
from usuarios.models import Notifications, ContentTypeSican
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied
from django_datatables_view.base_datatable_view import BaseDatatableView
from usuarios.models import User, Titulos
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework.permissions import AllowAny
from usuarios.tasks import send_mail_templated
from config.settings.base import DEFAULT_FROM_EMAIL, EMAIL_HOST_USER
import random
from django.contrib.auth import authenticate, login
from usuarios.models import PaqueteActivacion, CodigoActivacion,Municipios, Experiencias, ConsejosResguardosProyectosIraca, \
    ComunidadesProyectosIraca
from dal import autocomplete
from django.utils import timezone
from django.core import serializers
from django.shortcuts import render
from uuid import UUID

class NotificationsApi(APIView):
    """
    """

    def get_object(self, pk):
        try:
            notification = Notifications.objects.get(pk=pk)
        except Notifications.DoesNotExist:
            raise Http404
        else:
            if(notification.user == self.request.user):
                return notification
            else:
                raise PermissionDenied

    def delete(self, request, format=None):

        if(request.POST['pk'] == 'all'):
            Notifications.objects.filter(user = request.user).delete()
        else:
            notification = self.get_object(request.POST['pk'])
            notification.delete()

        return Response({'length':Notifications.objects.filter(user = request.user).count()},status=status.HTTP_200_OK)

class CuentasListApi(BaseDatatableView):
    model = User
    columns = ['id','email','first_name','last_name','last_online','is_active']
    order_columns = ['id','email', 'first_name','last_name','last_online','is_active']


    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(email__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search)
            qs = qs.filter(q)
        return qs


    def render_column(self, row, column):
        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.usuarios.cuentas.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar usuario: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.email)

            else:
                ret = '<div class="center-align">' \
                           '<i class="material-icons">edit</i>' \
                       '</div>'.format(row.id,row.email)

            return ret

        elif column == 'last_online':
            return row.last_login_natural_time()

        elif column == 'is_active':

            render = ""

            if row.is_active:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Usuario activo">' \
                            '<i class="material-icons">account_circle</i>' \
                          '</a>'
            if row.is_staff:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Usuario staff">' \
                            '<i class="material-icons">airplay</i>' \
                          '</a>'

            if row.is_superuser:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Super usuario">' \
                            '<i class="material-icons">supervisor_account</i>' \
                          '</a>'

            if row.is_verificated:
                render += '<a class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Cuenta verificada">' \
                            '<i class="material-icons">verified_user</i>' \
                          '</a>'

            return '<div class="center-align">' + render + '</div>'

        else:
            return super(CuentasListApi, self).render_column(row, column)

class PermisosListApi(BaseDatatableView):
    model = Permission
    columns = ['id','name','codename']
    order_columns = ['id','name','codename']

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(name__icontains=search) | Q(codename__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.usuarios.permisos.editar'):
                ret = '<div class="center-align">' \
                       '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar: {1}">' \
                            '<i class="material-icons">edit</i>' \
                       '</a>' \
                   '</div>'.format(row.id,row.codename)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">edit</i>' \
                      '</div>'.format(row.id, row.codename)

            return ret


        return super(PermisosListApi, self).render_column(row, column)

    def get_initial_queryset(self):
        content_type = ContentType.objects.get_for_model(ContentTypeSican)
        exclude_perms = ['add_contenttypesican','change_contenttypesican','delete_contenttypesican']
        return Permission.objects.filter(content_type = content_type).exclude(codename__in = exclude_perms)

class RolesListApi(BaseDatatableView):
    model = Group
    columns = ['id','name','permissions']
    order_columns = ['id','name','permissions']

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(name__icontains=search) | Q(permissions__name__icontains=search) | Q(permissions__codename__icontains=search)
            qs = qs.filter(q).distinct()
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.usuarios.roles.editar'):
                ret = '<div class="center-align">' \
                           '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Editar: {1}">' \
                                '<i class="material-icons">edit</i>' \
                           '</a>' \
                       '</div>'.format(row.id,row.name)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">edit</i>' \
                      '</div>'.format(row.id, row.name)

            return ret


        if column == 'permissions':

            ret = ''

            for permiso in row.permissions.all():
                ret += '<p>' + permiso.codename + '</p>'

            return ret

        return super(RolesListApi, self).render_column(row, column)

class RecoveryApi(APIView):
    """
    """
    permission_classes = (AllowAny,)
    def post(self, request, format=None):

        email = request.POST.get('email')
        codigo = request.POST.get('codigo')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        response = ''

        if codigo == None and password1 == None and password2 == None:
            try:
                user = User.objects.get(email = email)
            except:
                response = 'no_existe'
            else:
                user.recovery_code = random.randint(100000,999999)
                user.save()

                url_base = self.request.META['HTTP_ORIGIN']

                send_mail_templated.delay('mail/recovery/recovery.tpl',
                                          {
                                              'url_base': url_base,
                                              'first_name': user.first_name,
                                              'email': user.email,
                                              'codigo': str(user.recovery_code)
                                          },
                                          DEFAULT_FROM_EMAIL,
                                          [user.email, EMAIL_HOST_USER])

                response = 'enviado'
        else:
            try:
                user = User.objects.get(email = email)
            except:
                response = 'no_existe'
            else:
                if int(codigo) != user.recovery_code:
                    response = 'codigo_invalido'
                else:
                    if password1 != password2:
                        response = 'pasword_error'
                    else:
                        if len(password1) < 5:
                            response = 'password_len'
                        else:
                            user.set_password(password1)
                            user.save()

                            url_base = self.request.META['HTTP_ORIGIN']

                            hide = ''

                            for val in range(0, len(password1) - 4):
                                hide += '*'

                            send_mail_templated.delay('mail/password/change.tpl',
                                                      {
                                                          'url_base': url_base,
                                                          'first_name': user.first_name,
                                                          'email': user.email,
                                                          'password': password1[:1] + hide + password1[len(password1) - 3:]
                                                      },
                                                      DEFAULT_FROM_EMAIL,
                                                      [user.email, EMAIL_HOST_USER])

                            user = authenticate(username=email, password=password1)
                            login(self.request, user)
                            response = 'ok'

        return Response({
            'response': response
        },status=status.HTTP_200_OK)

class PaquetesListApi(BaseDatatableView):
    model = PaqueteActivacion
    columns = ['id','permissions','creation','description','generados','usados','file']
    order_columns = ['id','permissions','creation','description','generados','usados','file']

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(description__icontains=search)
            qs = qs.filter(q)
        return qs

    def render_column(self, row, column):

        if column == 'id':
            ret = ''
            if self.request.user.has_perm('usuarios.usuarios.codigos.editar'):
                ret = '<div class="center-align">' \
                       '<a href="editar/{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Ver: {1}">' \
                            '<i class="material-icons">edit</i>' \
                       '</a>' \
                   '</div>'.format(row.id,row.description)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">edit</i>' \
                      '</div>'.format(row.id, row.description)

            return ret

        elif column == 'permissions':
            if self.request.user.has_perm('usuarios.usuarios.codigos.ver'):
                ret = '<div class="center-align">' \
                      '<a href="{0}" class="tooltipped link-sec" data-position="top" data-delay="50" data-tooltip="Ver códigos: {1}">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</a>' \
                      '</div>'.format(row.id, row.description)

            else:
                ret = '<div class="center-align">' \
                      '<i class="material-icons">remove_red_eye</i>' \
                      '</div>'.format(row.id, row.description)

            return ret

        elif column == 'creation':
            return '<p>' + row.pretty_creation_datetime() + '</p>'

        elif column == 'description':
            return '<p>' + row.description + '</p>'

        elif column == 'file':

            try:
                url = row.file.url
            except:
                return ''
            else:
                return '<div class="center-align">' \
                       '<a href="{0}" class="tooltipped edit-table" data-position="top" data-delay="50" data-tooltip="Excel: {1}">' \
                            '<i class="material-icons" style="font-size: 3rem;">insert_drive_file</i>' \
                       '</a>' \
                   '</div>'.format(url, row.description)


        return super(PaquetesListApi, self).render_column(row, column)

class PaquetesCodigosListApi(BaseDatatableView):
    model = CodigoActivacion
    columns = ['id','user','activation_date']
    order_columns = ['id','user','activation_date']

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            q = Q(user__email__icontains=search)| Q(id__icontains=search)
            qs = qs.filter(q)
        return qs

    def get_initial_queryset(self):
        return self.model.objects.filter(paquete__id=self.kwargs['pk'])

    def render_column(self, row, column):
        if column == 'user':
            if row.user == None:
                return 'Ninguno'
            else:
                return row.user.email

        if column == 'activation_date':
            if row.activation_date == None:
                return 'Ninguna'
            else:
                return row.pretty_activation_date_datetime()

        return super(PaquetesCodigosListApi, self).render_column(row, column)

class MunicipiosAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):

        qs = Municipios.objects.all()

        if self.q:
            q = Q(nombre__icontains = self.q) | Q(departamento__nombre__icontains = self.q)
            qs = qs.filter(q)

        return qs

class EducacionSuperiorAPI(APIView):
    """
    """

    def delete(self, request, format=None):

        response = ''
        status_response = None
        data = request.POST
        id = data.get('id')

        try:
            titulo = Titulos.objects.filter(usuario = request.user).get(id = id)
        except:
            response = 'No existe el id'
            status_response = status.HTTP_203_NON_AUTHORITATIVE_INFORMATION
        else:
            titulo.delete()
            response = 'Eliminado'
            status_response = status.HTTP_200_OK

        return Response({'response': response}, status=status_response)


    def post(self, request, format=None):

        response = ''
        status_response = None
        data = []

        data = request.POST

        modalidad_academica = data.get('modalidad_academica')
        semestres_aprobados = data.get('semestres_aprobados')
        graduado = data.get('graduado')
        nombre_estudio = data.get('nombre_estudio')
        fecha_terminacion = data.get('fecha_terminacion')
        numero_tarjeta_profesional = data.get('numero_tarjeta_profesional')
        fecha_tarjeta_profesional = data.get('fecha_tarjeta_profesional')

        if modalidad_academica == None or semestres_aprobados == None or graduado == None or nombre_estudio == '' \
                or fecha_terminacion == '':
            response = 'Por favor completa todos los campos obligatorios (marcados con *)'
            status_response = status.HTTP_206_PARTIAL_CONTENT

        elif numero_tarjeta_profesional != '' and fecha_tarjeta_profesional == '':
            response = 'Por favor ingresa la fecha de expedición de la tarjeta profesional'
            status_response = status.HTTP_206_PARTIAL_CONTENT

        elif numero_tarjeta_profesional == '' and fecha_tarjeta_profesional != '':
            response = 'Por favor ingresa el numero de la tarjeta profesional'
            status_response = status.HTTP_206_PARTIAL_CONTENT

        else:
            if numero_tarjeta_profesional != '' and fecha_tarjeta_profesional != '':
                titulo = Titulos.objects.create(
                    usuario = request.user,
                    modalidad = modalidad_academica,
                    semestres = semestres_aprobados,
                    graduado = graduado,
                    nombre = nombre_estudio,
                    fecha_terminacion = timezone.datetime.strptime(fecha_terminacion,"%d/%m/%Y"),
                    numero_tarjeta = numero_tarjeta_profesional,
                    fecha_expedicion = timezone.datetime.strptime(fecha_tarjeta_profesional,"%d/%m/%Y"),
                )
            else:
                titulo = Titulos.objects.create(
                    usuario=request.user,
                    modalidad=modalidad_academica,
                    semestres=semestres_aprobados,
                    graduado=graduado,
                    nombre=nombre_estudio,
                    fecha_terminacion=timezone.datetime.strptime(fecha_terminacion,"%d/%m/%Y"),
                )
            response = 'Creado'
            data = serializers.serialize("json",Titulos.objects.filter(usuario = request.user).filter(id = titulo.id))

            status_response = status.HTTP_201_CREATED



        return Response({'response': response,'data':data},status=status_response)

class ExperienciaAPI(APIView):
    """
    """

    def delete(self, request, format=None):

        response = ''
        status_response = None
        data = request.POST
        id = data.get('id')

        try:
            experiencia = Experiencias.objects.filter(usuario = request.user).get(id = id)
        except:
            response = 'No existe el id'
            status_response = status.HTTP_203_NON_AUTHORITATIVE_INFORMATION
        else:
            experiencia.delete()
            response = 'Eliminado'
            status_response = status.HTTP_200_OK

        return Response({'response': response}, status=status_response)


    def post(self, request, format=None):

        response = ''
        status_response = None
        data = []

        data = request.POST

        nombre_empresa = data.get('nombre_empresa')
        tipo_empresa = data.get('tipo_empresa')
        email_empresa = data.get('email_empresa')
        telefono_empresa = data.get('telefono_empresa')
        cargo_empresa = data.get('cargo_empresa')
        dependencia_empresa = data.get('dependencia_empresa')
        direccion_empresa = data.get('direccion_empresa')
        fecha_ingreso = data.get('fecha_ingreso')
        fecha_retiro = data.get('fecha_retiro')
        municipio = data.get('municipio')

        if nombre_empresa == '' or tipo_empresa == None or cargo_empresa == '' or dependencia_empresa == '' \
                or fecha_ingreso == '' or fecha_retiro == '' or municipio == None:
            response = 'Por favor completa todos los campos obligatorios (marcados con *)'
            status_response = status.HTTP_206_PARTIAL_CONTENT

        elif timezone.datetime.strptime(fecha_ingreso, "%d/%m/%Y") > timezone.datetime.strptime(fecha_retiro, "%d/%m/%Y"):
            response = 'La fecha de ingreso no puede ser superior a la fecha de retiro'
            status_response = status.HTTP_206_PARTIAL_CONTENT


        else:
            experiencia = Experiencias.objects.create(
                usuario=request.user,
                nombre_empresa=nombre_empresa,
                tipo_empresa=tipo_empresa,
                email_empresa=email_empresa,
                telefono_empresa=telefono_empresa,
                cargo = cargo_empresa,
                dependencia = dependencia_empresa,
                direccion = direccion_empresa,
                fecha_ingreso=timezone.datetime.strptime(fecha_ingreso, "%d/%m/%Y"),
                fecha_retiro=timezone.datetime.strptime(fecha_retiro, "%d/%m/%Y"),
                municipio = Municipios.objects.get(id = municipio)
            )
            response = 'Creado'
            data = serializers.serialize("json",Experiencias.objects.filter(usuario = request.user).filter(id = experiencia.id))

            status_response = status.HTTP_201_CREATED



        return Response({'response': response,'data':data},status=status_response)

class AvatarAPI(APIView):
    """
    """

    def delete(self, request, format=None):

        response = 'Eliminado'
        status_response = None
        user = request.user

        user.photo.delete()
        user.usar_photo_social_login = False
        user.save()
        status_response = status.HTTP_200_OK

        return Response({'response': response}, status=status_response)

class HvAPI(APIView):
    """
    """

    def delete(self, request, format=None):

        response = 'Eliminado'
        status_response = None
        user = request.user

        user.hv.delete()
        user.save()
        status_response = status.HTTP_200_OK

        return Response({'response': response}, status=status_response)

def cargar_consejos(request):
    municipio_id = request.GET.get('municipio')
    try:
        UUID(municipio_id)
    except:
        consejos = ConsejosResguardosProyectosIraca.objects.none()
    else:
        consejos = ConsejosResguardosProyectosIraca.objects.filter(municipio=municipio_id).order_by('nombre')

    return render(request, 'consejos/load/consejos_dropdown_list_options.html', {'consejos': consejos})

def cargar_comunidades(request):
    consejo_id = request.GET.get('consejo')
    try:
        UUID(consejo_id)
    except:
        comunidades = ComunidadesProyectosIraca.objects.none()
    else:
        comunidades = ComunidadesProyectosIraca.objects.filter(consejo_resguardo__id=consejo_id).order_by('nombre')

    return render(request, 'comunidades/load/comunidades_dropdown_list_options.html', {'comunidades': comunidades})
