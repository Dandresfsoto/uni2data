from django.db import models
import uuid
from djmoney.models.fields import MoneyField
from usuarios.models import Departamentos, User, Municipios
from django.conf import settings
from pytz import timezone


settings_time_zone = timezone(settings.TIME_ZONE)

# Create your models here.
def upload_dinamic_images(instance, filename):
    return '/'.join(['Ofertas', str(instance.id), 'Imagen', filename])

class Ofertas(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    cargo = models.CharField(max_length=100)
    perfil = models.CharField(max_length=1000)
    experiencia = models.CharField(max_length=1000)
    tipo_contrato = models.CharField(max_length=100)
    honorarios = MoneyField(max_digits=10, decimal_places=2, default_currency='COP',default=0)
    departamentos = models.ManyToManyField(Departamentos,related_name='departamentos_ofertas',blank=True)
    municipios = models.ManyToManyField(Municipios, related_name='municipios_ofertas', blank=True)
    vacantes = models.IntegerField()
    estado = models.BooleanField(default=True)

    def get_aplicaciones_count(self):
        return AplicacionOferta.objects.filter(oferta = self).count()

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def get_aplicacion(self, user):

        response = ''
        aplicacion = None

        try:
            aplicacion = AplicacionOferta.objects.get(usuario = user, oferta = self)
        except:
            pass

        if aplicacion != None:
            response = 'Aplicaste a la oferta el {0}'.format(aplicacion.pretty_creation_datetime())

        return response

    def get_departamentos_string(self):
        string = ''

        for departamento in self.departamentos.all():
            string += departamento.nombre + ', '

        return string[:-2]

    def get_municipios_string(self):
        string = ''

        for municipio in self.municipios.all():
            string += municipio.nombre + ', '

        return string[:-2]


    def pretty_print_valor(self):
        return str(self.honorarios).replace('COL','')

    def __str__(self):
        return self.cargo

class AplicacionOferta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    oferta = models.ForeignKey(Ofertas,on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    departamentos = models.ManyToManyField(Departamentos, related_name='departamentos_aplicacion', blank=True)
    municipios = models.ManyToManyField(Municipios, related_name='municipios_aplicacion', blank=True)
    observacion = models.CharField(max_length=500,blank=True,null=True)

    cualificacion_perfil = models.CharField(max_length=100,blank=True,null=True)
    cualificacion_experiencia = models.CharField(max_length=100, blank=True, null=True)
    cualificacion_seleccion = models.CharField(max_length=100, blank=True, null=True)
    cualificacion_observacion = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def get_departamentos_string(self):
        string = ''

        for departamento in self.departamentos.all():
            string += departamento.nombre + ', '

        return string[:-2]

    def get_municipios_string(self):
        string = ''

        for municipio in self.municipios.all():
            string += municipio.nombre + ', '

        return string[:-2]