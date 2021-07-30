# Generated by Django 2.0.1 on 2018-03-07 13:22

from django.db import migrations, models
import storages.backends.ftp
import usuarios.models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0007_auto_20180306_1618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paqueteactivacion',
            name='file',
            field=models.FileField(blank=True, null=True, storage=storages.backends.ftp.FTPStorage(), upload_to=usuarios.models.upload_dinamic_dir_paquete),
        ),
    ]
