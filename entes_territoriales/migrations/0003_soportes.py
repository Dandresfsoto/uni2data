# Generated by Django 2.0.1 on 2018-05-16 19:54

from django.db import migrations, models
import django.db.models.deletion
import entes_territoriales.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('entes_territoriales', '0002_contactos'),
    ]

    operations = [
        migrations.CreateModel(
            name='Soportes',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('tipo', models.CharField(max_length=100)),
                ('file', models.FileField(blank=True, max_length=255, null=True, upload_to=entes_territoriales.models.upload_dinamic_soportes)),
                ('observaciones', models.TextField(blank=True, max_length=500, null=True)),
                ('contacto', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='entes_territoriales.Contactos')),
            ],
        ),
    ]
