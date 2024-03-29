# Generated by Django 2.0.1 on 2018-08-28 20:14

import cpe_2018.models
from django.db import migrations
import config.extrafields
import storages.backends.ftp


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0094_encuestamonitoreo_registroencuestamonitoreo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='red',
            name='file',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, storage=storages.backends.ftp.FTPStorage(), upload_to=cpe_2018.models.upload_dinamic_red),
        ),
    ]
