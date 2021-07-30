#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from usuarios.models import User, ContentTypeSican, PaqueteActivacion
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset
from crispy_forms.layout import ButtonHolder
from crispy_forms_materialize.layout import Layout, Row, Column, Submit, HTML, Hidden
from config.layouts import Stepper, Step, StepInitial, StepFinal
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

class UserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['photo'].widget = forms.FileInput(attrs={'data-max-file-size':'1M','data-height':"230"})
        self.fields['is_active'].widget.attrs['class'] = 'filled-in'
        self.fields['is_staff'].widget.attrs['class'] = 'filled-in'
        self.fields['is_superuser'].widget.attrs['class'] = 'filled-in'
        self.fields['is_verificated'].widget.attrs['class'] = 'filled-in'
        self.fields['celular'].widget = PhoneNumberInternationalFallbackWidget()

        if 'photo' in self.initial.keys():
            try:
                url = self.initial['photo'].url
            except:
                pass
            else:
                self.fields['photo'].widget.attrs['data-default-file'] = url

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Fieldset(
                'Datos personales',
                Row(
                    Column(
                        Div(
                            'photo',
                            css_id='avatar-container'
                        ),
                        css_class='s12 m5'
                    ),
                    Column(
                        Column(
                            'email',
                            css_class='s12'
                        ),
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
                            css_class='s12 m6'
                        ),
                        Column(
                            'cedula',
                            css_class='s12 m6'
                        ),
                        css_class="s12 m7"
                    )
                ),
            ),

            Fieldset(
                'Permisos',
                Row(
                    Column(
                        Div(
                            'groups',
                            css_class='s12'
                        ),
                        css_class='s12'
                    ),
                    Column(
                        Div(
                            'is_active',
                            'is_staff',
                            'is_superuser',
                            'is_verificated',
                            css_class='s12'
                        ),
                        css_class='s12'
                    )
                ),
            ),
            Row(
                Column(
                    Div(
                        Submit(
                            'submit',
                            'Guardar',
                            css_class='button-submit'
                        ),
                        css_class="right-align"
                    ),
                    css_class="s12"
                ),
            )
        )

    class Meta:
        model = User
        fields = ['email','photo','first_name','last_name','cedula','groups','is_active','celular',
                  'is_staff','is_superuser','is_verificated']

        labels = {
            'email': 'Email',
            'first_name': 'Nombre(s)',
            'last_name': 'Apellidos',
            'cedula': 'Cédula',
            'tipo_sangre': 'Tipo de sangre',
            'is_active': 'Usuario activo',
            'is_staff': 'Usuario staff',
            'is_superuser': 'Super usuario',
            'is_verificated': 'Cuenta verificada'
        }

class PermisoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PermisoForm, self).__init__(*args, **kwargs)
        self.fields['content_type'].initial = ContentType.objects.get_for_model(ContentTypeSican)
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset(
                'Información del permiso:',
                Div(
                    Div('name',css_class='col s12 m6'),
                    Div('codename', css_class='col s12 m6'),
                    css_class = 'row'
                ),
                Div(
                    Div('content_type'),
                    css_class = 'hide'
                ),
                Div(
                    Submit(
                        'submit',
                        'Guardar',
                        css_class = 'button-submit'
                    ),
                    css_class="right-align"
                )
            ),
        )

    class Meta:
        model = Permission
        fields = '__all__'
        labels = {
            'codename': 'Codename'
        }
        widget = {
        }

class GroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        content_type = ContentType.objects.get_for_model(ContentTypeSican)
        exclude_perms = ['add_contenttypesican', 'change_contenttypesican', 'delete_contenttypesican']
        self.fields['permissions'].queryset = Permission.objects.filter(content_type=content_type).exclude(codename__in=exclude_perms)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Div(
                Div('name',css_class='col s12'),
                css_class = 'row'
            ),
            Div(
                Div('permissions',css_class='col s12'),
                css_class = 'row'
            ),
            Div(
                Submit(
                    'submit',
                    'Guardar',
                    css_class='button-submit'
                ),
                css_class="right-align"
            )
        )

    class Meta:
        model = Group
        fields = '__all__'

class PaqueteCodigoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PaqueteCodigoForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Paquete de códigos:',
                ),
                Column(
                    'generados',
                    css_class='s12 m4'
                ),
                Column(
                    'description',
                    css_class='s12 m8'
                ),
                Column(
                    'permissions',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="color:#9e9e9e;font-size:0.8rem;">- Los permisos que selecciones en este formulario se asignaran 
                        a las claves de activación.</p>
                        """
                    ),
                css_class = 's12'
                )
            ),
            Row(
                Submit(
                    'submit',
                    'Guardar',
                    css_class='button-submit'
                ),
                css_class="right-align"
            )
        )

    class Meta:
        model = PaqueteActivacion
        fields = ['description','permissions','generados']
        labels = {
            'permissions': 'Permisos',
            'description': 'Descripción del paquete',
            'generados': 'Cantidad de códigos'
        }

class PaqueteCodigoUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PaqueteCodigoUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Paquete de códigos:',
                ),
                Column(
                    'description',
                    css_class='s12'
                ),
                Column(
                    'permissions',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="color:#9e9e9e;font-size:0.8rem;">- Los permisos que selecciones en este formulario se asignaran 
                        a las claves de activación.</p>
                        """
                    ),
                css_class = 's12'
                )
            ),
            Row(
                Submit(
                    'submit',
                    'Guardar',
                    css_class='button-submit'
                ),
                css_class="right-align"
            )
        )

    class Meta:
        model = PaqueteActivacion
        fields = ['description','permissions']
        labels = {
            'permissions': 'Permisos',
            'description': 'Descripción del paquete'
        }

class HojaDeVidaForm(forms.Form):

    photo = forms.ImageField()
    first_name = forms.CharField(max_length=100,label='Nombre(s)')
    last_name = forms.CharField(max_length=100,label='Apellidos')
    celular = forms.CharField(max_length=15,widget=PhoneNumberInternationalFallbackWidget())
    cedula = forms.IntegerField()
    birthday = forms.DateField(label="Fecha de nacimiento")
    tipo_sangre = forms.CharField(max_length=100,label="Grupo sanguíneo")

    lugar_nacimiento = forms.ChoiceField(choices=[('','----------')],label='Municipio de nacimiento')
    lugar_expedicion = forms.ChoiceField(choices=[('', '----------')], label='Municipio de expedición de la cedula')
    lugar_residencia = forms.ChoiceField(choices=[('', '----------')], label='Municipio de residencia')
    nivel_educacion_basica = forms.ChoiceField(choices=[
        ('','----------'),
        ('1°','1° primaria'),
        ('2°', '2° primaria'),
        ('3°', '3° primaria'),
        ('4°', '4° primaria'),
        ('5°', '5° primaria'),
        ('6°', '6° secundaria'),
        ('7°', '7° secundaria'),
        ('8°', '8° secundaria'),
        ('9°', '9° secundaria'),
        ('10°', '10° secundaria'),
        ('11°', '11° secundaria'),
    ])
    grado_educacion_basica = forms.DateField(label="Fecha aproximada de grado")


    def __init__(self, *args, **kwargs):
        super(HojaDeVidaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.fields['photo'].widget = forms.FileInput(attrs={'data-max-file-size': '1M', 'data-height': "300"})

        self.fields['birthday'].widget.attrs['required'] = 'required'

        self.fields['tipo_sangre'].widget = forms.Select(attrs={'required': 'required'}, choices=[
            ('', '----------'),
            ('A+', 'A+'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B-', 'B-'),
            ('AB+', 'AB+'),
            ('AB-', 'AB-'),
            ('O+', 'O+'),
            ('O-', 'O-'),
        ])

        usuario = User.objects.get(id = kwargs['initial']['user'])

        self.fields['first_name'].initial = usuario.first_name
        self.fields['last_name'].initial = usuario.last_name
        self.fields['celular'].initial = usuario.celular
        self.fields['cedula'].initial = usuario.cedula
        self.fields['birthday'].initial = usuario.birthday
        self.fields['tipo_sangre'].initial = usuario.tipo_sangre

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
                        )
                    ),
                    Row(
                        Column(
                            'celular',
                            css_class='s12 m6'
                        ),
                        Column(
                            'cedula',
                            css_class='s12 m6'
                        )
                    ),
                    Row(
                        Column(
                            'birthday',
                            css_class='s12 m6'
                        ),
                        Column(
                            'tipo_sangre',
                            css_class='s12 m6'
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
                    css_class='s12 m6 l4'
                ),
                Column(
                    Div(
                        'lugar_expedicion',
                    ),
                    css_class='s12 m6 l4'
                ),
                Column(
                    Div(
                        'lugar_residencia',
                    ),
                    css_class='s12 m6 l4'
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
                        <a class="btn-floating btn-small waves-effect waves-light red tooltipped" data-position="top" 
                        data-delay="50" data-tooltip="Agregar estudio o titulo académico"><i class="material-icons">add</i></a>
                        """
                    ),
                    css_class='s12'
                ),
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
                        <a class="btn-floating btn-small waves-effect waves-light red tooltipped" data-position="top"
                        data-delay="50" data-tooltip="Agregar una experiencia laboral"><i class="material-icons">add</i></a>
                        """
                    ),
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