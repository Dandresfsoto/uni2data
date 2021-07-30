# Generated by Django 2.1.5 on 2019-12-14 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fest_2019', '0052_auto_20191214_1733'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hogares',
            name='area_tierra',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='area_unidos',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='barrio',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='cabeza_hogar',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='codigo_corregimiento',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='codigo_familia_mfa',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='codigo_vereda',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='dependientes',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='direccion',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='existe_mfa',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='existe_unidos',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='fecha_hecho_victimizante',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='folio',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='genero',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='hecho_victimizante',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='id_archivo',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='id_elegible',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='id_tipo_documento',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='id_zona',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='nombre_corregimiento',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='nombre_vereda',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='puntaje_mfa',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='puntaje_sisben',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='puntaje_ssv',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='puntaje_tiempo',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='puntaje_total',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='puntaje_unidos',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='ruta_1',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='ruta_2',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='ruta_3',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='ruta_4',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='ruta_vinculacion',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='tiene_tierra',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='ubicacion',
        ),
        migrations.RemoveField(
            model_name='hogares',
            name='zona_microfocalizada',
        ),
        migrations.AddField(
            model_name='hogares',
            name='rutas',
            field=models.ManyToManyField(blank=True, related_name='rutas', to='fest_2019.Rutas'),
        ),
    ]
