# Generated by Django 2.2.24 on 2022-01-28 20:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0081_auto_20220128_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='cut',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='recursos_humanos.Cuts'),
        ),
    ]