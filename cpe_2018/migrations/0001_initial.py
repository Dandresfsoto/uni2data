# Generated by Django 2.0.1 on 2018-06-05 14:09

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Departamentos',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ver', models.BooleanField(default=True)),
                ('nombre', models.CharField(max_length=100)),
                ('numero', models.IntegerField(unique=True)),
                ('cantidad_municipios', models.IntegerField(default=0)),
                ('cantidad_radicados', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Municipios',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ver', models.BooleanField(default=True)),
                ('nombre', models.CharField(max_length=100)),
                ('numero', models.IntegerField(unique=True)),
                ('cantidad_radicados', models.IntegerField(default=0)),
                ('latitud', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitud', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('departamento', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Departamentos')),
            ],
        ),
        migrations.CreateModel(
            name='Regiones',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ver', models.BooleanField(default=True)),
                ('nombre', models.CharField(max_length=100)),
                ('numero', models.IntegerField(unique=True)),
                ('cantidad_departamentos', models.IntegerField(default=0)),
                ('cantidad_municipios', models.IntegerField(default=0)),
                ('cantidad_radicados', models.IntegerField(default=0)),
                ('color', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='departamentos',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Regiones'),
        ),
    ]
