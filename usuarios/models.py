#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from config.extrafields import ContentTypeRestrictedFileField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models.signals import post_save
from django.dispatch import receiver
#from channels import Group as ChannelGroup
import json
import uuid
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import Group
from storages.backends.ftp import FTPStorage
from django.conf import settings
from pytz import timezone

settings_time_zone = timezone(settings.TIME_ZONE)

fs = FTPStorage()

class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        try:
            user = self.get(email=email)
        except:
            user = self.create(email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_online', False)
        extra_fields.setdefault('is_verificated', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_online', False)
        extra_fields.setdefault('is_verificated', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')
        if extra_fields.get('is_verificated') is not True:
            raise ValueError('Superuser must have is_verificated=True.')
        return self._create_user(email, password, **extra_fields)

def upload_dinamic_dir(instance, filename):
    return '/'.join(['Cuentas','Avatar',str(instance.id),filename])

def upload_dinamic_dir_hv(instance, filename):
    return '/'.join(['Cuentas','Hv',str(instance.id),filename])

def upload_dinamic_dir_paquete(instance, filename):
    return '/'.join(['Cuentas','Paquetes',str(instance.id),filename])

class Departamentos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ver = models.BooleanField(default=True)
    nombre = models.CharField(max_length=100)
    codigo = models.IntegerField(unique=True)

    def __str__(self):
        return self.nombre

class Municipios(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    ver = models.BooleanField(default=True)
    departamento = models.ForeignKey(Departamentos,on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=100)
    codigo = models.IntegerField(unique=True)
    latitud = models.DecimalField(max_digits=9,decimal_places=6,blank=True,null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6,blank=True,null=True)

    def __str__(self):
        return '{0}, {1}'.format(self.nombre,self.departamento.nombre)

class Corregimientos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    municipio = models.ForeignKey(Municipios,on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=100)
    codigo = models.IntegerField(unique=True)

    def __str__(self):
        return '{0}'.format(self.nombre)

class Veredas(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    municipio = models.ForeignKey(Municipios,on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=100)
    codigo = models.IntegerField(unique=True)

    def __str__(self):
        return '{0}'.format(self.nombre)

class PueblosIndigenas(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class ResguardosIndigenas(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class ComunidadesIndigenas(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class ConsejosAfro(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    codigo = models.IntegerField(unique=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class ComunidadesAfro(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class LenguasNativas(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre



class CategoriaDiscapacidad(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class DificultadesPermanentesDiscapacidad(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class ElementosDiscapacidad(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class TiposRehabilitacionDiscapacidad(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    objects = UserManager()

    #--------------------------------------- datos generales ----------------------------------------------

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    fullname = models.CharField(max_length=100)



    #-------------------------------------------------------------------------------------------------------

    notifications = models.IntegerField(default=0)
    messages = models.IntegerField(default=0)

    #-------------------------------------------------------------------------------------------------------

    photo = ContentTypeRestrictedFileField(upload_to=upload_dinamic_dir, blank=True,
                                           content_types=['image/jpg', 'image/jpeg', 'image/png'],
                                           max_upload_size=1048576)


    cedula = models.BigIntegerField(unique=True, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    celular = PhoneNumberField(blank=True, null=True)
    sexo = models.CharField(max_length=100, blank=True, null=True)
    tipo_sangre = models.CharField(max_length=100, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)

    lugar_nacimiento = models.ForeignKey(Municipios,on_delete=models.DO_NOTHING,blank=True,null=True,related_name='lugar_nacimiento_municipio')
    lugar_expedicion = models.ForeignKey(Municipios,on_delete=models.DO_NOTHING,blank=True,null=True,related_name='lugar_expedicion_municipio')
    lugar_residencia = models.ForeignKey(Municipios,on_delete=models.DO_NOTHING,blank=True,null=True,related_name='lugar_residencia_municipio')

    nivel_educacion_basica = models.CharField(max_length=100, blank= True, null=True)
    grado_educacion_basica = models.CharField(max_length=100, blank= True, null=True)

    hv = ContentTypeRestrictedFileField(upload_to=upload_dinamic_dir_hv, blank=True,
                                           content_types=['application/pdf', 'application/x-pdf'],
                                           max_upload_size=20971520)

    usar_photo_social_login = models.BooleanField(default=True)

    formulario_completo_ofertas = models.BooleanField(default=False)

    # -------------------------------------------------------------------------------------------------------

    last_online = models.DateTimeField(blank=True,null=True)
    recovery_code = models.IntegerField(blank=True,null=True)
    is_online = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verificated = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ['first_name']
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


    def get_nivel_academico(self):

        try:
            niveles = {
                'Técnica': 1,
                'Técnologica': 2,
                'Técnologica especializada': 3,
                'Universitaria': 4,
                'Especialización': 5,
                'Maestria o magíster': 6,
                'Doctorado o PHD': 7
            }

            niveles_inv = {
                1:'Técnica',
                2:'Técnologica',
                3:'Técnologica especializada',
                4:'Universitaria',
                5:'Especialización',
                6:'Maestria o magíster',
                7:'Doctorado o PHD'
            }

            titulos = Titulos.objects.filter(usuario = self).values_list('modalidad',flat=True).distinct()

            t = []
            for titulo in titulos:
                t.append(niveles[titulo])


            return niveles_inv[max(t)]
        except:
            return ''

    def calculate_age(self):
        import datetime
        return int((datetime.datetime.now().date() - self.birthday).days / 365.25)

    def hv_filename(self):
        url = self.url_hv()
        if url != None:
            return url.split('/')[-1]
        else:
            return ''

    def url_hv(self):
        url = None
        try:
            url = self.hv.url
        except:
            pass
        return url

    def url_photo(self):
        url = None
        try:
            url = self.photo.url
        except:
            pass
        return url

    def last_login_natural_time(self):
        return naturaltime(self.last_online)

    def get_full_name(self):
        return self.email

    def get_full_name_string(self):
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' - ' + self.email

class Titulos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='usuario_titulo')
    creation = models.DateTimeField(auto_now_add=True)

    modalidad = models.CharField(max_length=100)
    semestres = models.IntegerField()
    graduado = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    fecha_terminacion = models.DateField()
    numero_tarjeta = models.CharField(max_length=100,blank=True,null=True)
    fecha_expedicion = models.DateField(blank=True,null=True)

    def __str__(self):
        return self.nombre


class Experiencias(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='usuario_experiencia')
    creation = models.DateTimeField(auto_now_add=True)

    nombre_empresa = models.CharField(max_length=100)
    tipo_empresa = models.CharField(max_length=100)
    email_empresa = models.EmailField(max_length=100,blank=True,null=True)
    telefono_empresa = models.CharField(max_length=100,blank=True,null=True)
    cargo = models.CharField(max_length=100)
    dependencia = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100,blank=True,null=True)
    fecha_ingreso = models.DateField()
    fecha_retiro = models.DateField()
    municipio = models.ForeignKey(Municipios,on_delete=models.DO_NOTHING)

    def get_duracion_meses(self):
        return int((self.fecha_retiro - self.fecha_ingreso).days / 30)

    def __str__(self):
        return self.nombre_empresa


class Notifications(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User,related_name="user_notifications",on_delete=models.DO_NOTHING)
    read = models.BooleanField(default=False)
    title = models.CharField(max_length=100)
    short_description = models.CharField(max_length=500)
    body = models.TextField(max_length=2000)
    date = models.DateTimeField(auto_now=True)
    icon = models.CharField(max_length=100)
    color = models.CharField(max_length=100)

class ContentTypeSican(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name = 'sican'

    def __str__(self):
        return self.name

class PaqueteActivacion(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, unique = True, editable = False)
    creation = models.DateTimeField(auto_now_add = True)
    description = models.CharField(max_length=100)
    generados = models.IntegerField()
    usados = models.IntegerField(null=True)
    file = models.FileField(upload_to='Cuentas/Paquetes/',blank=True,null=True,storage=fs)
    permissions = models.ManyToManyField(Group)

    def __str__(self):
        return str(self.id)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

class CodigoActivacion(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, unique = True, editable = False)
    paquete = models.ForeignKey(PaqueteActivacion, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.DO_NOTHING)
    activation_date = models.DateTimeField(blank=True,null=True)
    permissions = models.ManyToManyField(Group)

    def __str__(self):
        return str(self.id)

    def pretty_activation_date_datetime(self):
        return self.activation_date.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

class HojasDeVida(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    actualizacion = models.DateTimeField(auto_now=True)

    sexo = models.CharField(max_length=100)
    nacionalidad = models.CharField(max_length=100)

    municipio_residencia = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)

    educacion_basica = models.CharField(max_length=100)
    educacion_secundaria = models.CharField(max_length=100)
    fecha_grado = models.DateField()

    def __str__(self):
        return str(self.id)



class ConsejosResguardosProyectosIraca(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING, blank=True, null=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class ComunidadesProyectosIraca(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    consejo_resguardo = models.ForeignKey(ConsejosResguardosProyectosIraca,on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre




@receiver(post_save, sender=User)
def UserPostSave(sender, instance, **kwargs):

    titulos = Titulos.objects.filter(usuario=instance)
    experiencias = Experiencias.objects.filter(usuario=instance)

    formulario_completo_ofertas = False

    if titulos.count() > 0 and experiencias.count() > 0:
        if instance.url_hv() != None:
            formulario_completo_ofertas = True

    User.objects.filter(id = instance.id).update(formulario_completo_ofertas = formulario_completo_ofertas)

    from recursos_humanos.models import Contratistas

    try:
        contratista = Contratistas.objects.get(usuario_asociado = instance)
    except:
        Contratistas.objects.filter(cedula = instance.cedula).update(usuario_asociado = instance)
    else:
        if contratista.cedula != instance.cedula:
            contratista.usuario_asociado = None
            contratista.save()

            Contratistas.objects.filter(cedula=instance.cedula).update(usuario_asociado=instance)

@receiver(post_save, sender=Notifications)
def RealtimeNotifications(sender, instance, **kwargs):
    notification = {
        'notifications':[
            {
                'id_notification': str(instance.id),
                'title': instance.title,
                'short_description': instance.short_description,
                'icon_notification': '/static/img/icon-192.png',
                'timeout': 4000,
                'body': instance.body,
                'color': instance.color,
                'icon': instance.icon,
                'date': naturaltime(instance.date).capitalize(),
            }
        ]
    }
    #ChannelGroup(str(instance.user.id)).send({'text':json.dumps(notification)})

@receiver(post_save, sender=PaqueteActivacion)
def PaqueteActivacionPostSave(sender, instance, **kwargs):

    cantidad = 0
    permisos = instance.permissions.all()

    for codigo in CodigoActivacion.objects.filter(paquete = instance).all():

        codigo.permissions.clear()
        codigo.permissions.add(*permisos)

        if codigo.user != None:
            cantidad += 1
            user = codigo.user
            user.groups.clear()
            user.groups.add(*permisos)

    PaqueteActivacion.objects.filter(id = instance.id).update(usados = cantidad)

@receiver(post_save, sender=CodigoActivacion)
def CodigoActivacionPostSave(sender, instance, **kwargs):

    cantidad = 0

    for codigo in CodigoActivacion.objects.filter(paquete = instance.paquete).all():
        if codigo.user != None:
            cantidad += 1

    PaqueteActivacion.objects.filter(id = instance.paquete.id).update(usados = cantidad)