# Generated by Django 2.1.5 on 2019-09-30 03:54

from django.db import migrations, models
import reportes.models


class Migration(migrations.Migration):

    dependencies = [
        ('reportes', '0004_auto_20190325_1914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportes',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=reportes.models.upload_dinamic_dir_reporte),
        ),
    ]
