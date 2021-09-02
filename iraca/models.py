import uuid
from django.db import models
from phonenumber_field.formfields import PhoneNumberField
from pytz import timezone
from django.conf import settings

from usuarios.models import User, Municipios, Departamentos

settings_time_zone = timezone(settings.TIME_ZONE)

class Certificates(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100)
    code = models.IntegerField()
    color = models.CharField(max_length=100)


    def __str__(self):
        return self.name

class Meetings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    creation_user = models.ForeignKey(User, related_name="creation_user_meting", on_delete=models.DO_NOTHING)
    update_datetime = models.DateTimeField(auto_now=True)
    user_update = models.ForeignKey(User, related_name="update_user_meeting",
                                              on_delete=models.DO_NOTHING,
                                              blank=True, null=True)
    municipality = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING)
    certificate = models.ForeignKey(Certificates, on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.id)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y a las %I:%M:%S %p')

def upload_dinamic_miltone(instance, filename):
    return '/'.join(['Reuniones', 'Entes territoriales', str(instance.reunion.municipio.departamento.nombre),
                     str(instance.reunion.municipio.nombre), 'Hitos', filename])

class Milestones(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    meeting = models.ForeignKey(Meetings, on_delete=models.DO_NOTHING)
    type = models.CharField(max_length=100)
    date = models.DateField()
    estate = models.CharField(max_length=100,default='Esperando aprobación')
    observation = models.CharField(max_length=500, blank=True, null=True)
    file = models.FileField(upload_to=upload_dinamic_miltone, blank=True, null=True, max_length=255)
    file2 = models.FileField(upload_to=upload_dinamic_miltone, blank=True, null=True, max_length=255)
    file3 = models.FileField(upload_to=upload_dinamic_miltone, blank=True, null=True, max_length=255)
    foto_1 = models.FileField(upload_to=upload_dinamic_miltone, blank=True, null=True, max_length=255)
    foto_2 = models.FileField(upload_to=upload_dinamic_miltone, blank=True, null=True, max_length=255)
    foto_3 = models.FileField(upload_to=upload_dinamic_miltone, blank=True, null=True, max_length=255)
    foto_4 = models.FileField(upload_to=upload_dinamic_miltone, blank=True, null=True, max_length=255)

    def __str__(self):
        return self.type

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

class Contacts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    meeting = models.ForeignKey(Meetings,on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=100)
    surnames = models.CharField(max_length=100)
    position = models.CharField(max_length=200)
    movil = PhoneNumberField()
    email = models.EmailField(max_length=100,blank=True,null=True)
    reservation = models.CharField(max_length=100)
    community = models.CharField(max_length=100)
    tongues = models.CharField(max_length=100, null=True, blank=True)
    observations = models.TextField(max_length=500,blank=True,null=True)





    def __str__(self):
        return self.name

class Record(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    meeting = models.ForeignKey(Meetings, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, related_name="record_user_meeting",on_delete=models.DO_NOTHING)
    delta = models.CharField(max_length=10000)
    miltone = models.ForeignKey(Milestones, on_delete=models.DO_NOTHING, blank=True, null=True)
    contact = models.ForeignKey(Contacts, on_delete=models.DO_NOTHING, blank=True, null=True)

    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')

def upload_dinamic_suport(instance, filename):
    return '/'.join(['Reuniones', 'Entes territoriales', str(instance.contacto.reunion.municipio.departamento.nombre),
                     str(instance.contacto.reunion.municipio.nombre), str(instance.contacto.cargo), str(instance.contacto.nombres), filename])

class Suport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    contact = models.ForeignKey(Contacts, on_delete=models.DO_NOTHING)
    type = models.CharField(max_length=100)
    file = models.FileField(upload_to=upload_dinamic_suport, blank=True, null=True, max_length=255)
    observation = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.type

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