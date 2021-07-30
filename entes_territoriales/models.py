from django.db import models
import uuid
from usuarios.models import Municipios, User
from django.conf import settings
from pytz import timezone
from phonenumber_field.modelfields import PhoneNumberField
from cpe_2018.models import Departamentos as DepartamentosCpe2018

settings_time_zone = timezone(settings.TIME_ZONE)

# Create your models here.
class Reuniones(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)

    creation = models.DateTimeField(auto_now_add=True)
    usuario_creacion = models.ForeignKey(User, related_name="usuario_creacion_reunion", on_delete=models.DO_NOTHING)
    update_datetime = models.DateTimeField(auto_now=True)
    usuario_actualizacion = models.ForeignKey(User, related_name="usuario_actualizacion_reunion",
                                              on_delete=models.DO_NOTHING,
                                              blank=True, null=True)

    municipio = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING)
    region = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return str(self.id)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

    def get_region(self):
        codigo = self.municipio.departamento.codigo

        return DepartamentosCpe2018.objects.get(numero = codigo).region.nombre

def upload_dinamic_hito(instance, filename):
    return '/'.join(['Reuniones', 'Entes territoriales', str(instance.reunion.municipio.departamento.nombre),
                     str(instance.reunion.municipio.nombre), 'Hitos', filename])

class Hito(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    reunion = models.ForeignKey(Reuniones, on_delete=models.DO_NOTHING)
    tipo = models.CharField(max_length=100)
    fecha = models.DateField()
    estado = models.CharField(max_length=100,default='Esperando aprobación')
    observacion = models.CharField(max_length=500, blank=True, null=True)
    file = models.FileField(upload_to=upload_dinamic_hito, blank=True, null=True, max_length=255)
    file2 = models.FileField(upload_to=upload_dinamic_hito, blank=True, null=True, max_length=255)
    file3 = models.FileField(upload_to=upload_dinamic_hito, blank=True, null=True, max_length=255)
    foto_1 = models.FileField(upload_to=upload_dinamic_hito, blank=True, null=True, max_length=255)
    foto_2 = models.FileField(upload_to=upload_dinamic_hito, blank=True, null=True, max_length=255)
    foto_3 = models.FileField(upload_to=upload_dinamic_hito, blank=True, null=True, max_length=255)
    foto_4 = models.FileField(upload_to=upload_dinamic_hito, blank=True, null=True, max_length=255)

    def __str__(self):
        return self.tipo

    def get_fotos(self):
        fotos = []

        if self.foto_1 != '':
            fotos.append(self.foto_1.url)

        if self.foto_2 != '':
            fotos.append(self.foto_2.url)

        if self.foto_3 != '':
            fotos.append(self.foto_3.url)

        if self.foto_4 != '':
            fotos.append(self.foto_4.url)


        return fotos

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def get_extension(self):
        return str(self.file.path).split('.')[-1]


    def get_extension2(self):
        return str(self.file2.path).split('.')[-1]


    def get_extension3(self):
        return str(self.file3.path).split('.')[-1]


    def get_region(self):
        codigo = self.reunion.municipio.departamento.codigo

        return DepartamentosCpe2018.objects.get(numero = codigo).region.nombre

    def url_foto_1(self):
        url = None
        try:
            url = self.foto_1.url
        except:
            pass
        return url

    def url_foto_2(self):
        url = None
        try:
            url = self.foto_2.url
        except:
            pass
        return url

    def url_foto_3(self):
        url = None
        try:
            url = self.foto_3.url
        except:
            pass
        return url

    def url_foto_4(self):
        url = None
        try:
            url = self.foto_4.url
        except:
            pass
        return url

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

    def url_file3(self):
        url = None
        try:
            url = self.file3.url
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

    def pretty_print_url_file2(self):
        try:
            url = self.file2.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file2.name) +'</a>'

    def pretty_print_url_file3(self):
        try:
            url = self.file3.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file3.name) +'</a>'

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



class Contactos(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    reunion = models.ForeignKey(Reuniones,on_delete=models.DO_NOTHING)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cargo = models.CharField(max_length=200)
    celular = PhoneNumberField()
    email = models.EmailField(max_length=100,blank=True,null=True)
    resguardo = models.CharField(max_length=100)
    comunidad = models.CharField(max_length=100)
    lenguas = models.CharField(max_length=100, null=True, blank=True)
    observaciones = models.TextField(max_length=500,blank=True,null=True)





    def __str__(self):
        return self.nombres



class Registro(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    reunion = models.ForeignKey(Reuniones, on_delete=models.DO_NOTHING)
    usuario = models.ForeignKey(User, related_name="usuario_registro_reunion",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)
    hito = models.ForeignKey(Hito, on_delete=models.DO_NOTHING, blank=True, null=True)
    contacto = models.ForeignKey(Contactos, on_delete=models.DO_NOTHING, blank=True, null=True)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')



def upload_dinamic_soportes(instance, filename):
    return '/'.join(['Reuniones', 'Entes territoriales', str(instance.contacto.reunion.municipio.departamento.nombre),
                     str(instance.contacto.reunion.municipio.nombre), str(instance.contacto.cargo), str(instance.contacto.nombres), filename])

class Soportes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    contacto = models.ForeignKey(Contactos, on_delete=models.DO_NOTHING)
    tipo = models.CharField(max_length=100)
    file = models.FileField(upload_to=upload_dinamic_soportes, blank=True, null=True, max_length=255)
    observaciones = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.tipo

    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url

    def pretty_print_url_minuta(self):
        try:
            url = self.file.url
        except:
            return '<p style="display:inline;margin-left:5px;">No hay archivos cargados.</p>'
        else:
            return '<a href="'+ url +'"> '+ str(self.file.name) +'</a>'