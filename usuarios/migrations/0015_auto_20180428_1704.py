# Generated by Django 2.0.1 on 2018-04-28 22:04

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0014_auto_20180428_1703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='celular',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True),
        ),
    ]
