from django import forms

from iraca import models
from iraca.models import Types
from usuarios.models import Municipios
from django.forms.fields import Field, FileField
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset
from crispy_forms_materialize.layout import Layout, Row, Column, Submit, HTML, Button

class CertificateForm(forms.Form):

    municipality = forms.ModelChoiceField(label='Municipio', queryset=Municipios.objects.none(),
                                         required=False)

    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            if name not in ['municipality']:
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
        municipality = cleaned_data.get("municipality")

        municipality = models.Meetings.objects.filter(municipality = municipality)

        if municipality.count() > 0:
            self.add_error('municipality', 'Ya existe el ente territorial.')

    def __init__(self, *args, **kwargs):
        super(CertificateForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información de la gestión',
                )
            ),
            Row(
                Column(
                    'municipality',
                    css_class='s12'
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

class MiltonesForm(forms.Form):


    type = forms.ModelChoiceField(label='Tipo de hito', queryset=Types.objects.all(),
                                  required=False)

    date = forms.DateField(label = 'Fecha del acta')

    observation = forms.CharField(label="Observación",max_length=500,widget=forms.Textarea(attrs={'class':'materialize-textarea'}),required=False)


    file = forms.FileField(max_length=255,widget= forms.FileInput(attrs={'data-max-file-size': '10M',
                                                                         'accept': 'application/pdf'}))
    file2 = forms.FileField(max_length=255,widget= forms.FileInput(attrs={'data-max-file-size': '10M',
                                                                         'accept': 'application/pdf'}),required=False)
    file3 = forms.FileField(max_length=255,widget= forms.FileInput(attrs={'data-max-file-size': '10M',
                                                                         'accept': 'application/pdf'}),required=False)

    foto_1 = forms.ImageField(max_length=255,required=False,widget= forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                         'accept': 'image/jpg,image/jpeg,image/png'}))
    foto_2 = forms.ImageField(max_length=255, required=False,widget= forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                         'accept': 'image/jpg,image/jpeg,image/png'}))
    foto_3 = forms.ImageField(max_length=255, required=False,widget= forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                         'accept': 'image/jpg,image/jpeg,image/png'}))
    foto_4 = forms.ImageField(max_length=255, required=False,widget= forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                         'accept': 'image/jpg,image/jpeg,image/png'}))

    def __init__(self, *args, **kwargs):
        super(MiltonesForm, self).__init__(*args, **kwargs)

        certificate = models.Certificates.objects.get(id=kwargs['initial']['pk'])

        self.fields['type'].queryset = Types.objects.filter(certificate=certificate)

        if 'pk_milestone' in kwargs['initial'].keys():
            milestone = models.Milestones.objects.get(id=kwargs['initial']['pk_milestone'])

            self.fields['type'].initial = milestone.type
            self.fields['date'].initial = milestone.date
            self.fields['observation'].initial = milestone.observation

            self.fields['file'].required = False
            self.fields['file2'].required = False
            self.fields['file3'].required = False

            if milestone.url_foto_1() != None:
                self.fields['foto_1'].widget.attrs['data-default-file'] = milestone.url_foto_1()

            if milestone.url_foto_2() != None:
                self.fields['foto_2'].widget.attrs['data-default-file'] = milestone.url_foto_2()

            if milestone.url_foto_3() != None:
                self.fields['foto_3'].widget.attrs['data-default-file'] = milestone.url_foto_3()

            if milestone.url_foto_4() != None:
                self.fields['foto_4'].widget.attrs['data-default-file'] = milestone.url_foto_4()

        self.fields['file'].widget = forms.FileInput()
        self.fields['file2'].widget = forms.FileInput()
        self.fields['file3'].widget = forms.FileInput()

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Información del acta:'
                )
            ),
            Row(
                Column(
                    'type',
                    css_class='s12 m6 l6'
                ),
                Column(
                    'date',
                    css_class='s12 m6 l6'
                )
            ),
            Row(
                Fieldset(
                    'Formato del acta'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="font-size:1.2rem;"><b>Formato del acta</b></p>
                        <p style="display:inline;"><b>Actualmente:</b>{{ file_url | safe }}</p>
  
                        """
                    ),
                    'file',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Lista de asistencia'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;"><b>Actualmente:</b>{{ file2_url | safe }}</p>
                        """
                    ),
                    'file2',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Otros'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="display:inline;"><b>Actualmente:</b>{{ file3_url | safe }}</p>
                        """
                    ),
                    'file3',
                    css_class='s12'
                )
            ),
            Row(
                Fieldset(
                    'Registro fotográfico'
                )
            ),
            Row(
                Column(
                    'foto_1',
                    css_class='s12 m6 l3'
                ),
                Column(
                    'foto_2',
                    css_class='s12 m6 l3'
                ),
                Column(
                    'foto_3',
                    css_class='s12 m6 l3'
                ),
                Column(
                    'foto_4',
                    css_class='s12 m6 l3'
                )
            ),
            Row(
                Fieldset(
                    'Observación'
                ),
                Column(
                    'observation',
                    css_class='s12'
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
