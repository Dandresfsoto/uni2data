import uuid

from pytz import timezone
from django.conf import settings

from django.db import models
from djmoney.models.fields import MoneyField

settings_time_zone = timezone(settings.TIME_ZONE)

def upload_dinamic_dir_repaldo(instance, filename):
    return '/'.join(['Cargue productos', str(instance.id), 'Respaldo', filename])

class Productos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    codigo = models.CharField(max_length=150, verbose_name='Codigo')
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    valor = MoneyField(max_digits=20, decimal_places=2, default_currency='COP')
    stock = models.IntegerField(default=0, verbose_name='Cantidad')
    unidad = models.CharField(max_length=150, verbose_name='Unidad de medida', blank=True, null=True)
    impuesto = models.IntegerField(default=19, verbose_name='IVA', blank=True, null=True)

    def __str__(self):
        return str(self.codigo + " - " + self.nombre)

    def pretty_print_precio(self):
        precio = self.valor
        return str(precio).replace('COL','')

class CargarProductos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    consecutivo = models.IntegerField(default=0, verbose_name='Consecutivo')
    creacion = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(verbose_name='Observacion', blank=True, null=True)

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
    cantidad = models.CharField(max_length=150, verbose_name='Cantidad')
    observacion = models.TextField(verbose_name='Observacion', blank=True, null=True)


    def __str__(self):
        return str(str(self.cargue.consecutivo) + " - " + str(self.producto.codigo) + " - " + str(self.producto.nombre))