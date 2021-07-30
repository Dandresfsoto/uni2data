#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import FormView, TemplateView,ListView, View, UpdateView, CreateView
from django.shortcuts import redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from config.forms import LoginForm, RegisterForm, PerfilForm, PasswordForm, ActivarForm
from django.conf import settings
from braces.views import LoginRequiredMixin
from django.apps import apps
from usuarios.models import Notifications, User, CodigoActivacion, Titulos, Experiencias
from usuarios.tasks import send_mail_templated
from config.settings.base import DEFAULT_FROM_EMAIL, EMAIL_HOST_USER
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from ofertas.models import Ofertas
from ofertas import forms
from recursos_humanos import models as rh_models
from ofertas.models import Ofertas


class Login(FormView):
    """
    View que maneja el proceso de login, solicita dos input: Email y password que son comprobados en form_valid
    """
    template_name = 'no_auth/login.html'
    form_class = LoginForm
    success_url = settings.INIT_URL

    def form_valid(self, form):
        context = self.get_context_data()
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(username=email, password=password)

        if user is not None:
            if user.is_verificated:
                login(self.request, user)
                return redirect(settings.INIT_URL)
            else:
                context['error'] = "Tu usuario no se encuentra activo, verifica el vinculo enviado a " + str(email)
                return self.render_to_response(context)

        else:
            context['error'] = "El correo electrónico y la contraseña que ingresaste no coinciden."
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        kwargs['ofertas'] = Ofertas.objects.filter(estado=True).order_by('-creation')
        return super(Login,self).get_context_data(**kwargs)

class Logout(TemplateView):
    """
    View que maneja el logout de la aplicación, en el metodo dispatch solicita el cierre de sesión y retorna a la url de
    login.
    """
    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return redirect(settings.LOGIN_URL)

class Index(LoginRequiredMixin,
            TemplateView):
    """
    View de inicio, se usa un mixin que requiere el estado login del usuario, en caso de no estarlo regresa a la url de
    login.
    """
    login_url = settings.LOGIN_URL
    template_name = 'index.html'


    def get_apps_data(self):
        items = []
        activar = True


        for app in apps.get_app_configs():
            if hasattr(app, 'sican_name'):
                if self.request.user.has_perm(app.sican_permiso):
                    items.append({
                        'sican_name':app.sican_name,
                        'sican_icon':app.sican_icon,
                        'sican_description':app.sican_description,
                        'sican_color':app.sican_color,
                        'sican_url':app.sican_url,
                        'sican_categoria':app.sican_categoria,
                        'sican_order':app.sican_order
                    })
                    activar = False

        items.append({
            'sican_name': 'Mi hoja de vida',
            'sican_icon': 'insert_drive_file',
            'sican_description': 'Actualizar la información de mi hoja de vida',
            'sican_color': 'orange darken-4',
            'sican_url': '/perfil/',
            'sican_categoria': 'sion',
            'sican_order': 9
        })

        items.append({
            'sican_name': 'Ofertas laborales',
            'sican_icon': 'insert_emoticon',
            'sican_description': 'Postular mi hoja de vida a una oferta laboral',
            'sican_color': 'teal darken-4',
            'sican_url': '/ofertas/aplicar/',
            'sican_categoria': 'sion',
            'sican_order': 10
        })

        if rh_models.Contratistas.objects.filter(usuario_asociado = self.request.user).count() > 0:
            items.append({
                'sican_name': 'Mis contratos',
                'sican_icon': 'insert_drive_file',
                'sican_description': 'Gestión de contratos suscritos y soportes para legalización',
                'sican_color': 'purple darken-4',
                'sican_url': '/contratos/',
                'sican_categoria': 'sion',
                'sican_order': 7
            })

        return {'items':items,'activar':activar}

    def get_filters_data(self):

        categorias = []
        items = [{'data_filter':'all','id':'all','name':'Todo','checked':'checked'}]


        for app in self.get_apps_data()['items']:
            categorias.append( app['sican_categoria'] )

        categorias = sorted(set(categorias))

        for categoria in categorias:
            items.append({
                'data_filter': '.' + categoria,
                'id': 'id' + categoria,
                'name': categoria.replace("_"," ").capitalize(),
            })


        return items

    def get_context_data(self, **kwargs):

        apps_data = self.get_apps_data()
        kwargs['items'] = apps_data['items']

        kwargs['title'] = "sistema de información"
        kwargs['filtros'] = self.get_filters_data()
        kwargs['activar_cuenta'] = apps_data['activar']

        return super(Index,self).get_context_data(**kwargs)

class AplicarOferta(LoginRequiredMixin,
                    CreateView):
    """
    """
    login_url = settings.LOGIN_URL
    template_name = 'aplicar_oferta.html'
    form_class = forms.OfertasForm
    success_url = "../../"


    def get_context_data(self, **kwargs):
        oferta = Ofertas.objects.get(id = self.kwargs['pk'])
        kwargs['title'] = "Aplicar a Oferta de empleo"
        kwargs['oferta'] = oferta
        return super(AplicarOferta,self).get_context_data(**kwargs)

class Notificaciones(LoginRequiredMixin,
                     ListView):
    """
    View de inicio, se usa un mixin que requiere el estado login del usuario, en caso de no estarlo regresa a la url de
    login.
    """
    model = Notifications
    paginate_by = 10
    context_object_name = 'notifications'
    login_url = settings.LOGIN_URL
    template_name = 'notificaciones.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "notificaciones"
        kwargs['url_rest_notification'] = "/rest/v1.0/usuarios/notificaciones/"
        return super(Notificaciones,self).get_context_data(**kwargs)

    def get_queryset(self):
        queryset = self.model.objects.filter(user = self.request.user).order_by('-date')
        return queryset

