from django import forms

from iraca import models
from iraca.models import Types, Households
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
        certificate = models.Certificates.objects.get(id=self.pk)

        municipality = models.Meetings.objects.filter(municipality = municipality,certificate=certificate )

        if municipality.count() > 0:
            self.add_error('municipality', 'Ya existe el ente territorial.')

    def __init__(self, *args, **kwargs):
        super(CertificateForm, self).__init__(*args, **kwargs)

        pk = kwargs['initial'].get('pk')
        self.pk = pk

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

class ContactForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)

        self.fields['observation'].widget = forms.Textarea(
            attrs={'class': 'materialize-textarea', 'data-length': '500'})

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información del contacto',
                )
            ),
            Row(
                Column(
                    'name',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'surname',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'charge',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Column(
                    'movil',
                    css_class='s12 m6'
                ),
                Column(
                    'email',
                    css_class='s12 m6'
                )
            ),
            Row(
                Column(
                    'reservation',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'community',
                    css_class='s12 m6 l4'
                ),
                Column(
                    'languahe',
                    css_class='s12 m6 l4'
                )
            ),
            Row(
                Column(
                    'observation',
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
        model = models.Contacts
        fields = ['name', 'surname', 'charge', 'movil', 'email', 'reservation', 'community', 'languahe','observation']
        labels = {
            'name': 'Nombres',
            'surname': 'Apellidos',
            'charge': 'Cargo',
            'movil': 'Celular',
            'email': 'Correo electronico',
            'reservation': 'Resguardo',
            'community': 'Comunidad',
            'languahe': 'Lengua',
            'observation': 'Observaciones',
        }

class MiltonesEstateForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        estate = cleaned_data.get("estate")
        observation = cleaned_data.get("observation")

        if estate == 'Rechazado':
            if observation == None or observation == '':
                self.add_error('observation', 'Por favor agrega una observación al rechazo')

    def __init__(self, *args, **kwargs):
        super(MiltonesEstateForm, self).__init__(*args, **kwargs)

        self.fields['observation'].widget = forms.Textarea(
            attrs={'class': 'materialize-textarea', 'data-length': '500'})

        self.fields['estate'].widget = forms.Select(choices=[
            ('','----------'),
            ('Aprobado', 'Aprobado'),
            ('Esperando aprobación', 'Esperando aprobación'),
            ('Rechazado', 'Rechazado')
        ])

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Estado del hito',
                )
            ),
            Row(
                Column(
                    'estate',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    'observation',
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
        model = models.Milestones
        fields = ['estate', 'observation']

class HogarCreateForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(HogarCreateForm, self).__init__(*args, **kwargs)

        self.fields['routes'] = forms.ModelMultipleChoiceField(queryset=models.Routes.objects.all(),required=False)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Información del hogar',
                )
            ),
            Row(
                Column(
                    'document',css_class="s12 m6 l4"
                ),
                Column(
                    'first_name', css_class="s12 m6 l4"
                ),
                Column(
                    'second_name', css_class="s12 m6 l4"
                ),
            ),
            Row(
                Column(
                    'first_surname', css_class="s12 m6 l4"
                ),
                Column(
                    'second_surname', css_class="s12 m6 l4"
                ),
                Column(
                    'birth_date', css_class="s12 m6 l4"
                )
            ),
            Row(
                Column(
                    'municipality_attention', css_class="s12 m6 "
                ),
                Column(
                    'municipality_residence', css_class="s12 m6 "
                ),
            ),
            Row(
                Column(
                    'routes', css_class="s12 m12 "
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
        model = models.Households
        fields = ['document','municipality_attention','first_name','second_name','first_surname','second_surname','birth_date','municipality_residence','routes']
        labels = {
            'document':'Documento',
            'first_name':'Primer nombre',
            'second_name':'Segundo nombre',
            'first_surname':'Primer apellido',
            'second_surname':'Segundo apellido',
            'municipality_attention':'Municipio de atencion',
            'municipality_residence':'Municipio de residencia',
            'birth_date':'Fecha de nacimiento',
            'routes':'Rutas',
        }

class implementationCreateForm(forms.Form):

    name = forms.CharField(label='Nombre de la ruta', max_length=100)
    visible = forms.BooleanField(required=False)

    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            if name not in ['name']:
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
                                models.Routes.objects.get(nombre = value)
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
        super(implementationCreateForm, self).__init__(*args, **kwargs)
        ruta = None

        if 'pk' in kwargs['initial']:
            ruta = models.Routes.objects.get(id = kwargs['initial']['pk'])
            self.fields['name'].initial = ruta.name
            self.fields['visible'].initial = ruta.visible

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información de la ruta:',
                )
            ),
            Row(
                Column(
                    'name',
                    css_class='s12 m12'
                ),
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
