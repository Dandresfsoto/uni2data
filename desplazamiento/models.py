from django.db import models
import uuid
from usuarios.models import User
from djmoney.models.fields import MoneyField
from django.conf import settings
from pytz import timezone
from djmoney.models.fields import MoneyField
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


settings_time_zone = timezone(settings.TIME_ZONE)
# Create your models here.

def upload_dinamic_dir_file(instance, filename):
    return '/'.join(['Acceso - CPE', 'Desplazamiento', str(instance.usuario_creacion.id), filename])

class Solicitudes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    consecutivo = models.IntegerField()
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_solicitud_desplazamiento",
                                         on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=100)
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='COP', default=0)
    estado = models.CharField(max_length=500)
    file = models.FileField(max_length=255,upload_to=upload_dinamic_dir_file, blank=True, null=True)
    file2 = models.FileField(max_length=255, upload_to=upload_dinamic_dir_file, blank=True, null=True)
    actualizacion = models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return self.nombre

    def pretty_print_url_file2(self):
        try:
            url = self.file2.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file2.name) +'</a>'

    def get_contratista(self):
        from recursos_humanos.models import Contratistas
        try:
            contratista = Contratistas.objects.get(usuario_asociado = self.usuario_creacion).get_full_name()
        except:
            contratista = self.usuario_creacion.get_full_name_string()
        return contratista

    def get_contratista_cedula(self):
        from recursos_humanos.models import Contratistas
        try:
            contratista = Contratistas.objects.get(usuario_asociado = self.usuario_creacion).cedula
        except:
            contratista = self.usuario_creacion.cedula
        return contratista

    def get_cantidad_desplazamientos(self):
        return Desplazamiento.objects.filter(solicitud = self).count()

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def pretty_actualizacion_datetime(self):
        if self.actualizacion != None:
            return self.actualizacion.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')
        else:
            return ''

    def pretty_print_valor(self):
        return str(self.valor).replace('COL','')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def url_file2(self):
        url = None
        try:
            url = self.file2.url
        except:
            pass
        return url

class Desplazamiento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    solicitud = models.ForeignKey(Solicitudes, on_delete=models.DO_NOTHING)
    creation = models.DateTimeField(auto_now_add=True)

    fecha = models.DateField()
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)

    tipo_transporte = models.CharField(max_length=100)
    transportador = models.CharField(max_length=100)
    telefono = models.CharField(max_length=100)

    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='COP')
    observaciones = models.TextField(blank=True,null=True)
    estado = models.CharField(max_length=100,blank=True,null=True)
    verificado = models.BooleanField(default=False)

    valor_original = MoneyField(max_digits=10, decimal_places=2, default_currency='COP')

    def __str__(self):
        return self.pretty_print_valor()

    def get_name(self):
        return 'De {0} a {1}'.format(self.origen, self.destino)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def pretty_print_valor(self):
        return str(self.valor).replace('COL','')

    def pretty_print_valor_original(self):
        return str(self.valor_original).replace('COL','')



@receiver(post_save, sender=Desplazamiento)
def ReportesUpdate(sender, instance, **kwargs):
    solicitud = instance.solicitud
    valor = 0

    for desplazamiento in Desplazamiento.objects.filter(solicitud = solicitud):
        valor += desplazamiento.valor.amount

    solicitud.valor = valor
    solicitud.save()

@receiver(post_delete, sender=Desplazamiento)
def ReportesDelete(sender, instance, **kwargs):
    solicitud = instance.solicitud
    valor = 0

    for desplazamiento in Desplazamiento.objects.filter(solicitud = solicitud):
        valor += desplazamiento.valor.amount

    solicitud.valor = valor
    solicitud.save()