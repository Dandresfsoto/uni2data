# Generated by Django 2.1.3 on 2019-01-09 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0123_docentes_efectivo'),
    ]

    operations = [
        migrations.AddField(
            model_name='docentes',
            name='producto_final_andes',
            field=models.BooleanField(default=False),
        ),
    ]
