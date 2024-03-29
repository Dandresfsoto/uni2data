# Generated by Django 2.0.1 on 2018-07-06 16:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cpe_2018', '0044_entregablerutaobject_habilitado'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grupos',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('estrategia', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Estrategias')),
                ('ruta', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Rutas')),
                ('usuario_actualizacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='usuario_actualizacion_grupo', to=settings.AUTH_USER_MODEL)),
                ('usuario_creacion', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='usuario_creacion_grupo', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
