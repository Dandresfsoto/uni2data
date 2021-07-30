# Generated by Django 2.0.1 on 2018-03-22 22:55

import direccion_financiera.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('direccion_financiera', '0006_auto_20180322_1646'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportes',
            name='firma',
            field=models.FileField(blank=True, null=True, upload_to=direccion_financiera.models.upload_dinamic_dir_soporte_firma),
        ),
        migrations.AddField(
            model_name='reportes',
            name='respaldo',
            field=models.FileField(blank=True, null=True, upload_to=direccion_financiera.models.upload_dinamic_dir_soporte_respaldo),
        ),
    ]
