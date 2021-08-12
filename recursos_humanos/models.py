from djmoney.models.fields import MoneyField
from django.db import models
import uuid
from phonenumber_field.modelfields import PhoneNumberField
from usuarios.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from config.extrafields import ContentTypeRestrictedFileField, PDFFileField
from direccion_financiera.models import Bancos
from django.conf import settings
from django.utils import timezone
from pytz import timezone as timezone_pyzt
from recursos_humanos import tasks
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import Permission, Group
from direccion_financiera.models import Proyecto
from usuarios.models import Municipios

settings_time_zone = timezone_pyzt(settings.TIME_ZONE)
# Create your models here.

def upload_dinamic_dir_carga_masiva_contratos(instance, filename):
    return '/'.join(['Carga Masiva Contratos', filename])

class CargaMasivaContratos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)
    file = models.FileField(upload_to=upload_dinamic_dir_carga_masiva_contratos, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Cargos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Contratistas(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion", on_delete=models.DO_NOTHING)
    update = models.DateTimeField(auto_now=True)
    usuario_actualizacion = models.ForeignKey(User, related_name="usuario_actualizacion", on_delete=models.DO_NOTHING, blank=True, null=True)

    tipo_identificacion = models.IntegerField(default=2)
    cedula = models.BigIntegerField(unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)

    celular = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(blank=True,null=True)
    birthday = models.DateField(blank=True, null=True)

    tipo_cuenta = models.CharField(max_length=50, blank=True, null=True)
    banco = models.ForeignKey(Bancos, blank=True, null=True, on_delete=models.DO_NOTHING)
    cuenta = models.CharField(max_length=100, blank=True, null=True)
    cargo = models.ForeignKey(Cargos, on_delete=models.DO_NOTHING, blank=True, null=True)

    usuario_asociado = models.ForeignKey(User, related_name="usuario_asociado", on_delete=models.DO_NOTHING, blank=True, null=True)


    def __str__(self):
        return '{0} {1} - {2}'.format(self.nombres,self.apellidos,str(self.cedula))

    def get_cedula(self):
        return str(self.cedula)

    def get_celular(self):
        celular = ''

        try:
            celular = str(self.usuario_asociado.celular)
        except:
            pass

        return celular


    def get_lugar_expedicion(self):
        expedicion = ''

        if self.usuario_asociado != None:
            usuario = self.usuario_asociado

            if usuario.lugar_expedicion != None:
                expedicion = usuario.lugar_expedicion.nombre

        else:
            pass

        return expedicion



    def get_lugar_residencia(self):
        residencia = ''

        if self.usuario_asociado != None:
            usuario = self.usuario_asociado

            if usuario.lugar_residencia != None:
                departamento = usuario.lugar_residencia.departamento.nombre
                municipio = usuario.lugar_residencia.nombre

                residencia = '{0}, {1}'.format(municipio,departamento)

        else:
            pass

        return residencia




    def get_full_name(self):
        return self.nombres + ' ' + self.apellidos

    def get_full_name_cedula(self):
        return self.nombres + ' ' + self.apellidos + ' - C.C. ' + str(self.cedula)

    def get_years_pagos(self):
        from direccion_financiera.models import Pagos

        years = {}

        for pago in Pagos.objects.filter(tercero=self):
            if pago.creation.year not in years.keys():
                years[pago.creation.year] = []
            if pago.creation.month not in years[pago.creation.year]:
                years[pago.creation.year].append(pago.creation.month)

        return years

    def get_banco(self):
        banco = ''
        try:
            banco = self.banco.nombre
        except:
            pass
        return banco

    def get_usuario_asociado(self):
        email = ''
        try:
            email = self.usuario_asociado.email
        except:
            pass
        return email

    def get_cargo_nombre(self):
        cargo = ''
        try:
            cargo = self.cargo.nombre
        except:
            pass
        return cargo

    def get_tipo_identificacion(self):
        tipo = ''

        if self.tipo_identificacion == 1:
            tipo = 'Nit'

        if self.tipo_identificacion == 2:
            tipo = 'Cédula de Ciudadania'

        if self.tipo_identificacion == 3:
            tipo = 'Tarjeta de Identidad'

        if self.tipo_identificacion == 4:
            tipo = 'Cédula de Extranjeria'

        if self.tipo_identificacion == 5:
            tipo = 'Pasaporte'

        if self.tipo_identificacion == 6:
            tipo = 'Tajeta Seguro Social'

        if self.tipo_identificacion == 7:
            tipo = 'Nit Menores'

        return tipo

    def get_email(self):
        if self.email == None:
            return ''
        else:
            return self.email

    def fullname(self):
        return self.nombres + " " + self.apellidos

    def get_banco_name(self):
        if self.banco == None:
            nombre = None
        else:
            nombre = self.banco.nombre
        return nombre

def upload_dinamic_dir(instance, filename):
    return '/'.join(['Contratos', 'Minutas',str(instance.nombre), filename])

def upload_dinamic_dir_liquidacion(instance, filename):
    return '/'.join(['Contratos', 'Liquidaciones',str(instance.nombre), filename])

def upload_dinamic_dir_renuncia(instance, filename):
    return '/'.join(['Contratos', 'Renuncias',str(instance.nombre), filename])

class Soportes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    numero = models.IntegerField(unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(max_length=500)
    requerido = models.BooleanField(default=True)
    categoria = models.CharField(max_length=100)

    def __str__(self):
        return '{0}. {1}'.format(self.numero,self.nombre)

class GruposSoportes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=100, unique=True)
    soportes = models.ManyToManyField(Soportes)

    def __str__(self):
        return self.nombre

def upload_dinamic_dir_certificacion_word(instance, filename):
    return '/'.join(['Certificaciones', str(instance.codigo), filename])

def upload_dinamic_dir_certificacion_pdf(instance, filename):
    return '/'.join(['Certificaciones', str(instance.codigo), filename])

class Certificaciones(models.Model):
    contratista = models.ForeignKey(Contratistas,on_delete=models.DO_NOTHING)
    firma = models.CharField(max_length=100)

    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_certificacion", on_delete=models.DO_NOTHING)
    update = models.DateTimeField(auto_now=True)
    usuario_actualizacion = models.ForeignKey(User, related_name="usuario_actualizacion_certificacion", on_delete=models.DO_NOTHING,
                                              blank=True, null=True)

    codigo = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    pdf = models.FileField(upload_to=upload_dinamic_dir_certificacion_pdf, blank=True, null=True)
    html = models.FileField(upload_to=upload_dinamic_dir_certificacion_pdf, blank=True, null=True)
    html_template = models.FileField(upload_to=upload_dinamic_dir_certificacion_pdf, blank=True, null=True)
    delta = models.CharField(max_length=1000000)

    def url_pdf(self):
        url = None
        try:
            url = self.pdf.url
        except:
            pass
        return url

    def pretty_update_datetime(self):
        return self.update.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

class Contratos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length=30,unique=True)
    contratista = models.ForeignKey(Contratistas, on_delete=models.DO_NOTHING)

    creation = models.DateTimeField(auto_now_add=True)

    inicio = models.DateField()
    fin = models.DateField()

    objeto_contrato = models.TextField(max_length=1000)
    tipo_contrato = models.CharField(max_length=100)

    grupo_soportes = models.ForeignKey(GruposSoportes, on_delete=models.DO_NOTHING)

    valor = MoneyField(max_digits=20,decimal_places=2,default_currency = 'COP')

    file = PDFFileField(upload_to=upload_dinamic_dir,
                        max_upload_size=20971520,
                        blank=True, null=True
    )

    soporte_liquidacion = models.FileField(
        upload_to=upload_dinamic_dir_liquidacion,
        blank=True, null=True
    )

    soporte_renuncia = models.FileField(
        upload_to=upload_dinamic_dir_renuncia,
        blank=True, null=True
    )

    suscrito = models.BooleanField(default=False)
    ejecucion = models.BooleanField(default=False)
    ejecutado = models.BooleanField(default=False)
    liquidado = models.BooleanField(default=False)
    estado = models.CharField(max_length=100,blank=True,null=True)
    fecha_legalizacion = models.DateField(blank=True,null=True)
    proyecto = models.ForeignKey(Proyecto,on_delete=models.DO_NOTHING,blank=True,null=True)
    cargo = models.ForeignKey(Cargos, on_delete=models.DO_NOTHING, blank=True, null=True)
    fecha_liquidacion = models.DateField(blank=True,null=True)
    fecha_renuncia = models.DateField(blank=True, null=True)
    visible = models.BooleanField(default=True)

    otro_si_1 = PDFFileField(upload_to=upload_dinamic_dir,
                        max_upload_size=20971520,
                        blank=True, null=True
                        )

    otro_si_2 = PDFFileField(upload_to=upload_dinamic_dir,
                             max_upload_size=20971520,
                             blank=True, null=True
                             )

    otro_si_3 = PDFFileField(upload_to=upload_dinamic_dir,
                             max_upload_size=20971520,
                             blank=True, null=True
                             )

    def __str__(self):
        return 'Contrato:{0} - Valor: {1}'.format(
            self.nombre,
            self.pretty_print_valor()
        )

    def get_autocomplete_text(self):
        return '{0} - {1} - {2}'.format(
            self.contratista.get_full_name_cedula(),
            self.nombre,
            self.pretty_print_valor()
        )

    def rest_contratista(self):
        return '{0} - Contratista: {1}'.format(
            self.nombre,
            self.contratista.get_full_name_cedula()
        )



    def get_estado_contrato(self):
        estado = ''

        if self.fecha_liquidacion != None and self.fecha_liquidacion != '':
            estado = 'Contrato liquidado'

        if self.fecha_renuncia != None and self.fecha_renuncia != '':
            estado = 'Renuncia de contratista'

        return estado

    def get_cargo(self):
        cargo = ''
        try:
            cargo = self.cargo.nombre
        except:
            pass
        return cargo

    def get_proyecto(self):
        proyecto = ''
        try:
            proyecto = self.proyecto.nombre
        except:
            pass
        return proyecto

    def get_tipo_sangre(self):
        tipo_sangre = ''
        try:
            user = self.contratista.usuario_asociado
        except:
            pass
        else:
            try:
                tipo_sangre = user.tipo_sangre
            except:
                pass
        return tipo_sangre

    def get_fecha_nacimiento(self):
        fecha_nacimiento = ''
        try:
            user = self.contratista.usuario_asociado
        except:
            pass
        else:
            try:
                fecha_nacimiento = user.birthday
            except:
                pass
        return fecha_nacimiento


    def get_email(self):
        email = ''
        try:
            user = self.contratista.usuario_asociado
        except:
            pass
        else:
            try:
                email = user.email
            except:
                pass
        return email


    def get_direccion(self):
        direccion = ''
        try:
            user = self.contratista.usuario_asociado
        except:
            pass
        else:
            try:
                direccion = user.direccion
            except:
                pass
        return direccion


    def get_user_or_none(self):
        try:
            user = self.contratista.usuario_asociado
        except:
            user = None
        return user

    def cantidad_soportes(self):
        cantidad = SoportesContratos.objects.filter(contrato = self).exclude(file = '').count()
        return cantidad

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


    def url_soporte_liquidacion(self):
        url = None
        try:
            url = self.soporte_liquidacion.url
        except:
            pass
        return url


    def url_soporte_renuncia(self):
        url = None
        try:
            url = self.soporte_renuncia.url
        except:
            pass
        return url


    def pretty_print_inicio(self):
        return self.inicio.strftime('%d de %B del %Y')

    def pretty_print_fin(self):
        return self.fin.strftime('%d de %B del %Y')

    def pretty_print_valor(self):
        return str(self.valor).replace('COL','')

    def pretty_print_url_minuta(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'


    def pretty_print_url_liquidacion(self):
        try:
            url = self.soporte_liquidacion.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.soporte_liquidacion.name) +'</a>'


    def pretty_print_url_renuncia(self):
        try:
            url = self.soporte_renuncia.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.soporte_renuncia.name) +'</a>'



    def pretty_print_url_otrosi_1(self):
        try:
            url = self.otrosi_1.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.otrosi_1.name) +'</a>'


    def pretty_print_url_otrosi_2(self):
        try:
            url = self.otrosi_2.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.otrosi_2.name) +'</a>'


    def pretty_print_url_otrosi_3(self):
        try:
            url = self.otrosi_3.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.otrosi_3.name) +'</a>'



