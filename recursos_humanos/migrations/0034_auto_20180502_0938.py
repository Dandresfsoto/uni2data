# Generated by Django 2.0.1 on 2018-05-02 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0033_auto_20180426_1739'),
    ]

    operations = [
        migrations.AddField(
            model_name='soportescontratos',
            name='estado',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='soportescontratos',
            name='obervacion',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
