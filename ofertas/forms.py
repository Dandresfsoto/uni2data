#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from ofertas import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset
from crispy_forms_materialize.layout import Layout, Row, Column, Submit, HTML, Button
from crispy_forms.layout import ButtonHolder
from recursos_humanos.models import Contratistas, Contratos
from django.db.models import Q
from django.conf import settings
import openpyxl
from dal import autocomplete
from django.forms.fields import Field, FileField
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from usuarios.models import Departamentos, User, Municipios

class OfertasForm(forms.ModelForm):

    honorarios = forms.CharField(label='Honorarios')

    def __init__(self, *args, **kwargs):
        super(OfertasForm, self).__init__(*args, **kwargs)

        self.fields['perfil'].widget = forms.Textarea(
            attrs={'class': 'materialize-textarea', 'data-length': '1000'})

        self.fields['experiencia'].widget = forms.Textarea(
            attrs={'class': 'materialize-textarea', 'data-length': '1000'})

        self.fields['tipo_contrato'].widget = forms.Select(choices=[
            ('', '---------'),
            ('Ops', 'Ops')
        ])

        if 'pk' in kwargs['initial'].keys():
            oferta = models.Ofertas.objects.get(id = kwargs['initial']['pk'])
            self.fields['honorarios'].initial = oferta.honorarios.amount

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información de la oferta',
                )
            ),
            Row(
                Column(
                    'cargo',
                    css_class="s12 m6 l5"
                ),
                Column(
                    'tipo_contrato',
                    css_class="s12 m6 l3"
                ),
                Column(
                    'honorarios',
                    css_class="s12 m6 l4"
                ),
            ),
            Row(
                Column(
                    'municipios',
                    css_class="s12 m6 l8"
                ),
                Column(
                    'vacantes',
                    css_class="s12 m6 l4"
                )
            ),
            Row(
                Column(
                    'perfil',
                    css_class="s12"
                )
            ),
            Row(
                Column(
                    'experiencia',
                    css_class="s12"
                )
            ),
            Row(
                Column(
                    'estado',
                    css_class="s12"
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
        model = models.Ofertas
        fields = ['cargo','perfil','experiencia','tipo_contrato','vacantes','estado','municipios']

class CreateAplicacion(forms.Form):
    municipios = forms.ModelMultipleChoiceField(label='Municipios',queryset=Municipios.objects.none(),required=False)
    observacion = forms.CharField(max_length=500,required=False)

    def __init__(self, *args, **kwargs):
        super(CreateAplicacion, self).__init__(*args, **kwargs)

        oferta = models.Ofertas.objects.get(id = kwargs['initial']['pk'])
        usuario = User.objects.get(id = kwargs['initial']['usuario_id'])

        try:
            aplicacion = models.AplicacionOferta.objects.get(oferta = oferta,usuario=usuario)
        except:
            pass
        else:
            self.fields['municipios'].initial = aplicacion.municipios.all()
            self.fields['observacion'].initial = aplicacion.observacion


        self.fields['municipios'].queryset = oferta.municipios.all()
        self.fields['observacion'].widget = forms.Textarea(attrs={'class': 'materialize-textarea','data-length':'500'})

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Column(
                    'municipios',
                    css_class="s12"
                )
            ),
            Row(
                Column(
                    'observacion',
                    css_class="s12"
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

class CualificacionAplicacion(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        cualificacion_perfil = cleaned_data.get("cualificacion_perfil")
        cualificacion_experiencia = cleaned_data.get("cualificacion_experiencia")
        cualificacion_seleccion = cleaned_data.get("cualificacion_seleccion")

        if cualificacion_perfil == None:
            self.add_error('cualificacion_perfil', 'Completa este campo')

        if cualificacion_experiencia == None:
            self.add_error('cualificacion_experiencia', 'Completa este campo')

        if cualificacion_seleccion == None:
            self.add_error('cualificacion_seleccion', 'Completa este campo')

    def __init__(self, *args, **kwargs):
        super(CualificacionAplicacion, self).__init__(*args, **kwargs)

        self.fields['cualificacion_observacion'].widget = forms.Textarea(
            attrs={'class': 'materialize-textarea', 'data-length': '500'})

        self.fields['cualificacion_perfil'].widget = forms.Select(choices=[
            ('','----------'),
            ('Cumple con el perfil', 'Cumple con el perfil'),
            ('No cumple con el perfil', 'No cumple con el perfil')
        ])

        self.fields['cualificacion_experiencia'].widget = forms.Select(choices=[
            ('', '----------'),
            ('Cumple con la experiencia', 'Cumple con la experiencia'),
            ('No cumple con la experiencia', 'No cumple con la experiencia')
        ])

        self.fields['cualificacion_seleccion'].widget = forms.Select(choices=[
            ('', '----------'),
            ('No seleccionado', 'No seleccionado'),
            ('Preseleccionado', 'Preseleccionado'),
            ('Seleccionado', 'Seleccionado'),
            ('Pendiente', 'Pendiente')
        ])

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Column(
                    HTML(
                        """
                        <h5><b>CUALIFICACIÓN:</b></h5>
                        """
                    ),
                    css_class="s12"
                )
            ),
            Row(
                Column(
                    'cualificacion_perfil',
                    css_class="s12 m6 l4"
                ),
                Column(
                    'cualificacion_experiencia',
                    css_class="s12 m6 l4"
                ),
                Column(
                    'cualificacion_seleccion',
                    css_class="s12 m6 l4"
                )
            ),

            Row(
                Column(
                    'cualificacion_observacion',
                    css_class="s12"
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
        model = models.AplicacionOferta
        fields = ['cualificacion_perfil','cualificacion_experiencia','cualificacion_seleccion','cualificacion_observacion']
        labels = {
            'cualificacion_perfil': 'Cumple con el perfil?',
            'cualificacion_experiencia': 'Cumple con la experiencia?',
            'cualificacion_seleccion': 'Estado de la aplicación',
            'cualificacion_observacion': 'Observaciónes'
        }