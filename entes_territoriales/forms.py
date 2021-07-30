#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from entes_territoriales import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset
from crispy_forms_materialize.layout import Layout, Row, Column, Submit, HTML, Button
from usuarios.models import Municipios
from recursos_humanos.models import Contratistas, Contratos
from django.db.models import Q
from django.conf import settings
import openpyxl
from dal import autocomplete
from django.forms.fields import Field, FileField
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
import json
from entes_territoriales import functions

class ReunionesForm(forms.Form):

    municipio = forms.ModelChoiceField(label='Municipio', queryset=Municipios.objects.none(),
                                         required=False)

    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            if name not in ['municipio']:
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
                self.cleaned_data[name] = value

    def clean(self):
        cleaned_data = super().clean()
        municipio = cleaned_data.get("municipio")

        reuniones = models.Reuniones.objects.filter(municipio = municipio)

        if reuniones.count() > 0:
            self.add_error('municipio', 'Ya existe el ente territorial.')

    def __init__(self, *args, **kwargs):
        super(ReunionesForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información de la gestión',
                )
            ),
            Row(
                Column(
                    'municipio',
                    css_class='s12'
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

class ContactosForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContactosForm, self).__init__(*args, **kwargs)

        self.fields['observaciones'].widget = forms.Textarea(
            attrs={'class': 'materialize-textarea', 'data-length': '500'})

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del contacto',
                )
            ),
            Row(
                Column(
                    'nombres',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'apellidos',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'cargo',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Column(
                    'celular',
                    css_class='s12 m6'
                ),
                Column(
                    'email',
                    css_class='s12 m6'
                )
            ),
            Row(
                Column(
                    'resguardo',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'comunidad',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'lenguas',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Column(
                    'observaciones',
                    css_class='s12'
                )
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
        model = models.Contactos
        fields = ['nombres', 'apellidos', 'cargo', 'celular', 'email', 'resguardo', 'comunidad', 'lenguas','observaciones']

class SoportesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SoportesForm, self).__init__(*args, **kwargs)

        self.fields['file'].widget = forms.FileInput()

        self.fields['tipo'].widget = forms.Select(choices=[
            ('','----------'),
            ('Acta de posesión','Acta de posesión'),
            ('Base de datos', 'Base de datos'),
            ('Fotocopia de cédula', 'Fotocopia de cédula'),
            ('Otros', 'Otros')
        ])

        self.fields['observaciones'].widget = forms.Textarea(
            attrs={'class': 'materialize-textarea', 'data-length': '500'})

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del soporte',
                )
            ),
            Row(
                Column(
                    'tipo',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'observaciones',
                    css_class='s12'
                )
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
        model = models.Soportes
        fields = ['tipo', 'file', 'observaciones']

class GestionForm(forms.Form):

    contenido = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        super(GestionForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Column(
                    HTML(
                        """
                        <div id="contenido" style="min-height:200px;"></div>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'contenido',
                    css_class='s12'
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

class HitoForm(forms.Form):

    tipo = forms.CharField(label='Tipo de acta',max_length=100, widget= forms.Select(choices=[
        ('','----------'),
        ('Acta de socialización y concertación', 'Acta de socialización y concertación'),
        ('Otro', 'Otro')
    ]))
    fecha = forms.DateField(label = 'Fecha del acta')
    contenido = forms.CharField(widget=forms.HiddenInput())
    inicial = forms.CharField(widget=forms.HiddenInput())
    file = forms.FileField(max_length=255,widget= forms.FileInput(attrs={'data-max-file-size': '10M',
                                                                         'accept': 'application/pdf'}))
    file2 = forms.FileField(max_length=255,widget= forms.FileInput(attrs={'data-max-file-size': '10M',
                                                                         'accept': 'application/pdf'}))
    file3 = forms.FileField(max_length=255,widget= forms.FileInput(attrs={'data-max-file-size': '10M',
                                                                         'accept': 'application/pdf'}))

    foto_1 = forms.ImageField(max_length=255,required=False,widget= forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                         'accept': 'image/jpg,image/jpeg,image/png'}))
    foto_2 = forms.ImageField(max_length=255, required=False,widget= forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                         'accept': 'image/jpg,image/jpeg,image/png'}))
    foto_3 = forms.ImageField(max_length=255, required=False,widget= forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                         'accept': 'image/jpg,image/jpeg,image/png'}))
    foto_4 = forms.ImageField(max_length=255, required=False,widget= forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                         'accept': 'image/jpg,image/jpeg,image/png'}))

    def __init__(self, *args, **kwargs):
        super(HitoForm, self).__init__(*args, **kwargs)

        if 'pk_hito' in kwargs['initial'].keys():
            hito = models.Hito.objects.get(id=kwargs['initial']['pk_hito'])
            #registro = models.Registro.objects.filter(hito = hito)[0]

            self.fields['inicial'].initial = json.dumps(functions.delta_empty())
            self.fields['tipo'].initial = hito.tipo
            self.fields['fecha'].initial = hito.fecha

            self.fields['file'].required = False
            self.fields['file2'].required = False
            self.fields['file3'].required = False

            if hito.url_foto_1() != None:
                self.fields['foto_1'].widget.attrs['data-default-file'] = hito.url_foto_1()

            if hito.url_foto_2() != None:
                self.fields['foto_2'].widget.attrs['data-default-file'] = hito.url_foto_2()

            if hito.url_foto_3() != None:
                self.fields['foto_3'].widget.attrs['data-default-file'] = hito.url_foto_3()

            if hito.url_foto_4() != None:
                self.fields['foto_4'].widget.attrs['data-default-file'] = hito.url_foto_4()

        else:
            self.fields['inicial'].initial = json.dumps({
                'ops': [
                    {
                        'insert': '\n'
                    }
                ]
            })



        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Información del acta:'
                )
            ),
            Row(
                Column(
                    'tipo',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'fecha',
                    css_class='s12 m6 l6'
                )
            ),
            Row(
                Fieldset(
                    'Formato acta'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Lista de asistencia'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;"><b>Actualmente:</b>{{ file2_url | safe }}</p>
                        """
                    ),
                    'file2',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Otros'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;"><b>Actualmente:</b>{{ file3_url | safe }}</p>
                        """
                    ),
                    'file3',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Registro fotográfico'
                )
            ),
            Row(
                Column(
                    'foto_1',
                    css_class='s12 m6 l3'
                ),
                Column(
                    'foto_2',
                    css_class='s12 m6 l3'
                ),
                Column(
                    'foto_3',
                    css_class='s12 m6 l3'
                ),
                Column(
                    'foto_4',
                    css_class='s12 m6 l3'
                )
            ),
            Row(
                Fieldset(
                    'Observación'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Descripción:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <div id="contenido" style="min-height:200px;"></div>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'contenido',
                    css_class='s12'
                ),
                Column(
                    'inicial',
                    css_class='s12'
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

class HitoEstadoForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get("estado")
        observacion = cleaned_data.get("observacion")

        if estado == 'Rechazado':
            if observacion == None or observacion == '':
                self.add_error('observacion', 'Por favor agrega una observación al rechazo')

    def __init__(self, *args, **kwargs):
        super(HitoEstadoForm, self).__init__(*args, **kwargs)

        self.fields['observacion'].widget = forms.Textarea(
            attrs={'class': 'materialize-textarea', 'data-length': '500'})

        self.fields['estado'].widget = forms.Select(choices=[
            ('','----------'),
            ('Aprobado', 'Aprobado'),
            ('Esperando aprobación', 'Esperando aprobación'),
            ('Rechazado', 'Rechazado')
        ])

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Estado del hito',
                )
            ),
            Row(
                Column(
                    'estado',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'observacion',
                    css_class='s12'
                )
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
        model = models.Hito
        fields = ['estado', 'observacion']