# Generated by Django 2.0.1 on 2018-04-29 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0019_auto_20180429_0715'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='sexo',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
