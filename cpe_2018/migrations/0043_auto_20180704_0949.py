# Generated by Django 2.0.1 on 2018-07-04 14:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0042_auto_20180703_1853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cuenticostallerapertura',
            name='radicado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Radicados'),
        ),
        migrations.AlterField(
            model_name='dibuartetallercontenidoseducativos',
            name='radicado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Radicados'),
        ),
        migrations.AlterField(
            model_name='documentolegalizacionterminales',
            name='radicado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Radicados'),
        ),
        migrations.AlterField(
            model_name='ecoraeetallerraee',
            name='radicado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Radicados'),
        ),
        migrations.AlterField(
            model_name='infotictalleradministratic',
            name='radicado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Radicados'),
        ),
        migrations.AlterField(
            model_name='registrofotograficotalleradministratic',
            name='radicado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Radicados'),
        ),
        migrations.AlterField(
            model_name='registrofotograficotallerapertura',
            name='radicado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Radicados'),
        ),
        migrations.AlterField(
            model_name='registrofotograficotallercontenidoseducativos',
            name='radicado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Radicados'),
        ),
        migrations.AlterField(
            model_name='registrofotograficotallerraee',
            name='radicado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Radicados'),
        ),
        migrations.AlterField(
            model_name='relatoriatalleradministratic',
            name='radicado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Radicados'),
        ),
        migrations.AlterField(
            model_name='relatoriatallerapertura',
            name='radicado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Radicados'),
        ),
        migrations.AlterField(
            model_name='relatoriatallercontenidoseducativos',
            name='radicado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Radicados'),
        ),
        migrations.AlterField(
            model_name='relatoriatallerraee',
            name='radicado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cpe_2018.Radicados'),
        ),
    ]
