# Generated by Django 2.2.24 on 2021-09-02 19:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import iraca.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('usuarios', '0029_auto_20200424_1125'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Certificates',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('code', models.IntegerField()),
                ('color', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Meetings',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('certificate', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='iraca.Certificates')),
                ('creation_user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='creation_user_meting', to=settings.AUTH_USER_MODEL)),
                ('municipality', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='usuarios.Municipios')),
                ('user_update', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='update_user_meeting', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Types',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('certificate', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='iraca.Certificates')),
            ],
        ),
        migrations.CreateModel(
            name='Milestones',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('creation', models.DateTimeField(auto_now_add=True)),
                ('date', models.DateField()),
                ('estate', models.CharField(default='Esperando aprobación', max_length=100)),
                ('observation', models.CharField(blank=True, max_length=500, null=True)),
                ('file', models.FileField(blank=True, max_length=255, null=True, upload_to=iraca.models.upload_dinamic_miltone)),
                ('file2', models.FileField(blank=True, max_length=255, null=True, upload_to=iraca.models.upload_dinamic_miltone)),
                ('file3', models.FileField(blank=True, max_length=255, null=True, upload_to=iraca.models.upload_dinamic_miltone)),
                ('foto_1', models.FileField(blank=True, max_length=255, null=True, upload_to=iraca.models.upload_dinamic_miltone)),
                ('foto_2', models.FileField(blank=True, max_length=255, null=True, upload_to=iraca.models.upload_dinamic_miltone)),
                ('foto_3', models.FileField(blank=True, max_length=255, null=True, upload_to=iraca.models.upload_dinamic_miltone)),
                ('foto_4', models.FileField(blank=True, max_length=255, null=True, upload_to=iraca.models.upload_dinamic_miltone)),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='iraca.Meetings')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='iraca.Types')),
            ],
        ),
    ]