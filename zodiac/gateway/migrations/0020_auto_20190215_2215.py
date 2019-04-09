# Generated by Django 2.0.8 on 2019-02-16 03:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gateway', '0019_auto_20190116_1001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestlog',
            name='service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requestlog', to='gateway.ServiceRegistry'),
        ),
    ]
