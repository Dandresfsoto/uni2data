# Generated by Django 2.0.1 on 2018-03-21 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recursos_humanos', '0016_auto_20180320_1721'),
    ]

    operations = [
        migrations.AddField(
            model_name='contratistas',
            name='tipo_cuenta',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
