# Generated by Django 2.0.1 on 2018-04-29 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ofertas', '0011_ofertas_vacantes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ofertas',
            name='imagen',
        ),
    ]
