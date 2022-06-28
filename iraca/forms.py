from django import forms

from iraca import models
from iraca.models import Types, Households, Actas
from recursos_humanos.models import Collects_Account
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


    observation = forms.CharField(label="Observación",max_length=500,widget=forms.Textarea(attrs={'class':'materialize-textarea'}),required=False)


    file = forms.FileField(max_length=255,widget= forms.FileInput(attrs={'data-max-file-size': '10M',
                                                                         'accept': 'application/pdf'}))

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
        meeting = models.Meetings.objects.get(id=kwargs['initial']['pk_meeting'])
        type = models.Milestones.objects.filter(meeting=meeting).values_list("type", flat=True)

        if certificate.name == "ACTAS ARTICULACION":
            self.fields['type'] = forms.ModelChoiceField(queryset=models.Types.objects.filter(name__contains="ARTICULACION").exclude(id__in=type))
        elif certificate.name == "ACTAS REUNION ALCALDIAS":
            self.fields['type'] = forms.ModelChoiceField(queryset=models.Types.objects.filter(name__contains="REUNION ALCALDIAS").exclude(id__in=type))
        else:
            self.fields['type'] = forms.ModelChoiceField(queryset=models.Types.objects.all().exclude(id__in=type))

        if 'pk_milestone' in kwargs['initial'].keys():
            milestone = models.Milestones.objects.get(id=kwargs['initial']['pk_milestone'])

            if certificate.name == "ACTAS ARTICULACION":
                type = models.Milestones.objects.filter(meeting=meeting,name__contains="ARTICULACION").exclude(id=milestone.id).values_list("type",flat=True)
            elif certificate.name == "ACTAS REUNION ALCALDIAS":
                type = models.Milestones.objects.filter(meeting=meeting, name__contains="REUNION ALCALDIAS").exclude(id=milestone.id).values_list("type", flat=True)
            else:
                type = models.Milestones.objects.filter(meeting=meeting).exclude(id=milestone.id).values_list("type", flat=True)

            if certificate.name == "ACTAS ARTICULACION":
                self.fields['type'] = forms.ModelChoiceField(queryset=models.Types.objects.filter(name__contains="ARTICULACION").exclude(id__in=type))
            elif certificate.name == "ACTAS REUNION ALCALDIAS":
                self.fields['type'] = forms.ModelChoiceField(queryset=models.Types.objects.filter(name__contains="REUNION ALCALDIAS").exclude(id__in=type))
            else:
                self.fields['type'] = forms.ModelChoiceField(queryset=models.Types.objects.all().exclude(id__in=type))

            self.fields['type'].initial = milestone.type
            self.fields['observation'].initial = milestone.observation

            self.fields['file'].required = False

            if milestone.url_foto_1() != None:
                self.fields['foto_1'].widget.attrs['data-default-file'] = milestone.url_foto_1()

            if milestone.url_foto_2() != None:
                self.fields['foto_2'].widget.attrs['data-default-file'] = milestone.url_foto_2()

            if milestone.url_foto_3() != None:
                self.fields['foto_3'].widget.attrs['data-default-file'] = milestone.url_foto_3()

            if milestone.url_foto_4() != None:
                self.fields['foto_4'].widget.attrs['data-default-file'] = milestone.url_foto_4()

        self.fields['file'].widget = forms.FileInput()

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
                    css_class='s12'
                ),
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

