# Generated by Django 2.0.1 on 2018-03-23 13:27

import direccion_financiera.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('direccion_financiera', '0007_auto_20180322_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportes',
            name='file_banco',
            field=models.FileField(blank=True, null=True, upload_to=direccion_financiera.models.upload_dinamic_dir_soporte_file_banco),
        ),
    ]
