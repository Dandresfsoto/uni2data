# Generated by Django 2.0.1 on 2018-06-15 19:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0012_auto_20180614_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entregablerutaobject',
            name='entregable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Entregables'),
        ),
    ]
