# Generated by Django 2.0.1 on 2018-08-04 16:41

import cpe_2018.models
from django.db import migrations
import config.extrafields


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0065_auto_20180804_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ecoraeetallerraee',
            name='file',
            field=config.extrafields.ContentTypeRestrictedFileField(max_length=255, upload_to=cpe_2018.models.upload_dinamic_video_taller_raee),
        ),
    ]
