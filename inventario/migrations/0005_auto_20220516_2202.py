# Generated by Django 2.2.24 on 2022-05-17 03:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0004_auto_20220516_2145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productos',
            name='proyectos',
        ),
        migrations.RemoveField(
            model_name='productos',
            name='visible',
        ),
        migrations.AddField(
            model_name='despachos',
            name='proyectos',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='inventario.Proyectos', verbose_name='Proyectos'),
        ),
        migrations.AddField(
            model_name='despachos',
            name='visible',
            field=models.BooleanField(default=False),
        ),
    ]
