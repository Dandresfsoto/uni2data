# Generated by Django 2.0.1 on 2018-10-26 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0052_auto_20180614_1557'),
    ]

    operations = [
        migrations.AddField(
            model_name='contratos',
            name='visible',
            field=models.BooleanField(default=True),
        ),
    ]
