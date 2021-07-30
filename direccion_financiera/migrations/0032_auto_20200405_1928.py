# Generated by Django 2.1.5 on 2020-04-06 00:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0056_cargamasivacontratos'),
        ('direccion_financiera', '0031_auto_20200405_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagos',
            name='banco',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='direccion_financiera.Bancos'),
        ),
        migrations.AddField(
            model_name='pagos',
            name='cargo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='recursos_humanos.Cargos'),
        ),
        migrations.AddField(
            model_name='pagos',
            name='cuenta',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='pagos',
            name='tipo_cuenta',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