class Chat(LoginRequiredMixin,
                     ListView):
    """
    """
    model = User
    paginate_by = 10
    context_object_name = 'users'
    login_url = settings.LOGIN_URL
    template_name = 'chat.html'


    def get_context_data(self, **kwargs):
        kwargs['title'] = "chat"
        return super(Chat,self).get_context_data(**kwargs)

class Registro(FormView):
    """

    """
    form_class = RegisterForm
    success_url = '/registro/completo/'
    template_name = 'no_auth/registro.html'

    def form_valid(self, form):
        url_base = self.request.META['HTTP_ORIGIN']

        user = User.objects.create_user(email=form.cleaned_data['email'],
                                        password=form.cleaned_data['password'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])

        user.fullname = user.first_name + " " + user.last_name
        user.save()

        password = form.cleaned_data['password']

        hide = ''

        for val in range(0,len(password)-4):
            hide += '*'

        send_mail_templated.delay('mail/verificar/verificar.tpl',
                                  {
                                      'url_base':url_base,
                                      'first_name': user.first_name,
                                      'email': user.email,
                                      'password': password[:1] + hide + password[len(password)-3:],
                                      'code': str(user.id)
                                  },
                                  DEFAULT_FROM_EMAIL,
                                  [user.email,EMAIL_HOST_USER])

        return super(Registro, self).form_valid(form)

class RegistroCompleto(TemplateView):
    """

    """
    template_name = 'no_auth/registro_completo.html'

class Privacidad(TemplateView):
    """

    """
    template_name = 'no_auth/privacidad.html'

class Verificar(TemplateView):
    """

    """
    template_name = 'no_auth/verificar.html'

    def get(self, request, *args, **kwargs):



        mensaje = ''

        email = self.request.GET.get('email')
        code = self.request.GET.get('code')


        try:
            user = User.objects.get(email = email)
        except:
            mensaje = 'No existe ninguna cuenta con el email: ' + email
        else:
            if user.is_verificated:
                mensaje = 'La cuenta asociada a ' + email + ' ya se encuentra verificada'
            else:
                if str(user.id) == code:
                    user.is_verificated = True
                    user.save()
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(self.request, user)
                    return redirect(settings.INIT_URL)

                else:
                    mensaje = 'Ups!, se presento un error en la verificación de tu cuenta, intenta registrarte usando alguna red social o escribe a sistemas@asoandes.org'

        kwargs['mensaje'] = mensaje
        context = self.get_context_data(**kwargs)

        return self.render_to_response(context)

class Perfil(LoginRequiredMixin,
             UpdateView):
    """
    """
    template_name = 'auth/perfil/perfil.html'
    form_class = PerfilForm
    success_url = settings.INIT_URL
    login_url = settings.LOGIN_URL
    model = User

    def get_object(self):
        return User.objects.get(email=self.request.user.email)

    def get_context_data(self, **kwargs):
        kwargs['title'] = "perfil"
        kwargs['url_guardar_educacion_superior'] = "/rest/v1.0/usuarios/perfil/educacion_superior/"
        kwargs['url_guardar_experiencia'] = "/rest/v1.0/usuarios/perfil/experiencia/"
        kwargs['url_avatar'] = "/rest/v1.0/usuarios/avatar/"
        kwargs['url_hv'] = "/rest/v1.0/usuarios/hv/"
        kwargs['hv_url'] = self.request.user.url_hv()
        kwargs['hv_url_filename'] = self.request.user.hv_filename()
        kwargs['titulos'] = Titulos.objects.filter(usuario = self.request.user).order_by('-creation')
        kwargs['experiencias'] = Experiencias.objects.filter(usuario=self.request.user).order_by('-creation')
        if not self.request.user.formulario_completo_ofertas:
            kwargs['error'] = 'Para aplicar a ofertas de empleo debes registrar tu información académica, experiencia laboral y' \
                              ' adjuntar tu hoja de vida.'

        if self.request.user.cedula == None:
            #kwargs['error'] = "Por favor completa tus datos personales."
            kwargs['modal'] = True

        return super(Perfil,self).get_context_data(**kwargs)

    def get_initial(self):
        return {'user_id':str(self.request.user.id)}

class CambioPassword(LoginRequiredMixin,
                     FormView):
    """
    """
    template_name = 'auth/password/password.html'
    form_class = PasswordForm
    success_url = settings.INIT_URL

    def get_initial(self):
        return {'email':self.request.user.email}

    def form_valid(self, form):
        password = form.cleaned_data['password1']
        user = self.request.user

        user.set_password(password)
        user.save()

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        update_session_auth_hash(self.request, user)

        url_base = self.request.META['HTTP_ORIGIN']

        hide = ''

        for val in range(0, len(password) - 4):
            hide += '*'

        send_mail_templated.delay('mail/password/change.tpl',
                                  {
                                      'url_base': url_base,
                                      'first_name': user.first_name,
                                      'email': user.email,
                                      'password': password[:1] + hide + password[len(password) - 3:]
                                  },
                                  DEFAULT_FROM_EMAIL,
                                  [user.email, EMAIL_HOST_USER])

        return HttpResponseRedirect(self.get_success_url())


class ActivarCuenta(LoginRequiredMixin,
                     FormView):
    """
    """
    template_name = 'auth/activar/activar.html'
    form_class = ActivarForm
    success_url = settings.INIT_URL

    def form_valid(self, form):
        codigo = CodigoActivacion.objects.get(id = form.cleaned_data['codigo'])

        user = self.request.user

        codigo.user = user
        codigo.activation_date = timezone.now()
        codigo.save()

        user.groups.add(*codigo.permissions.all())
        user.save()

        return super(ActivarCuenta, self).form_valid(form)