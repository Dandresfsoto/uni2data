# Generated by Django 2.0.1 on 2018-11-16 15:23

from django.db import migrations
import recursos_humanos.models
import config.extrafields


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0053_contratos_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='contratos',
            name='otro_si_1',
            field=config.extrafields.PDFFileField(blank=True, null=True, upload_to=recursos_humanos.models.upload_dinamic_dir),
        ),
        migrations.AddField(
            model_name='contratos',
            name='otro_si_2',
            field=config.extrafields.PDFFileField(blank=True, null=True, upload_to=recursos_humanos.models.upload_dinamic_dir),
        ),
        migrations.AddField(
            model_name='contratos',
            name='otro_si_3',
            field=config.extrafields.PDFFileField(blank=True, null=True, upload_to=recursos_humanos.models.upload_dinamic_dir),
        ),
    ]
