# Generated by Django 2.2.24 on 2022-06-11 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iraca', '0019_auto_20220611_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='milestones',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
    ]