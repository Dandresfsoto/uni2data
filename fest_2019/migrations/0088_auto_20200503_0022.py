# Generated by Django 2.1.5 on 2020-05-03 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fest_2019', '0087_auto_20200502_2332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proyectosapi',
            name='convenio',
            field=models.TextField(default='213-19'),
        ),
    ]
