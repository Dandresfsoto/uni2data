# Generated by Django 2.0.1 on 2018-04-05 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('direccion_financiera', '0013_consecutivoreportes'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportes',
            name='consecutivo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='direccion_financiera.ConsecutivoReportes'),
        ),
    ]
