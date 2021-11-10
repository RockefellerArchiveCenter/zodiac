# Generated by Django 3.2.5 on 2021-10-14 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gateway', '0005_alter_user_first_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviceregistry',
            name='callback_service',
        ),
        migrations.AddField(
            model_name='serviceregistry',
            name='has_external_trigger',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='serviceregistry',
            name='external_uri',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='serviceregistry',
            name='name',
            field=models.CharField(max_length=128),
        ),
    ]
