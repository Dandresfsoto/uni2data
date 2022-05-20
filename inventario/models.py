import uuid

from pytz import timezone
from django.conf import settings

from django.db import models
from djmoney.models.fields import MoneyField

from usuarios.models import Municipios

settings_time_zone = timezone(settings.TIME_ZONE)

def upload_dinamic_dir_repaldo(instance, filename):
    return '/'.join(['Cargue productos', str(instance.id), 'Respaldo', filename])

class Proyectos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=150, verbose_name='Nombre',blank=True, null=True)

    def __str__(self):
        return str(self.nombre)

class Productos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    codigo = models.CharField(unique=True, max_length=150, verbose_name='Codigo')
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    valor = MoneyField(max_digits=20, decimal_places=2, default_currency='COP', verbose_name="Valor de venta")
    valor_compra = MoneyField(max_digits=20, decimal_places=2, default_currency='COP', blank=True, null=True, verbose_name="Valor de compra")
    stock = models.IntegerField(default=0, verbose_name='Cantidad')
    unidad = models.CharField(max_length=150, verbose_name='Unidad de medida', blank=True, null=True)
    impuesto = models.IntegerField(default=19, verbose_name='IVA', blank=True, null=True)
    descripcion = models.TextField(verbose_name='Descripcion', blank=True, null=True)
    marca = models.CharField(max_length=150, verbose_name='Marca', blank=True, null=True)

    def __str__(self):
        return str(self.codigo + " - " + self.nombre)

    def pretty_print_precio(self):
        precio = self.valor
        return str(precio).replace('COL','')

    def pretty_print_precio_compra(self):
        precio = self.valor_compra
        return str(precio).replace('COL','')

    def get_marca(self):
        if self.marca:
            return str(self.marca)
        else:
            return ""

class CargarProductos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    consecutivo = models.IntegerField(default=0, verbose_name='Consecutivo')
    creacion = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(verbose_name='Observacion', blank=True, null=True)
    estado = models.CharField(default="Cargando", max_length=150, verbose_name='estado', blank=True, null=True)

    respaldo = models.FileField(upload_to=upload_dinamic_dir_repaldo, verbose_name='Respaldo',blank=True, null=True)

    def __str__(self):
        return str(str(self.consecutivo) + " - " + str(self.observacion))

    def pretty_creation_datetime(self):
        return self.creacion.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def url_respaldo(self):
        url = None
        try:
            url = self.respaldo.url
        except:
            pass
        return url

    def pretty_print_respaldo(self):
        try:
            url = self.respaldo.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.respaldo.name) +'</a>'

