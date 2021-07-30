# Generated by Django 2.0.1 on 2018-06-05 22:32

from django.db import migrations, models
import django.db.models.deletion
import formatos.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Level1',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('consecutivo', models.IntegerField()),
                ('cantidad', models.IntegerField()),
                ('file', models.FileField(blank=True, max_length=255, null=True, upload_to=formatos.models.upload_dinamic_dir_level_1)),
                ('nivel', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Level2',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('consecutivo', models.IntegerField()),
                ('cantidad', models.IntegerField()),
                ('file', models.FileField(blank=True, max_length=255, null=True, upload_to=formatos.models.upload_dinamic_dir_level_2)),
                ('nivel', models.BooleanField(default=False)),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='formatos.Level1')),
            ],
        ),
        migrations.CreateModel(
            name='Level3',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('consecutivo', models.IntegerField()),
                ('cantidad', models.IntegerField()),
                ('file', models.FileField(blank=True, max_length=255, null=True, upload_to=formatos.models.upload_dinamic_dir_level_3)),
                ('nivel', models.BooleanField(default=False)),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='formatos.Level2')),
            ],
        ),
        migrations.CreateModel(
            name='Level4',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('consecutivo', models.IntegerField()),
                ('cantidad', models.IntegerField()),
                ('file', models.FileField(blank=True, max_length=255, null=True, upload_to=formatos.models.upload_dinamic_dir_level_4)),
                ('nivel', models.BooleanField(default=False)),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='formatos.Level3')),
            ],
        ),
        migrations.CreateModel(
            name='Level5',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('consecutivo', models.IntegerField()),
                ('cantidad', models.IntegerField()),
                ('file', models.FileField(blank=True, max_length=255, null=True, upload_to=formatos.models.upload_dinamic_dir_level_5)),
                ('nivel', models.BooleanField(default=False)),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='formatos.Level4')),
            ],
        ),
        migrations.CreateModel(
            name='Level6',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('consecutivo', models.IntegerField()),
                ('cantidad', models.IntegerField()),
                ('file', models.FileField(blank=True, max_length=255, null=True, upload_to=formatos.models.upload_dinamic_dir_level_6)),
                ('nivel', models.BooleanField(default=False)),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='formatos.Level5')),
            ],
        ),
        migrations.CreateModel(
            name='Level7',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('consecutivo', models.IntegerField()),
                ('cantidad', models.IntegerField()),
                ('file', models.FileField(blank=True, max_length=255, null=True, upload_to=formatos.models.upload_dinamic_dir_level_7)),
                ('nivel', models.BooleanField(default=False)),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='formatos.Level6')),
            ],
        ),
        migrations.CreateModel(
            name='Level8',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('consecutivo', models.IntegerField()),
                ('cantidad', models.IntegerField()),
                ('file', models.FileField(blank=True, max_length=255, null=True, upload_to=formatos.models.upload_dinamic_dir_level_8)),
                ('nivel', models.BooleanField(default=False)),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='formatos.Level7')),
            ],
        ),
    ]
