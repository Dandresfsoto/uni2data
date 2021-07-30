#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from recursos_humanos.models import Contratistas, Contratos, Soportes, GruposSoportes, SoportesContratos, Certificaciones
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset
from crispy_forms_materialize.layout import Layout, Row, Column, Submit, HTML, Hidden
from recursos_humanos import functions
import json
from recursos_humanos import models
from dal import autocomplete
from django.forms.fields import Field, FileField
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


class ContratistaForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        banco = cleaned_data.get("banco")
        tipo_cuenta = cleaned_data.get("tipo_cuenta")
        cuenta = cleaned_data.get("cuenta")
        cargo = cleaned_data.get("cargo")

        if cargo == None:
            self.add_error('cargo', 'Campo requerido')

        if banco != None or tipo_cuenta != None or cuenta != None:
            if banco == None:
                self.add_error('banco', 'Campo requerido')
            if tipo_cuenta == None:
                self.add_error('tipo_cuenta', 'Campo requerido')
            if cuenta == None:
                self.add_error('cuenta', 'Campo requerido')

        if banco != None and cuenta != None:
            longitudes = banco.longitud.split(',')
            if str(len(cuenta)) not in longitudes:
                self.add_error('cuenta', 'La cuenta debe tener {0} digitos.'.format(banco.longitud))


    def __init__(self, *args, **kwargs):
        super(ContratistaForm, self).__init__(*args, **kwargs)

        self.fields['tipo_cuenta'].widget = forms.Select(choices=[
            ('','----------'),
            ('Ahorros', 'Ahorros'),
            ('Corriente', 'Corriente')
        ])

        self.fields['tipo_identificacion'].widget = forms.Select(choices=[
            ('', '----------'),
            ('1', 'Nit'),
            ('2', 'Cédula de Ciudadania'),
            ('3', 'Tarjeta de Identidad'),
            ('4', 'Cédula de Extranjeria'),
            ('5', 'Pasaporte'),
            ('6', 'Tajeta Seguro Social'),
            ('7', 'Nit Menores'),
        ])

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información personal',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'nombres',
                            css_class='s12 m6 l3'
                        ),
                        Column(
                            'apellidos',
                            css_class='s12 m6 l3'
                        ),
                        Column(
                            'tipo_identificacion',
                            css_class='s12 m6 l3'
                        ),
                        Column(
                            'cedula',
                            css_class='s12 m6 l3'
                        ),
                    ),
                    Row(
                        Column(
                            'celular',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'email',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'birthday',
                            css_class='s12 m6 l4'
                        ),
                    ),
                    css_class="s12"
                ),
            ),

            Row(
                Fieldset(
                    'Información laboral',
                )
            ),

            Row(
                Column(
                    Row(
                        Column(
                            'cargo',
                            css_class='s12'
                        )
                    ),
                    css_class="s12"
                ),
            ),

            Row(
                Fieldset(
                    'Información bancaria',
                )
            ),

            Row(
                Column(
                    Row(
                        Column(
                            'cuenta',
                            css_class='s12'
                        ),
                        Column(
                            'banco',
                            css_class='s12 m6'
                        ),
                        Column(
                            'tipo_cuenta',
                            css_class='s12 m6'
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
        model = Contratistas
        fields = ['nombres','apellidos','tipo_identificacion','cedula','celular','email','birthday','tipo_cuenta','banco','cuenta','cargo']
        labels = {
            'birthday': 'Fecha de nacimiento',
            'cedula': 'Documento #',
            'tipo_identificacion': 'Tipo',
            'cuenta': 'Número de cuenta'
        }

class ContratoForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        soporte_liquidacion = cleaned_data.get("soporte_liquidacion")
        soporte_renuncia = cleaned_data.get("soporte_renuncia")

        fecha_liquidacion = cleaned_data.get("fecha_liquidacion")
        fecha_renuncia = cleaned_data.get("fecha_renuncia")

        if soporte_liquidacion != None and fecha_liquidacion == None:
            self.add_error('fecha_liquidacion', 'Por favor completa este campo')

        if soporte_renuncia != None and fecha_renuncia == None:
            self.add_error('fecha_renuncia', 'Por favor completa este campo')

    def __init__(self, *args, **kwargs):
        super(ContratoForm, self).__init__(*args, **kwargs)

        self.fields['valor_char'] = forms.CharField(label="Valor del contrato ($)")

        try:
            valor = kwargs['instance'].valor
        except:
            pass
        else:
            self.fields['valor_char'].initial = valor.amount

        self.fields['file'].widget = forms.FileInput(attrs={'accept':'application/pdf,application/x-pdf'})
        #self.fields['soporte_liquidacion'].widget = forms.FileInput(attrs={'accept':'application/pdf,application/x-pdf'})
        #self.fields['soporte_renuncia'].widget = forms.FileInput(attrs={'accept':'application/pdf,application/x-pdf'})
        self.fields['objeto_contrato'].widget = forms.Textarea(attrs={'class': 'materialize-textarea','data-length':'1000'})
        self.fields['tipo_contrato'].widget = forms.Select(choices=[
            ('','----------'),
            ('Ops', 'Ops'),
            ('Laboral', 'Laboral')
        ])

        self.fields['suscrito'].widget.attrs['class'] = 'filled-in'
        self.fields['ejecucion'].widget.attrs['class'] = 'filled-in'
        self.fields['ejecutado'].widget.attrs['class'] = 'filled-in'
        self.fields['liquidado'].widget.attrs['class'] = 'filled-in'

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información contrato:',
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Nombre del contratista: </b> {{ contratista_nombre }} </p>
                        <p><b>Cédula del contratista: </b> {{ contratista_cedula }} </p>
                        """
                    ),
                    css_class = 's12'
                )
            ),

            Row(
                Column(
                    Row(
                        Column(
                            'proyecto',
                            css_class='s12 m6 l4'
                        )
                    ),
                    Row(
                        Column(
                            'cargo',
                            css_class='s12'
                        )
                    ),
                    Row(
                        Column(
                            'nombre',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'tipo_contrato',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'valor_char',
                            css_class='s12 m6 l4'
                        )
                    ),
                    Row(
                        Column(
                            'inicio',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'fin',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'grupo_soportes',
                            css_class='s12 m6 l4'
                        )
                    ),
                    Row(
                        Column(
                            'objeto_contrato',
                            css_class='s12'
                        )
                    ),
                    css_class="s12"
                ),
            ),

            Row(
                Column(
                    Row(
                        Fieldset(
                            'Estado del contrato:',
                        ),
                    ),
                    Row(
                        Column(
                            'suscrito',
                            css_class='s12 m6'
                        ),
                        Column(
                            'ejecucion',
                            css_class='s12 m6'
                        ),
                        Column(
                            'ejecutado',
                            css_class='s12 m6'
                        ),
                        Column(
                            'liquidado',
                            css_class='s12 m6'
                        )
                    ),
                    css_class="s12"
                ),
            ),

            Row(
                Column(
                    Row(
                        Fieldset(
                            'Minuta del contrato:',
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b>{{ minuta_url | safe }}</p>
                                """
                            ),
                            'file',
                            css_class='s12'
                        )
                    ),
                    css_class="s12"
                ),
            ),

            Row(
                Column(
                    Row(
                        Fieldset(
                            'Soporte de liquidación o renuncia:',
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b> {{ liquidacion_url | safe }} </p>
                                """
                            ),
                            'soporte_liquidacion',
                            'fecha_liquidacion',
                            css_class='s12 m6'
                        ),
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b> {{ renuncia_url | safe }} </p>
                                """
                            ),
                            'soporte_renuncia',
                            'fecha_renuncia',
                            css_class='s12 m6'
                        )
                    ),
                    css_class="s12"
                ),
            ),

            Row(
                Column(
                    Row(
                        Fieldset(
                            'Otrosi:',
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b> {{ otro_si_1_url | safe }} </p>
                                """
                            ),
                            'otro_si_1',
                            css_class='s12'
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b> {{ otro_si_2_url | safe }} </p>
                                """
                            ),
                            'otro_si_2',
                            css_class='s12'
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b> {{ otro_si_3_url | safe }} </p>
                                """
                            ),
                            'otro_si_3',
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
        model = Contratos
        fields = [
            'nombre','inicio','fin','file','tipo_contrato','objeto_contrato','soporte_liquidacion',
            'soporte_renuncia','suscrito','ejecucion','ejecutado','liquidado','grupo_soportes', 'proyecto', 'cargo',
            'fecha_liquidacion', 'fecha_renuncia', 'otro_si_1', 'otro_si_2', 'otro_si_3'
        ]

        labels = {
            'nombre': 'Código del contrato',
            'inicio': 'Fecha de inicio del contrato',
            'fin': 'Fecha de finalización del contrato',
            'suscrito': 'Contrato suscrito',
            'ejecucion': 'Contrato en ejecución',
            'ejecutado': 'Contrato ejecutado',
            'liquidado': 'Contrato liquidado'
        }

class ContratoFormSuperUser(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        soporte_liquidacion = cleaned_data.get("soporte_liquidacion")
        soporte_renuncia = cleaned_data.get("soporte_renuncia")

        fecha_liquidacion = cleaned_data.get("fecha_liquidacion")
        fecha_renuncia = cleaned_data.get("fecha_renuncia")

        if soporte_liquidacion != None and fecha_liquidacion == None:
            self.add_error('fecha_liquidacion', 'Por favor completa este campo')

        if soporte_renuncia != None and fecha_renuncia == None:
            self.add_error('fecha_renuncia', 'Por favor completa este campo')



    def __init__(self, *args, **kwargs):
        super(ContratoFormSuperUser, self).__init__(*args, **kwargs)

        self.fields['valor_char'] = forms.CharField(label="Valor del contrato ($)")

        try:
            valor = kwargs['instance'].valor
        except:
            pass
        else:
            self.fields['valor_char'].initial = valor.amount

        self.fields['file'].widget = forms.FileInput(attrs={'accept':'application/pdf,application/x-pdf'})
        #self.fields['soporte_liquidacion'].widget = forms.FileInput(attrs={'accept':'application/pdf,application/x-pdf'})
        #self.fields['soporte_renuncia'].widget = forms.FileInput(attrs={'accept':'application/pdf,application/x-pdf'})
        self.fields['objeto_contrato'].widget = forms.Textarea(attrs={'class': 'materialize-textarea','data-length':'1000'})
        self.fields['tipo_contrato'].widget = forms.Select(choices=[
            ('','----------'),
            ('Ops', 'Ops'),
            ('Laboral', 'Laboral')
        ])

        self.fields['suscrito'].widget.attrs['class'] = 'filled-in'
        self.fields['ejecucion'].widget.attrs['class'] = 'filled-in'
        self.fields['ejecutado'].widget.attrs['class'] = 'filled-in'
        self.fields['liquidado'].widget.attrs['class'] = 'filled-in'
        self.fields['visible'].widget.attrs['class'] = 'filled-in'

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información contrato:',
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Nombre del contratista: </b> {{ contratista_nombre }} </p>
                        <p><b>Cédula del contratista: </b> {{ contratista_cedula }} </p>
                        """
                    ),
                    css_class = 's12'
                )
            ),

            Row(
                Column(
                    Row(
                        Column(
                            'proyecto',
                            css_class='s12 m6 l4'
                        )
                    ),
                    Row(
                        Column(
                            'cargo',
                            css_class='s12'
                        )
                    ),
                    Row(
                        Column(
                            'nombre',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'tipo_contrato',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'valor_char',
                            css_class='s12 m6 l4'
                        )
                    ),
                    Row(
                        Column(
                            'inicio',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'fin',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'grupo_soportes',
                            css_class='s12 m6 l4'
                        )
                    ),
                    Row(
                        Column(
                            'objeto_contrato',
                            css_class='s12'
                        )
                    ),
                    css_class="s12"
                ),
            ),

            Row(
                Column(
                    Row(
                        Fieldset(
                            'Estado del contrato:',
                        ),
                    ),
                    Row(
                        Column(
                            'suscrito',
                            css_class='s12 m6'
                        ),
                        Column(
                            'ejecucion',
                            css_class='s12 m6'
                        ),
                        Column(
                            'ejecutado',
                            css_class='s12 m6'
                        ),
                        Column(
                            'liquidado',
                            css_class='s12 m6'
                        )
                    ),
                    css_class="s12"
                ),
            ),

            Row(
                Column(
                    Row(
                        Fieldset(
                            'Minuta del contrato:',
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b>{{ minuta_url | safe }}</p>
                                """
                            ),
                            'file',
                            css_class='s12'
                        )
                    ),
                    css_class="s12"
                ),
            ),

            Row(
                Column(
                    Row(
                        Fieldset(
                            'Soporte de liquidación o renuncia:',
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b> {{ liquidacion_url | safe }} </p>
                                """
                            ),
                            'soporte_liquidacion',
                            'fecha_liquidacion',
                            css_class='s12 m6'
                        ),
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b> {{ renuncia_url | safe }} </p>
                                """
                            ),
                            'soporte_renuncia',
                            'fecha_renuncia',
                            css_class='s12 m6'
                        )
                    ),
                    css_class="s12"
                ),
            ),

            Row(
                Column(
                    Row(
                        Fieldset(
                            'Otrosi:',
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b> {{ otro_si_1_url | safe }} </p>
                                """
                            ),
                            'otro_si_1',
                            css_class='s12'
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b> {{ otro_si_2_url | safe }} </p>
                                """
                            ),
                            'otro_si_2',
                            css_class='s12'
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b> {{ otro_si_3_url | safe }} </p>
                                """
                            ),
                            'otro_si_3',
                            css_class='s12'
                        )
                    ),
                    css_class="s12"
                ),
            ),

            Row(
                Column(
                    Row(
                        Fieldset(
                            'Super Usuario:',
                        )
                    ),
                    Row(

                        Column(
                            'visible',
                            css_class='s12 m6'
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
        model = Contratos
        fields = [
            'nombre','inicio','fin','file','tipo_contrato','objeto_contrato','soporte_liquidacion',
            'soporte_renuncia','suscrito','ejecucion','ejecutado','liquidado','grupo_soportes', 'proyecto', 'cargo',
            'fecha_liquidacion', 'fecha_renuncia', 'visible', 'otro_si_1', 'otro_si_2', 'otro_si_3'
        ]

        labels = {
            'nombre': 'Código del contrato',
            'inicio': 'Fecha de inicio del contrato',
            'fin': 'Fecha de finalización del contrato',
            'suscrito': 'Contrato suscrito',
            'ejecucion': 'Contrato en ejecución',
            'ejecutado': 'Contrato ejecutado',
            'liquidado': 'Contrato liquidado'
        }

class SoporteForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SoporteForm, self).__init__(*args, **kwargs)

        self.fields['descripcion'].widget.attrs['class'] = 'materialize-textarea'
        self.fields['requerido'].widget.attrs['class'] = 'filled-in'

        self.fields['categoria'].widget = forms.Select(choices=[
            ('','---------'),
            ('Suscripción del contrato', 'Suscripción del contrato'),
            ('Ejecución del contrato', 'Ejecución del contrato'),
            ('Liquidación del contrato', 'Liquidación del contrato')
        ])

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Soporte para recursos humanos',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'nombre',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'categoria',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'numero',
                            css_class='s12 m6 l4'
                        )
                    ),
                    Row(
                        Column(
                            'descripcion',
                            css_class='s12'
                        )
                    ),
                    Row(
                        Column(
                            'requerido',
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
        model = Soportes
        fields = ['nombre','numero','descripcion','requerido','categoria']
        labels = {
            'requerido': 'Soporte obligatorio.'
        }

class GruposSoportesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(GruposSoportesForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Grupo de soportes para recursos humanos',
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
                    Row(
                        Column(
                            'soportes',
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
        model = GruposSoportes
        fields = ['nombre','soportes']

class SoportesContratosForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        estado = cleaned_data.get("estado")
        observacion = cleaned_data.get("observacion")

        if estado != None or estado != '':
            if estado == 'Solicitar subsanación':
                if observacion == None or observacion == '':
                    self.add_error('observacion', 'Por favor completa este campo')

    def __init__(self, *args, **kwargs):
        super(SoportesContratosForm, self).__init__(*args, **kwargs)

        contrato = Contratos.objects.get(id = kwargs['initial']['pk_soporte'])

        self.fields['file'].widget = forms.FileInput()

        self.fields['estado'].widget = forms.Select(choices=[
            ('','----------'),
            ('Aprobado', 'Aprobado'),
            ('Solicitar subsanación', 'Solicitar subsanación'),
        ])

        self.fields['observacion'].widget = forms.Textarea(
            attrs={'class': 'materialize-textarea', 'data-length': '100'})

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Soporte del contrato',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                """
                                <p><b>{{nombre_soporte}}</b></p>
                                """
                            ),
                            css_class='s12'
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b> {{ soporte_url | safe }} </p>
                                """
                            ),
                            'file',
                            css_class='s12'
                        )
                    ),
                    css_class="s12"
                ),
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
        model = SoportesContratos
        fields = ['file','estado','observacion']
        labels = {
            'estado': 'Aprobar o solicitar subsanación',
            'observacion': 'Observación del soporte'
        }

class SoportesContratosCreateForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        estado = cleaned_data.get("estado")
        observacion = cleaned_data.get("observacion")

        if estado != None or estado != '':
            if estado == 'Solicitar subsanación':
                if observacion == None or observacion == '':
                    self.add_error('observacion', 'Por favor completa este campo')

    def __init__(self, *args, **kwargs):
        super(SoportesContratosCreateForm, self).__init__(*args, **kwargs)

        contrato = Contratos.objects.get(id = kwargs['initial']['pk_soporte'])
        soportes_contrato = SoportesContratos.objects.filter(contrato = contrato)

        self.fields['soporte'].queryset = Soportes.objects.exclude(id__in = soportes_contrato.values_list('soporte__id',flat=True))

        self.fields['file'].widget = forms.FileInput()

        self.fields['estado'].widget = forms.Select(choices=[
            ('','----------'),
            ('Aprobado', 'Aprobado'),
            ('Solicitar subsanación', 'Solicitar subsanación'),
        ])

        self.fields['observacion'].widget = forms.Textarea(
            attrs={'class': 'materialize-textarea', 'data-length': '100'})

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Soporte del contrato',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'soporte',
                            css_class='s12'
                        )
                    ),
                    Row(
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b> {{ soporte_url | safe }} </p>
                                """
                            ),
                            'file',
                            css_class='s12'
                        )
                    ),
                    css_class="s12"
                ),
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
        model = SoportesContratos
        fields = ['soporte','file','estado','observacion']
        labels = {
            'estado': 'Aprobar o solicitar subsanación',
            'observacion': 'Observación del soporte'
        }

class CertificacionesForm(forms.Form):
    contenido = forms.CharField(widget=forms.HiddenInput())
    inicial = forms.CharField(widget=forms.HiddenInput())
    firma = forms.CharField(widget=forms.Select(choices=[
        ('','----------'),
        ('Director administrativo y financiero', 'Director administrativo y financiero'),
        ('Gerencia', 'Gerencia')
    ]))
    notificar = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(CertificacionesForm, self).__init__(*args, **kwargs)

        contratista = Contratistas.objects.get(id = kwargs['initial']['pk'])

        inicial = functions.certificacion_laboral(contratista)

        self.fields['inicial'].initial = json.dumps(inicial)
        self.fields['notificar'].widget.attrs['class'] = 'filled-in'

        if contratista.email != None and contratista.email != '':
            self.fields['notificar'].label = 'Enviar copia a ' + contratista.email
        else:
            self.fields['notificar'].label = 'No hay correo registrado del contratista'
            self.fields['notificar'].widget.attrs['disabled'] = 'disabled'

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Contenido de la certificación',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'firma',
                            css_class='s12'
                        ),
                        Column(
                            HTML(
                                """
                                <div id="contenido" style="min-height:300px;"></div>
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
                        Column(
                            'notificar',
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

class CertificacionesUpdateForm(forms.Form):
    contenido = forms.CharField(widget=forms.HiddenInput())
    inicial = forms.CharField(widget=forms.HiddenInput())
    firma = forms.CharField(widget=forms.Select(choices=[
        ('','----------'),
        ('Director administrativo y financiero', 'Director administrativo y financiero'),
        ('Gerencia', 'Gerencia')
    ]))
    notificar = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(CertificacionesUpdateForm, self).__init__(*args, **kwargs)

        certificacion = Certificaciones.objects.get(id = kwargs['initial']['pk'])
        contratista = certificacion.contratista

        self.fields['inicial'].initial = certificacion.delta
        self.fields['firma'].initial = certificacion.firma
        self.fields['notificar'].widget.attrs['class'] = 'filled-in'

        if contratista.email != None and contratista.email != '':
            self.fields['notificar'].label = 'Enviar copia a ' + contratista.email
        else:
            self.fields['notificar'].label = 'No hay correo registrado del contratista'
            self.fields['notificar'].widget.attrs['disabled'] = 'disabled'

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Contenido de la certificación',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'firma',
                            css_class='s12'
                        ),
                        Column(
                            HTML(
                                """
                                <div id="contenido" style="min-height:300px;"></div>
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
                        Column(
                            'notificar',
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

class CertificacionesSearchForm(forms.Form):
    cedula = forms.IntegerField(label='Documento de identidad')

    def __init__(self, *args, **kwargs):
        super(CertificacionesSearchForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Column(
                    Row(
                        Column(
                            Fieldset(
                                'Consulta de certificaciones:',
                            ),
                            css_class='s12 fieldset-certificaciones'
                        ),
                        Column(
                            'cedula',
                            css_class='s12'
                        ),
                        Column(
                            HTML(
                                """
                                <div id="captcha" style="margin-bottom:20px;" class="g-recaptcha" data-sitekey="6LeQ5iMTAAAAAL6Xzt0mbtAoZkwkw0pMr1vW2f8o"></div>
                                """
                            ),
                            css_class='s12'
                        ),
                        Column(
                            Div(
                                Submit(
                                    'submit',
                                    'Consultar',
                                    css_class='button-submit'
                                ),
                                css_class="right-align"
                            ),
                            css_class="s12"
                        ),
                        Column(
                            HTML(
                                """
                                <div style="margin-top:30px;">
                                <p style="color:#ccc;display:inline">* Toda la información almacenada en el sistema de información SICAN 
                                respeta las </p>
                                <a href="#" style="display:inline;">politicas de privacidad</a>
                                </div>
                                """
                            ),
                            css_class='s12'
                        )
                    ),
                    css_class = 's12 m6 l5'
                ),
                Column(
                    HTML(
                        """
                        <div id="container-certificaciones">
                            <p style="font-size:18px;"><b class="teal-text text-darken-4">Certificaciones:</b></p>
                            <div id="certificaciones-div">
                                <span>Ingresa un documento de identidad valido y presiona el boton "CONSULTAR", en este espacio 
                                encontraras los enlaces a las certificaciones.</span>
                                <p class="center"><i class="large material-icons teal-text text-darken-4">search</i></p>
                            </div>
                        </div>
                        """
                    ),
                    css_class='s12 m6 l7'
                )
            )
        )

class HvForm(forms.Form):

    contratista = forms.ModelChoiceField(label='Contratista',queryset=models.Contratistas.objects.none(),required=False)
    cargo = forms.CharField(max_length=100)
    region = forms.CharField(max_length=100)
    envio = forms.IntegerField(label="Consecutivo de envio")
    file = forms.FileField(widget=forms.FileInput(attrs={'accept':'application/pdf,application/x-pdf'}))

    numero_tarjeta = forms.CharField(label='Número de tarjeta', max_length=200, required=False)
    fecha_expedicion = forms.DateField(label='Fecha de expedición', required=False)
    folio = forms.IntegerField(label='Folio', required=False)

    titulo_1 = forms.CharField(label='Titulo obtenido',max_length=200)
    institucion_1 = forms.CharField(label='Institución',max_length=200)
    nivel_1 = forms.CharField(label='Nivel educativo',max_length=200)
    grado_1 = forms.DateField(label='Fecha de grado')
    folio_1 = forms.IntegerField(label='Folio')

    titulo_2 = forms.CharField(label='Titulo obtenido', max_length=200, required=False)
    institucion_2 = forms.CharField(label='Institución', max_length=200, required=False)
    nivel_2 = forms.CharField(label='Nivel educativo', max_length=200, required=False)
    grado_2 = forms.DateField(label='Fecha de grado', required=False)
    folio_2 = forms.IntegerField(label='Folio', required=False)

    titulo_3 = forms.CharField(label='Titulo obtenido', max_length=200, required=False)
    institucion_3 = forms.CharField(label='Institución', max_length=200, required=False)
    nivel_3 = forms.CharField(label='Nivel educativo', max_length=200, required=False)
    grado_3 = forms.DateField(label='Fecha de grado', required=False)
    folio_3 = forms.IntegerField(label='Folio', required=False)

    titulo_4 = forms.CharField(label='Titulo obtenido', max_length=200, required=False)
    institucion_4 = forms.CharField(label='Institución', max_length=200, required=False)
    nivel_4 = forms.CharField(label='Nivel educativo', max_length=200, required=False)
    grado_4 = forms.DateField(label='Fecha de grado', required=False)
    folio_4 = forms.IntegerField(label='Folio', required=False)

    titulo_5 = forms.CharField(label='Titulo obtenido', max_length=200, required=False)
    institucion_5 = forms.CharField(label='Institución', max_length=200, required=False)
    nivel_5 = forms.CharField(label='Nivel educativo', max_length=200, required=False)
    grado_5 = forms.DateField(label='Fecha de grado', required=False)
    folio_5 = forms.IntegerField(label='Folio', required=False)

    titulo_6 = forms.CharField(label='Titulo obtenido', max_length=200, required=False)
    institucion_6 = forms.CharField(label='Institución', max_length=200, required=False)
    nivel_6 = forms.CharField(label='Nivel educativo', max_length=200, required=False)
    grado_6 = forms.DateField(label='Fecha de grado', required=False)
    folio_6 = forms.IntegerField(label='Folio', required=False)

    titulo_7 = forms.CharField(label='Titulo obtenido', max_length=200, required=False)
    institucion_7 = forms.CharField(label='Institución', max_length=200, required=False)
    nivel_7 = forms.CharField(label='Nivel educativo', max_length=200, required=False)
    grado_7 = forms.DateField(label='Fecha de grado', required=False)
    folio_7 = forms.IntegerField(label='Folio', required=False)

    empresa_1 = forms.CharField(label='Empresa', max_length=200)
    fecha_inicio_1 = forms.DateField(label='Fecha de inicio')
    fecha_fin_1 = forms.DateField(label='Fecha de terminación')
    cargo_1 = forms.CharField(label='Cargo', max_length=200)
    folio_empresa_1 = forms.IntegerField(label='Folio')
    observaciones_1 = forms.CharField(label='Observaciones', max_length=200)

    empresa_2 = forms.CharField(label='Empresa', max_length=200, required=False)
    fecha_inicio_2 = forms.DateField(label='Fecha de inicio', required=False)
    fecha_fin_2 = forms.DateField(label='Fecha de terminación', required=False)
    cargo_2 = forms.CharField(label='Cargo', max_length=200, required=False)
    folio_empresa_2 = forms.IntegerField(label='Folio', required=False)
    observaciones_2 = forms.CharField(label='Observaciones', max_length=200, required=False)

    empresa_3 = forms.CharField(label='Empresa', max_length=200, required=False)
    fecha_inicio_3 = forms.DateField(label='Fecha de inicio', required=False)
    fecha_fin_3 = forms.DateField(label='Fecha de terminación', required=False)
    cargo_3 = forms.CharField(label='Cargo', max_length=200, required=False)
    folio_empresa_3 = forms.IntegerField(label='Folio', required=False)
    observaciones_3 = forms.CharField(label='Observaciones', max_length=200, required=False)

    empresa_4 = forms.CharField(label='Empresa', max_length=200, required=False)
    fecha_inicio_4 = forms.DateField(label='Fecha de inicio', required=False)
    fecha_fin_4 = forms.DateField(label='Fecha de terminación', required=False)
    cargo_4 = forms.CharField(label='Cargo', max_length=200, required=False)
    folio_empresa_4 = forms.IntegerField(label='Folio', required=False)
    observaciones_4 = forms.CharField(label='Observaciones', max_length=200, required=False)

    empresa_5 = forms.CharField(label='Empresa', max_length=200, required=False)
    fecha_inicio_5 = forms.DateField(label='Fecha de inicio', required=False)
    fecha_fin_5 = forms.DateField(label='Fecha de terminación', required=False)
    cargo_5 = forms.CharField(label='Cargo', max_length=200, required=False)
    folio_empresa_5 = forms.IntegerField(label='Folio', required=False)
    observaciones_5 = forms.CharField(label='Observaciones', max_length=200, required=False)

    empresa_6 = forms.CharField(label='Empresa', max_length=200, required=False)
    fecha_inicio_6 = forms.DateField(label='Fecha de inicio', required=False)
    fecha_fin_6 = forms.DateField(label='Fecha de terminación', required=False)
    cargo_6 = forms.CharField(label='Cargo', max_length=200, required=False)
    folio_empresa_6 = forms.IntegerField(label='Folio', required=False)
    observaciones_6 = forms.CharField(label='Observaciones', max_length=200, required=False)

    empresa_7 = forms.CharField(label='Empresa', max_length=200, required=False)
    fecha_inicio_7 = forms.DateField(label='Fecha de inicio', required=False)
    fecha_fin_7 = forms.DateField(label='Fecha de terminación', required=False)
    cargo_7 = forms.CharField(label='Cargo', max_length=200, required=False)
    folio_empresa_7 = forms.IntegerField(label='Folio', required=False)
    observaciones_7 = forms.CharField(label='Observaciones', max_length=200, required=False)

    empresa_8 = forms.CharField(label='Empresa', max_length=200, required=False)
    fecha_inicio_8 = forms.DateField(label='Fecha de inicio', required=False)
    fecha_fin_8 = forms.DateField(label='Fecha de terminación', required=False)
    cargo_8 = forms.CharField(label='Cargo', max_length=200, required=False)
    folio_empresa_8 = forms.IntegerField(label='Folio', required=False)
    observaciones_8 = forms.CharField(label='Observaciones', max_length=200, required=False)

    empresa_9 = forms.CharField(label='Empresa', max_length=200, required=False)
    fecha_inicio_9 = forms.DateField(label='Fecha de inicio', required=False)
    fecha_fin_9 = forms.DateField(label='Fecha de terminación', required=False)
    cargo_9 = forms.CharField(label='Cargo', max_length=200, required=False)
    folio_empresa_9 = forms.IntegerField(label='Folio', required=False)
    observaciones_9 = forms.CharField(label='Observaciones', max_length=200, required=False)

    empresa_10 = forms.CharField(label='Empresa', max_length=200, required=False)
    fecha_inicio_10 = forms.DateField(label='Fecha de inicio', required=False)
    fecha_fin_10 = forms.DateField(label='Fecha de terminación', required=False)
    cargo_10 = forms.CharField(label='Cargo', max_length=200, required=False)
    folio_empresa_10 = forms.IntegerField(label='Folio', required=False)
    observaciones_10 = forms.CharField(label='Observaciones', max_length=200, required=False)

    empresa_11 = forms.CharField(label='Empresa', max_length=200, required=False)
    fecha_inicio_11 = forms.DateField(label='Fecha de inicio', required=False)
    fecha_fin_11 = forms.DateField(label='Fecha de terminación', required=False)
    cargo_11 = forms.CharField(label='Cargo', max_length=200, required=False)
    folio_empresa_11 = forms.IntegerField(label='Folio', required=False)
    observaciones_11 = forms.CharField(label='Observaciones', max_length=200, required=False)

    def clean(self):
        cleaned_data = super().clean()
        contratista = cleaned_data.get("contratista")

        if contratista == None or contratista == '':
            self.add_error('contratista', 'Seleccione un contratista')

        if cleaned_data.get("numero_tarjeta") != '' or cleaned_data.get("fecha_expedicion") != None or cleaned_data.get("folio") != None:

            if cleaned_data.get("numero_tarjeta") == '':
                self.add_error('numero_tarjeta', 'Completa este campo')

            if cleaned_data.get("fecha_expedicion") == None:
                self.add_error('fecha_expedicion', 'Completa este campo')

            if cleaned_data.get("folio") == None:
                self.add_error('folio', 'Completa este campo')

        for i in range(2,8):
            if cleaned_data.get("titulo_"+str(i)) != '' or cleaned_data.get("institucion_"+str(i)) != '' or \
                cleaned_data.get("nivel_"+str(i)) != '' or cleaned_data.get("grado_"+str(i)) != None or \
                    cleaned_data.get("folio_"+str(i)) != None:

                if cleaned_data.get("titulo_"+str(i)) == '':
                    self.add_error("titulo_"+str(i), 'Completa este campo')

                if cleaned_data.get("institucion_"+str(i)) == '':
                    self.add_error("institucion_"+str(i), 'Completa este campo')

                if cleaned_data.get("nivel_"+str(i)) == '':
                    self.add_error("nivel_"+str(i), 'Completa este campo')

                if cleaned_data.get("grado_"+str(i)) == None:
                    self.add_error("grado_"+str(i), 'Completa este campo')

                if cleaned_data.get("folio_"+str(i)) == '':
                    self.add_error("folio_"+str(i), 'Completa este campo')

        for i in range(2,12):
            if cleaned_data.get("empresa_"+str(i)) != '' or cleaned_data.get("fecha_inicio_"+str(i)) != None or \
                cleaned_data.get("fecha_fin_"+str(i)) != None or cleaned_data.get("cargo_"+str(i)) != '' or \
                    cleaned_data.get("folio_empresa_"+str(i)) != None or cleaned_data.get("observaciones_"+str(i)) != '':

                if cleaned_data.get("empresa_"+str(i)) == '':
                    self.add_error("empresa_"+str(i), 'Completa este campo')

                if cleaned_data.get("fecha_inicio_"+str(i)) == None:
                    self.add_error("fecha_inicio_"+str(i), 'Completa este campo')

                if cleaned_data.get("fecha_fin_"+str(i)) == None:
                    self.add_error("fecha_fin_"+str(i), 'Completa este campo')

                if cleaned_data.get("cargo_"+str(i)) == '':
                    self.add_error("cargo_"+str(i), 'Completa este campo')

                if cleaned_data.get("folio_empresa_"+str(i)) == None:
                    self.add_error("folio_empresa_"+str(i), 'Completa este campo')

                if cleaned_data.get("observaciones_"+str(i)) == '':
                    self.add_error("observaciones_"+str(i), 'Completa este campo')


    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            if name not in ['contratista']:
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


    def __init__(self, *args, **kwargs):
        super(HvForm, self).__init__(*args, **kwargs)

        CHOICES_NIVEL = [
            ('', '----------'),
            ('Técnico profesional','Técnico profesional'),
            ('Tecnológico', 'Tecnológico'),
            ('Profesional', 'Profesional'),
            ('Especialización', 'Especialización'),
            ('Maestría', 'Maestría'),
            ('Doctorado', 'Doctorado')
        ]

        if 'pk' in kwargs['initial'].keys():

            hv = models.Hv.objects.get(id = kwargs['initial']['pk'])

            self.fields['envio'].initial = hv.envio
            self.fields['contratista'].queryset = models.Contratistas.objects.filter(id = hv.contratista.id)
            self.fields['contratista'].initial = models.Contratistas.objects.get(id = hv.contratista.id)
            self.fields['cargo'].initial = hv.cargo
            self.fields['region'].initial = hv.region

            self.fields['numero_tarjeta'].initial = hv.numero_tarjeta
            self.fields['fecha_expedicion'].initial = hv.fecha_expedicion
            self.fields['folio'].initial = hv.folio

            for i in range(1, 8):
                self.fields["titulo_" + str(i)].initial = getattr(hv,"titulo_" + str(i))
                self.fields["institucion_" + str(i)].initial = getattr(hv, "institucion_" + str(i))
                self.fields["nivel_" + str(i)].initial = getattr(hv, "nivel_" + str(i))
                self.fields["grado_" + str(i)].initial = getattr(hv, "grado_" + str(i))
                self.fields["folio_" + str(i)].initial = getattr(hv, "folio_" + str(i))

            for i in range(1, 12):
                self.fields["empresa_" + str(i)].initial = getattr(hv,"empresa_" + str(i))
                self.fields["fecha_inicio_" + str(i)].initial = getattr(hv, "fecha_inicio_" + str(i))
                self.fields["fecha_fin_" + str(i)].initial = getattr(hv, "fecha_fin_" + str(i))
                self.fields["cargo_" + str(i)].initial = getattr(hv, "cargo_" + str(i))
                self.fields["folio_empresa_" + str(i)].initial = getattr(hv, "folio_empresa_" + str(i))
                self.fields["observaciones_" + str(i)].initial = getattr(hv, "observaciones_" + str(i))


        self.fields['cargo'].widget = forms.Select(choices=[
            ('','----------'),
            ('Coordinador operativo', 'Coordinador operativo'),
            ('Profesional en campo', 'Profesional en campo'),
            ('Profesional de calidad', 'Profesional de calidad'),
            ('Lider institucional', 'Lider institucional'),
            ('Lider de servicio en zona', 'Lider de servicio en zona'),
            ('Asistentes', 'Asistentes')
        ])

        self.fields['region'].widget = forms.Select(choices=[
            ('', '----------'),
            ('Región 1', 'Región 1'),
            ('Región 2', 'Región 2'),
            ('Región 3', 'Región 3'),
        ])

        self.fields['nivel_1'].widget = forms.Select(choices=CHOICES_NIVEL)
        self.fields['nivel_2'].widget = forms.Select(choices=CHOICES_NIVEL)
        self.fields['nivel_3'].widget = forms.Select(choices=CHOICES_NIVEL)
        self.fields['nivel_4'].widget = forms.Select(choices=CHOICES_NIVEL)
        self.fields['nivel_5'].widget = forms.Select(choices=CHOICES_NIVEL)
        self.fields['nivel_6'].widget = forms.Select(choices=CHOICES_NIVEL)
        self.fields['nivel_7'].widget = forms.Select(choices=CHOICES_NIVEL)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Contratista',
                )
            ),
            Row(
                Column(
                    'envio',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Column(
                    'contratista',
                    css_class='s12 m6 l5'
                ),
                Column(
                    'cargo',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'region',
                    css_class='s12 m6 l3'
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
                    'Tarjeta profesional (en los casos que aplique)',
                )
            ),
            Row(
                Column(
                    'numero_tarjeta',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'fecha_expedicion',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio',
                    css_class='s12 m6 l2'
                )
            ),
            Row(
                Fieldset(
                    'Formación académica',
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Titulo #1:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'titulo_1',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'institucion_1',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'nivel_1',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'grado_1',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_1',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Titulo #2:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'titulo_2',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'institucion_2',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'nivel_2',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'grado_2',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_2',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Titulo #3:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'titulo_3',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'institucion_3',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'nivel_3',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'grado_3',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_3',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Titulo #4:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'titulo_4',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'institucion_4',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'nivel_4',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'grado_4',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_4',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Titulo #5:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'titulo_5',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'institucion_5',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'nivel_5',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'grado_5',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_5',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Titulo #6:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'titulo_6',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'institucion_6',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'nivel_6',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'grado_6',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_6',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Titulo #7:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'titulo_7',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'institucion_7',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'nivel_7',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'grado_7',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_7',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Fieldset(
                    'EXPERIENCIA',
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Experiencia #1:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'empresa_1',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_inicio_1',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_fin_1',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'cargo_1',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_empresa_1',
                    css_class='s12 m6 l2'
                ),
                Column(
                    'observaciones_1',
                    css_class='s12 m6 l6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Experiencia #2:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'empresa_2',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_inicio_2',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_fin_2',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'cargo_2',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_empresa_2',
                    css_class='s12 m6 l2'
                ),
                Column(
                    'observaciones_2',
                    css_class='s12 m6 l6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Experiencia #3:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'empresa_3',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_inicio_3',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_fin_3',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'cargo_3',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_empresa_3',
                    css_class='s12 m6 l2'
                ),
                Column(
                    'observaciones_3',
                    css_class='s12 m6 l6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Experiencia #4:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'empresa_4',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_inicio_4',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_fin_4',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'cargo_4',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_empresa_4',
                    css_class='s12 m6 l2'
                ),
                Column(
                    'observaciones_4',
                    css_class='s12 m6 l6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Experiencia #5:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'empresa_5',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_inicio_5',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_fin_5',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'cargo_5',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_empresa_5',
                    css_class='s12 m6 l2'
                ),
                Column(
                    'observaciones_5',
                    css_class='s12 m6 l6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Experiencia #6:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'empresa_6',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_inicio_6',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_fin_6',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'cargo_6',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_empresa_6',
                    css_class='s12 m6 l2'
                ),
                Column(
                    'observaciones_6',
                    css_class='s12 m6 l6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Experiencia #7:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'empresa_7',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_inicio_7',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_fin_7',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'cargo_7',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_empresa_7',
                    css_class='s12 m6 l2'
                ),
                Column(
                    'observaciones_7',
                    css_class='s12 m6 l6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Experiencia #8:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'empresa_8',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_inicio_8',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_fin_8',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'cargo_8',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_empresa_8',
                    css_class='s12 m6 l2'
                ),
                Column(
                    'observaciones_8',
                    css_class='s12 m6 l6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Experiencia #9:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'empresa_9',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_inicio_9',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_fin_9',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'cargo_9',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_empresa_9',
                    css_class='s12 m6 l2'
                ),
                Column(
                    'observaciones_9',
                    css_class='s12 m6 l6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Experiencia #10:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'empresa_10',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_inicio_10',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_fin_10',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'cargo_10',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_empresa_10',
                    css_class='s12 m6 l2'
                ),
                Column(
                    'observaciones_10',
                    css_class='s12 m6 l6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Experiencia #11:</b></p>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'empresa_11',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_inicio_11',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'fecha_fin_11',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'cargo_11',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'folio_empresa_11',
                    css_class='s12 m6 l2'
                ),
                Column(
                    'observaciones_11',
                    css_class='s12 m6 l6'
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

class HvEstado(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get("estado")
        observacion = cleaned_data.get("observacion")

        if estado == 'Rechazada' and observacion == '':
            self.add_error('observacion', 'Por favor agrega una observación al rechazo')

    def __init__(self, *args, **kwargs):
        super(HvEstado, self).__init__(*args, **kwargs)

        self.fields['estado'].widget = forms.Select(choices=[
            ('Esperando aprobación', 'Esperando aprobación'),
            ('Aprobada','Aprobada'),
            ('Rechazada','Rechazada')
        ])

        self.fields['observacion'].widget = forms.Textarea(
            attrs={'class': 'materialize-textarea', 'data-length': '500'})

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Estado de la hoja de vida',
                )
            ),
            Row(
                Column(
                    'estado',
                    css_class='s12'
                ),
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
        model = models.Hv
        fields = ['estado','observacion']
        labels = {
            'estado': 'Aprobar o rechazar hoja de vida',
            'observacion': 'Observación'
        }