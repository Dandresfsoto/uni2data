# Generated by Django 2.0.1 on 2018-06-20 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entes_territoriales', '0012_auto_20180530_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='hito',
            name='estado',
            field=models.CharField(default='Esperando aprobación', max_length=100),
            preserve_default=False,
        ),
    ]
