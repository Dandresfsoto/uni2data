#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, ButtonHolder, Fieldset
from crispy_forms_materialize.layout import Layout, Row, Column, Submit, HTML, Hidden, Div, Button
from usuarios.models import User, CodigoActivacion, Municipios
from django.contrib.auth import authenticate
from django.forms.fields import Field, FileField
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

class LoginForm(forms.Form):

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Div(
                HTML(
                    """
                    <div>
                        <p class="title-login center-align">INICIAR SESIÓN</p>
                    </div>
                    """
                ),
                Div(
                    'email',
                    'password'
                ),
                Div(
                    HTML(
                        '''
                        <a href="#recovery" class="modal-trigger">Olvidaste la contraseña?</a>
                        '''
                    ),
                    css_class='right-align margin-space'
                ),
                ButtonHolder(
                    Submit('submit','Continuar',css_class='button-submit'),
                    css_class='right-align'
                ),
                HTML(
                    """
                    <div>
                        <p class="center-align" style="color:#aaa;font-size:0.8rem;margin-top:30px;">
                            Puedes iniciar sesión o registrarte usando redes sociales, conoce nuestra <a href="/privacidad/">politica de privacidad</a>.
                        </p>
                    </div>
                    """
                ),
                Div(
                    HTML(
                        """
                        <div style="margin-top:20px;">
                            
                            <div class="col s12 center-align">
                                <a href="{% url 'social:begin' 'google-oauth2' %}"
                                        class="waves-effect waves-light btn-floating btn-large social google"
                                        style="display: inline-block;">
                                        
                                    <i class="fab fa-fw fa-google"></i>
                                </a>
                            </div>
                            
                        </div>
                        """
                    )
                ),
                css_class = 'login-body-container'
            )
        )

class RegisterForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=100,label="Nombres")
    last_name = forms.CharField(max_length=100,label="Apellidos")

    password = forms.CharField(widget=forms.PasswordInput(),label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput(),label="Confirmar contraseña")

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        email = cleaned_data.get("email")

        if password != password2:
            self.add_error('password2','Las contraseñas no coinciden')

        if User.objects.filter(email = email).count() > 0:
            self.add_error('email', 'El email ya se encuentra registrado')

        if password == password2 and len(password) < 5:
            self.add_error('password', 'La contraseña debe contener como minimo 5 caracteres')


    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Div(
                HTML(
                    """
                    <div style="margin-bottom:20px;">
                        <h4 class="center-align" style="font-weight:bold;">Regístrate</h4>
                        <p class="p-login" style="display:inline"> ¿Ya tienes cuenta? </p>
                        <a href="/login/">Inicia Sesión</a>
                    </div>
                    """
                ),
                Div(
                    Row(
                        Column(
                            HTML(
                                """
                                <h5 class="center-align" style="font-weight:bold;">Con tus redes sociales</h5>
                                
                                <div style="margin:60px 0;">
                                
                                    
                                    <div class="row">
                                        <a href="{% url 'social:begin' 'google-oauth2' %}"
                                            class="waves-effect waves-light btn col s12 social google" 
                                            style = "padding:0;">
                                            <i class="fab fa-google"></i>
                                            Regístrate con Google
                                        </a>
                                    </div>
                                    
                                    
                                    <div style="margin-top:50px;">
                                        <p class="p-login" style="display:inline;">No te preocupes por tu </p>
                                        <a href="/privacidad/" style="display:inline;">privacidad</a>
                                        <p class="p-login" style="display:inline;"> solo usamos las redes sociales para conocer tu 
                                        email y nombre completo, es una contraseña menos para recordar.</p>
                                    </div>
                                    
                                </div>
                                """
                            ),
                            css_class="l6 s12"
                        ),
                        Column(
                            HTML(
                                """
                                <h5 class="center-align" style="font-weight:bold;margin-bottom:20px;">Con un usuario y contraseña</h5>
                                """
                            ),
                            'email',
                            'first_name',
                            'last_name',
                            'password',
                            'password2',
                            ButtonHolder(
                                Submit('submit', 'Registrarse', css_class='button-submit'),
                                css_class='right-align margin-submit'
                            ),
                            css_class="l6 s12 register-container-border"
                        )
                    ),
                    css_class = "register-container"
                ),
                css_class='login-body-container'
            )
        )

