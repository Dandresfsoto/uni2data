# Generated by Django 2.1.5 on 2021-08-05 16:46

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0029_auto_20200424_1125'),
        ('recursos_humanos', '0058_auto_20210805_1125'),
    ]

    operations = [
        migrations.CreateModel(
            name='CargosHv',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.RemoveField(
            model_name='hv',
            name='cargo_1',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='cargo_10',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='cargo_11',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='cargo_2',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='cargo_3',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='cargo_4',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='cargo_5',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='cargo_6',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='cargo_7',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='cargo_8',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='cargo_9',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='empresa_1',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='empresa_10',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='empresa_11',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='empresa_2',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='empresa_3',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='empresa_4',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='empresa_5',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='empresa_6',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='empresa_7',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='empresa_8',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='empresa_9',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_expedicion',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_fin_1',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_fin_10',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_fin_11',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_fin_2',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_fin_3',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_fin_4',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_fin_5',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_fin_6',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_fin_7',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_fin_8',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_fin_9',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_inicio_1',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_inicio_10',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_inicio_11',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_inicio_2',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_inicio_3',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_inicio_4',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_inicio_5',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_inicio_6',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_inicio_7',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_inicio_8',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='fecha_inicio_9',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_1',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_2',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_3',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_4',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_5',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_6',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_7',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_empresa_1',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_empresa_10',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_empresa_11',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_empresa_2',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_empresa_3',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_empresa_4',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_empresa_5',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_empresa_6',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_empresa_7',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_empresa_8',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='folio_empresa_9',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='grado_1',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='grado_2',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='grado_3',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='grado_4',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='grado_5',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='grado_6',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='grado_7',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='institucion_1',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='institucion_2',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='institucion_3',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='institucion_4',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='institucion_5',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='institucion_6',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='institucion_7',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='nivel_1',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='nivel_2',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='nivel_3',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='nivel_4',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='nivel_5',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='nivel_6',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='nivel_7',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='numero_tarjeta',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='observaciones_1',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='observaciones_10',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='observaciones_11',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='observaciones_2',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='observaciones_3',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='observaciones_4',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='observaciones_5',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='observaciones_6',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='observaciones_7',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='observaciones_8',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='observaciones_9',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='region',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='titulo_1',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='titulo_2',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='titulo_3',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='titulo_4',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='titulo_5',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='titulo_6',
        ),
        migrations.RemoveField(
            model_name='hv',
            name='titulo_7',
        ),
        migrations.AddField(
            model_name='hv',
            name='municipio',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='usuarios.Municipios'),
        ),
        migrations.AlterField(
            model_name='hv',
            name='cargo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='recursos_humanos.CargosHv'),
        ),
    ]