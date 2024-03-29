# Generated by Django 2.0.1 on 2018-08-08 16:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0067_auto_20180808_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='cortes',
            name='consecutivo',
            field=models.IntegerField(),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cortes',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Regiones'),
            preserve_default=False,
        ),
    ]