class MiltonesUnitForm(forms.Form):
    observation = forms.CharField(label="Observación", max_length=500,
                                  widget=forms.Textarea(attrs={'class': 'materialize-textarea'}), required=False)

    file = forms.FileField(max_length=255, widget=forms.FileInput(attrs={'data-max-file-size': '10M',
                                                                         'accept': 'application/pdf'}))

    foto_1 = forms.ImageField(max_length=255, required=False, widget=forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                                            'accept': 'image/jpg,image/jpeg,image/png'}))
    foto_2 = forms.ImageField(max_length=255, required=False, widget=forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                                            'accept': 'image/jpg,image/jpeg,image/png'}))
    foto_3 = forms.ImageField(max_length=255, required=False, widget=forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                                            'accept': 'image/jpg,image/jpeg,image/png'}))
    foto_4 = forms.ImageField(max_length=255, required=False, widget=forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                                            'accept': 'image/jpg,image/jpeg,image/png'}))

    def __init__(self, *args, **kwargs):
        super(MiltonesUnitForm, self).__init__(*args, **kwargs)

        certificate = models.Certificates.objects.get(id=kwargs['initial']['pk'])

        if certificate.code == 4:
            transversal = models.Milestones.objects.all().exclude(transversal__id=None).values_list("transversal", flat=True)

            self.fields['transversal'] = forms.ModelChoiceField(queryset=models.Actas_Individual.objects.filter(type="cnt").exclude(id__in=transversal))

            if 'pk_milestone' in kwargs['initial'].keys():
                milestone = models.Milestones.objects.get(id=kwargs['initial']['pk_milestone'])

                transversal = models.Milestones.objects.all().exclude(transversal__id=None).values_list("transversal",flat=True)

                self.fields['transversal'] = forms.ModelChoiceField(queryset=models.Actas_Individual.objects.filter(type="cnt").exclude(id=milestone.id,id__in=transversal))

                self.fields['transversal'].initial = milestone.transversal
                self.fields['observation'].initial = milestone.observation

                self.fields['file'].required = False

                if milestone.url_foto_1() != None:
                    self.fields['foto_1'].widget.attrs['data-default-file'] = milestone.url_foto_1()

                if milestone.url_foto_2() != None:
                    self.fields['foto_2'].widget.attrs['data-default-file'] = milestone.url_foto_2()

                if milestone.url_foto_3() != None:
                    self.fields['foto_3'].widget.attrs['data-default-file'] = milestone.url_foto_3()

                if milestone.url_foto_4() != None:
                    self.fields['foto_4'].widget.attrs['data-default-file'] = milestone.url_foto_4()

            self.fields['file'].widget = forms.FileInput()

            self.helper = FormHelper(self)
            self.helper.layout = Layout(
                Row(
                    Fieldset(
                        'Información del acta:'
                    )
                ),
                Row(
                    Column(
                        'transversal',
                        css_class='s12'
                    ),
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
        elif certificate.code == 5:
            transversal = models.Milestones.objects.all().exclude(transversal__id=None,).values_list("transversal",
                                                                                                    flat=True)

            self.fields['transversal'] = forms.ModelChoiceField(
                queryset=models.Actas_Individual.objects.filter(type="ctr").exclude(id__in=transversal))

            if 'pk_milestone' in kwargs['initial'].keys():
                milestone = models.Milestones.objects.get(id=kwargs['initial']['pk_milestone'])

                transversal = models.Milestones.objects.all().exclude(transversal__id=None).values_list("transversal",
                                                                                                        flat=True)

                self.fields['transversal'] = forms.ModelChoiceField(
                    queryset=models.Actas_Individual.objects.filter(type="ctr").exclude(id=milestone.id, id__in=transversal))

                self.fields['transversal'].initial = milestone.transversal
                self.fields['observation'].initial = milestone.observation

                self.fields['file'].required = False

                if milestone.url_foto_1() != None:
                    self.fields['foto_1'].widget.attrs['data-default-file'] = milestone.url_foto_1()

                if milestone.url_foto_2() != None:
                    self.fields['foto_2'].widget.attrs['data-default-file'] = milestone.url_foto_2()

                if milestone.url_foto_3() != None:
                    self.fields['foto_3'].widget.attrs['data-default-file'] = milestone.url_foto_3()

                if milestone.url_foto_4() != None:
                    self.fields['foto_4'].widget.attrs['data-default-file'] = milestone.url_foto_4()

            self.fields['file'].widget = forms.FileInput()

            self.helper = FormHelper(self)
            self.helper.layout = Layout(
                Row(
                    Fieldset(
                        'Información del acta:'
                    )
                ),
                Row(
                    Column(
                        'transversal',
                        css_class='s12'
                    ),
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
        elif certificate.code == 6:
            resguard = models.Resguards.objects.get(id=kwargs['initial']['pk_resguard'])
            transversal = models.Milestones.objects.filter(resguard=resguard).exclude(transversal__id=None).values_list("transversal",flat=True)

            self.fields['transversal'] = forms.ModelChoiceField(queryset=models.Actas_Individual.objects.filter(type="css").exclude(id__in=transversal))

            if 'pk_milestone' in kwargs['initial'].keys():
                milestone = models.Milestones.objects.get(id=kwargs['initial']['pk_milestone'])

                transversal = models.Milestones.objects.filter(resguard=resguard).exclude(transversal__id=None).values_list("transversal",
                                                                                                        flat=True)

                self.fields['transversal'] = forms.ModelChoiceField(
                    queryset=models.Actas_Individual.objects.filter(type="css").exclude(id=milestone.id, id__in=transversal))

                self.fields['transversal'].initial = milestone.transversal
                self.fields['observation'].initial = milestone.observation

                self.fields['file'].required = False

                if milestone.url_foto_1() != None:
                    self.fields['foto_1'].widget.attrs['data-default-file'] = milestone.url_foto_1()

                if milestone.url_foto_2() != None:
                    self.fields['foto_2'].widget.attrs['data-default-file'] = milestone.url_foto_2()

                if milestone.url_foto_3() != None:
                    self.fields['foto_3'].widget.attrs['data-default-file'] = milestone.url_foto_3()

                if milestone.url_foto_4() != None:
                    self.fields['foto_4'].widget.attrs['data-default-file'] = milestone.url_foto_4()

            self.fields['file'].widget = forms.FileInput()

            self.helper = FormHelper(self)
            self.helper.layout = Layout(
                Row(
                    Fieldset(
                        'Información del acta:'
                    )
                ),
                Row(
                    Column(
                        'transversal',
                        css_class='s12'
                    ),
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

    resguard = forms.ModelChoiceField(label='Comunidad', queryset=models.Resguards.objects.all())
    name = forms.CharField(label='Nombre de la ruta', max_length=100)
    visible = forms.BooleanField(required=False)
    goal = forms.IntegerField(label="Meta hogares")

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
            self.fields['resguard'].initial = ruta.resguard
            self.fields['name'].initial = ruta.name
            self.fields['visible'].initial = ruta.visible
            self.fields['goal'].initial = ruta.goal

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Información de la ruta:',
                )
            ),
            Row(
                Column(
                    'resguard',
                    css_class='s12 m12'
                ),
            ),
            Row(
                Column(
                    'name',
                    css_class='s12 m4'
                ),
                Column(
                    'goal',
                    css_class='s12 m4'
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

class InstrumentsRejectForm(forms.Form):

    observation = forms.CharField(label="Observacion",widget=forms.Textarea(attrs={'class':'materialize-textarea'}))



    def __init__(self, *args, **kwargs):
        super(InstrumentsRejectForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Observación de rechazo',
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

class ResguardCreateForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(ResguardCreateForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Información del resguardo',
                )
            ),
            Row(
                Column(
                    'name',css_class="s12"
                ),
            ),
            Row(
                Column(
                    'certificate', css_class="s12"
                ),
            ),
            Row(
                Column(
                    'color', css_class="s12"
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
        model = models.Resguards
        fields = ['name','certificate','color']
        labels = {
            'name':'Nombre',
            'certificate':'Municipio',
            'color': 'Color en ingles',
        }

class ComunityForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(ComunityForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Información de la comunidad',
                )
            ),
            Row(
                Column(
                    'name',css_class="s12"
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
        model = models.Comunity
        fields = ['name']
        labels = {
            'name':'Nombre',
        }

class CollectsAccountInformsRejectForm(forms.Form):

    observaciones_inform = forms.CharField(widget=forms.Textarea(attrs={'class':'materialize-textarea'}))



    def __init__(self, *args, **kwargs):
        super(CollectsAccountInformsRejectForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Observación de rechazo',
                )
            ),
            Row(
                Column(
                    'observaciones_inform',
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

class AccountActivityForm(forms.Form):
    contenido = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(AccountActivityForm, self).__init__(*args, **kwargs)

        account = Collects_Account.objects.get(id=kwargs['initial']['pk_collect_account'])

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

class InidividualRouteForm(forms.Form):

    comunity = forms.ModelChoiceField(label='Comunidad', queryset=models.Comunity.objects.all())
    name = forms.CharField(label='Nombre de la ruta', max_length=100)
    visible = forms.BooleanField(required=False)
    goal = forms.IntegerField(label="Meta hogares")

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
        super(InidividualRouteForm, self).__init__(*args, **kwargs)

        self.fields['comunity'] = forms.ModelChoiceField(queryset=models.Comunity.objects.filter(resguard__id=kwargs['initial']['pk_resguardo']))

        if 'pk_ruta' in kwargs['initial']:
            ruta = models.Routes.objects.get(id = kwargs['initial']['pk_ruta'])
            self.fields['comunity'].initial = ruta.comunity
            self.fields['visible'].initial = ruta.visible
            self.fields['goal'].initial = ruta.goal

        self.helper = FormHelper(self)
        self.helper.layout = Layout(


            Row(
                Fieldset(
                    'Información de la ruta:',
                )
            ),
            Row(
                Column(
                    'comunity',
                    css_class='s12 m12'
                ),
            ),
            Row(
                Column(
                    'goal',
                    css_class='s12'
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

class HogarVinculacionMasivoForm(forms.Form):

    file = forms.FileField(widget=forms.FileInput(attrs={'accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}))

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")

        if file.name.split('.')[-1] == 'xlsx':
            pass
        else:
            self.add_error('file', 'El archivo cargado no tiene un formato valido')

    def __init__(self, *args, **kwargs):
        super(HogarVinculacionMasivoForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Archivo XLSX:',
                )
            ),
            Row(
                Column(
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

class ResguardMiltonesForm(forms.Form):


    observation = forms.CharField(label="Observación", max_length=500,
                                  widget=forms.Textarea(attrs={'class': 'materialize-textarea'}), required=False)

    file = forms.FileField(max_length=255, widget=forms.FileInput(attrs={'data-max-file-size': '10M',
                                                                         'accept': 'application/pdf'}))

    foto_1 = forms.ImageField(max_length=255, required=False, widget=forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                                            'accept': 'image/jpg,image/jpeg,image/png'}))
    foto_2 = forms.ImageField(max_length=255, required=False, widget=forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                                            'accept': 'image/jpg,image/jpeg,image/png'}))
    foto_3 = forms.ImageField(max_length=255, required=False, widget=forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                                            'accept': 'image/jpg,image/jpeg,image/png'}))
    foto_4 = forms.ImageField(max_length=255, required=False, widget=forms.FileInput(attrs={'data-max-file-size': '5M',
                                                                                            'accept': 'image/jpg,image/jpeg,image/png'}))

    def __init__(self, *args, **kwargs):
        super(ResguardMiltonesForm, self).__init__(*args, **kwargs)

        certificate = models.Certificates.objects.get(id=kwargs['initial']['pk'])
        resguard= models.Resguards.objects.get(id=kwargs['initial']['pk_resguard'])
        actas = models.Milestones.objects.filter(resguard=resguard).values_list("acta", flat=True)

        self.fields['acta'] = forms.ModelChoiceField(queryset=models.Actas.objects.all().exclude(id__in=actas))

        if 'pk_milestone' in kwargs['initial'].keys():
            milestone = models.Milestones.objects.get(id=kwargs['initial']['pk_milestone'])

            actas = models.Milestones.objects.filter(resguard=resguard).exclude(id=milestone.id).values_list("acta", flat=True)

            self.fields['acta'] = forms.ModelChoiceField(queryset=models.Actas.objects.all().exclude(id__in=actas))

            self.fields['acta'].initial = milestone.acta
            self.fields['observation'].initial = milestone.observation

            self.fields['file'].required = False

            if milestone.url_foto_1() != None:
                self.fields['foto_1'].widget.attrs['data-default-file'] = milestone.url_foto_1()

            if milestone.url_foto_2() != None:
                self.fields['foto_2'].widget.attrs['data-default-file'] = milestone.url_foto_2()

            if milestone.url_foto_3() != None:
                self.fields['foto_3'].widget.attrs['data-default-file'] = milestone.url_foto_3()

            if milestone.url_foto_4() != None:
                self.fields['foto_4'].widget.attrs['data-default-file'] = milestone.url_foto_4()

        self.fields['file'].widget = forms.FileInput()


        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Información del acta:'
                )
            ),
            Row(
                Column(
                    'acta',
                    css_class='s12'
                ),
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

class IndividualRejectForm(forms.Form):

    observation = forms.CharField(widget=forms.Textarea(attrs={'class':'materialize-textarea'}))



    def __init__(self, *args, **kwargs):
        super(IndividualRejectForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Observación de rechazo',
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

class GrupalRejectForm(forms.Form):

    observation = forms.CharField(widget=forms.Textarea(attrs={'class':'materialize-textarea'}))



    def __init__(self, *args, **kwargs):
        super(GrupalRejectForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Observación de rechazo',
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

class TransversalRejectForm(forms.Form):

    observation = forms.CharField(widget=forms.Textarea(attrs={'class':'materialize-textarea'}))

    def __init__(self, *args, **kwargs):
        super(TransversalRejectForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(

            Row(
                Fieldset(
                    'Observación de rechazo',
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

#----------------------------------------------------------------------------------

#---------------------------- FORMS OBJECTS  -------------------------------------

class DocumentoForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")

        if file.name.split('.')[-1] == 'pdf' or file.name.split('.')[-1] == 'PDF':
            pass
        else:
            self.add_error('file', 'El archivo cargado no tiene un formato valido')


    def __init__(self, *args, **kwargs):
        super(DocumentoForm, self).__init__(*args, **kwargs)


        instrument = models.Instruments.objects.get(id = kwargs['initial']['pk_instrument'])



        if instrument.level == 'ruta':


            self.helper = FormHelper(self)
            self.helper.layout = Layout(

                Row(
                    Fieldset(
                        kwargs['initial'].get('short_name'),
                    )
                ),
                Row(
                    Column(
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

        elif instrument.level == 'individual':
            self.fields['households'] = forms.ModelChoiceField(label = "Hogar",queryset = models.Households.objects.filter(routes=kwargs['initial']['pk']))

            if 'pk_instrument_object' in kwargs['initial']:

                instrument_object = models.ObjectRouteInstrument.objects.get(id = kwargs['initial']['pk_instrument_object'])

                try:
                    self.fields['households'].initial = instrument_object.households.all()[0]
                except:
                    pass

            self.helper = FormHelper(self)
            self.helper.layout = Layout(

                Row(
                    Fieldset(
                        kwargs['initial'].get('short_name'),
                    )
                ),
                Row(
                    Column(
                        'file',
                        css_class='s12'
                    )
                ),
                Row(
                    Column(
                        'households',
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

        else:
            self.fields['households'] = forms.ModelMultipleChoiceField(queryset=models.Households.objects.filter(routes=kwargs['initial']['pk']))

            if 'pk_instrument_object' in kwargs['initial']:
                instrument_object = models.ObjectRouteInstrument.objects.get(id=kwargs['initial']['pk_instrument_object'])

                self.fields['households'].initial = instrument_object.households.all()

            self.helper = FormHelper(self)
            self.helper.layout = Layout(

                Row(
                    Fieldset(
                        kwargs['initial'].get('short_name'),
                    )
                ),
                Row(
                    Column(
                        'file',
                        css_class='s12'
                    )
                ),
                Row(
                    Column(
                        'households',
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
        model = models.Documento
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'data-max-file-size': "10M",
                'accept': 'application/pdf,application/x-pdf'}
            ),
        }

class DocumentoHogarForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")

        if file.name.split('.')[-1] == 'pdf' or file.name.split('.')[-1] == 'PDF':
            pass
        else:
            self.add_error('file', 'El archivo cargado no tiene un formato valido')


    def __init__(self, *args, **kwargs):
        super(DocumentoHogarForm, self).__init__(*args, **kwargs)


        instrument = models.Instruments.objects.get(id = kwargs['initial']['pk_instrument'])



        if instrument.level == 'ruta':


            self.helper = FormHelper(self)
            self.helper.layout = Layout(

                Row(
                    Fieldset(
                        kwargs['initial'].get('short_name'),
                    )
                ),
                Row(
                    Column(
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

        elif instrument.level == 'individual':


            self.helper = FormHelper(self)
            self.helper.layout = Layout(

                Row(
                    Fieldset(
                        kwargs['initial'].get('short_name'),
                    )
                ),
                Row(
                    Column(
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

        else:
            self.fields['households'] = forms.ModelMultipleChoiceField(queryset=models.Households.objects.filter(routes=kwargs['initial']['pk']))

            if 'pk_instrument_object' in kwargs['initial']:
                instrument_object = models.ObjectRouteInstrument.objects.get(id=kwargs['initial']['pk_instrument_object'])

                self.fields['households'].initial = instrument_object.households.all()

            self.helper = FormHelper(self)
            self.helper.layout = Layout(

                Row(
                    Fieldset(
                        kwargs['initial'].get('short_name'),
                    )
                ),
                Row(
                    Column(
                        'file',
                        css_class='s12'
                    )
                ),
                Row(
                    Column(
                        'households',
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
        model = models.Documento
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'data-max-file-size': "50M",
                'accept': 'application/pdf,application/x-pdf'}
            ),
        }

