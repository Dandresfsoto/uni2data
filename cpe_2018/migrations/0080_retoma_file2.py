# Generated by Django 2.0.1 on 2018-08-13 22:41

import cpe_2018.models
from django.db import migrations
import config.extrafields


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0079_auto_20180813_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='retoma',
            name='file2',
            field=config.extrafields.ContentTypeRestrictedFileField(default='', max_length=255, upload_to=cpe_2018.models.upload_dinamic_retomas),
            preserve_default=False,
        ),
    ]
