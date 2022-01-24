# Generated by Django 2.2.24 on 2022-01-20 14:11

import config.extrafields
from django.db import migrations, models
import recursos_humanos.models


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0076_liquidations'),
    ]

    operations = [
        migrations.AddField(
            model_name='liquidations',
            name='visible',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='liquidations',
            name='file',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=recursos_humanos.models.upload_dinamic_dir_liquidation, verbose_name='liquidacion sin firmar'),
        ),
        migrations.AlterField(
            model_name='liquidations',
            name='file2',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=recursos_humanos.models.upload_dinamic_dir_liquidation, verbose_name='liquidacion firmada'),
        ),
        migrations.AlterField(
            model_name='liquidations',
            name='html',
            field=models.FileField(blank=True, null=True, upload_to=recursos_humanos.models.upload_dinamic_dir_liquidation),
        ),
        migrations.AlterField(
            model_name='liquidations',
            name='html2',
            field=models.FileField(blank=True, null=True, upload_to=recursos_humanos.models.upload_dinamic_dir_liquidation),
        ),
    ]
