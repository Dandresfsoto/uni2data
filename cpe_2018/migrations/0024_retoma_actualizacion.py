# Generated by Django 2.0.1 on 2018-06-25 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0023_auto_20180622_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='retoma',
            name='actualizacion',
            field=models.BooleanField(default=False),
        ),
    ]
