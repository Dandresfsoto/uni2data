# Generated by Django 2.1.5 on 2019-12-18 04:18

import config.extrafields
from django.db import migrations, models
import django.db.models.deletion
import fest_2019.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0028_elementosdiscapacidad_tiposrehabilitaciondiscapacidad'),
        ('fest_2019', '0064_formulariocaracterizacion'),
    ]

    operations = [
        migrations.CreateModel(
            name='FichaIcoe',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('nombre_comunidad', models.CharField(max_length=100)),
                ('resguado_indigena_consejo_comunitario', models.CharField(max_length=100)),
                ('fecha_entrada', models.DateField()),
                ('fecha_salida', models.DateField()),
                ('aspecto_1_entrada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_1_salida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_1_variacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_2_entrada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_2_salida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_2_variacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_3_entrada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_3_salida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_3_variacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_4_entrada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_4_salida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_4_variacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subindice_1_entrada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subindice_1_salida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subindice_1_variacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_5_entrada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_5_salida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_5_variacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_6_entrada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_6_salida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_6_variacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_7_entrada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_7_salida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_7_variacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_8_entrada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_8_salida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_8_variacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subindice_2_entrada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subindice_2_salida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subindice_2_variacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_9_entrada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_9_salida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_9_variacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_10_entrada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_10_salida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_10_variacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_11_entrada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_11_salida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('aspecto_11_variacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subindice_3_entrada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subindice_3_salida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subindice_3_variacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_entrada', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_salida', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_variacion', models.DecimalField(decimal_places=2, max_digits=10)),
                ('file', config.extrafields.ContentTypeRestrictedFileField(max_length=255, upload_to=fest_2019.models.upload_dinamic_ficha_icoe)),
                ('file2', config.extrafields.ContentTypeRestrictedFileField(max_length=255, upload_to=fest_2019.models.upload_dinamic_ficha_icoe)),
                ('foto1', config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=fest_2019.models.upload_dinamic_ficha_icoe)),
                ('foto2', config.extrafields.ContentTypeRestrictedFileField(blank=True, max_length=255, null=True, upload_to=fest_2019.models.upload_dinamic_ficha_icoe)),
                ('hogares', models.ManyToManyField(blank=True, related_name='hogares_ficha_icoe', to='fest_2019.Hogares')),
                ('instrumento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='instrumento_ficha_icoe', to='fest_2019.Instrumentos')),
                ('municipio', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='municipio_ficha_icoe', to='usuarios.Municipios')),
                ('ruta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='ruta_ficha_icoe', to='fest_2019.Rutas')),
            ],
        ),
    ]
