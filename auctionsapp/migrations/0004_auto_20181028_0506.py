# Generated by Django 2.1 on 2018-10-28 05:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctionsapp', '0003_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auction',
            name='photo',
        ),
        migrations.RemoveField(
            model_name='auction',
            name='slug',
        ),
    ]