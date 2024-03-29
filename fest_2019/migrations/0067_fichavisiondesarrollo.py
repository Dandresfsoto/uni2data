# Generated by Django 2.1.5 on 2019-12-18 05:42

import config.extrafields
from django.db import migrations, models
import django.db.models.deletion
import fest_2019.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0028_elementosdiscapacidad_tiposrehabilitaciondiscapacidad'),
        ('fest_2019', '0066_auto_20191218_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='FichaVisionDesarrollo',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('fecha', models.DateField()),
                ('lugar', models.CharField(max_length=100)),
                ('dependencia', models.CharField(max_length=100)),
                ('asistentes', models.IntegerField()),
                ('file', config.extrafields.ContentTypeRestrictedFileField(max_length=255, upload_to=fest_2019.models.upload_dinamic_ficha_vision_desarrollo)),
                ('file2', config.extrafields.ContentTypeRestrictedFileField(max_length=255, upload_to=fest_2019.models.upload_dinamic_ficha_vision_desarrollo)),
                ('foto1', config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=fest_2019.models.upload_dinamic_ficha_vision_desarrollo)),
                ('foto2', config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=fest_2019.models.upload_dinamic_ficha_vision_desarrollo)),
                ('hogares', models.ManyToManyField(blank=True, related_name='hogares_ficha_vision_desarrollo', to='fest_2019.Hogares')),
                ('instrumento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='instrumento_ficha_vision_desarrollo', to='fest_2019.Instrumentos')),
                ('municipio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='municipio_ficha_vision_desarrollo', to='usuarios.Municipios')),
                ('ruta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='ruta_ficha_vision_desarrollo', to='fest_2019.Rutas')),
            ],
        ),
    ]
