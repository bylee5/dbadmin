# Generated by Django 3.0.4 on 2020-07-10 01:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_post'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Faq',
        ),
        migrations.DeleteModel(
            name='Post',
        ),
    ]
