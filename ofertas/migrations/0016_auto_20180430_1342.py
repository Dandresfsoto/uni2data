# Generated by Django 2.0.1 on 2018-04-30 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ofertas', '0015_auto_20180429_1311'),
    ]

    operations = [
        migrations.AddField(
            model_name='aplicacionoferta',
            name='aplica',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='aplicacionoferta',
            name='preseleccionado',
            field=models.BooleanField(default=True),
        ),
    ]
