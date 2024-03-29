# Generated by Django 2.1.3 on 2019-07-09 14:52

from django.db import migrations, models
import django.db.models.deletion
import fest_2019.models
import config.extrafields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('fest_2019', '0047_cuposrutaobject_translado'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchivoRarZip',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('file', config.extrafields.ContentTypeRestrictedFileField(max_length=255, upload_to=fest_2019.models.upload_dinamic_fest)),
                ('hogar', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='hogar_rar_zip', to='fest_2019.Hogares')),
                ('instrumento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='instrumento_rar_zip', to='fest_2019.Instrumentos')),
            ],
        ),
    ]
