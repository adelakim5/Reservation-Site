# Generated by Django 2.2.6 on 2019-11-23 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0010_auto_20191122_1658'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='phone',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cart2',
            name='phone',
            field=models.PositiveIntegerField(default=0),
        ),
    ]