#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from direccion_financiera.models import Bancos, Reportes, Pagos, Descuentos, Amortizaciones
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset
from crispy_forms_materialize.layout import Layout, Row, Column, Submit, HTML, Button
from recursos_humanos.models import Contratistas
from django.db.models import Q
from django.conf import settings
from desplazamiento.models import Desplazamiento
import json


class BancoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BancoForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del banco',
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
                            'codigo',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'longitud',
                            css_class='s12 m6 l4'
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
        model = Bancos
        fields = ['codigo','nombre','longitud']
        labels = {
            'longitud': 'Cantidad caracteres'
        }

class TerceroForm(forms.ModelForm):

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
        super(TerceroForm, self).__init__(*args, **kwargs)

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
                        )
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
            'cedula': 'Cédula'
        }

class ReporteForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(ReporteForm, self).__init__(*args, **kwargs)

        pk = kwargs['initial'].get('pk')

        if pk != None:
            reporte = Reportes.objects.get(id = pk)
            self.fields['servicio'].widget.attrs['disabled'] = 'disabled'
            self.fields['servicio'].initial = reporte.servicio

        self.fields['respaldo'].widget = forms.FileInput()
        self.fields['firma'].widget = forms.FileInput()

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del reporte',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'nombre',
                            css_class='s12'
                        ),
                    ),
                    Row(
                        Column(
                            'servicio',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'proyecto',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'tipo_soporte',
                            css_class='s12 m6 l4'
                        ),
                    ),
                    Row(
                        Column(
                            'efectivo',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'rubro',
                            css_class='s12 m6 l4'
                        ),
                    ),

                    Row(
                        Column(
                            'inicio',
                            css_class='s12 m6'
                        ),
                        Column(
                            'fin',
                            css_class='s12 m6'
                        )
                    ),
                    Row(
                        Column(
                            'numero_contrato',
                            css_class='s12 m6'
                        ),
                        Column(
                            'numero_documento_equivalente',
                            css_class='s12 m6'
                        )
                    ),
                    css_class="s12"
                ),
            ),
            Row(
                Fieldset(
                    'Observaciones',
                )
            ),
            Row(
                Column(
                    'observacion',
                    css_class='s12'
                ),
            ),
            Row(
                Fieldset(
                    'Archivos',
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="font-size:1.2rem;"><b>Respaldo del reporte</b></p>
                        <p style="display:inline;"><b>Actualmente:</b>{{ respaldo_url | safe }}</p>
                        """
                    ),
                    'respaldo',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="font-size:1.2rem;"><b>Reporte interno firmado</b></p>
                        <p style="display:inline;"><b>Actualmente:</b>{{ firma_url | safe }}</p>
                        """
                    ),
                    'firma',
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
        model = Reportes
        fields = ['nombre','servicio','proyecto','tipo_soporte','inicio','fin','respaldo','firma','efectivo','numero_contrato','numero_documento_equivalente', 'rubro', 'observacion']
        labels = {
            'servicio': 'Bien o servicio a gestionar',
            'tipo_soporte': 'Respaldo del reporte',
            'inicio': 'Fecha de pago',
            'fin': 'Fecha de cargue',
            'efectivo': 'Tipo de reporte'
        }
        widgets = {
            'efectivo': forms.Select(choices=[(False,'Bancarizado'),(True,'Efectivo')]),
            'observacion': forms.Textarea(attrs={'class': 'materialize-textarea'})
        }

class ReporteUpdateForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(ReporteUpdateForm, self).__init__(*args, **kwargs)


        self.fields['respaldo'].widget = forms.FileInput()
        self.fields['firma'].widget = forms.FileInput()

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del reporte',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'nombre',
                            css_class='s12'
                        ),
                    ),
                    Row(
                        Column(
                            'proyecto',
                            css_class='s12 m6'
                        ),
                        Column(
                            'tipo_soporte',
                            css_class='s12 m6'
                        ),
                    ),
                    Row(
                        Column(
                            'rubro',
                            css_class='s12 m6 l4'
                        ),
                    ),
                    Row(
                        Column(
                            'inicio',
                            css_class='s12 m6'
                        ),
                        Column(
                            'fin',
                            css_class='s12 m6'
                        )
                    ),
                    Row(
                        Column(
                            'numero_contrato',
                            css_class='s12 m6'
                        ),
                        Column(
                            'numero_documento_equivalente',
                            css_class='s12 m6'
                        )
                    ),
                    css_class="s12"
                ),
            ),
            Row(
                Fieldset(
                    'Observaciones',
                )
            ),
            Row(
                Column(
                    'observacion',
                    css_class='s12'
                ),
            ),
            Row(
                Fieldset(
                    'Archivos',
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="font-size:1.2rem;"><b>Respaldo del reporte</b></p>
                        <p style="display:inline;"><b>Actualmente:</b>{{ respaldo_url | safe }}</p>
                        """
                    ),
                    'respaldo',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="font-size:1.2rem;"><b>Reporte interno firmado</b></p>
                        <p style="display:inline;"><b>Actualmente:</b>{{ firma_url | safe }}</p>
                        """
                    ),
                    'firma',
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
        model = Reportes
        fields = ['nombre','proyecto','tipo_soporte','inicio','fin','respaldo','firma','numero_contrato','numero_documento_equivalente', 'observacion', 'rubro']
        labels = {
            'tipo_soporte': 'Respaldo del reporte',
            'inicio': 'Fecha de pago',
            'fin': 'Fecha de cargue'
        }
        widgets = {
            'observacion': forms.Textarea(attrs={'class': 'materialize-textarea'})
        }

class ResultadoReporteForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        reporte = Reportes.objects.get(id = self.pk)
        file_banco = cleaned_data.get("file_banco")

        if file_banco == None:
            self.add_error('file_banco', 'Campo requerido')

        if reporte.firma.name != None and reporte.firma.name != '':
            pass
        else:
            self.add_error('file_banco', 'No se ha cargado el reporte firmado')

    def __init__(self, *args, **kwargs):
        super(ResultadoReporteForm, self).__init__(*args, **kwargs)

        pk = kwargs['initial'].get('pk')
        self.pk = pk
        self.fields['file_banco'].widget = forms.FileInput()

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Resultado del reporte',
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="font-size:1.2rem;"><b>Archivo de respuesta plataforma de pago</b></p>
                        <p style="display:inline;"><b>Actualmente:</b>{{ file_banco_url | safe }}</p>
                        """
                    ),
                    'file_banco',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Pagos:',
                )
            ),
            Row(
                css_class = 'id_pagos_row'
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

        i = 1

        for pago in Pagos.objects.filter(reporte__id=pk):

            self.fields[str(pago.id)] = forms.CharField(
                max_length=100,
                required=False,
                label = str(i) + ': ' + str(pago.tercero.fullname()) + ' - ' + str(pago.pretty_print_valor_descuentos()),
                widget = forms.Select(choices = [
                    ('Pago exitoso','Pago exitoso'),
                    ('Pago rechazado', 'Pago rechazado'),
                    ('Enviado a otro banco', 'Enviado a otro banco')
                ])
            )

            self.fields['reportar_'+str(pago.id)] = forms.BooleanField(required=False,label = 'Reportar a ' + pago.tercero.get_email())
            self.fields['reportar_'+str(pago.id)].widget.attrs['class'] = 'filled-in'

            if pago.tercero.get_email() == '':
                self.fields['reportar_' + str(pago.id)].initial = False
                self.fields['reportar_' + str(pago.id)].widget.attrs['disabled'] = 'disabled'
                self.fields['reportar_' + str(pago.id)].label = 'Actualice el email del tercero para notificar'
            else:
                self.fields['reportar_' + str(pago.id)].initial = True

            if pago.estado == 'Reportado':
                self.fields[str(pago.id)].initial = 'Pago exitoso'

            else:
                self.fields[str(pago.id)].initial = pago.estado


            self.helper.layout.fields[3].fields.append(
                Div(
                    Row(
                        Column(
                            str(pago.id),
                            css_class='s12 m6 l7'
                        ),
                        Column(
                            'reportar_' + str(pago.id),
                            css_class='s12 m6 l5'
                        )
                    ),
                    css_class = 'pago_div'
                )
            )
            i += 1

    class Meta:
        model = Reportes
        fields = ['file_banco']
        labels = {
            'file_banco': 'Bien o servicio a gestionar'
        }

class PagoForm(forms.Form):
    CHOICES = [
        ('', '----------'),
        ('Anticipo', 'Anticipo'),
        ('Incapacidad', 'Incapacidad'),
        ('Prestamo', 'Prestamo'),
        ('Retención en la fuente', 'Retención en la fuente'),
        ('Seguridad social', 'Seguridad social'),
        ('Otro', 'Otro')
    ]

    tercero = forms.CharField(max_length=100,label='Nombre',widget=forms.TextInput(attrs={'class':'autocomplete','autocomplete':'off'}))
    valor = forms.CharField(label="Valor del pago sin descuentos ($)")
    observacion = forms.CharField(label="Observación",max_length=500,widget=forms.Textarea(attrs={'class':'materialize-textarea'}))
    cedula = forms.IntegerField(label="Cédula",widget=forms.HiddenInput())
    publico = forms.BooleanField(initial=True, required=False)

    uuid_descuento_1 = forms.UUIDField(required=False, widget=forms.HiddenInput())
    valor_descuento_1 = forms.CharField(label = "Valor ($)",required=False)
    concepto_descuento_1 = forms.CharField(label="Concepto",widget = forms.Select(choices=CHOICES),required=False)
    observacion_descuento_1 = forms.CharField(label="Observación",max_length=500,required=False)

    uuid_descuento_2 = forms.UUIDField(required=False, widget=forms.HiddenInput())
    valor_descuento_2 = forms.CharField(label="Valor ($)", required=False)
    concepto_descuento_2 = forms.CharField(label="Concepto",widget=forms.Select(choices=CHOICES), required=False)
    observacion_descuento_2 = forms.CharField(label="Observación", max_length=500, required=False)

    uuid_descuento_3 = forms.UUIDField(required=False, widget=forms.HiddenInput())
    valor_descuento_3 = forms.CharField(label="Valor ($)", required=False)
    concepto_descuento_3 = forms.CharField(label="Concepto",widget=forms.Select(choices=CHOICES), required=False)
    observacion_descuento_3 = forms.CharField(label="Observación", max_length=500, required=False)

    uuid_descuento_4 = forms.UUIDField(required=False, widget=forms.HiddenInput())
    valor_descuento_4 = forms.CharField(label="Valor ($)", required=False)
    concepto_descuento_4 = forms.CharField(label="Concepto",widget=forms.Select(choices=CHOICES), required=False)
    observacion_descuento_4 = forms.CharField(label="Observación", max_length=500, required=False)

    uuid_descuento_5 = forms.UUIDField(required=False, widget=forms.HiddenInput())
    valor_descuento_5 = forms.CharField(label="Valor ($)", required=False)
    concepto_descuento_5 = forms.CharField(label="Concepto",widget=forms.Select(choices=CHOICES), required=False)
    observacion_descuento_5 = forms.CharField(label="Observación", max_length=500, required=False)

    descuentos_pendientes = forms.CharField(max_length=1000,required=False,widget=forms.HiddenInput(), initial='{}')
    descuentos_pendientes_otro_valor = forms.CharField(max_length=1000, required=False, widget=forms.HiddenInput(), initial='{}')

    def clean(self):
        cleaned_data = super().clean()

        cedula = cleaned_data.get("cedula")
        valor = float(cleaned_data.get("valor").replace('$ ', '').replace(',', ''))

        uuid_descuento_1 = cleaned_data.get("uuid_descuento_1")
        valor_descuento_1 = cleaned_data.get("valor_descuento_1")
        concepto_descuento_1 = cleaned_data.get("concepto_descuento_1")
        observacion_descuento_1 = cleaned_data.get("observacion_descuento_1")

        uuid_descuento_2 = cleaned_data.get("uuid_descuento_2")
        valor_descuento_2 = cleaned_data.get("valor_descuento_2")
        concepto_descuento_2 = cleaned_data.get("concepto_descuento_2")
        observacion_descuento_2 = cleaned_data.get("observacion_descuento_2")

        uuid_descuento_3 = cleaned_data.get("uuid_descuento_3")
        valor_descuento_3 = cleaned_data.get("valor_descuento_3")
        concepto_descuento_3 = cleaned_data.get("concepto_descuento_3")
        observacion_descuento_3 = cleaned_data.get("observacion_descuento_3")

        uuid_descuento_4 = cleaned_data.get("uuid_descuento_4")
        valor_descuento_4 = cleaned_data.get("valor_descuento_4")
        concepto_descuento_4 = cleaned_data.get("concepto_descuento_4")
        observacion_descuento_4 = cleaned_data.get("observacion_descuento_4")

        uuid_descuento_5 = cleaned_data.get("uuid_descuento_5")
        valor_descuento_5 = cleaned_data.get("valor_descuento_5")
        concepto_descuento_5 = cleaned_data.get("concepto_descuento_5")
        observacion_descuento_5 = cleaned_data.get("observacion_descuento_5")

        descuentos_pendientes = json.loads(cleaned_data.get("descuentos_pendientes"))
        descuentos_pendientes_otro_valor = json.loads(cleaned_data.get("descuentos_pendientes_otro_valor"))



        q = Q(reporte__id = self.pk) & Q(tercero__cedula = cedula)

        pagos = Pagos.objects.filter(q)


        if valor_descuento_1 == '' or valor_descuento_1 == None:
            v_d_1 = 0.0
        else:
            v_d_1 = float(valor_descuento_1.replace('$ ', '').replace(',', ''))


        if valor_descuento_2 == '' or valor_descuento_2 == None:
            v_d_2 = 0.0
        else:
            v_d_2 = float(valor_descuento_2.replace('$ ', '').replace(',', ''))


        if valor_descuento_3 == '' or valor_descuento_3 == None:
            v_d_3 = 0.0
        else:
            v_d_3 = float(valor_descuento_3.replace('$ ', '').replace(',', ''))


        if valor_descuento_4 == '' or valor_descuento_4 == None:
            v_d_4 = 0.0
        else:
            v_d_4 = float(valor_descuento_4.replace('$ ', '').replace(',', ''))


        if valor_descuento_5 == '' or valor_descuento_5 == None:
            v_d_5 = 0.0
        else:
            v_d_5 = float(valor_descuento_5.replace('$ ', '').replace(',', ''))


        descuentos_amortizaciones = 0


        for key in descuentos_pendientes.keys():
            pago = Pagos.objects.get(id = key)
            for key2 in descuentos_pendientes[key]:
                amortizacion = Amortizaciones.objects.get(id = key2)
                if descuentos_pendientes[key][key2]['descontar']:
                    if str(pago.id) in descuentos_pendientes_otro_valor.keys():
                        descuentos_amortizaciones += float(descuentos_pendientes_otro_valor[str(pago.id)].replace('$ ', '').replace(',', ''))
                    else:
                        descuentos_amortizaciones += float(amortizacion.valor.amount)



        valor_pago = valor - descuentos_amortizaciones - v_d_1 - v_d_2 - v_d_3 - v_d_4 - v_d_5

        if valor < 0.0:
            self.add_error('valor', 'Debes ingresar un monto valido.')

        if valor_pago < 0.0:
            self.add_error('valor', 'El valor de los descuentos es superior al pago.')


        if self.pk_pago != None:

            if pagos.exclude(id = self.pk_pago).count() > 0:
                self.add_error('tercero', 'Existe un pago registrado en el reporte para esta persona.')

        else:
            if pagos.count() > 0:
                self.add_error('tercero', 'Existe un pago registrado en el reporte para esta persona.')

            if Pagos.objects.filter(reporte__id = self.pk).count() > 19:
                self.add_error('tercero', 'Por reporte solo se permiten 20 pagos.')


        if valor_descuento_1 != '' or concepto_descuento_1 != '' or observacion_descuento_1 != '':

            if valor_descuento_1 == '':
                self.add_error('valor_descuento_1', 'El campo es obligatorio')

            if concepto_descuento_1 == '':
                self.add_error('concepto_descuento_1', 'El campo es obligatorio')

            if observacion_descuento_1 == '':
                self.add_error('observacion_descuento_1', 'El campo es obligatorio')


        if valor_descuento_2 != '' or concepto_descuento_2 != '' or observacion_descuento_2 != '':

            if valor_descuento_2 == '':
                self.add_error('valor_descuento_2', 'El campo es obligatorio')

            if concepto_descuento_2 == '':
                self.add_error('concepto_descuento_2', 'El campo es obligatorio')

            if observacion_descuento_2 == '':
                self.add_error('observacion_descuento_2', 'El campo es obligatorio')


        if valor_descuento_3 != '' or concepto_descuento_3 != '' or observacion_descuento_3 != '':

            if valor_descuento_3 == '':
                self.add_error('valor_descuento_3', 'El campo es obligatorio')

            if concepto_descuento_3 == '':
                self.add_error('concepto_descuento_3', 'El campo es obligatorio')

            if observacion_descuento_3 == '':
                self.add_error('observacion_descuento_3', 'El campo es obligatorio')


        if valor_descuento_4 != '' or concepto_descuento_4 != '' or observacion_descuento_4 != '':

            if valor_descuento_4 == '':
                self.add_error('valor_descuento_4', 'El campo es obligatorio')

            if concepto_descuento_4 == '':
                self.add_error('concepto_descuento_4', 'El campo es obligatorio')

            if observacion_descuento_4 == '':
                self.add_error('observacion_descuento_4', 'El campo es obligatorio')


        if valor_descuento_5 != '' or concepto_descuento_5 != '' or observacion_descuento_5 != '':

            if valor_descuento_5 == '':
                self.add_error('valor_descuento_5', 'El campo es obligatorio')

            if concepto_descuento_5 == '':
                self.add_error('concepto_descuento_5', 'El campo es obligatorio')

            if observacion_descuento_5 == '':
                self.add_error('observacion_descuento_5', 'El campo es obligatorio')


    def __init__(self, *args, **kwargs):
        super(PagoForm, self).__init__(*args, **kwargs)

        self.pk = kwargs['initial'].get('pk')
        self.pk_pago = kwargs['initial'].get('pk_pago')
        self.fields['publico'].widget.attrs['class'] = 'filled-in'

        if self.pk_pago != None:
            pago = Pagos.objects.get(id = self.pk_pago)
            self.pk = pago.reporte.id
            self.fields['tercero'].initial = pago.tercero.fullname() + ' - ' + str(pago.tercero.cedula)
            self.fields['valor'].initial = pago.valor.amount
            self.fields['observacion'].initial = pago.observacion
            self.fields['cedula'].initial = pago.tercero.cedula
            self.fields['publico'].initial = pago.publico
            self.fields['descuentos_pendientes'].initial = pago.descuentos_pendientes
            self.fields['descuentos_pendientes_otro_valor'].initial = pago.descuentos_pendientes_otro_valor

            descuentos = Descuentos.objects.filter(pago = pago).order_by('creation')
            i = 1

            for descuento in descuentos:
                self.fields['uuid_descuento_' + str(i)].initial = descuento.id
                self.fields['valor_descuento_' + str(i)].initial = descuento.valor.amount
                self.fields['concepto_descuento_' + str(i)].initial = descuento.concepto
                self.fields['observacion_descuento_' + str(i)].initial = descuento.observacion
                i += 1


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Column(
                    Row(
                        Fieldset(
                            'Información del tercero',
                        ),
                        Column(
                            'tercero',
                            css_class='s12'
                        ),
                        Column(
                            'cedula',
                            css_class='s12'
                        ),
                        Column(
                            HTML(
                                """
                                <p><b>Tipo cuenta:</b><span id="tipo_cuenta" style="margin-left:5px;">{{tipo_cuenta}}</span></p>
                                <p><b>Banco:</b><span id="banco" style="margin-left:5px;">{{banco}}</span></p>
                                <p><b>Número de cuenta:</b><span id="cuenta" style="margin-left:5px;">{{cuenta}}</span></p>
                                """
                            ),
                            css_class='s12'
                        ),
                    ),
                    Row(
                        Fieldset(
                            'Información del pago',
                        ),
                        Column(
                            'valor',
                            css_class='s12'
                        ),
                        Column(
                            'observacion',
                            css_class='s12'
                        ),
                        Column(
                            'publico',
                            css_class='s12'
                        )
                    ),
                    css_class="s12"
                ),
            ),
            Row(
                Fieldset(
                    'Descuentos',
                ),
                Column(
                    HTML(
                        """
                        <div id="descuentos-pendientes">
                        <p><b>Seleccione un contratista para visualizar los descuentos pendientes.</b></p>
                        </div>
                        """
                    ),
                    css_class='s12'
                ),
                Column(
                    'descuentos_pendientes',
                    'descuentos_pendientes_otro_valor',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Otros descuentos',
                ),
            ),
            Row(
                'uuid_descuento_1',
                Column(
                    'valor_descuento_1',
                    css_class='s12 m6 l3'
                ),
                Column(
                    'concepto_descuento_1',
                    css_class='s12 m6 l4 margin_concepto'
                ),
                Column(
                    'observacion_descuento_1',
                    css_class='s12 m6 l5'
                )
            ),
            Row(
                'uuid_descuento_2',
                Column(
                    'valor_descuento_2',
                    css_class='s12 m6 l3'
                ),
                Column(
                    'concepto_descuento_2',
                    css_class='s12 m6 l4 margin_concepto'
                ),
                Column(
                    'observacion_descuento_2',
                    css_class='s12 m6 l5'
                )
            ),
            Row(
                'uuid_descuento_3',
                Column(
                    'valor_descuento_3',
                    css_class='s12 m6 l3'
                ),
                Column(
                    'concepto_descuento_3',
                    css_class='s12 m6 l4 margin_concepto'
                ),
                Column(
                    'observacion_descuento_3',
                    css_class='s12 m6 l5'
                )
            ),
            Row(
                'uuid_descuento_4',
                Column(
                    'valor_descuento_4',
                    css_class='s12 m6 l3'
                ),
                Column(
                    'concepto_descuento_4',
                    css_class='s12 m6 l4 margin_concepto'
                ),
                Column(
                    'observacion_descuento_4',
                    css_class='s12 m6 l5'
                )
            ),
            Row(
                'uuid_descuento_5',
                Column(
                    'valor_descuento_5',
                    css_class='s12 m6 l3'
                ),
                Column(
                    'concepto_descuento_5',
                    css_class='s12 m6 l4 margin_concepto'
                ),
                Column(
                    'observacion_descuento_5',
                    css_class='s12 m6 l5'
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

class PagoDescontableForm(forms.Form):

    tercero = forms.CharField(max_length=100,label='Nombre',widget=forms.TextInput(attrs={'class':'autocomplete','autocomplete':'off'}))
    valor = forms.CharField(label="Valor del pago ($)")
    observacion = forms.CharField(label="Observación",max_length=500,widget=forms.Textarea(attrs={'class':'materialize-textarea'}))
    cedula = forms.IntegerField(label="Cédula",widget=forms.HiddenInput())
    publico = forms.BooleanField(initial=True, required=False)
    cuotas = forms.IntegerField(initial=1)

    def clean(self):
        cleaned_data = super().clean()

        cedula = cleaned_data.get("cedula")
        cuotas = cleaned_data.get("cuotas")


        q = Q(reporte__id = self.pk) & Q(tercero__cedula = cedula)

        pagos = Pagos.objects.filter(q)


        if self.pk_pago != None:

            if pagos.exclude(id = self.pk_pago).count() > 0:
                self.add_error('tercero', 'Existe un pago registrado en el reporte para esta persona.')

        else:
            if pagos.count() > 0:
                self.add_error('tercero', 'Existe un pago registrado en el reporte para esta persona.')

            if Pagos.objects.filter(reporte__id = self.pk).count() > 19:
                self.add_error('tercero', 'Por reporte solo se permiten 20 pagos.')

        if cuotas < 1:
            self.add_error('cuotas', 'Debe seleccionar por lo menos 1 cuota')



    def __init__(self, *args, **kwargs):
        super(PagoDescontableForm, self).__init__(*args, **kwargs)

        self.pk = kwargs['initial'].get('pk')
        self.pk_pago = kwargs['initial'].get('pk_pago')
        self.fields['publico'].widget.attrs['class'] = 'filled-in'

        if self.pk_pago != None:
            pago = Pagos.objects.get(id = self.pk_pago)
            self.pk = pago.reporte.id
            self.fields['tercero'].initial = pago.tercero.fullname() + ' - ' + str(pago.tercero.cedula)
            self.fields['valor'].initial = pago.valor.amount
            self.fields['observacion'].initial = pago.observacion
            self.fields['cedula'].initial = pago.tercero.cedula
            self.fields['publico'].initial = pago.publico
            self.fields['cuotas'].initial = pago.cuotas


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Column(
                    Row(
                        Fieldset(
                            'Información del tercero',
                        ),
                        Column(
                            'tercero',
                            css_class='s12'
                        ),
                        Column(
                            'cedula',
                            css_class='s12'
                        ),
                        Column(
                            HTML(
                                """
                                <p><b>Tipo cuenta:</b><span id="tipo_cuenta" style="margin-left:5px;">{{tipo_cuenta}}</span></p>
                                <p><b>Banco:</b><span id="banco" style="margin-left:5px;">{{banco}}</span></p>
                                <p><b>Número de cuenta:</b><span id="cuenta" style="margin-left:5px;">{{cuenta}}</span></p>
                                """
                            ),
                            css_class='s12'
                        ),
                    ),
                    Row(
                        Fieldset(
                            'Información del pago',
                        ),
                        Column(
                            'valor',
                            css_class='s12'
                        ),
                        Column(
                            'cuotas',
                            css_class='s12'
                        ),
                        Column(
                            'observacion',
                            css_class='s12'
                        ),
                        Column(
                            'publico',
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

class ReportarReporteForm(forms.Form):
    CHOICES = [
        ('', '----------'),
        (settings.EMAIL_DIRECCION_FINANCIERA, settings.EMAIL_DIRECCION_FINANCIERA),
        (settings.EMAIL_GERENCIA, settings.EMAIL_GERENCIA),
        (settings.EMAIL_CONTABILIDAD, settings.EMAIL_CONTABILIDAD),
        (settings.EMAIL_REPRESENTANTE_LEGAL, settings.EMAIL_REPRESENTANTE_LEGAL),
    ]

    email = forms.EmailField(widget=forms.Select(choices=CHOICES))



    def __init__(self, *args, **kwargs):
        super(ReportarReporteForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Column(
                    Row(
                        Fieldset(
                            'Enviar email de reporte',
                        ),
                        Column(
                            'email',
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

class DesplazamientoFinancieraForm(forms.ModelForm):

    valor = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(DesplazamientoFinancieraForm, self).__init__(*args, **kwargs)

        if 'pk_desplazamiento' in kwargs['initial'].keys():
            self.fields['valor'].initial = Desplazamiento.objects.get(id = kwargs['initial']['pk_desplazamiento']).valor.amount

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
                    'verificado',
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
        model = Desplazamiento
        fields = ['origen','destino','fecha','tipo_transporte','transportador','telefono','observaciones','verificado']
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

class AmortizacionesUpdate(forms.Form):

    valor = forms.CharField(label="Nuevo valor ($)")

    def clean(self):
        cleaned_data = super().clean()
        amortizacion = Amortizaciones.objects.get(id = self.initial['pk_amortizacion'])

        valor = float(cleaned_data.get('valor').replace('$ ', '').replace(',', ''))

        if amortizacion.valor.amount < valor:
            self.add_error('valor', 'El nuevo valor debe ser inferior a {0}'.format(amortizacion.pretty_print_valor()))


    def __init__(self, *args, **kwargs):
        super(AmortizacionesUpdate, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Nueva información para la amortización',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'valor',
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