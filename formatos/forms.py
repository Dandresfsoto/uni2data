#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from formatos import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset
from crispy_forms_materialize.layout import Layout, Row, Column, Submit, HTML, Button
from recursos_humanos.models import Contratistas
from django.db.models import Q
from django.conf import settings

class Level1Form(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        file = cleaned_data.get("file")
        url = cleaned_data.get("url")
        nivel = cleaned_data.get("nivel")


        if nivel:
            if file != None:
                self.add_error('file', 'Los niveles no aceptan archivos')
            if url != None:
                self.add_error('url', 'Los niveles no aceptan url')

        else:
            if file != None:
                if url != None:
                    self.add_error('url', 'Solo se permite cargar la url o el archivo')

            else:
                if url == None:
                    self.add_error('nombre', 'Debes cargar un archivo o una url')



    def __init__(self, *args, **kwargs):
        super(Level1Form, self).__init__(*args, **kwargs)

        self.fields['nivel'].widget.attrs['class'] = 'filled-in'
        #self.fields['file'].widget = forms.FileInput()

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del nuevo item',
                )
            ),
            Row(
                Column(
                    'nombre',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <p style="display:inline;"><b>Actualmente:</b> {{ url_file | safe }} </p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'url',
                    css_class='s12'
                ),
                Column(
                    'nivel',
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
        model = models.Level1
        fields = ['nombre','file','url','nivel']
        labels = {
            'nivel': 'Es un nuevo nivel?',
            'consecutivo': 'Número'
        }

class Level2Form(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        file = cleaned_data.get("file")
        url = cleaned_data.get("url")
        nivel = cleaned_data.get("nivel")


        if nivel:
            if file != None:
                self.add_error('file', 'Los niveles no aceptan archivos')
            if url != None:
                self.add_error('url', 'Los niveles no aceptan url')

        else:
            if file != None:
                if url != None:
                    self.add_error('url', 'Solo se permite cargar la url o el archivo')

            else:
                if url == None:
                    self.add_error('nombre', 'Debes cargar un archivo o una url')



    def __init__(self, *args, **kwargs):
        super(Level2Form, self).__init__(*args, **kwargs)

        self.fields['nivel'].widget.attrs['class'] = 'filled-in'
        #self.fields['file'].widget = forms.FileInput()

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del nuevo item',
                )
            ),
            Row(
                Column(
                    'nombre',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <p style="display:inline;"><b>Actualmente:</b> {{ url_file | safe }} </p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'url',
                    css_class='s12'
                ),
                Column(
                    'nivel',
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
        model = models.Level2
        fields = ['nombre','file','url','nivel']
        labels = {
            'nivel': 'Es un nuevo nivel?',
            'consecutivo': 'Número'
        }

class Level3Form(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        file = cleaned_data.get("file")
        url = cleaned_data.get("url")
        nivel = cleaned_data.get("nivel")


        if nivel:
            if file != None:
                self.add_error('file', 'Los niveles no aceptan archivos')
            if url != None:
                self.add_error('url', 'Los niveles no aceptan url')

        else:
            if file != None:
                if url != None:
                    self.add_error('url', 'Solo se permite cargar la url o el archivo')

            else:
                if url == None:
                    self.add_error('nombre', 'Debes cargar un archivo o una url')



    def __init__(self, *args, **kwargs):
        super(Level3Form, self).__init__(*args, **kwargs)

        self.fields['nivel'].widget.attrs['class'] = 'filled-in'
        #self.fields['file'].widget = forms.FileInput()

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del nuevo item',
                )
            ),
            Row(
                Column(
                    'nombre',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <p style="display:inline;"><b>Actualmente:</b> {{ url_file | safe }} </p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'url',
                    css_class='s12'
                ),
                Column(
                    'nivel',
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
        model = models.Level3
        fields = ['nombre','file','url','nivel']
        labels = {
            'nivel': 'Es un nuevo nivel?',
            'consecutivo': 'Número'
        }

class Level4Form(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        file = cleaned_data.get("file")
        url = cleaned_data.get("url")
        nivel = cleaned_data.get("nivel")


        if nivel:
            if file != None:
                self.add_error('file', 'Los niveles no aceptan archivos')
            if url != None:
                self.add_error('url', 'Los niveles no aceptan url')

        else:
            if file != None:
                if url != None:
                    self.add_error('url', 'Solo se permite cargar la url o el archivo')

            else:
                if url == None:
                    self.add_error('nombre', 'Debes cargar un archivo o una url')



    def __init__(self, *args, **kwargs):
        super(Level4Form, self).__init__(*args, **kwargs)

        self.fields['nivel'].widget.attrs['class'] = 'filled-in'
        #self.fields['file'].widget = forms.FileInput()

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del nuevo item',
                )
            ),
            Row(
                Column(
                    'nombre',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <p style="display:inline;"><b>Actualmente:</b> {{ url_file | safe }} </p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'url',
                    css_class='s12'
                ),
                Column(
                    'nivel',
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
        model = models.Level4
        fields = ['nombre','file','url','nivel']
        labels = {
            'nivel': 'Es un nuevo nivel?',
            'consecutivo': 'Número'
        }

class Level5Form(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        file = cleaned_data.get("file")
        url = cleaned_data.get("url")
        nivel = cleaned_data.get("nivel")


        if nivel:
            if file != None:
                self.add_error('file', 'Los niveles no aceptan archivos')
            if url != None:
                self.add_error('url', 'Los niveles no aceptan url')

        else:
            if file != None:
                if url != None:
                    self.add_error('url', 'Solo se permite cargar la url o el archivo')

            else:
                if url == None:
                    self.add_error('nombre', 'Debes cargar un archivo o una url')



    def __init__(self, *args, **kwargs):
        super(Level5Form, self).__init__(*args, **kwargs)

        self.fields['nivel'].widget.attrs['class'] = 'filled-in'
        #self.fields['file'].widget = forms.FileInput()

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del nuevo item',
                )
            ),
            Row(
                Column(
                    'nombre',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <p style="display:inline;"><b>Actualmente:</b> {{ url_file | safe }} </p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'url',
                    css_class='s12'
                ),
                Column(
                    'nivel',
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
        model = models.Level5
        fields = ['nombre','file','url','nivel']
        labels = {
            'nivel': 'Es un nuevo nivel?',
            'consecutivo': 'Número'
        }

class Level6Form(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        file = cleaned_data.get("file")
        url = cleaned_data.get("url")
        nivel = cleaned_data.get("nivel")


        if nivel:
            if file != None:
                self.add_error('file', 'Los niveles no aceptan archivos')
            if url != None:
                self.add_error('url', 'Los niveles no aceptan url')

        else:
            if file != None:
                if url != None:
                    self.add_error('url', 'Solo se permite cargar la url o el archivo')

            else:
                if url == None:
                    self.add_error('nombre', 'Debes cargar un archivo o una url')



    def __init__(self, *args, **kwargs):
        super(Level6Form, self).__init__(*args, **kwargs)

        self.fields['nivel'].widget.attrs['class'] = 'filled-in'
        #self.fields['file'].widget = forms.FileInput()

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del nuevo item',
                )
            ),
            Row(
                Column(
                    'nombre',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <p style="display:inline;"><b>Actualmente:</b> {{ url_file | safe }} </p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'url',
                    css_class='s12'
                ),
                Column(
                    'nivel',
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
        model = models.Level6
        fields = ['nombre','file','url','nivel']
        labels = {
            'nivel': 'Es un nuevo nivel?',
            'consecutivo': 'Número'
        }

class Level7Form(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        file = cleaned_data.get("file")
        url = cleaned_data.get("url")
        nivel = cleaned_data.get("nivel")


        if nivel:
            if file != None:
                self.add_error('file', 'Los niveles no aceptan archivos')
            if url != None:
                self.add_error('url', 'Los niveles no aceptan url')

        else:
            if file != None:
                if url != None:
                    self.add_error('url', 'Solo se permite cargar la url o el archivo')

            else:
                if url == None:
                    self.add_error('nombre', 'Debes cargar un archivo o una url')



    def __init__(self, *args, **kwargs):
        super(Level7Form, self).__init__(*args, **kwargs)

        self.fields['nivel'].widget.attrs['class'] = 'filled-in'
        #self.fields['file'].widget = forms.FileInput()

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del nuevo item',
                )
            ),
            Row(
                Column(
                    'nombre',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <p style="display:inline;"><b>Actualmente:</b> {{ url_file | safe }} </p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'url',
                    css_class='s12'
                ),
                Column(
                    'nivel',
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
        model = models.Level7
        fields = ['nombre','file','url','nivel']
        labels = {
            'nivel': 'Es un nuevo nivel?',
            'consecutivo': 'Número'
        }

class Level8Form(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        file = cleaned_data.get("file")
        url = cleaned_data.get("url")

        if file != None:
            if url != None:
                self.add_error('url', 'Solo se permite cargar la url o el archivo')

        else:
            if url == None:
                self.add_error('nombre', 'Debes cargar un archivo o una url')



    def __init__(self, *args, **kwargs):
        super(Level8Form, self).__init__(*args, **kwargs)

        #self.fields['file'].widget = forms.FileInput()

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del nuevo item',
                )
            ),
            Row(
                Column(
                    'nombre',
                    css_class='s12'
                ),
                Column(
                    HTML(
                        """
                        <p style="display:inline;"><b>Actualmente:</b> {{ url_file | safe }} </p>
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'url',
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
        model = models.Level8
        fields = ['nombre','file','url']
        labels = {
            'consecutivo': 'Número'
        }