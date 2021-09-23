import uuid
from django.db import models
from pytz import timezone
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from self import self

from config.extrafields import ContentTypeRestrictedFileField
from mobile.models import FormMobile
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

class Types(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100)
    certificate = models.ForeignKey(Certificates, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name

def upload_dinamic_miltone(instance, filename):
    return '/'.join(['Iraca 2021',str(instance.meeting.certificate.name),str(instance.meeting.municipality.nombre),str(instance.type), filename])

class Milestones(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    meeting = models.ForeignKey(Meetings, on_delete=models.DO_NOTHING)
    type = models.ForeignKey(Types, on_delete=models.DO_NOTHING, verbose_name="Tipo de Acta")
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
        return self.type.name

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
    meting = models.ForeignKey(Meetings,on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    charge = models.CharField(max_length=200)
    movil = PhoneNumberField()
    email = models.EmailField(max_length=100,blank=True,null=True)
    reservation = models.CharField(max_length=100,blank=True,null=True)
    community = models.CharField(max_length=100,blank=True,null=True)
    languahe = models.CharField(max_length=100, null=True, blank=True)
    observation = models.TextField(max_length=500,blank=True,null=True)

    def __str__(self):
        return self.name



#----------------------------------------------------------------------------------

#------------------------------- ROUTES  ------------------------------------------

class Moments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100)
    consecutive = models.IntegerField()
    instruments = models.IntegerField()
    type = models.CharField(max_length=100)
    novelty = models.BooleanField(default=True)
    progress = models.BooleanField(default=True)
    type_moment = models.CharField(max_length=100)

    def __str__(self):
        return '{0} - {1}' .format(self.name, self.type_moment)

    def get_number_instruments(self):
        return Instruments.objects.filter(moment=self).count()

    def get_consecutive(self):
        return '{0}'.format(self.consecutive)

    def get_novelty(self, route):
        return ObjectRouteInstrument.objects.filter(route=route, moment=self, estate='cargado').distinct().count()

    def get_progress_moment(self,route):

        query = ObjectRouteInstrument.objects.filter(route=route, moment=self)

        households__ids = query.filter(estate__in=['aprobado']).values_list('households__id',flat=True)

        households = Households.objects.filter(id__in = households__ids)

        try:
            progress = (households.count() / route.goal) * 100.0
        except:
            progress = 0


        return progress

class Instruments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    moment = models.ForeignKey(Moments,on_delete=models.DO_NOTHING,related_name='instrument_moment_iraca_2021', verbose_name="Momento")
    name = models.CharField(max_length=100, verbose_name="Nombre")
    short_name = models.CharField(max_length=100,  verbose_name="Nombre corto")
    consecutive = models.IntegerField(verbose_name="Consecutivo")
    model = models.CharField(max_length=100, verbose_name="Modelo")
    color = models.CharField(max_length=100, verbose_name="Color")
    icon = models.CharField(max_length=100,  verbose_name="Icono")
    level = models.CharField(max_length=100, verbose_name="Nivel")

    def __str__(self):
        return self.name

    def get_consecutive(self):
        return '{0}.{1}'.format(self.moment.consecutive,self.consecutive)

class Routes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    name = models.CharField(unique=True, max_length=100)

    novelties = models.IntegerField(default=0)
    progress = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)
    creation_user = models.ForeignKey(User, related_name="creation_user_route_iraca_2021", on_delete=models.DO_NOTHING)
    update_datetime = models.DateTimeField(auto_now=True)
    user_update = models.ForeignKey(User, related_name="user_update_route_iraca_2021",
                                              on_delete=models.DO_NOTHING,
                                              blank=True, null=True)

    estate = models.CharField(max_length=100,blank=True)

    regitered_household = models.IntegerField(default=0)

    visible = models.BooleanField(default=True)
    goal = models.PositiveIntegerField(default=0)
    novelties_form =models.IntegerField(default=0)
    progress_form = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)

    def __str__(self):
        return self.name

    def update_progreso(self):

        query = ObjectRouteInstrument.objects.filter(route=self)
        moments = Moments.objects.filter(type_moment="implementacion")

        households__ids = query.filter(estate__in=['aprobado'],moment__type_moment__contains="implementacion").values_list('households__id', flat=True)

        try:
            progress = (households__ids.count()/(self.goal * moments.count()))*100.0
        except:
            progress = 0

        self.progress = progress
        self.save()

        return self.progress

    def update_progres_formulation(self):

        query = ObjectRouteInstrument.objects.filter(route=self)
        moments = Moments.objects.filter(type_moment="formulacion")

        households__ids = query.filter(estate__in=['aprobado'],moment__type_moment__contains="formulacion").values_list('households__id', flat=True)

        try:
            progress_form = (households__ids.count()/(self.goal * moments.count()))*100.0
        except:
            progress_form = 0

        self.progress_form = progress_form
        self.save()

        return self.progress_form

    def update_novedades(self):
        self.novelties = ObjectRouteInstrument.objects.filter(route=self, estate='cargado',moment__type_moment__contains="implementacion").count()
        self.save()
        self.update_progreso()
        return 'Ok'

    def update_novelties_form(self):
        self.novelties_form = ObjectRouteInstrument.objects.filter(route=self, estate='cargado',moment__type_moment__contains="formulacion").count()
        self.save()
        self.update_progreso()
        return 'Ok'

    def get_instruments_list(self,moment):

        instruments_return = []

        for instrument in Instruments.objects.filter(moment = moment).order_by('consecutive'):
            instruments_return.append({
                'id': instrument.id,
                'short_name': instrument.short_name,
                'icon': instrument.icon,
                'color': instrument.color
            })

        return instruments_return

    def get_household_count(self):
        count=0
        try:
            count=Households.objects.filter(routes=self.id).count()
        except:
            pass
        return count

