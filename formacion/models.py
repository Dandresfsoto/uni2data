from django.db import models
import uuid
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from pytz import timezone
from recursos_humanos.models import Contratistas, Contratos
from djmoney.models.fields import MoneyField
from usuarios.models import User
from storages.backends.ftp import FTPStorage

fs = FTPStorage()

settings_time_zone = timezone(settings.TIME_ZONE)
# Create your models here.

class Regiones(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ver = models.BooleanField(default=True)
    nombre = models.CharField(max_length=100)
    numero = models.IntegerField(unique=True)
    cantidad_departamentos = models.IntegerField(default=0)
    cantidad_municipios = models.IntegerField(default=0)
    cantidad_sedes = models.IntegerField(default=0)
    color = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    def get_cantidad_departamentos(self):
        return Departamentos.objects.filter(region__id = self.id).count()

    def get_cantidad_municipios(self):
        return Municipios.objects.filter(departamento__region__id = self.id).count()

    def get_cantidad_sedes(self):
        return Sedes.objects.filter(municipio__departamento__region__id=self.id).count()

    def get_cantidad_formados(self):
        return DocentesFormados.objects.filter(sede__municipio__departamento__region__id=self.id).count()

class Departamentos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ver = models.BooleanField(default=True)
    region = models.ForeignKey(Regiones, on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=100)
    numero = models.IntegerField(unique=True)
    cantidad_municipios = models.IntegerField(default=0)
    cantidad_sedes = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

    def get_cantidad_municipios(self):
        return Municipios.objects.filter(departamento__id = self.id).count()

    def get_cantidad_sedes(self):
        return Sedes.objects.filter(municipio__departamento__id = self.id).count()

    def get_cantidad_formados(self):
        return DocentesFormados.objects.filter(sede__municipio__departamento__id = self.id).count()

class Municipios(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ver = models.BooleanField(default=True)
    departamento = models.ForeignKey(Departamentos,on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=100)
    numero = models.IntegerField(unique=True)
    cantidad_sedes = models.IntegerField(default=0)
    latitud = models.DecimalField(max_digits=9,decimal_places=6,blank=True,null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6,blank=True,null=True)

    def __str__(self):
        return '{0}, {1}'.format(self.nombre,self.departamento.nombre)

    def get_cantidad_sedes(self):
        return Sedes.objects.filter(municipio__id = self.id).count()

    def get_cantidad_formados(self):
        return DocentesFormados.objects.filter(sede__municipio__id = self.id).count()

class Sedes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ver = models.BooleanField(default=True)
    municipio = models.ForeignKey(Municipios,on_delete=models.DO_NOTHING)


    dane_sede = models.CharField(max_length=100,unique=True)
    nombre_sede = models.CharField(max_length=200)
    dane_ie = models.CharField(max_length=100)
    nombre_ie = models.CharField(max_length=200)

    def get_cantidad_formados(self):
        return DocentesFormados.objects.filter(sede__id = self.id).count()

    def __str__(self):
        return '{0}'.format(str(self.dane_sede))

class DocentesFormados(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)

    sede = models.ForeignKey(Sedes, on_delete=models.DO_NOTHING)

    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula = models.BigIntegerField(unique=True)

    vigencia = models.CharField(max_length=100)
    diplomado = models.CharField(max_length=100)

    def __str__(self):
        return '{0}'.format(self.cedula)

def upload_dinamic_dir_file(instance, filename):
    return '/'.join(['CPE 2018', 'Formación', 'BD', str(instance.id), filename])

class ActualizacionSedes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_db_formacion", on_delete=models.DO_NOTHING)

    file = models.FileField(upload_to=upload_dinamic_dir_file, blank=True, null=True)
    result = models.FileField(upload_to=upload_dinamic_dir_file, blank=True, null=True,storage=fs)
    modificados = models.IntegerField(default=0)
    nuevos = models.IntegerField(default=0)
    rechazados = models.IntegerField(default=0)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def url_result(self):
        url = None
        try:
            url = self.result.url
        except:
            pass
        return url

class ActualizacionDocentes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_db_formacion_docentes", on_delete=models.DO_NOTHING)

    file = models.FileField(upload_to=upload_dinamic_dir_file, blank=True, null=True)
    result = models.FileField(upload_to=upload_dinamic_dir_file, blank=True, null=True,storage=fs)
    modificados = models.IntegerField(default=0)
    nuevos = models.IntegerField(default=0)
    rechazados = models.IntegerField(default=0)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def url_result(self):
        url = None
        try:
            url = self.result.url
        except:
            pass
        return url

class Diplomados(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)
    niveles = models.IntegerField()
    sesiones = models.IntegerField()
    actividades = models.IntegerField()

    def __str__(self):
        return '{0}'.format(self.nombre)

    def get_actividades_count(self):
        return Actividades.objects.filter(sesion__nivel__diplomado=self).count()

    def get_sesiones_count(self):
        return Sesiones.objects.filter(nivel__diplomado=self).count()

    def get_nivel_count(self):
        return Niveles.objects.filter(diplomado=self).count()

class Niveles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    diplomado = models.ForeignKey(Diplomados, on_delete=models.DO_NOTHING, related_name='niveles_diplomado')
    nombre = models.CharField(max_length=100)
    sesiones = models.IntegerField()
    actividades = models.IntegerField()

    def __str__(self):
        return '{0}'.format(self.nombre)

    def get_actividades_count(self):
        return Actividades.objects.filter(sesion__nivel=self).count()

    def get_sesiones_count(self):
        return Sesiones.objects.filter(nivel=self).count()

class Sesiones(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nivel = models.ForeignKey(Niveles, on_delete=models.DO_NOTHING, related_name='niveles_sesiones')
    nombre = models.CharField(max_length=100)
    actividades = models.IntegerField()

    def __str__(self):
        return '{0}'.format(self.nombre)

    def get_actividades_count(self):
        return Actividades.objects.filter(sesion=self).count()

def upload_dinamic_dir_file_actividades(instance, filename):
    return '/'.join([
        'CPE 2018',
        'Formación',
        'Diplomados',
        str(instance.sesion.nivel.diplomado.nombre),
        str(instance.sesion.nivel.nombre),
        str(instance.sesion.nombre),
        str(instance.numero) + '. ' + str(instance.nombre),
        filename
    ])

class Actividades(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    sesion = models.ForeignKey(Sesiones, on_delete=models.DO_NOTHING, related_name='niveles_actividades')
    numero = models.IntegerField()
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)
    file = models.FileField(upload_to=upload_dinamic_dir_file_actividades, blank=True, null=True)

    def __str__(self):
        return '{0}'.format(self.nombre)

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url