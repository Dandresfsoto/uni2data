# Generated by Django 2.1.3 on 2019-02-05 22:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fest_2019', '0005_auto_20190205_1401'),
    ]

    operations = [
        migrations.AddField(
            model_name='hogares',
            name='ruta',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='ruta_hogares', to='fest_2019.Rutas'),
        ),
    ]
