# Generated by Django 2.2.24 on 2021-08-31 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0062_auto_20210831_1106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contratistas',
            name='first_active_account',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='contratistas',
            name='second_active_account',
            field=models.BooleanField(default=False),
        ),
    ]
