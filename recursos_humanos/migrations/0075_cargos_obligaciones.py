# Generated by Django 2.2.24 on 2022-01-13 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0074_registration'),
    ]

    operations = [
        migrations.AddField(
            model_name='cargos',
            name='obligaciones',
            field=models.TextField(blank=True, max_length=10000, null=True),
        ),
    ]