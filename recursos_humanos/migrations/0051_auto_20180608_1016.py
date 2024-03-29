# Generated by Django 2.0.1 on 2018-06-08 15:16

from django.db import migrations, models
import recursos_humanos.models


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0050_auto_20180608_1006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contratos',
            name='soporte_liquidacion',
            field=models.FileField(blank=True, null=True, upload_to=recursos_humanos.models.upload_dinamic_dir_liquidacion),
        ),
        migrations.AlterField(
            model_name='contratos',
            name='soporte_renuncia',
            field=models.FileField(blank=True, null=True, upload_to=recursos_humanos.models.upload_dinamic_dir_renuncia),
        ),
    ]
