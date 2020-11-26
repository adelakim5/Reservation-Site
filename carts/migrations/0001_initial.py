# Generated by Django 3.1.3 on 2020-11-26 14:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0004_auto_20191126_0023'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('people', models.PositiveIntegerField(default=0)),
                ('total_price', models.PositiveIntegerField(default=0)),
                ('request_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('phone', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Cart2',
            fields=[
                ('tid', models.CharField(default='default', max_length=30, primary_key=True, serialize=False)),
                ('order_id', models.PositiveIntegerField(default=0)),
                ('people', models.PositiveIntegerField(default=0)),
                ('total_price', models.PositiveIntegerField(default=0)),
                ('request_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(choices=[('-1', 'failed'), ('0', 'pending'), ('1', 'approved')], default='0', max_length=3)),
                ('phone', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=100)),
                ('others', models.TextField()),
                ('customer', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('whose', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.profile')),
            ],
        ),
        migrations.CreateModel(
            name='Cart3',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.PositiveIntegerField(default=0)),
                ('people', models.PositiveIntegerField(default=0)),
                ('total_price', models.PositiveIntegerField(default=0)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(default='0', max_length=3)),
                ('receiver', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.profile')),
                ('sender', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
