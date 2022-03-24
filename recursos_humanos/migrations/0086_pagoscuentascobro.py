# Generated by Django 2.2.24 on 2022-03-01 17:06

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('direccion_financiera', '0052_historicalpagos_historicalreportes'),
        ('recursos_humanos', '0085_otros_si_fecha_original'),
    ]

    operations = [
        migrations.CreateModel(
            name='PagosCuentasCobro',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('cuenta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='cuenta_pagos', to='recursos_humanos.Collects_Account')),
                ('pago', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='pago_pagosCuentasCobro', to='direccion_financiera.Pagos')),
            ],
        ),
    ]