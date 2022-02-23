# Generated by Django 2.2.24 on 2022-01-28 20:30

import config.extrafields
from django.db import migrations
import recursos_humanos.models


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0080_auto_20220126_0939'),
    ]

    operations = [
        migrations.AddField(
            model_name='liquidations',
            name='file3',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=recursos_humanos.models.upload_dinamic_dir_liquidation, verbose_name='informe de actividades firmado'),
        ),
        migrations.AddField(
            model_name='liquidations',
            name='file4',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=recursos_humanos.models.upload_dinamic_dir_liquidation, verbose_name='seguridad social'),
        ),
    ]