def upload_dinamic_dir_soporte_contrato(instance, filename):
    return '/'.join(['Contratos', 'Soportes', str(instance.contrato.id), str(instance.soporte.id), filename])


class SoportesContratos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    codigo = models.IntegerField(blank=True,null=True)
    soporte = models.ForeignKey(Soportes, on_delete=models.DO_NOTHING)
    numero = models.IntegerField(blank=True,null=True)
    contrato = models.ForeignKey(Contratos, on_delete=models.DO_NOTHING)
    file = models.FileField(upload_to=upload_dinamic_dir_soporte_contrato,blank=True,null=True, max_length=255)
    estado = models.CharField(max_length=100,blank=True,null=True)
    observacion = models.CharField(max_length=500, blank=True, null=True)


    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'

@receiver(post_save, sender=Contratistas)
def ContratistasPostSave(sender, instance, **kwargs):
    cedula = instance.cedula

    try:
        user = User.objects.get(cedula=cedula)
    except:
        Contratistas.objects.filter(id = instance.id).update(usuario_asociado = None)
    else:
        Contratistas.objects.filter(id=instance.id).update(usuario_asociado = user)

@receiver(post_save, sender=Contratos)
def ContratosPostSave(sender, instance, **kwargs):
    for soporte in instance.grupo_soportes.soportes.all():
        try:
            p, created = SoportesContratos.objects.get_or_create(soporte = soporte, contrato = instance)
        except:
            pass

