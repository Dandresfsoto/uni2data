# Generated by Django 2.0.1 on 2018-08-24 13:08

import cpe_2018.models
from django.db import migrations
import config.extrafields


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0084_auto_20180823_1742'),
    ]

    operations = [
        migrations.AddField(
            model_name='red',
            name='file',
            field=config.extrafields.ContentTypeRestrictedFileField(max_length=255, upload_to=cpe_2018.models.upload_dinamic_red),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='red',
            name='file2',
            field=config.extrafields.ContentTypeRestrictedFileField(max_length=255, upload_to=cpe_2018.models.upload_dinamic_red),
            preserve_default=False,
        ),
    ]