class PerfilForm(forms.ModelForm):

    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            if name not in ['lugar_nacimiento','lugar_expedicion','lugar_residencia']:
                if field.disabled:
                    value = self.get_initial_for_field(field, name)
                else:
                    value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
                try:
                    if isinstance(field, FileField):
                        initial = self.get_initial_for_field(field, name)
                        value = field.clean(value, initial)
                    else:
                        value = field.clean(value)
                    self.cleaned_data[name] = value
                    if hasattr(self, 'clean_%s' % name):
                        value = getattr(self, 'clean_%s' % name)()
                        self.cleaned_data[name] = value
                except ValidationError as e:
                    self.add_error(name, e)
            else:
                value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
                if value != '':
                    self.cleaned_data[name] = Municipios.objects.get(id = value)
                else:
                    self.add_error(name, 'Completa este campo')

    def clean(self):
        cleaned_data = super().clean()

        birthday = cleaned_data.get("birthday")
        tipo_sangre = cleaned_data.get("tipo_sangre")
        sexo = cleaned_data.get("sexo")

        if birthday == None:
            self.add_error('birthday', 'Completa este campo')

        if tipo_sangre == None:
            self.add_error('tipo_sangre', 'Completa este campo')

        if sexo == None:
            self.add_error('sexo', 'Completa este campo')


    def __init__(self, *args, **kwargs):
        super(PerfilForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        usuario = User.objects.get(id = kwargs['initial']['user_id'])

        self.fields['photo'].widget = forms.FileInput(attrs={'data-max-file-size': '1M', 'data-height': "300",
                                                             'accept': 'image/jpg,image/jpeg,image/png'})


        self.fields['hv'].widget = forms.FileInput(attrs={'data-max-file-size': '20M',
                                                          'accept': 'application/pdf,application/x-pdf'})


        self.fields['celular'].widget.attrs['required'] = 'required'
        self.fields['cedula'].widget.attrs['required'] = 'required'
        self.fields['birthday'].widget.attrs['required'] = 'required'
        self.fields['direccion'].widget.attrs['required'] = 'required'

        self.fields['celular'].widget.attrs['lugar_nacimiento'] = 'required'
        self.fields['cedula'].widget.attrs['lugar_expedicion'] = 'required'
        self.fields['birthday'].widget.attrs['lugar_residencia'] = 'required'

        self.fields['tipo_sangre'].widget = forms.Select(choices = [
            ('','----------'),
            ('A+', 'A+'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B-', 'B-'),
            ('AB+', 'AB+'),
            ('AB-', 'AB-'),
            ('O+', 'O+'),
            ('O-', 'O-'),
        ])
        self.fields['nivel_educacion_basica'].widget = forms.Select(choices = [
            ('', '----------'),
            ('1°', '1° primaria'),
            ('2°', '2° primaria'),
            ('3°', '3° primaria'),
            ('4°', '4° primaria'),
            ('5°', '5° primaria'),
            ('6°', '6° secundaria'),
            ('7°', '7° secundaria'),
            ('8°', '8° secundaria'),
            ('9°', '9° secundaria'),
            ('10°', '10° secundaria'),
            ('11°', '11° secundaria')
        ])
        self.fields['sexo'].widget = forms.Select(choices=[
            ('', '----------'),
            ('Femenino', 'Femenino'),
            ('Masculino', 'Masculino'),
            ('No especificarlo', 'No especificarlo')
        ])

        self.fields['lugar_nacimiento'].queryset = Municipios.objects.none()
        self.fields['lugar_expedicion'].queryset = Municipios.objects.none()
        self.fields['lugar_residencia'].queryset = Municipios.objects.none()

        if 'photo' in self.initial.keys():
            try:
                url = self.initial['photo'].url
            except:
                pass
            else:
                self.fields['photo'].widget.attrs['data-default-file'] = url

        if 'hv' in self.initial.keys():
            try:
                url = self.initial['hv'].url
            except:
                pass
            else:
                self.fields['hv'].widget.attrs['data-default-file'] = url

        if usuario.lugar_nacimiento != None:
            self.fields['lugar_nacimiento'].queryset = Municipios.objects.filter(id = usuario.lugar_nacimiento.id)
            self.fields['lugar_nacimiento'].initial = usuario.lugar_nacimiento

        if usuario.lugar_expedicion != None:
            self.fields['lugar_expedicion'].queryset = Municipios.objects.filter(id = usuario.lugar_expedicion.id)
            self.fields['lugar_expedicion'].initial = usuario.lugar_expedicion

        if usuario.lugar_residencia != None:
            self.fields['lugar_residencia'].queryset = Municipios.objects.filter(id = usuario.lugar_residencia.id)
            self.fields['lugar_residencia'].initial = usuario.lugar_residencia

        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Datos personales:'
                ),
                Column(
                    Div(
                        'photo',
                        css_id='avatar-container'
                    ),
                    css_class='s12 m5'
                ),
                Column(
                    Row(
                        Column(
                            HTML(
                                """
                                <p><b>Email:</b> {{user.email}}</p>
                                """
                            )
                        )
                    ),
                    Row(
                        Column(
                            'first_name',
                            css_class='s12 m6'
                        ),
                        Column(
                            'last_name',
                            css_class='s12 m6'
                        ),
                        Column(
                            'celular',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'cedula',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'sexo',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'birthday',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'tipo_sangre',
                            css_class='s12 m6 l3'
                        ),
                        Column(
                            'direccion',
                            css_class='s12 m6 l5'
                        )
                    ),
                    css_class="s12 m7"
                )
            ),
            Row(
                Column(
                    Div(
                        'lugar_nacimiento',
                    ),
                    css_class='s12 m6 l4 margin-bottom-select'
                ),
                Column(
                    Div(
                        'lugar_expedicion',
                    ),
                    css_class='s12 m6 l4 margin-bottom-select'
                ),
                Column(
                    Div(
                        'lugar_residencia',
                    ),
                    css_class='s12 m6 l4 margin-bottom-select'
                ),
            ),
            Row(
                Fieldset(
                    'Formación académica:'
                ),
                Column(
                    HTML(
                        """
                        <p style="margin-bottom:30px;"><b>EDUCACIÓN BÁSICA Y MEDIA</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'nivel_educacion_basica',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'grado_educacion_basica',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="margin-bottom:20px;"><b>EDUCACIÓN SUPERIOR (PREGRADO Y POSTGRADO)</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <div class = "row">
                            <div class = "col s12">
                                <a class="btn-floating btn-small waves-effect waves-light red tooltipped modal-trigger" 
                                data-position="top" data-delay="50" href="#modal_educacion_superior"
                                data-tooltip="Agregar estudio o titulo académico"><i class="material-icons">add</i></a>
                            </div>
                        </div>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        
                        <div class = "row" id="container_titulos">
                            {% for titulo in titulos %}
                            <div id="container_{{ titulo.id }}" class = "col s12 m6">
                                <div class = "card grey lighten-4">
                                    <div class="card-content">
                                        <span class="card-title"><b>{{ titulo.nombre }}</b></span>
                                        <p><b>Modalidad: </b>{{ titulo.modalidad }}</p>
                                        <p><b>Semestres aprobados: </b>{{ titulo.semestres }}</p>
                                        <p><b>Graduado: </b>{{ titulo.graduado }}</p>
                                        <p><b>Fecha de terminación: </b>{{ titulo.fecha_terminacion }}</p>
                                        
                                        {% if titulo.numero_tarjeta != None %}
                                        <p><b>Número de tarjeta profesional: </b>{{ titulo.numero_tarjeta }}</p>
                                        {% endif %}
                                        
                                        {% if titulo.numero_tarjeta != None %}
                                        <p><b>Fecha de expedición: </b>{{ titulo.fecha_expedicion }}</p>
                                        {% endif %}
                                        
                                    </div>
                                    <div class="card-action">
                                        <a id="{{ titulo.id }}" class="eliminar_titulo" style="cursor: pointer;">Eliminar</a>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="margin-bottom:20px;"><b>EXPERIENCIA LABORAL</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <div class = "row">
                            <div class = "col s12">
                                <a class="btn-floating btn-small waves-effect waves-light red tooltipped modal-trigger" 
                                data-position="top" data-delay="50" href="#modal_experiencia_laboral"
                                data-tooltip="Agregar experiencia laboral"><i class="material-icons">add</i></a>
                            </div>
                        </div>
                        
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """

                        <div class = "row" id="container_experiencia">
                            {% for experiencia in experiencias %}
                            <div id="container_experiencia_{{ experiencia.id }}" class = "col s12 m6">
                                <div class = "card grey lighten-4">
                                    <div class="card-content">
                                        <span class="card-title"><b>{{ experiencia.cargo }}</b></span>
                                        <p><b>Empresa: </b>{{ experiencia.nombre_empresa }}</p>
                                        <p><b>Tipo de empresa: </b>{{ experiencia.tipo_empresa }}</p>
                                        <p><b>Dependencia: </b>{{ experiencia.dependencia }}</p>
                                        <p><b>Fecha de ingreso: </b>{{ experiencia.fecha_ingreso }}</p>
                                        <p><b>Fecha de retiro: </b>{{ experiencia.fecha_retiro }}</p>
                                        <p><b>Municipio: </b>{{ experiencia.municipio }}</p>

                                        {% if experiencia.email_empresa != '' %}
                                        <p><b>Email: </b>{{ experiencia.email_empresa }}</p>
                                        {% endif %}

                                        {% if experiencia.telefono_empresa != '' %}
                                        <p><b>Telefono: </b>{{ experiencia.telefono_empresa }}</p>
                                        {% endif %}
                                        
                                        {% if experiencia.direccion != '' %}
                                        <p><b>Dirección: </b>{{ experiencia.direccion }}</p>
                                        {% endif %}

                                    </div>
                                    <div class="card-action">
                                        <a id="{{ experiencia.id }}" class="eliminar_experiencia" style="cursor: pointer;">Eliminar</a>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>

                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                HTML(
                    """
                    <p style="color:#9e9e9e;font-size:0.8rem;">- Los campos marcados con * son obligatorios.</p>
                    <p style="color:#9e9e9e;font-size:0.8rem;">- El uso de la imagen es opcional, en el registro 
                    con redes sociales se usa por defecto tu foto de perfil actual.</p>
                    """
                )
            ),
            Row(
                Fieldset(
                    'Hoja de vida:'
                ),
                Column(
                    HTML(
                        """
                        <p><b>Actualmente: </b><a id="hv_actualmente" href="{{hv_url}}">{{hv_url_filename}}</a></p>
                        """
                    ),
                    'hv',
                    css_class='s12'
                ),
            ),
            Row(
                ButtonHolder(
                    Submit('submit', 'Guardar', css_class='button-submit'),
                    css_class='right-align'
                )
            )

        )

    class Meta:
        model = User
        fields = ['first_name','last_name','cedula','celular','photo','birthday','tipo_sangre','lugar_nacimiento',
                  'lugar_expedicion','lugar_residencia','nivel_educacion_basica','grado_educacion_basica','hv','sexo',
                  'direccion']
        labels = {
            'first_name': 'Nombre(s)',
            'last_name': 'Apellidos',
            'birthday': 'Fecha de nacimiento *',
            'tipo_sangre': 'Grupo sanguíneo *',
            'celular': 'Celular *',
            'cedula': 'Cedula *',
            'lugar_nacimiento': 'Municipio de nacimiento *',
            'lugar_expedicion': 'Municipio de expedición de la cedula *',
            'lugar_residencia': 'Municipio de residencia *',
            'nivel_educacion_basica': 'Nivel de educación básica',
            'grado_educacion_basica': 'Fecha de grado',
            'sexo': 'Sexo *',
            'direccion': 'Dirección de residencia *'
        }

class PasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput(), label="Email")
    original = forms.CharField(widget=forms.PasswordInput(),label="Contraseña actual",min_length=5)
    password1 = forms.CharField(widget=forms.PasswordInput(),label="Nueva contraseña",min_length=5)
    password2 = forms.CharField(widget=forms.PasswordInput(),label="Confirme la nueva contraseña",min_length=5)

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        original = cleaned_data.get("original")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        user = authenticate(username = email, password = original)

        if password1 != password2:
            self.add_error('password1','Las contraseñas no coinciden')

        if user == None:
            self.add_error('original','La contraseña no corresponde')

    def __init__(self, *args, **kwargs):
        super(PasswordForm, self).__init__(*args, **kwargs)

        self.fields['email'].initial = kwargs['initial']['email']

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Cambiar contraseña'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="color:#9e9e9e;font-size:0.8rem;">Por favor ingrese la contraseña actual y confirme la nueva contraseña.</p>
                        """
                    ),
                    css_class="s12"
                )
            ),
            Row(
                Column(
                    'email',
                    'original',
                    css_class="s12 m6 l4"
                ),
                Column(
                    'password1',
                    css_class="s12 m6 l4"
                ),
                Column(
                    'password2',
                    css_class="s12 m6 l4"
                ),
            ),
            Row(
                ButtonHolder(
                    Submit('submit', 'Guardar', css_class='button-submit'),
                    css_class='right-align'
                )
            )
        )

class ActivarForm(forms.Form):

    codigo = forms.UUIDField(label="Código")

    def clean(self):
        cleaned_data = super().clean()

        codigo = cleaned_data.get("codigo")

        try:
            codigo_obj = CodigoActivacion.objects.get(id = codigo)
        except:
            self.add_error('codigo', 'El código de activación no existe')
        else:
            if codigo_obj.user != None:
                self.add_error('codigo', 'El código de activación ya fue utilizado')


    def __init__(self, *args, **kwargs):
        super(ActivarForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Activar cuenta'
                )
            ),
            Row(
                Column(
                    'codigo',
                    css_class = "s12"
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="color:#9e9e9e;">Por favor ingrese el código de activación para su cuenta y presione el boton "Guardar".<p>
                        """
                    ),
                    css_class="s12"
                )
            ),
            Row(
                ButtonHolder(
                    Submit('submit', 'Guardar', css_class='button-submit'),
                    css_class='right-align'
                )
            )
        )