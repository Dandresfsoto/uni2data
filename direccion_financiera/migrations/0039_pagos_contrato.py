# Generated by Django 2.1.5 on 2021-08-20 23:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0061_auto_20210809_1020'),
        ('direccion_financiera', '0038_auto_20210819_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagos',
            name='contrato',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='recursos_humanos.Contratos'),
        ),
    ]
