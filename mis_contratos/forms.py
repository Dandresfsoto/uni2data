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