# Generated by Django 2.1.5 on 2019-12-15 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fest_2019', '0054_auto_20191214_1814'),
    ]

    operations = [
        migrations.AddField(
            model_name='rutas',
            name='tipo_pago',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
