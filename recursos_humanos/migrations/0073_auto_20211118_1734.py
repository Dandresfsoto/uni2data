# Generated by Django 2.2.24 on 2021-11-18 22:34

import config.extrafields
from django.db import migrations
import recursos_humanos.models


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0072_auto_20211028_0945'),
    ]

    operations = [
        migrations.AddField(
            model_name='collects_account',
            name='foto1',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=recursos_humanos.models.upload_dinamic_collects_account),
        ),
        migrations.AddField(
            model_name='collects_account',
            name='foto2',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=recursos_humanos.models.upload_dinamic_collects_account),
        ),
        migrations.AddField(
            model_name='collects_account',
            name='foto3',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=recursos_humanos.models.upload_dinamic_collects_account),
        ),
        migrations.AddField(
            model_name='collects_account',
            name='foto4',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=recursos_humanos.models.upload_dinamic_collects_account),
        ),
    ]