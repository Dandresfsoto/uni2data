# Generated by Django 2.0.1 on 2018-06-26 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0028_entregables_peso'),
    ]

    operations = [
        migrations.AddField(
            model_name='actapostulacion',
            name='nombre',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='actapostulacion',
            name='novedades',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='actapostulacion',
            name='valor',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='actapostulacion',
            name='ver',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='basedatospostulante',
            name='nombre',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='basedatospostulante',
            name='novedades',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='basedatospostulante',
            name='valor',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='basedatospostulante',
            name='ver',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='eventoinstitucional',
            name='nombre',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='eventoinstitucional',
            name='novedades',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='eventoinstitucional',
            name='valor',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='eventoinstitucional',
            name='ver',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='eventomunicipal',
            name='nombre',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='eventomunicipal',
            name='novedades',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='eventomunicipal',
            name='valor',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='eventomunicipal',
            name='ver',
            field=models.IntegerField(default=0),
        ),
    ]
