# Generated by Django 2.2.6 on 2019-11-25 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0012_auto_20191123_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='address',
            field=models.CharField(default='', max_length=100),
        ),
    ]