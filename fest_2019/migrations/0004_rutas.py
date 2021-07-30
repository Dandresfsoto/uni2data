# Generated by Django 2.1.3 on 2019-02-05 18:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0055_auto_20181221_1135'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fest_2019', '0003_momentos_tipo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rutas',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('estado', models.CharField(blank=True, max_length=100)),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='contrato_ruta_fest_2019', to='recursos_humanos.Contratos')),
                ('usuario_actualizacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='usuario_actualizacion_ruta_fest_2019', to=settings.AUTH_USER_MODEL)),
                ('usuario_creacion', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='usuario_creacion_ruta_fest_2019', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
