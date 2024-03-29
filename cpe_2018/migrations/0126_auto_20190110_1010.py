# Generated by Django 2.1.3 on 2019-01-10 15:10

import cpe_2018.models
from django.db import migrations
import config.extrafields
import storages.backends.ftp


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0125_liquidaciones_file3'),
    ]

    operations = [
        migrations.AlterField(
            model_name='liquidaciones',
            name='file3',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, storage=storages.backends.ftp.FTPStorage(), upload_to=cpe_2018.models.upload_dinamic_liquidaciones),
        ),
    ]
