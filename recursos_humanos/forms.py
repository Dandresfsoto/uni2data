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
        ('Representante legal', 'Representante legal')
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

class HvForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(HvForm, self).__init__(*args, **kwargs)

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
                    css_class='s12 m6 l4'
                ),
                Column(
                    'cargo',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'municipio',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        """
                    ),
                    'file',
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
        fields = ["envio", "contratista", "cargo", "file", "municipio"]


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