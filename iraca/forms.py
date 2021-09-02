from django import forms

from iraca import models
from usuarios.models import Municipios
from django.forms.fields import Field, FileField
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset
from crispy_forms_materialize.layout import Layout, Row, Column, Submit, HTML, Button

