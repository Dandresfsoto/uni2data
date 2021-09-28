# Generated by Django 2.2.24 on 2021-09-28 14:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('direccion_financiera', '0048_auto_20210928_0948'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='purchaseorders',
            options={'verbose_name_plural': 'Ordenes de compra'},
        ),
        migrations.AddField(
            model_name='purchaseorders',
            name='project_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='direccion_financiera.Projects_order'),
        ),
        migrations.AlterField(
            model_name='purchaseorders',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='direccion_financiera.Proyecto'),
        ),
    ]
