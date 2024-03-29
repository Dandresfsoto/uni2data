# Generated by Django 2.0.1 on 2018-05-04 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0039_auto_20180504_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='hv',
            name='cargo_1',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hv',
            name='cargo_10',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='cargo_11',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='cargo_2',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='cargo_3',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='cargo_4',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='cargo_5',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='cargo_6',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='cargo_7',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='cargo_8',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='cargo_9',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='empresa_1',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hv',
            name='empresa_10',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='empresa_11',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='empresa_2',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='empresa_3',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='empresa_4',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='empresa_5',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='empresa_6',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='empresa_7',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='empresa_8',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='empresa_9',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_expedicion',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_fin_1',
            field=models.DateField(),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_fin_10',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_fin_11',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_fin_2',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_fin_3',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_fin_4',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_fin_5',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_fin_6',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_fin_7',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_fin_8',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_fin_9',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_inicio_1',
            field=models.DateField(),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_inicio_10',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_inicio_11',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_inicio_2',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_inicio_3',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_inicio_4',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_inicio_5',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_inicio_6',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_inicio_7',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_inicio_8',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='fecha_inicio_9',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='folio',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='folio_empresa_1',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hv',
            name='folio_empresa_10',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='folio_empresa_11',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='folio_empresa_2',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='folio_empresa_3',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='folio_empresa_4',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='folio_empresa_5',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='folio_empresa_6',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='folio_empresa_7',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='folio_empresa_8',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='folio_empresa_9',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='numero_tarjeta',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='observaciones_1',
            field=models.IntegerField(),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hv',
            name='observaciones_10',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='observaciones_11',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='observaciones_2',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='observaciones_3',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='observaciones_4',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='observaciones_5',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='observaciones_6',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='observaciones_7',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='observaciones_8',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hv',
            name='observaciones_9',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
