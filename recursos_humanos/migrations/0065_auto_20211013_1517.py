# Generated by Django 2.2.24 on 2021-10-13 20:17

import config.extrafields
from django.db import migrations, models
import recursos_humanos.models


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0064_collects_account_cuts'),
    ]

    operations = [
        migrations.AddField(
            model_name='cuts',
            name='month',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Mes'),
        ),
        migrations.AddField(
            model_name='cuts',
            name='year',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Año'),
        ),
        migrations.AlterField(
            model_name='collects_account',
            name='file',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=recursos_humanos.models.upload_dinamic_collects_account, verbose_name='Cuenta de cobro honorarios sin firmar'),
        ),
        migrations.AlterField(
            model_name='collects_account',
            name='file2',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=recursos_humanos.models.upload_dinamic_collects_account, verbose_name='Cuenta de cobro transporte sin firmar'),
        ),
        migrations.AlterField(
            model_name='collects_account',
            name='file3',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=recursos_humanos.models.upload_dinamic_collects_account, verbose_name='Cuenta de cobro honorarios firmada'),
        ),
        migrations.AlterField(
            model_name='collects_account',
            name='file4',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=recursos_humanos.models.upload_dinamic_collects_account, verbose_name='Cuenta de cobro transporte firmada'),
        ),
    ]
