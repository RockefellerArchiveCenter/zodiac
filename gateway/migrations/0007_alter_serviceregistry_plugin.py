# Generated by Django 3.2.9 on 2021-11-23 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gateway', '0006_auto_20211014_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceregistry',
            name='plugin',
            field=models.IntegerField(choices=[(0, 'Remote auth'), (2, 'Key auth')], default=0),
        ),
    ]