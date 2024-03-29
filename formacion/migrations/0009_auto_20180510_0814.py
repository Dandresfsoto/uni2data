# Generated by Django 2.0.1 on 2018-05-10 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('formacion', '0008_actividades_diplomados_niveles_sesiones'),
    ]

    operations = [
        migrations.AddField(
            model_name='actividades',
            name='sesion',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, related_name='niveles_actividades', to='formacion.Sesiones'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='niveles',
            name='diplomado',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, related_name='niveles_diplomado', to='formacion.Diplomados'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sesiones',
            name='nivel',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.DO_NOTHING, related_name='niveles_sesiones', to='formacion.Niveles'),
            preserve_default=False,
        ),
    ]
