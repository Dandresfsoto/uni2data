# Generated by Django 2.0.1 on 2018-08-10 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0077_auto_20180810_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cuentascobro',
            name='valores_json',
            field=models.TextField(blank=True, default='[]', null=True),
        ),
    ]
