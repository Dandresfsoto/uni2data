# Generated by Django 2.0.1 on 2018-06-08 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0007_entregables'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entregables',
            name='cantidad',
        ),
        migrations.AddField(
            model_name='entregables',
            name='modelo',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
