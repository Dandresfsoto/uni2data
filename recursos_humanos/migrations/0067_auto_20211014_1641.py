# Generated by Django 2.2.24 on 2021-10-14 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0066_auto_20211014_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='collects_account',
            name='observaciones_inform',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Observaciones informe de actividades'),
        ),
        migrations.AlterField(
            model_name='collects_account',
            name='estate',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Estado seguridad social'),
        ),
        migrations.AlterField(
            model_name='collects_account',
            name='estate_inform',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Estado informe'),
        ),
        migrations.AlterField(
            model_name='collects_account',
            name='observaciones',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Observaciones seguridad social'),
        ),
    ]