@receiver(post_save, sender=SoportesContratos)
def SoportesContratosPostSave(sender, instance, **kwargs):
    SoportesContratos.objects.filter(id = instance.id).update(numero = instance.soporte.numero)


def upload_dinamic_dir_hv(instance, filename):
    return '/'.join(['Recursos Humanos', 'Hv', filename])

def upload_dinamic_dir_excel(instance, filename):
    return '/'.join(['Recursos Humanos', 'Hv',str(instance.region),str(instance.cargo),
                     str(instance.consecutivo_cargo).zfill(2) + '. ' + str(instance.contratista.nombres.lower())+ " " +str(instance.contratista.apellidos.lower()), filename])


class CargosHv(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Hv(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    contratista = models.ForeignKey(Contratistas,on_delete=models.DO_NOTHING)
    file = PDFFileField(upload_to=upload_dinamic_dir_hv,
                        max_length=250,
                        max_upload_size=20971520,
                        blank=True, null=True
                        )
    envio = models.IntegerField()
    cargo = models.ForeignKey(CargosHv, blank=True, null=True, on_delete=models.DO_NOTHING)
    municipio = models.ForeignKey(Municipios, blank=True, null=True, on_delete=models.DO_NOTHING)
    estado = models.CharField(max_length=100, default="Esperando aprobación")
    observacion = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.cargo

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def pretty_print_url_file(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name.split('/')[-1]) +'</a>'

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def url_excel(self):
        url = None
        try:
            url = self.excel.url
        except:
            pass
        return url

class TrazabilidadHv(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    hv = models.ForeignKey(Hv, related_name="trazabilidad_hv", on_delete=models.DO_NOTHING)
    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_trazabilidad_hv", on_delete=models.DO_NOTHING)
    observacion = models.CharField(max_length=200)

    def __str__(self):
        return self.hv.contratista.cedula


    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')


@receiver(post_save, sender=SoportesContratos)
def SoportesUpdate(sender, instance, **kwargs):
    contrato = instance.contrato

    soportes_obligatorios = SoportesContratos.objects.filter(contrato=contrato, soporte__requerido=True)
    soportes_opcionales = SoportesContratos.objects.filter(contrato=contrato, soporte__requerido=False)

    if soportes_obligatorios.exclude(estado='Aprobado').count() <= 0:
        contrato.fecha_legalizacion = timezone.now().date()
        contrato.save()

    else:
        contrato.fecha_legalizacion = None
        contrato.save()
