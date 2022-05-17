from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset
from crispy_forms_materialize.layout import Layout, Row, Column, Submit, HTML, Button

from inventario import choices
from inventario.models import Productos, CargarProductos, Adiciones, Despachos, Sustracciones, Clientes, Proyectos

from django.db.models import Q


class ProductForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

        self.fields['valor_char'] = forms.CharField(label="Valor de venta($)")
        self.fields['valor_compra_char'] = forms.CharField(label="Valor de compra($)")

        self.fields['unidad'].widget = forms.Select(choices=choices.UNIDAD)

        pk = kwargs['initial'].get('pk')
        if pk != None:
            producto = Productos.objects.get(id=pk)
            self.fields['codigo'].initial = producto.codigo
            self.fields['nombre'].initial = producto.nombre
            valor=str(producto.valor).replace('COL$','')
            valor_compra=str(producto.valor_compra).replace('COL$','')
            self.fields['valor_char'].initial = valor
            self.fields['valor_compra_char'].initial = valor_compra
            self.fields['stock'].initial = producto.stock
            self.fields['unidad'].initial = producto.unidad
            self.fields['impuesto'].initial = producto.impuesto
            self.fields['marca'].initial = producto.marca
            self.fields['descripcion'].initial = producto.descripcion

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
                    'valor_compra_char',
                    css_class="s12 m6"
                ),
            ),
            Row(
                Column(
                    'marca',
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
                    'descripcion',
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
        model = Productos
        fields = ['codigo','nombre','stock','unidad','impuesto','marca','descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        }

class AddProductForm(forms.Form):
    stock = forms.IntegerField(label="Stock")

    def __init__(self, *args, **kwargs):
        super(AddProductForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Agregar stock',
                )
            ),
            Row(
                Column(
                    'stock',
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

class AdicionalPlusForm(forms.Form):

    file = forms.FileField(widget=forms.FileInput(attrs={'accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}))

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")

        if file.name.split('.')[-1] == 'xlsx':
            pass
        else:
            self.add_error('file', 'El archivo cargado no tiene un formato valido')

    def __init__(self, *args, **kwargs):
        super(AdicionalPlusForm, self).__init__(*args, **kwargs)

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

class DespachoForm(forms.ModelForm):

    cliente = forms.CharField(max_length=100,label='Cliente',widget=forms.TextInput(attrs={'class':'autocomplete','autocomplete':'off'}))
    documento = forms.IntegerField(label="Documento",widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(DespachoForm, self).__init__(*args, **kwargs)

        self.pk = kwargs['initial'].get('pk_despacho')

        pk_despacho = kwargs['initial'].get('pk_despacho')
        if pk_despacho != None:
            despacho = Despachos.objects.get(id=pk_despacho)
            self.fields['cliente'].initial = str(despacho.cliente.documento) + ' - ' + str(despacho.cliente.nombre)+ ' ' + str(despacho.cliente.apellido)
            self.fields['documento'].initial = despacho.cliente.documento


        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Información del cliente',
                )
            ),
            Row(
                Column(
                    'cliente',
                    css_class="s12"
                ),
                Column(
                    'documento',
                    css_class="s12"
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
                Fieldset(
                    'Información del proyectos',
                )
            ),
            Row(
                Column(
                    'visible',
                    css_class="s12"
                ),
            ),
            Row(
                Column(
                    'proyectos',
                    css_class='s12',
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
        model = Despachos
        fields = ['fecha_envio','respaldo','legalizacion',
                  'transportador','conductor','placa','observacion', 'visible','proyectos']
        widgets = {
            'observacion': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        }

class SustraccionForm(forms.ModelForm):
    producto = forms.CharField(max_length=100,label='Producto',widget=forms.TextInput(attrs={'class':'autocomplete','autocomplete':'off'}))
    codigo = forms.CharField(label="ID producto",widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()

        codigo = cleaned_data.get("codigo")
        cantidad = cleaned_data.get("cantidad")

        q = Q(despacho__id=self.pk) & Q(producto__codigo=codigo)

        sustracciones = Sustracciones.objects.filter(q)


        if self.pk_sustracion != None:

            if sustracciones.exclude(id = self.pk_sustracion).count() > 0:
                self.add_error('producto', 'Existe un producto registrado para esta reporte.')

        else:
            if sustracciones.count() > 0:
                self.add_error('producto', 'Existe un producto registrado para esta reporte.')

        producto = Productos.objects.get(codigo=codigo)

        if cantidad >= producto.stock:
            self.add_error('producto', 'No existen suficientes productos, revisar el inventario')
            self.add_error('cantidad', 'No existen suficientes productos, revisar el inventario')


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

class ClienteForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(ClienteForm, self).__init__(*args, **kwargs)

        self.fields['tipo_documento'].widget = forms.Select(choices=[
            ('', '----------'),
            ('1', 'Nit'),
            ('2', 'Cédula de Ciudadania'),
            ('3', 'Tarjeta de Identidad'),
            ('4', 'Cédula de Extranjeria'),
            ('5', 'Pasaporte'),
            ('6', 'Tajeta Seguro Social'),
            ('7', 'Nit Menores'),
        ])

        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Información del cliente',
                )
            ),
            Row(
                Column(
                    'nombre',
                    css_class='s12 m6 l3'
                ),
                Column(
                    'apellido',
                    css_class='s12 m6 l3'
                ),
                Column(
                    'tipo_documento',
                    css_class='s12 m6 l3'
                ),
                Column(
                    'documento',
                    css_class='s12 m6 l3'
                ),
            ),
            Row(
                Column(
                    'telefono',
                    css_class='s12 m6'
                ),
                Column(
                    'email',
                    css_class='s12 m6'
                ),
            ),
            Row(
                Fieldset(
                    'Direccion del cliente',
                )
            ),
            Row(
                Column(
                    'ciudad',
                    css_class='s12'
                ),
            ),
            Row(
                Column(
                    'direccion',
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

    class Meta:
        model = Clientes
        fields = ['nombre','apellido','tipo_documento','documento','ciudad','direccion','telefono','email']
        labels = {
            'cedula': 'Documento #',
            'tipo_documento': 'Tipo',
        }

class SustraccionPlusForm(forms.Form):

    file = forms.FileField(widget=forms.FileInput(attrs={'accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}))

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")

        if file.name.split('.')[-1] == 'xlsx':
            pass
        else:
            self.add_error('file', 'El archivo cargado no tiene un formato valido')

    def __init__(self, *args, **kwargs):
        super(SustraccionPlusForm, self).__init__(*args, **kwargs)

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

class ProyectoForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super(ProyectoForm, self).__init__(*args, **kwargs)

        pk = kwargs['initial'].get('pk')
        if pk != None:
            proyecto = Proyectos.objects.get(id=pk)
            self.fields['nombre'].initial = proyecto.nombre


        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Row(
                Fieldset(
                    'Información del proyecto',
                )
            ),
            Row(
                Column(
                    'nombre',
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
        model = Proyectos
        fields = ['nombre']
