# Generated by Django 2.2.6 on 2019-11-18 02:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0004_customer_how_many2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='how_many',
        ),
    ]