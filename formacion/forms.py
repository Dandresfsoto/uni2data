#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from formacion import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset
from crispy_forms_materialize.layout import Layout, Row, Column, Submit, HTML, Button
from recursos_humanos.models import Contratistas, Contratos
from django.db.models import Q
from django.conf import settings
import openpyxl
from dal import autocomplete
from django.forms.fields import Field, FileField
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError

class RegionesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(RegionesForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información de la región',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'nombre',
                            css_class='s12'
                        )
                    ),
                    css_class="s12"
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
        model = models.Regiones
        fields = ['nombre']
        labels = {
            'nombre': 'Nombre de la región'
        }

class DepartamentosForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DepartamentosForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del departamento',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'nombre',
                            css_class='s12'
                        )
                    ),
                    css_class="s12"
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
        model = models.Departamentos
        fields = ['nombre']
        labels = {
            'nombre': 'Nombre del departamento'
        }

class MunicipiosForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(MunicipiosForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del municipio',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'nombre',
                            css_class='s12'
                        )
                    ),
                    css_class="s12"
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
        model = models.Municipios
        fields = ['nombre']

class SedesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SedesForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información de la sede',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'dane_sede',
                            css_class='s12 m6'
                        ),
                        Column(
                            'nombre_sede',
                            css_class='s12 m6'
                        )
                    ),
                    Row(
                        Column(
                            'dane_ie',
                            css_class='s12 m6'
                        ),
                        Column(
                            'nombre_ie',
                            css_class='s12 m6'
                        ),

                    ),
                    css_class="s12"
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
        model = models.Sedes
        fields = ['dane_sede','nombre_sede','dane_ie','nombre_ie']
        labels = {
            'dane_sede': 'Dane sede educativa',
            'nombre_sede': 'Nombre sede educativa',
            'dane_ie': 'Dane institución educativa',
            'nombre_ie': 'Nombre institución educativa',
        }

class DocentesFormadosForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DocentesFormadosForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del docente formado',
                )
            ),
            Row(
                Column(
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
                            'cedula',
                            css_class='s12 m6 l4'
                        )
                    ),
                    Row(
                        Column(
                            'vigencia',
                            css_class='s12 m6'
                        ),
                        Column(
                            'diplomado',
                            css_class='s12 m6'
                        ),

                    ),
                    css_class="s12"
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
        model = models.DocentesFormados
        fields = ['nombres','apellidos','cedula','vigencia','diplomado']


class ActualizacionSedesForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}))

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")

        if file.name.split('.')[-1] == 'xlsx':
            try:
                wb = openpyxl.load_workbook(file)
                sheet = wb.get_sheet_names()
            except:
                self.add_error('file', 'Por favor elimine los comentarios de la plantilla')
            else:
                if 'ACTUALIZACION SEDES' not in sheet:
                    self.add_error('file', 'El archivo cargado no tiene la estructura requerida, reuerde usar la plantilla')
        else:
            self.add_error('file', 'El archivo cargado no tiene un formato valido')

    def __init__(self, *args, **kwargs):
        super(ActualizacionSedesForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Formato actualización de sedes',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'file',
                            css_class='s12 12'
                        )
                    ),
                    css_class="s12"
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

class ActualizacionDocentesForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}))

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")

        if file.name.split('.')[-1] == 'xlsx':
            try:
                wb = openpyxl.load_workbook(file)
                sheet = wb.get_sheet_names()
            except:
                self.add_error('file', 'Por favor elimine los comentarios de la plantilla')
            else:
                if 'ACTUALIZACION DE DOCENTES' not in sheet:
                    self.add_error('file', 'El archivo cargado no tiene la estructura requerida, reuerde usar la plantilla')
        else:
            self.add_error('file', 'El archivo cargado no tiene un formato valido')

    def __init__(self, *args, **kwargs):
        super(ActualizacionDocentesForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Formato actualización de docentes formados',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'file',
                            css_class='s12 12'
                        )
                    ),
                    css_class="s12"
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