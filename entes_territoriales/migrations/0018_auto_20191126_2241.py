# Generated by Django 2.1.5 on 2019-11-27 03:41

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('entes_territoriales', '0017_auto_20191126_2150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactos',
            name='celular',
            field=phonenumber_field.modelfields.PhoneNumberField(default='', max_length=128),
            preserve_default=False,
        ),
    ]
