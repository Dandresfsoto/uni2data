# Generated by Django 2.2.24 on 2022-06-04 17:04

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('iraca', '0013_auto_20220604_1133'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comunity',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('resguard', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='resguard_certificate_iraca_2021', to='iraca.Resguards')),
            ],
        ),
    ]
