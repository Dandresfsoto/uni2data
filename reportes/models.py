from django.db import models
import uuid
from usuarios.models import User
from django.conf import settings
from pytz import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings
import os

settings_time_zone = timezone(settings.TIME_ZONE)

# Create your models here.


def upload_dinamic_dir_reporte(instance, filename):
    return '/'.join(['Informes', str(instance.usuario.id), str(instance.id), filename])


class Reportes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    consecutivo = models.IntegerField()
    creation = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, related_name="usuario_creacion_reportes", on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=1000)
    file = models.FileField(upload_to=upload_dinamic_dir_reporte,blank=True,null=True)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

@receiver(pre_save, sender=Reportes)
def PagoUpdate(sender, instance, **kwargs):
    path = settings.MEDIA_ROOT + '/' +'/'.join(['Informes', str(instance.usuario.id), str(instance.id)])
    if not os.path.exists(path):
        os.makedirs(path)
        x = 0