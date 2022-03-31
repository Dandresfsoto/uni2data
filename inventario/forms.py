from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset
from crispy_forms_materialize.layout import Layout, Row, Column, Submit, HTML, Button

from inventario import choices
from inventario.models import Productos, CargarProductos, Adiciones

from django.db.models import Q


class ProductForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

        self.fields['valor_char'] = forms.CharField(label="Valor ($)")

        self.fields['unidad'].widget = forms.Select(choices=choices.UNIDAD)

        pk = kwargs['initial'].get('pk')
        if pk != None:
            producto = Productos.objects.get(id=pk)
            self.fields['codigo'].initial = producto.codigo
            self.fields['nombre'].initial = producto.nombre
            valor=str(producto.valor).replace('COL$','')
            self.fields['valor_char'].initial = valor
            self.fields['stock'].initial = producto.stock
            self.fields['unidad'].initial = producto.unidad
            self.fields['impuesto'].initial = producto.impuesto

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Información del producto',
                )
            ),
            Row(
                Column(
                    'codigo',
                    css_class="s12 m6"
                ),
                Column(
                    'nombre',
                    css_class="s12 m6"
                ),
            ),
            Row(
                Column(
                    'valor_char',
                    css_class="s12 m6"
                ),
                Column(
                    'stock',
                    css_class="s12 m6"
                ),
            ),
            Row(
                Column(
                    'impuesto',
                    css_class="s12 m6"
                ),
                Column(
                    'unidad',
                    css_class="s12 m6"
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
        model = Productos
        fields = ['codigo','nombre','valor','stock','unidad','impuesto']

class CargueProductosForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(CargueProductosForm, self).__init__(*args, **kwargs)


        pk = kwargs['initial'].get('pk')
        if pk != None:
            cargue = CargarProductos.objects.get(id=pk)
            self.fields['observacion'].initial = cargue.observacion
            self.fields['respaldo'].widget = forms.FileInput()

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Información de la orden de cargue',
                )
            ),
            Row(
                Column(
                    'observacion',
                    css_class="s12"
                ),
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
        model = CargarProductos
        fields = ['observacion','respaldo']
        widgets = {
            'observacion': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        }

class AdicionalForm(forms.ModelForm):
    producto = forms.CharField(max_length=100,label='Producto',widget=forms.TextInput(attrs={'class':'autocomplete','autocomplete':'off'}))
    codigo = forms.CharField(label="ID producto",widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()

        codigo = cleaned_data.get("codigo")

        q = Q(cargue__id=self.pk) & Q(producto__codigo=codigo)

        adiciones = Adiciones.objects.filter(q)


        if self.pk_adicion != None:

            if adiciones.exclude(id = self.pk_adicion).count() > 0:
                self.add_error('producto', 'Existe un producto registrado para esta reporte.')

        else:
            if adiciones.count() > 0:
                self.add_error('producto', 'Existe un producto registrado para esta reporte.')

            if Adiciones.objects.filter(cargue__id = self.pk).count() > 19:
                self.add_error('producto', 'Por reporte solo se permiten 20 productos.')



    def __init__(self, *args, **kwargs):
        super(AdicionalForm, self).__init__(*args, **kwargs)

        self.pk = kwargs['initial'].get('pk')
        self.pk_adicion = kwargs['initial'].get('pk_adicion')

        pk_adicion = kwargs['initial'].get('pk_adicion')
        if pk_adicion != None:
            adicion = Adiciones.objects.get(id=pk_adicion)
            self.fields['producto'].initial = str(adicion.producto.codigo) + ' - ' + str(adicion.producto.nombre)
            self.fields['observacion'].initial = adicion.observacion
            self.fields['cantidad'].initial = adicion.cantidad
            self.fields['codigo'].initial = adicion.producto.codigo

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Información del producto',
                )
            ),
            Row(
                Column(
                    'producto',
                    css_class="s12"
                ),
            ),
            Row(
                Column(
                    'codigo',
                    css_class="s6"
                ),
            ),
            Row(
                Column(
                    'cantidad',
                    css_class="s6"
                ),
            ),
            Row(
                Column(
                    'observacion',
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
        model = Adiciones
        fields = ['observacion','cantidad']
        widgets = {
            'observacion': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        }