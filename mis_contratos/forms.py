#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from recursos_humanos.models import Contratistas, Contratos, Soportes, GruposSoportes, SoportesContratos, \
    Certificaciones, Collects_Account
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset
from crispy_forms_materialize.layout import Layout, Row, Column, Submit, HTML, Hidden
from recursos_humanos import functions
import json
from bs4 import BeautifulSoup
from delta import html

class SoportesContratosForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(SoportesContratosForm, self).__init__(*args, **kwargs)

        contrato = Contratos.objects.get(id = kwargs['initial']['pk_soporte'])

        self.fields['file'].widget = forms.FileInput()


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
        fields = ['file']

class SegurityUploadForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(SegurityUploadForm, self).__init__(*args, **kwargs)

        collec_account = Collects_Account.objects.get(id = kwargs['initial']['pk_accounts'])

        self.fields['file5'].widget = forms.FileInput()


        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Cargar seguridad social',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b> {{ file5_url | safe }} </p>
                                """
                            ),
                            'file5',
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
        model = Collects_Account
        fields = ['file5']

class AccountUploadForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(AccountUploadForm, self).__init__(*args, **kwargs)

        collec_account = Collects_Account.objects.get(id = kwargs['initial']['pk_accounts'])
        values = float(collec_account.value_transport)

        self.fields['file3'].widget = forms.FileInput()
        self.fields['file4'].widget = forms.FileInput()

        if values > 0:
            self.helper = FormHelper(self)
            self.helper.layout = Layout(

                Row(
                    Fieldset(
                        'Cargar cuentas de honorarios',
                    )
                ),
                Row(
                    Column(
                        Row(
                            Column(
                                HTML(
                                    """
                                    <p style="display:inline;"><b>Actualmente:</b> {{ file3_url | safe }} </p>
                                    """
                                ),
                                'file3',
                                css_class='s12'
                            )
                        ),
                        css_class="s12"
                    ),
                ),
                Row(
                    Fieldset(
                        'Cargar cuentas de transporte',
                    )
                ),
                Row(
                    Column(
                        Row(
                            Column(
                                HTML(
                                    """
                                    <p style="display:inline;"><b>Actualmente:</b> {{ file4_url | safe }} </p>
                                    """
                                ),
                                'file4',
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
        else:
            self.helper = FormHelper(self)
            self.helper.layout = Layout(

                Row(
                    Fieldset(
                        'Cargar cuentas de honorarios',
                    )
                ),
                Row(
                    Column(
                        Row(
                            Column(
                                HTML(
                                    """
                                    <p style="display:inline;"><b>Actualmente:</b> {{ file3_url | safe }} </p>
                                    """
                                ),
                                'file3',
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
        model = Collects_Account
        fields = ['file3','file4']

class AccountActivityForm(forms.Form):
    contenido = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(AccountActivityForm, self).__init__(*args, **kwargs)

        account = Collects_Account.objects.get(id=kwargs['initial']['pk_accounts'])

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Actividades realizadas durante el mes',
                )
            ),
            Row(
                Column(
                    Row(
                        HTML(
                            """
                            <div id="contenido" style="min-height:300px;"></div>
                            """
                        ),
                        css_class='s12'
                    )
                ),
                Column(
                    Row(
                        Column(
                            'contenido',
                            css_class='s12'
                        ),
                    ),
                    css_class="s12"
                ),
            ),
            Row(
                HTML(
                    """
                    <p style="display:inline; color:red"><b>Despues de presionar guardar, debe descargar, firmar y cargar el documento generado por el sistema</b></p>
                    """
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

class AccountUpdateActivityForm(forms.Form):
    contenido = forms.CharField(widget=forms.HiddenInput())
    inicial = forms.CharField(widget=forms.HiddenInput())



    def __init__(self, *args, **kwargs):
        super(AccountUpdateActivityForm, self).__init__(*args, **kwargs)

        account = Collects_Account.objects.get(id=kwargs['initial']['pk_accounts'])

        self.fields['inicial'].initial = account.delta

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Actividades realizadas durante el mes',
                )
            ),
            Row(
                Column(
                    Row(
                        HTML(
                            """
                            <div id="contenido" style="min-height:300px;"></div>
                            """
                        ),
                        css_class='s12'
                    )
                ),
                Column(
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
                    css_class="s12"
                ),
            ),

            Row(
                HTML(
                    """
                    <p style="display:inline; color:red"><b>Despues de presionar guardar, debe descargar, firmar y cargar el documento generado por el sistema</b></p>
                    """
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

class AccountUploadInformForm(forms.ModelForm):
    foto1 = forms.FileField(widget=forms.FileInput(attrs={'accept': 'image/jpg,image/jpeg,image/png'}))
    foto2 = forms.FileField(widget=forms.FileInput(attrs={'accept': 'image/jpg,image/jpeg,image/png'}))
    foto3 = forms.FileField(widget=forms.FileInput(attrs={'accept': 'image/jpg,image/jpeg,image/png'}), required=False)
    foto4 = forms.FileField(widget=forms.FileInput(attrs={'accept': 'image/jpg,image/jpeg,image/png'}), required=False)


    def clean(self):
        cleaned_data = super().clean()
        foto1 = cleaned_data.get("foto1")
        foto2 = cleaned_data.get("foto2")
        foto3 = cleaned_data.get("foto3")
        foto4 = cleaned_data.get("foto4")

        if foto1 != None:
            if foto1.name.split('.')[-1] in ['jpg', 'jpeg', 'png']:
                pass
            else:
                self.add_error('foto1', 'El archivo cargado no tiene un formato valido')

        if foto2 != None:
            if foto2.name.split('.')[-1] in ['jpg', 'jpeg', 'png']:
                pass
            else:
                self.add_error('foto2', 'El archivo cargado no tiene un formato valido')

        if foto3 != None:
            if foto3.name.split('.')[-1] in ['jpg', 'jpeg', 'png']:
                pass
            else:
                self.add_error('foto3', 'El archivo cargado no tiene un formato valido')

        if foto4 != None:
            if foto4.name.split('.')[-1] in ['jpg', 'jpeg', 'png']:
                pass
            else:
                self.add_error('foto4', 'El archivo cargado no tiene un formato valido')



    def __init__(self, *args, **kwargs):
        super(AccountUploadInformForm, self).__init__(*args, **kwargs)

        collec_account = Collects_Account.objects.get(id = kwargs['initial']['pk_accounts'])
        values = float(collec_account.value_transport)

        self.fields['file4'].widget = forms.FileInput()

        if collec_account.url_foto1() != None:
            self.fields['foto1'].widget.attrs['data-default-file'] = collec_account.url_foto1()

        if collec_account.url_foto2() != None:
            self.fields['foto2'].widget.attrs['data-default-file'] = collec_account.url_foto2()

        if collec_account.url_foto3() != None:
            self.fields['foto3'].widget.attrs['data-default-file'] = collec_account.url_foto3()

        if collec_account.url_foto4() != None:
            self.fields['foto4'].widget.attrs['data-default-file'] = collec_account.url_foto4()



        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Cargar informe de actividades firmado',
                )
            ),
            Row(
                Column(
                    Row(
                        Column(
                            HTML(
                                """
                                <p style="display:inline;"><b>Actualmente:</b> {{ file4_url | safe }} </p>
                                """
                            ),
                            'file4',
                            css_class='s12'
                        )
                    ),
                    css_class="s12"
                ),
            ),
            Row(
                Column(
                    'foto1',
                    css_class='s12 m6'
                ),
                Column(
                    'foto2',
                    css_class='s12 m6'
                ),
                Column(
                    'foto3',
                    css_class='s12 m6'
                ),
                Column(
                    'foto4',
                    css_class='s12 m6'
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
        model = Collects_Account
        fields = ['file4','foto1','foto2','foto3','foto4']



