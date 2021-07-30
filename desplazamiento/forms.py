#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from desplazamiento import models
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
import json

class SolicitudesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SolicitudesForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información de la solicitud',
                )
            ),
            Row(
                Column(
                    'nombre',
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
        model = models.Solicitudes
        fields = ['nombre']

class SolicitudesUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SolicitudesUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información de la solicitud',
                )
            ),
            Row(
                Column(
                    'nombre',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Formato de solicitud firmado',
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;"><b>Actualmente:</b>{{ formato_firmado | safe }}</p>
                        """
                    ),
                    'file2',
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
        model = models.Solicitudes
        fields = ['nombre','file2']

class DesplazamientoForm(forms.ModelForm):

    valor = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(DesplazamientoForm, self).__init__(*args, **kwargs)

        if 'pk_desplazamiento' in kwargs['initial'].keys():
            self.fields['valor'].initial = models.Desplazamiento.objects.get(id = kwargs['initial']['pk_desplazamiento']).valor.amount

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del desplazamiento',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'origen',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'destino',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Column(
                    'tipo_transporte',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'transportador',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'telefono',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Column(
                    'valor',
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
        model = models.Desplazamiento
        fields = ['origen','destino','fecha','tipo_transporte','transportador','telefono','observaciones']
        widgets = {
            'observaciones' : forms.Textarea(attrs={'class':'materialize-textarea'}),
            'tipo_transporte': forms.Select(choices=[
                ('','----------'),
                ('Aéreo', 'Aéreo'),
                ('Marítimo', 'Marítimo'),
                ('No convencional', 'No convencional'),
                ('Terrestre', 'Terrestre')
            ])
        }
        labels = {
            'fecha': 'Fecha del desplazamiento',
            'origen': 'Lugar de origen',
            'destino': 'Lugar de destino',
            'tipo_transporte': 'Tipo de transporte'
        }

class FinancieraSolicitudForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FinancieraSolicitudForm, self).__init__(*args, **kwargs)

        self.fields['estado'].widget = forms.Select(choices=[
            ('','----------'),
            ('Reportado a pagaduria', 'Reportado a pagaduria'),
            ('Pagado', 'Pagado'),
        ])

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Estado de la solicitud',
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
        model = models.Solicitudes
        fields = ['estado']