# Generated by Django 2.2.24 on 2021-08-30 16:15

import config.extrafields
import direccion_financiera.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('direccion_financiera', '0044_auto_20210830_0916'),
    ]

    operations = [
        migrations.AddField(
            model_name='enterprise',
            name='logo',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=direccion_financiera.models.upload_dinamic_logo),
        ),
    ]
