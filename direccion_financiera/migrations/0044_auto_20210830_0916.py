# Generated by Django 2.2.24 on 2021-08-30 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('direccion_financiera', '0043_auto_20210828_0917'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorders',
            name='counterpart',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='purchaseorders',
            name='departure',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='purchaseorders',
            name='meta',
            field=models.PositiveIntegerField(default=0),
        ),
    ]