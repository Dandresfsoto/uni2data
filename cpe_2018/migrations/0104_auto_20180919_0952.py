# Generated by Django 2.0.1 on 2018-09-19 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cpe_2018', '0103_auto_20180914_0814'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentolegalizacionterminales',
            name='tipo',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='relatoriatalleradministratic',
            name='tipo',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='relatoriatallerapertura',
            name='tipo',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='relatoriatallercontenidoseducativos',
            name='tipo',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='relatoriatallerraee',
            name='tipo',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='retoma',
            name='tipo',
            field=models.CharField(default='', max_length=100),
        ),
    ]
