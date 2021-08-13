# Generated by Django 2.1.5 on 2021-08-12 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('direccion_financiera', '0036_empresas'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportes',
            name='empresa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='empresa_reporte', to='direccion_financiera.Empresas'),
        ),
        migrations.AlterField(
            model_name='empresas',
            name='nombre',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='empresas',
            name='numero',
            field=models.BigIntegerField(blank=True),
        ),
    ]
