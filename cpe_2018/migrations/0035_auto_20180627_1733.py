# Generated by Django 2.0.1 on 2018-06-27 22:33

import cpe_2018.models
from django.db import migrations
import config.extrafields


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0034_auto_20180627_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actualizaciondirectoriomunicipios',
            name='file',
            field=config.extrafields.ContentTypeRestrictedFileField(max_length=255, upload_to=cpe_2018.models.upload_dinamic_actualizacion_directorio_municipios),
        ),
    ]
