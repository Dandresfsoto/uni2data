# Generated by Django 2.0.1 on 2018-06-21 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0017_entregablerutaobject_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='entregablerutaobject',
            name='actualizacion',
            field=models.BooleanField(default=False),
        ),
    ]
