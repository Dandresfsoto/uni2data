# Generated by Django 2.0.1 on 2018-06-21 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entes_territoriales', '0013_hito_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='hito',
            name='observacion',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='hito',
            name='estado',
            field=models.CharField(default='Esperando aprobación', max_length=100),
        ),
    ]
