from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset
from crispy_forms_materialize.layout import Layout, Row, Column, Submit, HTML, Button

from inventario import choices
from inventario.models import Productos, CargarProductos


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