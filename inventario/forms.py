from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset
from crispy_forms_materialize.layout import Layout, Row, Column, Submit, HTML, Button

from inventario import choices
from inventario.models import Productos, CargarProductos, Adiciones, Despachos, Sustracciones

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
        fields = ['codigo','nombre','stock','unidad','impuesto']

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
        cantidad = cleaned_data.get("cantidad")

        q = Q(cargue__id=self.pk) & Q(producto__codigo=codigo)

        adiciones = Adiciones.objects.filter(q)


        if self.pk_adicion != None:

            if adiciones.exclude(id = self.pk_adicion).count() > 0:
                self.add_error('producto', 'Existe un producto registrado para esta reporte.')

        else:
            if adiciones.count() > 0:
                self.add_error('producto', 'Existe un producto registrado para esta reporte.')


        producto = Productos.objects.get(codigo = codigo)



        if cantidad >= producto.cantidad:
            self.add_error('producto', 'No existen suficientes productos, revisar el inventario')
            self.add_error('cantidad', 'No existen suficientes productos, revisar el inventario')

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

class DespachoForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super().clean()

        nombre_cliente = cleaned_data.get("nombre_cliente")
        documento = cleaned_data.get("documento")
        direccion = cleaned_data.get("direccion")
        ciudad = cleaned_data.get("ciudad")

        if nombre_cliente == None:
            self.add_error('nombre_cliente', 'Campo requerido')

        if documento == None:
            self.add_error('documento', 'Campo requerido')

        if direccion == None:
            self.add_error('direccion', 'Campo requerido')

        if ciudad == None:
            self.add_error('ciudad', 'Campo requerido')

    def __init__(self, *args, **kwargs):
        super(DespachoForm, self).__init__(*args, **kwargs)


        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Información del cliente',
                )
            ),
            Row(
                Column(
                    'nombre_cliente',
                    css_class="s12"
                ),
            ),
            Row(
                Column(
                    'documento',
                    css_class="s6"
                ),
                Column(
                    'telefono',
                    css_class="s6"
                ),
            ),
            Row(
                Fieldset(
                    'Información del envio',
                )
            ),
            Row(
                Column(
                    'direccion',
                    css_class="s12"
                ),
            ),
            Row(
                Column(
                    'ciudad',
                    css_class="s12"
                ),
            ),
            Row(
                Column(
                    'fecha_envio',
                    css_class="s12"
                ),
            ),
            Row(
                Fieldset(
                    'Información del conductor',
                )
            ),
            Row(
                Column(
                    'transportador',
                    css_class="s12"
                ),
            ),
            Row(
                Column(
                    'conductor',
                    css_class="s6"
                ),
                Column(
                    'placa',
                    css_class="s6"
                ),
            ),
            Row(
                Fieldset(
                    'Observacion y documentos',
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
                        <p style="font-size:1.2rem;"><b>Respaldo</b></p>
                        """
                    ),
                    'respaldo',
                    css_class='s12'
                )
            ),
            Row(
                Column(
                    HTML(
                        """
                        <p style="font-size:1.2rem;"><b>Legalizacion</b></p>
                        """
                    ),
                    'legalizacion',
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
        model = Despachos
        fields = ['nombre_cliente','documento','telefono','direccion','ciudad','fecha_envio','respaldo','legalizacion',
                  'transportador','conductor','placa','observacion']
        widgets = {
            'observacion': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        }

class SustraccionForm(forms.ModelForm):
    producto = forms.CharField(max_length=100,label='Producto',widget=forms.TextInput(attrs={'class':'autocomplete','autocomplete':'off'}))
    codigo = forms.CharField(label="ID producto",widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()

        codigo = cleaned_data.get("codigo")

        q = Q(despacho__id=self.pk) & Q(producto__codigo=codigo)

        sustracciones = Sustracciones.objects.filter(q)


        if self.pk_sustracion != None:

            if sustracciones.exclude(id = self.pk_sustracion).count() > 0:
                self.add_error('producto', 'Existe un producto registrado para esta reporte.')

        else:
            if sustracciones.count() > 0:
                self.add_error('producto', 'Existe un producto registrado para esta reporte.')



    def __init__(self, *args, **kwargs):
        super(SustraccionForm, self).__init__(*args, **kwargs)

        self.pk = kwargs['initial'].get('pk')
        self.pk_sustracion = kwargs['initial'].get('pk_sustracion')

        pk_sustracion = kwargs['initial'].get('pk_sustracion')
        if pk_sustracion != None:
            sustraccion = Sustracciones.objects.get(id=pk_sustracion)
            self.fields['producto'].initial = str(sustraccion.producto.codigo) + ' - ' + str(sustraccion.producto.nombre)
            self.fields['observacion'].initial = sustraccion.observacion
            self.fields['cantidad'].initial = sustraccion.cantidad
            self.fields['codigo'].initial = sustraccion.producto.codigo

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
        model = Sustracciones
        fields = ['observacion','cantidad']
        widgets = {
            'observacion': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        }