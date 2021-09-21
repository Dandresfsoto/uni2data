# Generated by Django 2.2.24 on 2021-08-31 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('direccion_financiera', '0046_reportes_file_purchase_order'),
        ('recursos_humanos', '0061_auto_20210809_1020'),
    ]

    operations = [
        migrations.AddField(
            model_name='contratistas',
            name='account',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='contratistas',
            name='bank',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='contractor_bank', to='direccion_financiera.Bancos'),
        ),
        migrations.AddField(
            model_name='contratistas',
            name='first_active_account',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='contratistas',
            name='second_active_account',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='contratistas',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]