class Households(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)

    document = models.BigIntegerField(unique=True)
    municipality_attention = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING, related_name='household_municipality_attention_iraca_2021')

    first_surname = models.CharField(max_length=100)
    second_surname = models.CharField(max_length=100,blank=True,null=True)
    first_name = models.CharField(max_length=100)
    second_name = models.CharField(max_length=100,blank=True,null=True)
    birth_date = models.DateField()
    phone = models.CharField(max_length=100,blank=True,null=True)
    movil1 = models.CharField(max_length=100,blank=True,null=True)
    movil2 = models.CharField(max_length=100,blank=True,null=True)
    municipality_residence = models.ForeignKey(Municipios, on_delete=models.DO_NOTHING, related_name='household_municipality_residence_iraca_2021')

    routes = models.ManyToManyField(Routes, related_name='routes_iraca_2021',blank=True)


    def __str__(self):
        return self.get_names() + ' ' + self.get_surnames() + ' - ' + str(self.document)

    def get_names(self):
        if self.second_name != None:
            names = '{0} {1}'.format(self.first_name,self.second_name)
        else:
            names = self.first_name
        return names

    def get_surnames(self):
        if self.second_surname != None:
            surnames = '{0} {1}'.format(self.first_surname,self.second_surname)
        else:
            surnames = self.first_surname
        return surnames

    def get_full_name(self):
        return '{0} {1}'.format(self.get_names(),self.get_surnames())

    def get_routes(self):
        routes = ''
        for route in self.routes.all():
            routes += route.name + ', '

        if routes != '':
            routes = routes[:-2]

        return routes

    def get_estate_moment(self, moment, route):

        instruments = ObjectRouteInstrument.objects.filter(moment = moment, households=self, route=route).order_by('creation')

        try:
            estate = instruments[0].estate
        except:
            estate = ''

        return estate


class QuotasRouteObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    route = models.ForeignKey(Routes,on_delete=models.DO_NOTHING,related_name='quota_route_iraca_2021')
    moment = models.ForeignKey(Moments,on_delete=models.DO_NOTHING,related_name='quota_moment_iraca_2021', blank=True, null=True)
    estate = models.CharField(max_length=100)
    data = JSONField(default=dict)

class ObjectRouteInstrument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    creation = models.DateTimeField(auto_now_add=True)
    creacion_user = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='instrument_creation_user_iraca_2021',blank=True,null=True)

    route = models.ForeignKey(Routes, on_delete=models.DO_NOTHING, related_name='instrument_route_iraca_2021')
    moment = models.ForeignKey(Moments, on_delete=models.DO_NOTHING, related_name='instrument_route_moment_iraca_2021')
    households = models.ManyToManyField(Households, related_name='instrument_household_iraca_2021', blank=True)
    instrument = models.ForeignKey(Instruments, on_delete=models.DO_NOTHING, related_name='instrumentroute_instrument_iraca_2021',blank=True,null=True)

    model = models.CharField(max_length=100)
    support = models.UUIDField(blank=True,null=True)
    observation = models.TextField(blank=True,null=True)
    update_date = models.DateTimeField(blank=True,null=True)
    update_user = models.ForeignKey(User, on_delete=models.DO_NOTHING,related_name='instrument_update_user_iraca_2021',blank=True,null=True)
    estate = models.CharField(max_length=100,blank=True,null=True)
    name = models.CharField(max_length=100,blank=True,null=True)
    consecutive = models.IntegerField(blank=True,null=True)

class ObservationsInstrumentRouteObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    instrument = models.ForeignKey(ObjectRouteInstrument, on_delete=models.DO_NOTHING)
    creation = models.DateTimeField(auto_now_add=True)
    user_creation = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='instrument_observation_creation_user_iraca_2021',blank=True, null=True)
    observation = models.TextField(blank=True,null=True)


    def pretty_creation_datetime(self):
        return self.creation.astimezone(settings_time_zone).strftime('%d/%m/%Y - %I:%M:%S %p')

class InstrumentTraceabilityRouteObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    instrument = models.ForeignKey(ObjectRouteInstrument,on_delete=models.DO_NOTHING,related_name="traceability_instrument_iraca_2021")
    creacion = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='traceability_instrument_user_iraca_2021')
    observation = models.TextField()

#----------------------------------------------------------------------------------

#---------------------------- MODELS OBJECTS  -------------------------------------

def upload_dinamic_iraca_2021(instance, filename):
    return '/'.join(['Iraca 2021', str(instance.route.name),str(instance.instrument.moment.name), instance.name, filename])

class Documento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    households = models.ManyToManyField(Households,related_name='households_document_iraca_2021',blank=True, verbose_name="Hogares")
    instrument = models.ForeignKey(Instruments,on_delete=models.DO_NOTHING,related_name='instrument_document_iraca_2021',blank=True,null=True,  verbose_name="Instrumentos")
    route = models.ForeignKey(Routes,on_delete=models.DO_NOTHING,related_name='route_document_iraca_2021',blank=True,null=True, verbose_name="Ruta")
    name = models.CharField(max_length=100,  verbose_name="Nombre")

    file = ContentTypeRestrictedFileField(
        upload_to=upload_dinamic_iraca_2021,
        content_types=[
            'application/pdf',
        ],
        max_upload_size=50485760,
        max_length=255
    )



    def url_file(self):
        url = None
        try:
            url = self.file.url
        except:
            pass
        return url


    def get_extension(self):
        return self.file.name.split('.')[-1]
