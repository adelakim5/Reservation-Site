# Generated by Django 2.2.6 on 2019-11-03 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0013_auto_20191103_2300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='food',
            name='price',
            field=models.IntegerField(blank='True', default=0, null=True),
        ),
    ]
