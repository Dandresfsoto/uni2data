# Generated by Django 2.0.1 on 2018-03-12 21:38

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0011_auto_20180312_1533'),
    ]

    operations = [
        migrations.CreateModel(
            name='GruposSoportes',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('nombre', models.CharField(max_length=30, unique=True)),
                ('soportes', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='recursos_humanos.Soportes')),
            ],
        ),
        migrations.DeleteModel(
            name='SoportesContratos',
        ),
    ]
