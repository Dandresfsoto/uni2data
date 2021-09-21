# Generated by Django 2.1.5 on 2021-08-18 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('direccion_financiera', '0036_auto_20210817_1123'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportes',
            name='consecutive',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reportes',
            name='enterprise',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='direccion_financiera.Enterprise'),
        ),
    ]