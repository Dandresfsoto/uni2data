# Generated by Django 2.0.1 on 2018-08-02 19:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0060_auto_20180802_0924'),
    ]

    operations = [
        migrations.AddField(
            model_name='actaposesiondocente',
            name='entregable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Entregables'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='basedatosdocentes',
            name='entregable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Entregables'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='documentocompromisoinscripcion',
            name='entregable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Entregables'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='documentoproyeccioncronograma',
            name='entregable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Entregables'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='instrumentoautoreporte',
            name='entregable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Entregables'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='instrumentoestructuracionple',
            name='entregable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Entregables'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='instrumentoevaluacion',
            name='entregable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Entregables'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='instrumentohagamosmemoria',
            name='entregable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Entregables'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='listadoasistencia',
            name='entregable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Entregables'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='presentacionactividadpedagogica',
            name='entregable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Entregables'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='presentacionapa',
            name='entregable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Entregables'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productofinalple',
            name='entregable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Entregables'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='repositorioactividades',
            name='entregable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Entregables'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sistematizacionexperiencia',
            name='entregable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Entregables'),
            preserve_default=False,
        ),
    ]
