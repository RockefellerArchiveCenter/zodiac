# Generated by Django 2.2.10 on 2020-03-23 23:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gateway', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviceregistry',
            name='post_service',
        ),
    ]
