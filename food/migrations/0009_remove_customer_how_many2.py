# Generated by Django 2.2.6 on 2019-11-22 07:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0008_auto_20191122_0113'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='how_many2',
        ),
    ]