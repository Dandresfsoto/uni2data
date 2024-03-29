# Generated by Django 2.0.1 on 2018-04-28 14:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0012_auto_20180307_1340'),
    ]

    operations = [
        migrations.CreateModel(
            name='Departamentos',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ver', models.BooleanField(default=True)),
                ('nombre', models.CharField(max_length=100)),
                ('codigo', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='HojasDeVida',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('actualizacion', models.DateTimeField(auto_now=True)),
                ('sexo', models.CharField(max_length=100)),
                ('nacionalidad', models.CharField(max_length=100)),
                ('municipio_residencia', models.CharField(max_length=100)),
                ('direccion', models.CharField(max_length=100)),
                ('educacion_basica', models.CharField(max_length=100)),
                ('educacion_secundaria', models.CharField(max_length=100)),
                ('fecha_grado', models.DateField()),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Municipios',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ver', models.BooleanField(default=True)),
                ('nombre', models.CharField(max_length=100)),
                ('codigo', models.IntegerField(unique=True)),
                ('latitud', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitud', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('departamento', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='usuarios.Departamentos')),
            ],
        ),
    ]
