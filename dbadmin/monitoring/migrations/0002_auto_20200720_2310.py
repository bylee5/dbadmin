# Generated by Django 3.0.6 on 2020-07-20 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='JobInfo',
        ),
        migrations.DeleteModel(
            name='JobServerMap',
        ),
        migrations.DeleteModel(
            name='ServerList',
        ),
    ]
