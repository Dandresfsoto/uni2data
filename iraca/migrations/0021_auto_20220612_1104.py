# Generated by Django 2.2.24 on 2022-06-12 16:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('iraca', '0020_auto_20220611_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='types',
            name='certificate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='iraca.Certificates'),
        ),
    ]