class Adiciones(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    cargue = models.ForeignKey(CargarProductos, on_delete=models.DO_NOTHING, verbose_name="Cargue")
    producto = models.ForeignKey(Productos, on_delete=models.DO_NOTHING, verbose_name="Producto")
    cantidad = models.IntegerField(verbose_name='Cantidad')
    observacion = models.TextField(verbose_name='Observacion', blank=True, null=True)
    creacion = models.DateTimeField(auto_now_add=True,blank=True, null=True)


    def __str__(self):
        return str(str(self.cargue.consecutivo) + " - " + str(self.producto.codigo) + " - " + str(self.producto.nombre))

class Clientes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=150, verbose_name='Nombre del cliente', blank=True, null=True)
    apellido = models.CharField(max_length=150, verbose_name='Apellido del cliente', blank=True, null=True)
    ciudad = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING, verbose_name="Municipio", blank=True, null=True)
    tipo_documento = models.IntegerField(verbose_name='Tipo de documento', blank=True, null=True)
    documento = models.IntegerField(unique=True, verbose_name='Documento', blank=True, null=True)
    direccion = models.CharField(max_length=150, verbose_name='Direccion', blank=True, null=True)
    telefono = models.BigIntegerField(verbose_name='Telefono', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return str(self.documento) + " - " + str(self.nombre) + " " + str(self.apellido)

    def get_nombre_completo(self):
        return str(self.nombre + " " + self.apellido)

    def get_tipo_documento(self):
        tipo = ''

        if self.tipo_documento == 1:
            tipo = 'Nit'

        if self.tipo_documento == 2:
            tipo = 'Cédula de Ciudadania'

        if self.tipo_documento == 3:
            tipo = 'Tarjeta de Identidad'

        if self.tipo_documento == 4:
            tipo = 'Cédula de Extranjeria'

        if self.tipo_documento == 5:
            tipo = 'Pasaporte'

        if self.tipo_documento == 6:
            tipo = 'Tajeta Seguro Social'

        if self.tipo_documento == 7:
            tipo = 'Nit Menores'

        return tipo

class Despachos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    consecutivo = models.IntegerField(default=0, verbose_name='Consecutivo')
    creacion = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Clientes, on_delete=models.DO_NOTHING, verbose_name="Cliente")
    fecha_envio = models.DateField(verbose_name='Fecha de envio', blank=True, null=True)
    transportador = models.CharField(verbose_name='Transportadora', max_length=150, blank=True, null=True)
    conductor = models.CharField(verbose_name='Conductor', max_length=150, blank=True, null=True)
    placa = models.CharField(verbose_name='Placa', max_length=150, blank=True, null=True)
    observacion = models.TextField(verbose_name='Observacion', blank=True, null=True)
    estado = models.CharField(default="Cargando", max_length=150, verbose_name='Estado', blank=True, null=True)

    respaldo = models.FileField(upload_to=upload_dinamic_dir_repaldo, verbose_name='Respaldo',blank=True, null=True)
    legalizacion = models.FileField(upload_to=upload_dinamic_dir_repaldo, verbose_name='Legalizacion',blank=True, null=True)
    remision = models.FileField(upload_to=upload_dinamic_dir_repaldo, verbose_name='Remision',blank=True, null=True)

    visible = models.BooleanField(default=False)
    proyectos = models.ForeignKey(Proyectos, on_delete=models.DO_NOTHING, verbose_name="Proyectos", blank=True,null=True)

    def __str__(self):
        return str(str(self.consecutivo) + " - " + str(self.observacion))

    def get_info_cliente(self):
        return str(str(self.cliente.documento) + " - " + str(self.cliente.nombre))

    def get_info_destino(self):
        return str(str(self.cliente.direccion) + " - " + str(self.cliente.ciudad.nombre) + "/" + str(self.cliente.ciudad.departamento.nombre))

    def pretty_creation_datetime(self):
        return self.creacion.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def pretty_fecha_envio_datetime(self):
        return self.creacion.astimezone(settings_time_zone).strftime('%d/%m/%Y')

    def url_respaldo(self):
        url = None
        try:
            url = self.respaldo.url
        except:
            pass
        return url

    def pretty_print_respaldo(self):
        try:
            url = self.respaldo.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.respaldo.name) +'</a>'

    def url_legalizacion(self):
        url = None
        try:
            url = self.legalizacion.url
        except:
            pass
        return url

    def pretty_print_legalizacion(self):
        try:
            url = self.respaldo.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.legalizacion.name) +'</a>'

    def url_remision(self):
        url = None
        try:
            url = self.remision.url
        except:
            pass
        return url

    def pretty_print_remision(self):
        try:
            url = self.remision.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.remision.name) +'</a>'

    def get_proyect(self):
        if self.proyectos:
            return str(self.proyectos.nombre)
        else:
            return ""


class Sustracciones(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    despacho = models.ForeignKey(Despachos, on_delete=models.DO_NOTHING, verbose_name="Cargue")
    producto = models.ForeignKey(Productos, on_delete=models.DO_NOTHING, verbose_name="Producto")
    cantidad = models.IntegerField(verbose_name='Cantidad')
    observacion = models.TextField(verbose_name='Observacion', blank=True, null=True)
    valor_total = MoneyField(max_digits=20, decimal_places=2, default_currency='COP')
    creacion = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return str(str(self.despacho.consecutivo) + " - " + str(self.producto.codigo) + " - " + str(self.producto.nombre))

    def pretty_print_valor_total(self):
        valor_total = self.valor_total
        return str(valor_total).replace('COL','')
