#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from cpe_2018 import models
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
from cpe_2018.widgets import SelectWithDisabled
from django.utils import timezone

class RadicadosForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(RadicadosForm, self).__init__(*args, **kwargs)

        self.fields['tipologia_sede'].widget = forms.Select(choices=[
            ('','----------'),
            ('A', 'Tipo A'),
            ('D', 'Tipo D'),
            ('A,D', 'Tipo A y Tipo D')
        ])

        self.fields['ubicacion'].widget = forms.Select(choices=[
            ('', '----------'),
            ('Rural', 'Rural'),
            ('Urbana', 'Urbana')
        ])

        self.fields['estado'].widget = forms.Select(choices=[
            ('', '----------'),
            ('Aprobado', 'Aprobado'),
            ('Sale de beneficio', 'Sale de beneficio')
        ])

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del radicado',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'numero',
                            css_class='s12 m6 l3'
                        ),
                        Column(
                            'nombre_ie',
                            css_class='s12 m6 l9'
                        )
                    ),
                    Row(
                        Column(
                            'dane_sede',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'nombre_sede',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'tipologia_sede',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'ubicacion',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'estado',
                            css_class='s12 m6 l8'
                        )
                    ),
                    css_class="s12"
                ),
            ),
            Row(
                Fieldset(
                    'Beneficios de la sede y observaciones',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'portatiles',
                            css_class='s12 m4 l3'
                        ),
                        Column(
                            'kvd',
                            css_class='s12 m4 l3'
                        ),
                        Column(
                            'equipos_escritorio',
                            css_class='s12 m4 l3'
                        ),
                        Column(
                            'tabletas',
                            css_class='s12 m4 l3'
                        ),
                        Column(
                            'matricula',
                            css_class='s12 m4 l3'
                        ),
                        Column(
                            'observaciones',
                            css_class='s12 m4 l9'
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
        model = models.Radicados
        fields = ['numero','nombre_ie','dane_sede','nombre_sede','tipologia_sede','ubicacion','estado',
                  'portatiles','kvd','equipos_escritorio','tabletas','matricula','observaciones']
        labels = {
            'numero': 'Radicado',
            'nombre_ie': 'Nombre institución educativa',
            'dane_sede': 'Dane sede educativa',
            'nombre_sede': 'Nombre de la sede',
            'tipologia_sede': 'Tipologia de la sede'
        }

class RutasCreateForm(forms.Form):

    nombre = forms.CharField(label='Código ruta',max_length=100)
    contrato = forms.ModelChoiceField(label='Contrato',queryset=models.Contratos.objects.none(),required=False)
    radicados = forms.ModelMultipleChoiceField(label='Radicados',queryset=models.Radicados.objects.none(),required=False)
    visible = forms.BooleanField(initial=True,required=False)

    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            if name not in ['radicados','contrato','nombre']:
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

                        if name == 'nombre':
                            try:
                                models.Rutas.objects.get(nombre = value)
                            except:
                                pass
                            else:
                                self.add_error(name, 'El nombre de la ruta ya existe')

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
        names = {}

        for componente in models.Componentes.objects.exclude(numero='1'):
            names['peso_' + str(componente.id)] = cleaned_data.get('peso_' + str(componente.id))

        suma = 0
        for key in names.keys():
            suma += names[key]

        if suma > 100:
            for key in names.keys():
                self.add_error(key, 'No puede superar 100%')

    def __init__(self, *args, **kwargs):
        super(RutasCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información general',
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
                    'contrato',
                    css_class='s12'
                )
            ),
            Row(

            ),
            Row(
                Fieldset(
                    'Sedes educativas',
                )
            ),
            Row(
                Column(
                    'radicados',
                    css_class='s12'
                )
            ),
            Row(

            ),
            Row(
                Fieldset(
                    'Entregables por ruta',
                )
            ),
            Row(

            ),
            Row(
                Fieldset(
                    'Componentes',
                )
            ),
            Row(

            ),
            Row(
                Fieldset(
                    'Super Usuario',
                )
            ),
            Row(
                Column(
                    'visible',
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

        for entregable in models.Entregables.objects.filter(tipo = 'ruta&estrategia'):

            self.fields['entregable_' + str(entregable.id)] = forms.IntegerField(
                initial = 0,
                required = True,
                label = entregable.nombre
            )

            self.fields['valor_' + str(entregable.id)] = forms.FloatField(
                initial = 0,
                required = True,
                label = 'Valor ($)'
            )

            self.helper.layout.fields[8].fields.append(
                Div(
                    Div(
                        Column(
                            HTML(
                                """
                                <h6><b>{0} {1}</b></h6>
                                """.format(entregable.get_consecutivo(), entregable.momento.nombre)
                            ),
                            css_class='s12'
                        )
                    ),
                    Div(
                        Column(
                            'entregable_' + str(entregable.id),
                            css_class='s12 m6'
                        ),
                        Column(
                            'valor_' + str(entregable.id),
                            css_class='s12 m6'
                        )
                    )
                )
            )

        for componente in models.Componentes.objects.exclude(numero = '1'):

            self.fields['componente_' + str(componente.id)] = forms.IntegerField(
                initial=0,
                required=True,
                label = componente.nombre
            )

            self.fields['peso_' + str(componente.id)] = forms.IntegerField(
                initial=0,
                required=True,
                label='% Peso'
            )

            self.helper.layout.fields[10].fields.append(
                Div(
                    Column(
                        HTML(
                            """
                            <h6><b>{0} {1}</b></h6>
                            """.format(componente.numero,componente.nombre)
                        ),
                        css_class='s12'
                    ),
                    Div(
                        Column(
                            'componente_' + str(componente.id),
                            css_class='s12 m6'
                        ),
                        Column(
                            'peso_' + str(componente.id),
                            css_class='s12 m6'
                        ),
                    )
                )
            )


        if 'pk_ruta' in kwargs['initial'].keys():
            ruta = models.Rutas.objects.get(id = kwargs['initial']['pk_ruta'])
            radicados = models.Radicados.objects.filter(ruta = ruta)

            actividades_json = json.loads(ruta.actividades_json)

            for key in actividades_json:
                self.fields[key].initial = actividades_json[key]

            self.fields['nombre'].initial = ruta.nombre

            self.fields['contrato'].queryset = models.Contratos.objects.filter(id = ruta.contrato.id)
            self.fields['contrato'].initial = ruta.contrato

            self.fields['radicados'].queryset = radicados
            self.fields['radicados'].initial = radicados

class RutasEstadoForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(RutasEstadoForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.fields['estado'].widget = forms.Select(choices=[
            ('','----------'),
            ('Liquidación','Liquidación'),
            ('Reabrir', 'Reabrir')
        ])


        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Estado de la ruta',
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
        model = models.Rutas
        fields = ['estado']


class RetirarDocente(forms.Form):

    estado = forms.CharField(widget=forms.Select(choices=[
        ('Si','Si'),
        ('No', 'No')
    ]),label='Esta seguro de retirar al docente?')


    def __init__(self, *args, **kwargs):
        super(RetirarDocente, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Retirar docente',
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p><b>Nombre: </b>{{docente.nombre}}</p>
                        <p><b>Cedula: </b>{{docente.cedula}}</p>
                        <p><b>Grupo: </b>{{docente.grupo.get_nombre_grupo}}</p>
                        <p><b>Ruta: </b>{{docente.grupo.ruta.nombre}}</p>
                        <p><b>Contratista: </b>{{docente.grupo.ruta.contrato.contratista.get_full_name}}</p>
                        """
                    ),
                    css_class='s12'
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



class CortesCreateForm(forms.Form):

    descripcion = forms.CharField(max_length = 200)

    def __init__(self, *args, **kwargs):
        super(CortesCreateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Rutas con evidencias reportadas',
                )
            ),
            Row(
                Column(
                    'descripcion',
                    css_class = 's12'
                )
            ),
            Row(

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

        rutas_ids = models.EntregableRutaObject.objects.filter(
            estado = "Reportado",
            ruta__region__id = kwargs['initial']['pk']).values_list('ruta__id',flat=True).distinct()

        for ruta_id in rutas_ids:

            ruta = models.Rutas.objects.get(id = ruta_id)
            self.fields['ruta_' + str(ruta.id)] = forms.BooleanField(
                label = '{0} Ruta: {1} - {2}'.format('$ {:20,.2f}'.format(ruta.get_valor_corte()),ruta.nombre,ruta.contrato.contratista),
                required = False
            )
            self.fields['ruta_' + str(ruta.id)].widget.attrs['class'] = 'filled-in'

            self.helper.layout.fields[2].fields.append(
                Div(
                    Div(
                        Column(
                            'ruta_' + str(ruta.id),
                            css_class='s12'
                        )
                    )
                )
            )

class CuentaCobroForm(forms.Form):
    valores = forms.CharField(widget=forms.HiddenInput())
    valores_inicial = forms.CharField(widget=forms.HiddenInput())
    mes = forms.MultipleChoiceField(choices=[
        ('Enero','Enero'),
        ('Febrero', 'Febrero'),
        ('Marzo', 'Marzo'),
        ('Abril', 'Abril'),
        ('Mayo', 'Mayo'),
        ('Junio', 'Junio'),
        ('Julio', 'Julio'),
        ('Agosto', 'Agosto'),
        ('Septiembre', 'Septiembre'),
        ('Octubre', 'Octubre'),
        ('Noviembre', 'Noviembre'),
        ('Diciembre', 'Diciembre')
    ])
    year = forms.ChoiceField(label='Año')


    def clean(self):
        cleaned_data = super().clean()
        cuenta_cobro = models.CuentasCobro.objects.get(id = self.initial['pk_cuenta_cobro'])
        valores_meses_json = json.loads(cleaned_data['valores'])
        valor_total = 0

        if len(valores_meses_json) > 1:

            for valor_mes in valores_meses_json:
                valor = valor_mes.get('valor')
                if valor == None or valor == '':
                    pass
                else:
                    valor_total += float(valor.replace('$ ','').replace(',',''))

            if round(valor_total) != round(cuenta_cobro.valor.amount):
                self.add_error('mes', 'No coinciden los valores')




    def __init__(self, *args, **kwargs):
        super(CuentaCobroForm, self).__init__(*args, **kwargs)

        cuenta_cobro = models.CuentasCobro.objects.get(id=kwargs['initial']['pk_cuenta_cobro'])
        fecha = timezone.now()
        year = fecha.strftime('%Y')
        year_1 = str(int(year)-1)
        mes = fecha.strftime('%B').capitalize()

        self.fields['valores_inicial'].initial = cuenta_cobro.valores_json

        self.fields['year'].choices = [(year_1,year_1),(year,year)]

        if cuenta_cobro.data_json == '' or cuenta_cobro.data_json == None:
            self.fields['mes'].initial = mes
        else:
            self.fields['mes'].initial = json.loads(cuenta_cobro.data_json)['mes']
            self.fields['year'].initial = json.loads(cuenta_cobro.data_json)['year']

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Cuenta de cobro',
                )
            ),
            Row(
                HTML(
                    """
                    <div class="col s12">{{ cuentas| safe }}</div>
                    """
                )
            ),
            Row(
                HTML(
                    """
                    <div class="col s12 m6"><p><b>Valor:</b> {{valor}}</p></div>
                    <div class="col s12 m6"><p><b>Corte:</b> {{corte}}</p></div>
                    <div class="col s12 m6"><p><b>Contratista:</b> {{contratista}}</p></div>
                    <div class="col s12 m6"><p><b>Contrato:</b> {{contrato}}</p></div>
                    <div class="col s12 m6"><p><b>Inicio:</b> {{inicio}}</p></div>
                    <div class="col s12 m6"><p><b>Fin:</b> {{fin}}</p></div>
                    """
                )
            ),
            Row(),
            Row(
                Column(
                    'mes',
                    css_class="s12 m6"
                ),
                Column(
                    'year',
                    css_class="s12 m6"
                ),
                Column(
                    HTML(
                        """
                        <div id="container_meses"></div>
                        """
                    ),
                    css_class="s12"
                ),
            ),
            Row(
                Column(
                    'valores',
                    'valores_inicial',
                    css_class = 's12'
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

class RutasFinancieraForm(forms.Form):

    valor = forms.CharField(label='Valor')


    def __init__(self, *args, **kwargs):
        super(RutasFinancieraForm, self).__init__(*args, **kwargs)

        ruta = models.Rutas.objects.get(id=kwargs['initial']['pk_ruta'])

        self.fields['valor'].initial = ruta.valor.amount

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Valor de la ruta aprobado por la dirección financiera',
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
                    'contrato',
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

class RutaContratistaForm(forms.Form):

    contratista = forms.ModelChoiceField(label='Contratista de la ruta',queryset=models.Contratistas.objects.none(),required=False)



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

                        if name == 'nombre':
                            try:
                                models.Rutas.objects.get(nombre = value)
                            except:
                                pass
                            else:
                                self.add_error(name, 'El nombre de la ruta ya existe')

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
        super(RutaContratistaForm, self).__init__(*args, **kwargs)

        if 'pk_ruta' in kwargs['initial'].keys():
            ruta = models.Rutas.objects.get(id = kwargs['initial']['pk_ruta'])
            radicados = models.Radicados.objects.filter(ruta = ruta)

            if ruta.contratista != None:
                self.fields['contratista'].queryset = models.Contratistas.objects.filter(id = ruta.contratista.id)
                self.fields['contratista'].initial = ruta.contratista

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Selección del contratista',
                )
            ),

            Row(
                Column(
                    'contratista',
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

class RutaRhForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        ruta = models.Rutas.objects.get(id = self.initial['pk_ruta'])
        contrato = cleaned_data.get("contrato")

        if ruta.valor != contrato.valor:
            self.add_error('contrato', 'El valor del contrato y de la ruta deben ser iguales')


    def __init__(self, *args, **kwargs):
        super(RutaRhForm, self).__init__(*args, **kwargs)

        ruta = models.Rutas.objects.get(id = kwargs['initial']['pk_ruta'])

        contratista = None

        if ruta.contratista != None:
            contratista = ruta.contratista

        contratos_id = models.Rutas.objects.all().values_list('contrato__id',flat=True)

        self.fields['contrato'].queryset = Contratos.objects.exclude(id__in = contratos_id).filter(contratista = contratista)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Contrato de la ruta',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'contrato',
                            css_class='s12'
                        ),
                        Column(
                            HTML(
                                """
                                <p><b>Valor aprobado de la ruta: </b>{{valor_ruta}}</p>
                                """
                            ),
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
        model = models.Rutas
        fields = ['contrato']

class ActualizacionRadicadosForm(forms.Form):
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
                if 'ACTUALIZACION RADICADOS' not in sheet:
                    self.add_error('file', 'El archivo cargado no tiene la estructura requerida, reuerde usar la plantilla')
        else:
            self.add_error('file', 'El archivo cargado no tiene un formato valido')

    def __init__(self, *args, **kwargs):
        super(ActualizacionRadicadosForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Formato actualización de radicados',
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
                if 'DOCENTES' not in sheet:
                    self.add_error('file', 'No existe la hoja DOCENTES')
        else:
            self.add_error('file', 'El archivo cargado no tiene un formato valido')

    def __init__(self, *args, **kwargs):
        super(ActualizacionDocentesForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Formato actualización de docentes',
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

class CalificacionRetomaForm(forms.Form):

    delta = forms.CharField(widget=forms.HiddenInput())
    estado = forms.CharField(widget=forms.Select(choices=[
        ('', '----------'),
        ('Aprobado','Aprobado'),
        ('Rechazado', 'Rechazado')
    ]))

    def clean(self):
        cleaned_data = super().clean()

        estado = cleaned_data.get("estado")
        delta = cleaned_data.get("delta")

        if estado == 'Rechazado' or estado == 'Solicitud de subsanación':
            if json.loads(delta) == {'ops' : [{'insert':'\n'}]}:
                self.add_error('estado', 'Por favor escriba una observación')

    def __init__(self, *args, **kwargs):
        super(CalificacionRetomaForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Estado',
                )
            ),

            Row(
                Column(
                    'estado',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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

class CuentaCobroCargarForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(CuentaCobroCargarForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Cargar cuenta de cobro',
                )
            ),
            Row(
                HTML(
                    """
                    <p style="display:inline;margin-left: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                    """
                )
            ),
            Row(
                Column(
                    'file2',
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
        model = models.CuentasCobro
        fields = ['file2']
        widgets = {
            'file2': forms.FileInput(attrs={'data-max-file-size': "50M",'accept': 'application/pdf'})
        }

class CuentaCobroEstadoForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        estado = cleaned_data.get("estado")
        observaciones = cleaned_data.get("observaciones")

        if estado == 'Pendiente':
            if observaciones == None or observaciones == '':
                self.add_error('observaciones', 'Por favor escriba una observación')


    def __init__(self, *args, **kwargs):
        super(CuentaCobroEstadoForm, self).__init__(*args, **kwargs)

        self.fields['estado'].widget = forms.Select(choices = [
            ('','----------'),
            ('Reportado', 'Reportado'),
            ('Pendiente', 'Pendiente'),
            ('Liquidación', 'Liquidación'),
            ('Pagado', 'Pagado')
        ])

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Cargar cuenta de cobro',
                )
            ),
            Row(
                Column(
                    'estado',
                    css_class="s12"
                ),
                Column(
                    'observaciones',
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
        model = models.CuentasCobro
        fields = ['estado','observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'class': 'materialize-textarea'})
        }



class LiquidacionesEstadoForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        estado = cleaned_data.get("estado")
        observaciones = cleaned_data.get("observaciones")

        if estado == 'Pendiente':
            if observaciones == None or observaciones == '':
                self.add_error('observaciones', 'Por favor escriba una observación')


    def __init__(self, *args, **kwargs):
        super(LiquidacionesEstadoForm, self).__init__(*args, **kwargs)

        self.fields['estado'].widget = forms.Select(choices = [
            ('','----------'),
            ('Reportada', 'Reportada'),
            ('Pendiente', 'Pendiente'),
            ('Pagada', 'Pagada')
        ])

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Cargar liquidación',
                )
            ),
            Row(
                Column(
                    'estado',
                    css_class="s12"
                ),
                Column(
                    'observaciones',
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
        model = models.Liquidaciones
        fields = ['estado','observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'class': 'materialize-textarea'})
        }



class CalificacionSedeRutaForm(forms.Form):

    delta = forms.CharField(widget=forms.HiddenInput())
    estado = forms.CharField(widget=forms.Select(choices=[
        ('', '----------'),
        ('Aprobado','Aprobado'),
        ('Rechazado', 'Rechazado')
    ]))

    def clean(self):
        cleaned_data = super().clean()

        estado = cleaned_data.get("estado")
        delta = cleaned_data.get("delta")

        if estado == 'Rechazado' or estado == 'Solicitud de subsanación':
            if json.loads(delta) == {'ops' : [{'insert':'\n'}]}:
                self.add_error('estado', 'Por favor escriba una observación')

    def __init__(self, *args, **kwargs):
        super(CalificacionSedeRutaForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Estado',
                )
            ),

            Row(
                Column(
                    'estado',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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

class CalificacionEvidenciaFormacionForm(forms.Form):

    delta = forms.CharField(widget=forms.HiddenInput())
    estado = forms.CharField(widget=forms.Select(choices=[
        ('', '----------'),
        ('Aprobado','Aprobado'),
        ('Rechazado', 'Rechazado')
    ]))

    def clean(self):
        cleaned_data = super().clean()

        estado = cleaned_data.get("estado")
        delta = cleaned_data.get("delta")

        if estado == 'Rechazado' or estado == 'Solicitud de subsanación':
            if json.loads(delta) == {'ops' : [{'insert':'\n'}]}:
                self.add_error('estado', 'Por favor escriba una observación')

    def __init__(self, *args, **kwargs):
        super(CalificacionEvidenciaFormacionForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Estado',
                )
            ),

            Row(
                Column(
                    'estado',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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


class LiquidacionEvidenciaFormacionForm(forms.Form):


    def __init__(self, *args, **kwargs):
        super(LiquidacionEvidenciaFormacionForm, self).__init__(*args, **kwargs)

        entregable = models.Entregables.objects.get(id = kwargs['initial']['pk_entregable'])
        grupo = models.Grupos.objects.get(id=kwargs['initial']['pk_grupo'])
        ruta = models.Rutas.objects.get(id=kwargs['initial']['pk_ruta'])

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    entregable.nombre,
                )
            ),

            Row(
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

        for e in models.EntregableRutaObject.objects.filter(ruta = ruta,entregable = entregable, docente__grupo = grupo).exclude(valor = 0):
            self.fields[str(e.id)] = forms.BooleanField(
                required=False,
                label='{0} - {4} - {5} - Final Andes:{6} - Soporte: {7}: {1} - {2} - {3}'.format(
                    i,
                    e.docente.cedula,
                    e.docente.nombre,
                    '$ {:20,.2f}'.format(e.valor.amount),
                    e.docente.get_efectividad(),
                    'Habilitado' if e.para_pago else 'Deshabilitado',
                    'Si' if e.docente.producto_final_andes else 'No',
                    'No' if e.soporte == '' or e.soporte == None else 'Si'
                ),
                initial=True
            )

            self.fields[str(e.id)].widget.attrs['class'] = 'filled-in'

            if e.para_pago == True and e.estado in ["Reportado","Pagado"]:
                self.fields[str(e.id)].disabled = True
                self.fields[str(e.id)].initial = False


            self.helper.layout.fields[1].fields.append(
                Div(
                    Row(
                        Column(
                            str(e.id),
                            css_class='s12'
                        )
                    ),
                    css_class='docente_div'
                )
            )

            i += 1




class CalificacionEvidenciaCpeFormacionForm(forms.Form):

    delta = forms.CharField(widget=forms.HiddenInput())
    estado = forms.CharField(widget=forms.Select(choices=[
        ('', '----------'),
        ('Aprobado', 'Aprobado'),
        ('Rechazado', 'Rechazado')
    ]))

    def clean(self):
        cleaned_data = super().clean()

        estado = cleaned_data.get("estado")
        delta = cleaned_data.get("delta")

        if estado == 'Rechazado' or estado == 'Solicitud de subsanación':
            if json.loads(delta) == {'ops' : [{'insert':'\n'}]}:
                self.add_error('estado', 'Por favor escriba una observación')

    def __init__(self, *args, **kwargs):
        super(CalificacionEvidenciaCpeFormacionForm, self).__init__(*args, **kwargs)

        ids_docentes = json.loads(self.initial['ids_docentes'])

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Docentes:',
                )
            ),

            Row(

            ),

            Row(
                Column(
                    'estado',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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

        i = 1

        for docente in models.Docentes.objects.filter(id__in = ids_docentes):

            self.fields[str(docente.id)] = forms.BooleanField(
                required=False,
                label = '{0}: {1} - {2}'.format(i,docente.cedula,docente.nombre),
                initial=True
            )

            self.fields[str(docente.id)].widget.attrs['class'] = 'filled-in'

            self.helper.layout.fields[1].fields.append(
                Div(
                    Row(
                        Column(
                            str(docente.id),
                            css_class='s12 m6 l7'
                        )
                    ),
                    css_class='docente_div'
                )
            )

            i += 1


class RedForm(forms.Form):

    tipo = forms.CharField(widget=forms.Select(choices=[
        ('', '----------'),
        ('Acceso', 'Acceso'),
        ('Formación', 'Formación')
    ]))

    def __init__(self, *args, **kwargs):
        super(RedForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)


        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Nuevo RED',
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

class RedUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(RedUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Retroalimentación red',
                )
            ),
            Row(
                Column(
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
        model = models.Red
        fields = ['file2']


#------------------------------------- ACCESO -------------------------------------

class RetomaForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())

    def get_bolsas_calculadora(self, cpu, trc, lcd, portatil, impresora, tableta):
        bolsas = cpu*0.5 + trc*0.5 + lcd*0.5 + portatil*0.1 + impresora*0.5 + tableta*0.033
        if bolsas > 0.0 and bolsas < 1.0:
            return round(1)
        else:
            return round(bolsas)

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
                self.cleaned_data[name] = models.Municipios.objects.get(id = value)

    def clean(self):

        ruta = models.Rutas.objects.get(id = self.initial['pk_ruta'])
        cleaned_data = super().clean()
        radicado = cleaned_data.get("radicado")
        cpu = cleaned_data.get("cpu")
        trc = cleaned_data.get("trc")
        lcd = cleaned_data.get("lcd")
        portatil = cleaned_data.get("portatil")
        impresora = cleaned_data.get("impresora")
        tableta = cleaned_data.get("tableta")

        bolsas = self.get_bolsas_calculadora(cpu, trc, lcd, portatil, impresora, tableta )

        #if bolsas <= 0:
        #    self.add_error('cpu', 'La cantidad de bolsas debe ser mayor que cero')
        #else:
        #    disponibles = models.EntregableRutaObject.objects.filter(ruta=ruta, estado='asignado', padre="ruta&estrategia&{0}".format(ruta.id))
        #    if disponibles.count() < bolsas:
        #        self.add_error('cpu', 'La cantidad maxima de bolsas para la ruta es {0}'.format(disponibles.count()))

        if 'update' not in self.initial.keys():
            if models.Retoma.objects.filter(ruta = ruta, radicado = radicado, estado__in = ['Nuevo','Actualizado']).count() > 0:
                self.add_error('radicado', 'El radicado ya tiene una retoma en la ruta.')



    def __init__(self, *args, **kwargs):
        super(RetomaForm, self).__init__(*args, **kwargs)

        self.fields['municipio'].queryset = models.Municipios.objects.none()

        if 'pk_retoma' in kwargs['initial'].keys():
            retoma = models.Retoma.objects.get(id = kwargs['initial']['pk_retoma'])
            self.fields['municipio'].queryset = models.Municipios.objects.filter(id = retoma.municipio.id)
            self.fields['municipio'].initial = models.Municipios.objects.get(id = retoma.municipio.id)
            self.fields['file'].required = False


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del acta',
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
                    Row(
                        Column(
                            'municipio',
                            css_class='s12 m6'
                        )
                    ),
                    Row(
                        Column(
                            'fecha',
                            css_class='s12 m6 l2'
                        ),
                        Column(
                            'radicado',
                            css_class='s12 m6 l3'
                        ),
                        Column(
                            'dane',
                            css_class='s12 m6 l3'
                        ),
                        Column(
                            'sede_educativa',
                            css_class='s12 m6 l4'
                        )
                    ),
                    Row(
                        Column(
                            'rector',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'celular',
                            css_class='s12 m6 l4'
                        ),
                        Column(
                            'cedula',
                            css_class='s12 m6 l4'
                        )
                    ),
                    css_class="s12"
                ),
            ),
            Row(
                Fieldset(
                    'Información de la retoma',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            'bolsas_empacadas',
                            css_class='s12 m4 l3'
                        ),
                        Column(
                            'cpu',
                            css_class='s12 m4 l3'
                        ),
                        Column(
                            'trc',
                            css_class='s12 m4 l3'
                        ),
                        Column(
                            'lcd',
                            css_class='s12 m4 l3'
                        ),
                        Column(
                            'portatil',
                            css_class='s12 m4 l3'
                        ),
                        Column(
                            'impresora',
                            css_class='s12 m4 l3'
                        ),
                        Column(
                            'tableta',
                            css_class='s12 m4 l3'
                        ),
                        Column(
                            'perifericos',
                            css_class='s12 m4 l3'
                        )
                    ),
                    css_class="s12"
                ),
            ),
            Row(
                Fieldset(
                    'Acta en formato PDF',
                )
            ),
            Row(
                Column(
                    Row(
                        HTML(
                            """
                            <p style="display:inline;margin-left: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                            """
                        ),
                        Column(
                            'file',
                            css_class='s12'
                        )
                    ),
                    css_class="s12"
                ),
            ),
            Row(
                Fieldset(
                    'Registro fotografico en formato PDF',
                )
            ),
            Row(
                Column(
                    Row(
                        HTML(
                            """
                            <p style="display:inline;margin-left: 10px;"><b>Actualmente:</b>{{ file2_url | safe }}</p>
                            """
                        ),
                        Column(
                            'file2',
                            css_class='s12'
                        )
                    ),
                    css_class="s12"
                ),
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.Retoma
        fields = ['radicado','dane','fecha','sede_educativa','municipio','bolsas_empacadas','cpu','trc','lcd','portatil',
                  'impresora','tableta','perifericos','rector','celular','cedula','file','file2','tipo']
        labels = {

        }

        widgets = {
            'file': forms.FileInput(attrs={
                'accept': 'application/pdf',
                'data-max-file-size': "20M"
            }),
            'file2': forms.FileInput(attrs={
                'accept': 'application/pdf',
                'data-max-file-size': "20M"
            }),
            'tipo': forms.Select(choices=[('Sican', 'Sican'), ('Lupaap', 'Lupaap')])
        }


class EventoMunicipalForm(forms.ModelForm):
    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(EventoMunicipalForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Relatorias eventos institucionales',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.EventoMunicipal
        fields = ['file','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            })
        }
class EventoInstitucionalForm(forms.ModelForm):
    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(EventoInstitucionalForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Relatorias eventos institucionales',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.EventoInstitucional
        fields = ['file','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            })
        }
class ActaPostulacionForm(forms.ModelForm):
    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ActaPostulacionForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Acta de postulación, Formato de autorización, Carta Aval de coautores',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.ActaPostulacion
        fields = ['file','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            })
        }
class BaseDatosPostulanteForm(forms.ModelForm):
    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(BaseDatosPostulanteForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Base de datos con la información del postulantes',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.BaseDatosPostulante
        fields = ['file','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            })
        }
class ActualizacionDirectorioSedesForm(forms.ModelForm):
    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ActualizacionDirectorioSedesForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Actualización del directorio de las sedes beneficiadas',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.ActualizacionDirectorioSedes
        fields = ['file','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "5s0M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            })
        }
class ActualizacionDirectorioMunicipiosForm(forms.ModelForm):
    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ActualizacionDirectorioMunicipiosForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Actualización del directorio de los municipios',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.ActualizacionDirectorioMunicipios
        fields = ['file','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            })
        }
class CronogramaTalleresForm(forms.ModelForm):
    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(CronogramaTalleresForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Cronograma de talleres',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.CronogramaTalleres
        fields = ['file','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            })
        }
class DocumentoLegalizacionForm(forms.ModelForm):
    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(DocumentoLegalizacionForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Documento de legalización de entrega de terminales a docentes por municipio',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.DocumentoLegalizacion
        fields = ['file','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            })
        }
class RelatoriaGraduacionDocentesForm(forms.ModelForm):
    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(RelatoriaGraduacionDocentesForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Relatorias eventos municipales graduación de docentes',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.RelatoriaGraduacionDocentes
        fields = ['file','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            })
        }


class DocumentoLegalizacionTerminalesForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        super(DocumentoLegalizacionTerminalesForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Documento de legalización de la propiedad de las terminales',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12 m6'
                ),
                Column(
                    'tipo',
                    css_class='s12 m6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.DocumentoLegalizacionTerminales
        fields = ['file','fecha','tipo']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'tipo': forms.Select(choices=[('Sican','Sican'),('Lupaap','Lupaap')])
        }
class DocumentoLegalizacionTerminalesFormValle1(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        super(DocumentoLegalizacionTerminalesFormValle1, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Documento de legalización de la propiedad de las terminales',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12 m6'
                ),
                Column(
                    'tipo',
                    css_class='s12 m6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.DocumentoLegalizacionTerminalesValle1
        fields = ['file','fecha','tipo']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'tipo': forms.Select(choices=[('Sican','Sican'),('Lupaap','Lupaap')])
        }
class DocumentoLegalizacionTerminalesFormValle2(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        super(DocumentoLegalizacionTerminalesFormValle2, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Documento de legalización de la propiedad de las terminales',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12 m6'
                ),
                Column(
                    'tipo',
                    css_class='s12 m6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.DocumentoLegalizacionTerminalesValle2
        fields = ['file','fecha','tipo']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'tipo': forms.Select(choices=[('Sican','Sican'),('Lupaap','Lupaap')])
        }


class RelatoriaTallerAperturaForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        super(RelatoriaTallerAperturaForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Relatoría del taller firmada por un docente asistente',
                )
            ),
            Row(
                Row(
                    Column(
                        'fecha',
                        css_class='s12 m6'
                    ),
                    Column(
                        'tipo',
                        css_class='s12 m6'
                    )
                ),
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.RelatoriaTallerApertura
        fields = ['file','fecha','tipo']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'tipo': forms.Select(choices=[('Sican', 'Sican'), ('Lupaap', 'Lupaap')])
        }
class CuenticosTallerAperturaForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        super(CuenticosTallerAperturaForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'CuenTICos, Cuento herramienta Cuadernia',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.CuenticosTallerApertura
        fields = ['file','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            })
        }
class RelatoriaTallerAdministraticForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        super(RelatoriaTallerAdministraticForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Relatoría del taller firmada por un docente asistente',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12 m6'
                ),
                Column(
                    'tipo',
                    css_class='s12 m6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.RelatoriaTallerAdministratic
        fields = ['file','fecha','tipo']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'tipo': forms.Select(choices=[('Sican', 'Sican'), ('Lupaap', 'Lupaap')])
        }
class InfoticTallerAdministraticForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        super(InfoticTallerAdministraticForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Producto InfoTIC: infografía que pueda ser leída a través de un código QR',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.InfoticTallerAdministratic
        fields = ['file','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            })
        }
class RelatoriaTallerContenidosEducativosForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        super(RelatoriaTallerContenidosEducativosForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Relatoría del taller firmada por un docente asistente',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12 m6'
                ),
                Column(
                    'tipo',
                    css_class='s12 m6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.RelatoriaTallerContenidosEducativos
        fields = ['file','fecha','tipo']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'tipo': forms.Select(choices=[('Sican', 'Sican'), ('Lupaap', 'Lupaap')])
        }
class DibuarteTallerContenidosEducativosForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        super(DibuarteTallerContenidosEducativosForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Producto DibuARTE: dibujo en 3D herramienta digital Kodu',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.DibuarteTallerContenidosEducativos
        fields = ['file','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            })
        }

class RelatoriaTallerRAEEForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        super(RelatoriaTallerRAEEForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Relatoría del taller firmada por un docente asistente',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12 m6'
                ),
                Column(
                    'tipo',
                    css_class='s12 m6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.RelatoriaTallerRAEE
        fields = ['file','fecha','tipo']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'tipo': forms.Select(choices=[('Sican', 'Sican'), ('Lupaap', 'Lupaap')])
        }
class EcoraeeTallerRAEEForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        super(EcoraeeTallerRAEEForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Producto D-EcoRAEEesponsables: video editor con extensiones AVI, MOV, WMV, o enlace Tipo Yotuber (URL)',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.EcoraeeTallerRAEE
        fields = ['file','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            })
        }
class EncuestaMonitoreoForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        super(EncuestaMonitoreoForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Encuesta de monitoreo',
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12 m6'
                ),
                Column(
                    'tipo',
                    css_class='s12 m6'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.EncuestaMonitoreo
        fields = ['file','fecha','tipo']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'tipo': forms.Select(choices=[('Sican', 'Sican'), ('Lupaap', 'Lupaap')])
        }

#----------------------------------- FORMACIÓN ------------------------------------

class GrupoForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        numeros = list(models.Grupos.objects.filter(ruta = self.ruta).values_list('numero',flat=True))

        if cleaned_data['numero'] in numeros:
            self.add_error('numero', 'Ya existe un grupo con este numero.')

    def __init__(self, *args, **kwargs):
        super(GrupoForm, self).__init__(*args, **kwargs)

        self.region = models.Regiones.objects.get(id = kwargs['initial']['pk'])
        self.ruta = models.Rutas.objects.get(id=kwargs['initial']['pk_ruta'])

        self.fields['estrategia'].queryset = models.Estrategias.objects.exclude(nombre = "Prendo & Aprendo")

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del grupo',
                )
            ),

            Row(
                Column(
                    'numero',
                    css_class='s12 m6'
                ),
                Column(
                    'estrategia',
                    css_class='s12 m6'
                )
            ),

            Row(
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
        model = models.Grupos
        fields = ['estrategia','numero']
        labels = {
            'estrategia': 'Diplomado'
        }

class GrupoUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(GrupoUpdateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del grupo',
                )
            ),

            Row(
                Column(
                    'numero',
                    css_class='s12 m6'
                )
            ),

            Row(
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
        model = models.Grupos
        fields = ['numero']
        labels = {
            'estrategia': 'Diplomado'
        }

class AgregarDocenteGrupoForm(forms.Form):

    docentes = forms.ModelMultipleChoiceField(label='Docentes',queryset=models.Docentes.objects.none(),required=False)

    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            if name not in ['docentes']:
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

        ruta = models.Rutas.objects.get(id = self.initial['pk_ruta'])

        docentes = cleaned_data['docentes']
        objetos_formacion = models.EntregableRutaObject.objects.filter(
            ruta = ruta,
            padre = 'docente&{0}'.format(ruta.id),
            estado = 'asignado',
            tipo = 'Docente'
        )

        if len(docentes) > objetos_formacion.count():
            self.add_error('docentes', 'El limite de docentes es {0}'.format(objetos_formacion.count()))



    def __init__(self, *args, **kwargs):
        super(AgregarDocenteGrupoForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Selección de docentes',
                )
            ),
            Row(
                Column(
                    'docentes',
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

class DocumentoCompromisoInscripcionForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(DocumentoCompromisoInscripcionForm, self).__init__(*args, **kwargs)

        if 'pk_grupo' in kwargs['initial'].keys():

            choices = []
            src = {'disabled':{}}
            entregable = models.Entregables.objects.get(id = kwargs['initial']['pk_entregable'])

            for docente in models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo']):
                choices.append((str(docente.id),docente.__str__()))
                src['disabled'][str(docente.id)] = docente.get_disabled_entregable_form(entregable, ['Reportado','Pagado'])

            self.fields['docentes'].widget = SelectWithDisabled(choices=choices,src=src)

        if 'pk_objeto' in kwargs['initial'].keys():
            self.fields['file'].required = False

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    entregable.nombre,
                )
            ),
            Row(
                Column(
                    'docentes',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <a id="id_todos" style="display:inline-block;margin-top:10px;" class="waves-effect waves-light btn pink darken-4"><i class="material-icons left">done_all</i>todos</a>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.DocumentoCompromisoInscripcion
        fields = ['file','docentes']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'docentes': SelectWithDisabled()
        }
class ActaPosesionDocenteForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ActaPosesionDocenteForm, self).__init__(*args, **kwargs)

        if 'pk_grupo' in kwargs['initial'].keys():

            choices = []
            src = {'disabled':{}}
            entregable = models.Entregables.objects.get(id = kwargs['initial']['pk_entregable'])

            for docente in models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo']):
                choices.append((str(docente.id),docente.__str__()))
                src['disabled'][str(docente.id)] = docente.get_disabled_entregable_form(entregable, ['Reportado','Pagado'])

            self.fields['docentes'].widget = SelectWithDisabled(choices=choices,src=src)

        if 'pk_objeto' in kwargs['initial'].keys():
            self.fields['file'].required = False

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    entregable.nombre,
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'docentes',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <a id="id_todos" style="display:inline-block;margin-top:10px;" class="waves-effect waves-light btn pink darken-4"><i class="material-icons left">done_all</i>todos</a>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.ActaPosesionDocente
        fields = ['file','docentes','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'docentes': SelectWithDisabled()
        }
class BaseDatosDocentesForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(BaseDatosDocentesForm, self).__init__(*args, **kwargs)

        if 'pk_grupo' in kwargs['initial'].keys():

            choices = []
            src = {'disabled':{}}
            entregable = models.Entregables.objects.get(id = kwargs['initial']['pk_entregable'])

            for docente in models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo']):
                choices.append((str(docente.id),docente.__str__()))
                src['disabled'][str(docente.id)] = docente.get_disabled_entregable_form(entregable, ['Reportado','Pagado'])

            self.fields['docentes'].widget = SelectWithDisabled(choices=choices,src=src)
            #self.fields['docentes'].queryset = models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo'])

        if 'pk_objeto' in kwargs['initial'].keys():
            self.fields['file'].required = False

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    entregable.nombre,
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'docentes',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <a id="id_todos" style="display:inline-block;margin-top:10px;" class="waves-effect waves-light btn pink darken-4"><i class="material-icons left">done_all</i>todos</a>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.BaseDatosDocentes
        fields = ['file','docentes','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'docentes': SelectWithDisabled()
        }
class DocumentoProyeccionCronogramaForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(DocumentoProyeccionCronogramaForm, self).__init__(*args, **kwargs)

        if 'pk_grupo' in kwargs['initial'].keys():

            choices = []
            src = {'disabled':{}}
            entregable = models.Entregables.objects.get(id = kwargs['initial']['pk_entregable'])

            for docente in models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo']):
                choices.append((str(docente.id),docente.__str__()))
                src['disabled'][str(docente.id)] = docente.get_disabled_entregable_form(entregable, ['Reportado','Pagado'])

            self.fields['docentes'].widget = SelectWithDisabled(choices=choices,src=src)
            #self.fields['docentes'].queryset = models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo'])

        if 'pk_objeto' in kwargs['initial'].keys():
            self.fields['file'].required = False

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    entregable.nombre,
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'docentes',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <a id="id_todos" style="display:inline-block;margin-top:10px;" class="waves-effect waves-light btn pink darken-4"><i class="material-icons left">done_all</i>todos</a>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.DocumentoProyeccionCronograma
        fields = ['file','docentes','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'docentes': SelectWithDisabled()
        }
class ListadoAsistenciaForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ListadoAsistenciaForm, self).__init__(*args, **kwargs)

        if 'pk_grupo' in kwargs['initial'].keys():

            choices = []
            src = {'disabled':{}}
            entregable = models.Entregables.objects.get(id = kwargs['initial']['pk_entregable'])

            for docente in models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo']):
                choices.append((str(docente.id),docente.__str__()))
                src['disabled'][str(docente.id)] = docente.get_disabled_entregable_form(entregable, ['Reportado','Pagado'])

            self.fields['docentes'].widget = SelectWithDisabled(choices=choices,src=src)
            #self.fields['docentes'].queryset = models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo'])

        if 'pk_objeto' in kwargs['initial'].keys():
            self.fields['file'].required = False

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    entregable.nombre,
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                ),
                Column(
                    'tipo',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'docentes',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <a id="id_todos" style="display:inline-block;margin-top:10px;" class="waves-effect waves-light btn pink darken-4"><i class="material-icons left">done_all</i>todos</a>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.ListadoAsistencia
        fields = ['file','docentes','fecha','tipo']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'docentes': SelectWithDisabled(),
            'tipo': forms.Select(choices=[('Sican','Sican'),('Lupaap','Lupaap')])
        }
class InstrumentoAutoreporteForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(InstrumentoAutoreporteForm, self).__init__(*args, **kwargs)

        if 'pk_grupo' in kwargs['initial'].keys():

            choices = []
            src = {'disabled':{}}
            entregable = models.Entregables.objects.get(id = kwargs['initial']['pk_entregable'])

            for docente in models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo']):
                choices.append((str(docente.id),docente.__str__()))
                src['disabled'][str(docente.id)] = docente.get_disabled_entregable_form(entregable, ['Reportado','Pagado'])

            self.fields['docentes'].widget = SelectWithDisabled(choices=choices,src=src)

        if 'pk_objeto' in kwargs['initial'].keys():
            self.fields['file'].required = False

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    entregable.nombre,
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'docentes',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <a id="id_todos" style="display:inline-block;margin-top:10px;" class="waves-effect waves-light btn pink darken-4"><i class="material-icons left">done_all</i>todos</a>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.InstrumentoAutoreporte
        fields = ['file','docentes','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'docentes': SelectWithDisabled()
        }
class PresentacionApaForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(PresentacionApaForm, self).__init__(*args, **kwargs)

        if 'pk_grupo' in kwargs['initial'].keys():

            choices = []
            src = {'disabled':{}}
            entregable = models.Entregables.objects.get(id = kwargs['initial']['pk_entregable'])

            for docente in models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo']):
                choices.append((str(docente.id),docente.__str__()))
                src['disabled'][str(docente.id)] = docente.get_disabled_entregable_form(entregable, ['Reportado','Pagado'])

            self.fields['docentes'].widget = SelectWithDisabled(choices=choices,src=src)
            #self.fields['docentes'].queryset = models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo'])

        if 'pk_objeto' in kwargs['initial'].keys():
            self.fields['file'].required = False

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    entregable.nombre,
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'docentes',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <a id="id_todos" style="display:inline-block;margin-top:10px;" class="waves-effect waves-light btn pink darken-4"><i class="material-icons left">done_all</i>todos</a>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.PresentacionApa
        fields = ['file','docentes','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'docentes': SelectWithDisabled()
        }
class InstrumentoHagamosMemoriaForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(InstrumentoHagamosMemoriaForm, self).__init__(*args, **kwargs)

        if 'pk_grupo' in kwargs['initial'].keys():

            choices = []
            src = {'disabled':{}}
            entregable = models.Entregables.objects.get(id = kwargs['initial']['pk_entregable'])

            for docente in models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo']):
                choices.append((str(docente.id),docente.__str__()))
                src['disabled'][str(docente.id)] = docente.get_disabled_entregable_form(entregable, ['Reportado','Pagado'])

            self.fields['docentes'].widget = SelectWithDisabled(choices=choices,src=src)
            #self.fields['docentes'].queryset = models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo'])

        if 'pk_objeto' in kwargs['initial'].keys():
            self.fields['file'].required = False

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    entregable.nombre,
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'docentes',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <a id="id_todos" style="display:inline-block;margin-top:10px;" class="waves-effect waves-light btn pink darken-4"><i class="material-icons left">done_all</i>todos</a>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.InstrumentoHagamosMemoria
        fields = ['file','docentes','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'docentes': SelectWithDisabled()
        }
class PresentacionActividadPedagogicaForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(PresentacionActividadPedagogicaForm, self).__init__(*args, **kwargs)

        if 'pk_grupo' in kwargs['initial'].keys():

            choices = []
            src = {'disabled':{}}
            entregable = models.Entregables.objects.get(id = kwargs['initial']['pk_entregable'])

            for docente in models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo']):
                choices.append((str(docente.id),docente.__str__()))
                src['disabled'][str(docente.id)] = docente.get_disabled_entregable_form(entregable, ['Reportado','Pagado'])

            self.fields['docentes'].widget = SelectWithDisabled(choices=choices,src=src)
            #self.fields['docentes'].queryset = models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo'])

        if 'pk_objeto' in kwargs['initial'].keys():
            self.fields['file'].required = False

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    entregable.nombre,
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'docentes',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <a id="id_todos" style="display:inline-block;margin-top:10px;" class="waves-effect waves-light btn pink darken-4"><i class="material-icons left">done_all</i>todos</a>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.PresentacionActividadPedagogica
        fields = ['file','docentes','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'docentes': SelectWithDisabled()
        }
class RepositorioActividadesForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        super(RepositorioActividadesForm, self).__init__(*args, **kwargs)

        if 'pk_grupo' in kwargs['initial'].keys():

            choices = []
            src = {'disabled':{}}
            entregable = models.Entregables.objects.get(id = kwargs['initial']['pk_entregable'])

            for docente in models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo']):
                choices.append((str(docente.id),docente.__str__()))
                src['disabled'][str(docente.id)] = docente.get_disabled_entregable_form(entregable, ['Reportado','Pagado'])

            self.fields['docentes'].widget = SelectWithDisabled(choices=choices,src=src)
            #self.fields['docentes'].queryset = models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo'])

        if 'pk_objeto' in kwargs['initial'].keys():
            self.fields['file'].required = False

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    entregable.nombre,
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12 m6'
                ),
                Column(
                    'tipo',
                    css_class='s12 m6'
                )
            ),
            Row(
                Column(
                    'docentes',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <a id="id_todos" style="display:inline-block;margin-top:10px;" class="waves-effect waves-light btn pink darken-4"><i class="material-icons left">done_all</i>todos</a>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.RepositorioActividades
        fields = ['file','docentes','fecha','tipo']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'docentes': SelectWithDisabled(),
            'tipo': forms.Select(choices=[('Sican', 'Sican'), ('Lupaap', 'Lupaap')])
        }
class SistematizacionExperienciaForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())


    def __init__(self, *args, **kwargs):
        super(SistematizacionExperienciaForm, self).__init__(*args, **kwargs)

        if 'pk_grupo' in kwargs['initial'].keys():

            choices = []
            src = {'disabled':{}}
            entregable = models.Entregables.objects.get(id = kwargs['initial']['pk_entregable'])

            for docente in models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo']):
                choices.append((str(docente.id),docente.__str__()))
                src['disabled'][str(docente.id)] = docente.get_disabled_entregable_form(entregable, ['Reportado','Pagado'])

            self.fields['docentes'].widget = SelectWithDisabled(choices=choices,src=src)
            #self.fields['docentes'].queryset = models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo'])

        if 'pk_objeto' in kwargs['initial'].keys():
            self.fields['file'].required = False

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    entregable.nombre,
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'docentes',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <a id="id_todos" style="display:inline-block;margin-top:10px;" class="waves-effect waves-light btn pink darken-4"><i class="material-icons left">done_all</i>todos</a>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.SistematizacionExperiencia
        fields = ['file','docentes','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'docentes': SelectWithDisabled()
        }
class InstrumentoEvaluacionForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(InstrumentoEvaluacionForm, self).__init__(*args, **kwargs)

        if 'pk_grupo' in kwargs['initial'].keys():

            choices = []
            src = {'disabled':{}}
            entregable = models.Entregables.objects.get(id = kwargs['initial']['pk_entregable'])

            for docente in models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo']):
                choices.append((str(docente.id),docente.__str__()))
                src['disabled'][str(docente.id)] = docente.get_disabled_entregable_form(entregable, ['Reportado','Pagado'])

            self.fields['docentes'].widget = SelectWithDisabled(choices=choices,src=src)
            #self.fields['docentes'].queryset = models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo'])

        if 'pk_objeto' in kwargs['initial'].keys():
            self.fields['file'].required = False

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    entregable.nombre,
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'docentes',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <a id="id_todos" style="display:inline-block;margin-top:10px;" class="waves-effect waves-light btn pink darken-4"><i class="material-icons left">done_all</i>todos</a>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.InstrumentoEvaluacion
        fields = ['file','docentes','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'docentes': SelectWithDisabled()
        }
class InstrumentoEstructuracionPleForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(InstrumentoEstructuracionPleForm, self).__init__(*args, **kwargs)

        if 'pk_grupo' in kwargs['initial'].keys():

            choices = []
            src = {'disabled':{}}
            entregable = models.Entregables.objects.get(id = kwargs['initial']['pk_entregable'])

            for docente in models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo']):
                choices.append((str(docente.id),docente.__str__()))
                src['disabled'][str(docente.id)] = docente.get_disabled_entregable_form(entregable, ['Reportado','Pagado'])

            self.fields['docentes'].widget = SelectWithDisabled(choices=choices,src=src)
            #self.fields['docentes'].queryset = models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo'])

        if 'pk_objeto' in kwargs['initial'].keys():
            self.fields['file'].required = False

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    entregable.nombre,
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'docentes',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <a id="id_todos" style="display:inline-block;margin-top:10px;" class="waves-effect waves-light btn pink darken-4"><i class="material-icons left">done_all</i>todos</a>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.InstrumentoEstructuracionPle
        fields = ['file','docentes','fecha']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'docentes': SelectWithDisabled()
        }
class ProductoFinalPleForm(forms.ModelForm):

    delta = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(ProductoFinalPleForm, self).__init__(*args, **kwargs)

        if 'pk_grupo' in kwargs['initial'].keys():

            choices = []
            src = {'disabled':{}}
            entregable = models.Entregables.objects.get(id = kwargs['initial']['pk_entregable'])

            for docente in models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo']):
                choices.append((str(docente.id),docente.__str__()))
                src['disabled'][str(docente.id)] = docente.get_disabled_entregable_form(entregable, ['Reportado','Pagado'])

            self.fields['docentes'].widget = SelectWithDisabled(choices=choices,src=src)
            #self.fields['docentes'].queryset = models.Docentes.objects.filter(grupo__id = kwargs['initial']['pk_grupo'])

        if 'pk_objeto' in kwargs['initial'].keys():
            self.fields['file'].required = False

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    entregable.nombre,
                )
            ),
            Row(
                Column(
                    'fecha',
                    css_class='s12 m6'
                ),
                Column(
                    'tipo',
                    css_class='s12 m6'
                )
            ),
            Row(
                Column(
                    'docentes',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <a id="id_todos" style="display:inline-block;margin-top:10px;" class="waves-effect waves-light btn pink darken-4"><i class="material-icons left">done_all</i>todos</a>
                        """
                    ),
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;margin-right: 10px;"><b>Actualmente:</b>{{ file_url | safe }}</p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),

            Row(
                Fieldset(
                    'Observación',
                )
            ),

            Row(
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
                    'delta',
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
        model = models.ProductoFinalPle
        fields = ['file','docentes','fecha','tipo']
        labels = {

        }
        widgets = {
            'file': forms.FileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'image/jpg,'
                          'image/jpeg,'
                          'image/png,'
                          'application/pdf,'
                          'application/vnd.ms-excel,'
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                          'application/x-rar-compressed,'
                          'application/octet-stream,'
                          'application/zip,'
                          'application/octet-stream,'
                          'application/x-zip-compressed,'
                          'multipart/x-zip,'
                          'application/msword,'
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document,'
                          'application/vnd.ms-powerpoint,'
                          'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            }),
            'docentes': SelectWithDisabled(),
            'tipo': forms.Select(choices=[('Sican', 'Sican'), ('Lupaap', 'Lupaap')])
        }

#----------------------------------------------------------------------------------

class GenerarLiquidacionForm(forms.Form):
    valores = forms.CharField(widget=forms.HiddenInput())
    valores_inicial = forms.CharField(widget=forms.HiddenInput())
    mes = forms.MultipleChoiceField(choices=[
        ('Enero','Enero'),
        ('Febrero', 'Febrero'),
        ('Marzo', 'Marzo'),
        ('Abril', 'Abril'),
        ('Mayo', 'Mayo'),
        ('Junio', 'Junio'),
        ('Julio', 'Julio'),
        ('Agosto', 'Agosto'),
        ('Septiembre', 'Septiembre'),
        ('Octubre', 'Octubre'),
        ('Noviembre', 'Noviembre'),
        ('Diciembre', 'Diciembre')
    ])
    year = forms.ChoiceField(label='Año')
    anticipo = forms.CharField(label='Descuento anticipo')
    descuentos = forms.CharField(label='Otros descuentos')


    def clean(self):
        cleaned_data = super().clean()
        cuenta_cobro = models.CuentasCobro.objects.get(id = self.initial['pk_cuenta_cobro'])
        valores_meses_json = json.loads(cleaned_data['valores'])
        valor_total = 0

        if len(valores_meses_json) > 1:

            for valor_mes in valores_meses_json:
                valor = valor_mes.get('valor')
                if valor == None or valor == '':
                    pass
                else:
                    valor_total += float(valor.replace('$ ','').replace(',',''))

            if round(valor_total) != round(cuenta_cobro.ruta.get_valor_liquidacion()):
                self.add_error('mes', 'No coinciden los valores')




    def __init__(self, *args, **kwargs):
        super(GenerarLiquidacionForm, self).__init__(*args, **kwargs)

        cuenta_cobro = models.CuentasCobro.objects.get(id=kwargs['initial']['pk_cuenta_cobro'])
        fecha = timezone.now()
        year = fecha.strftime('%Y')
        year_1 = str(int(year)-1)
        mes = fecha.strftime('%B').capitalize()

        self.fields['valores_inicial'].initial = cuenta_cobro.valores_json
        self.fields['year'].choices = [(year_1, year_1), (year, year)]

        self.fields['anticipo'].initial = '0'
        self.fields['descuentos'].initial = '0'

        if cuenta_cobro.data_json == '' or cuenta_cobro.data_json == None:
            self.fields['mes'].initial = mes
        else:
            self.fields['mes'].initial = json.loads(cuenta_cobro.data_json)['mes']
            self.fields['year'].initial = json.loads(cuenta_cobro.data_json)['year']

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Liquidación de contrato',
                )
            ),
            Row(
                HTML(
                    """
                    <div class="col s12">{{ cuentas| safe }}</div>
                    """
                )
            ),
            Row(
                HTML(
                    """
                    <div class="col s12 m6"><p><b>Valor:</b> {{valor}}</p></div>
                    <div class="col s12 m6"><p><b>Contratista:</b> {{contratista}}</p></div>
                    <div class="col s12 m6"><p><b>Contrato:</b> {{contrato}}</p></div>
                    <div class="col s12 m6"><p><b>Inicio:</b> {{inicio}}</p></div>
                    <div class="col s12 m6"><p><b>Fin:</b> {{fin}}</p></div>
                    """
                )
            ),
            Row(),
            Row(
                Column(
                    'mes',
                    css_class="s12 m6"
                ),
                Column(
                    'year',
                    css_class="s12 m6"
                ),
                Column(
                    HTML(
                        """
                        <div id="container_meses"></div>
                        """
                    ),
                    css_class="s12"
                ),
            ),
            Row(
                Column(
                    'anticipo',
                    css_class="s12 m6"
                ),
                Column(
                    'descuentos',
                    css_class="s12 m6"
                )
            ),
            Row(
                Column(
                    'valores',
                    'valores_inicial',
                    css_class = 's12'
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