# Generated by Django 2.1.3 on 2019-03-26 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reportes', '0003_auto_20180409_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportes',
            name='nombre',
            field=models.CharField(max_length=1000),
        ),
    ]
