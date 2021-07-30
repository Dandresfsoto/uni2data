from django.db import models
import uuid
# Create your models here.

def upload_dinamic_dir_level_1(instance, filename):
    return '/'.join(['CPE 2018', 'Nivel 1', str(instance.id), filename])

class Level1(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    nombre = models.CharField(max_length = 100)
    consecutivo = models.IntegerField()
    file = models.FileField(max_length=255,upload_to=upload_dinamic_dir_level_1, blank=True, null=True)
    url = models.URLField(max_length=500,blank=True,null=True)
    nivel = models.BooleanField(default=False)

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


def upload_dinamic_dir_level_2(instance, filename):
    return '/'.join(['CPE 2018', 'Nivel 2', str(instance.id), filename])

class Level2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    level = models.ForeignKey(Level1,on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length = 100)
    consecutivo = models.IntegerField()
    file = models.FileField(max_length=255,upload_to=upload_dinamic_dir_level_2, blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    nivel = models.BooleanField(default=False)

    def get_consecutivo(self):
        return '{0}.{1}'.format(self.level.consecutivo,self.consecutivo)

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

def upload_dinamic_dir_level_3(instance, filename):
    return '/'.join(['CPE 2018', 'Nivel 3', str(instance.id), filename])

class Level3(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    level = models.ForeignKey(Level2,on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length = 100)
    consecutivo = models.IntegerField()
    file = models.FileField(max_length=255,upload_to=upload_dinamic_dir_level_3, blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    nivel = models.BooleanField(default=False)

    def get_consecutivo(self):
        return '{0}.{1}.{2}'.format(self.level.level.consecutivo,self.level.consecutivo,self.consecutivo)

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

def upload_dinamic_dir_level_4(instance, filename):
    return '/'.join(['CPE 2018', 'Nivel 4', str(instance.id), filename])

class Level4(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    level = models.ForeignKey(Level3,on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length = 100)
    consecutivo = models.IntegerField()
    file = models.FileField(max_length=255,upload_to=upload_dinamic_dir_level_4, blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    nivel = models.BooleanField(default=False)

    def get_consecutivo(self):
        return '{0}.{1}.{2}.{3}'.format(
            self.level.level.level.consecutivo,
            self.level.level.consecutivo,
            self.level.consecutivo,
            self.consecutivo
        )

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


def upload_dinamic_dir_level_5(instance, filename):
    return '/'.join(['CPE 2018', 'Nivel 5', str(instance.id), filename])

class Level5(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    level = models.ForeignKey(Level4,on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length = 100)
    consecutivo = models.IntegerField()
    file = models.FileField(max_length=255,upload_to=upload_dinamic_dir_level_5, blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    nivel = models.BooleanField(default=False)

    def get_consecutivo(self):
        return '{0}.{1}.{2}.{3}.{4}'.format(
            self.level.level.level.level.consecutivo,
            self.level.level.level.consecutivo,
            self.level.level.consecutivo,
            self.level.consecutivo,
            self.consecutivo
        )

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

def upload_dinamic_dir_level_6(instance, filename):
    return '/'.join(['CPE 2018', 'Nivel 6', str(instance.id), filename])

class Level6(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    level = models.ForeignKey(Level5,on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length = 100)
    consecutivo = models.IntegerField()
    file = models.FileField(max_length=255,upload_to=upload_dinamic_dir_level_6, blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    nivel = models.BooleanField(default=False)

    def get_consecutivo(self):
        return '{0}.{1}.{2}.{3}.{4}.{5}'.format(
            self.level.level.level.level.level.consecutivo,
            self.level.level.level.level.consecutivo,
            self.level.level.level.consecutivo,
            self.level.level.consecutivo,
            self.level.consecutivo,
            self.consecutivo
        )

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


def upload_dinamic_dir_level_7(instance, filename):
    return '/'.join(['CPE 2018', 'Nivel 7', str(instance.id), filename])

class Level7(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    level = models.ForeignKey(Level6,on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length = 100)
    consecutivo = models.IntegerField()
    file = models.FileField(max_length=255,upload_to=upload_dinamic_dir_level_7, blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    nivel = models.BooleanField(default=False)

    def get_consecutivo(self):
        return '{0}.{1}.{2}.{3}.{4}.{5}.{6}'.format(
            self.level.level.level.level.level.level.consecutivo,
            self.level.level.level.level.level.consecutivo,
            self.level.level.level.level.consecutivo,
            self.level.level.level.consecutivo,
            self.level.level.consecutivo,
            self.level.consecutivo,
            self.consecutivo
        )

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


def upload_dinamic_dir_level_8(instance, filename):
    return '/'.join(['CPE 2018', 'Nivel 8', str(instance.id), filename])

class Level8(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    level = models.ForeignKey(Level7,on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length = 100)
    consecutivo = models.IntegerField()
    file = models.FileField(max_length=255,upload_to=upload_dinamic_dir_level_8, blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)

    def get_consecutivo(self):
        return '{0}.{1}.{2}.{3}.{4}.{5}.{6}.{7}'.format(
            self.level.level.level.level.level.level.level.consecutivo,
            self.level.level.level.level.level.level.consecutivo,
            self.level.level.level.level.level.consecutivo,
            self.level.level.level.level.consecutivo,
            self.level.level.level.consecutivo,
            self.level.level.consecutivo,
            self.level.consecutivo,
            self.consecutivo
        )

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