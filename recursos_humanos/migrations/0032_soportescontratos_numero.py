# Generated by Django 2.0.1 on 2018-04-26 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0031_auto_20180426_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='soportescontratos',
            name='numero',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
