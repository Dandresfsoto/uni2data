# Generated by Django 2.0.1 on 2018-08-28 15:45

import cpe_2018.models
from django.db import migrations
import config.extrafields


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0092_auto_20180827_0759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='red',
            name='file',
            field=config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=cpe_2018.models.upload_dinamic_red),
        ),
    ]
