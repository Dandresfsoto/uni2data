# Generated by Django 2.1.5 on 2020-01-13 02:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fest_2019', '0069_auto_20191223_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='cuposrutaobject',
            name='instrumento_object',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='fest_2019.InstrumentosRutaObject'),
        ),
    ]
