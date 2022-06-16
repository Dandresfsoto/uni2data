# Generated by Django 2.2.24 on 2022-06-16 01:37

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('iraca', '0021_auto_20220612_1104'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actas_Individual',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='milestones',
            name='transversal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='iraca.Actas_Individual', verbose_name='Tipo de Acta'),
        ),
    ]