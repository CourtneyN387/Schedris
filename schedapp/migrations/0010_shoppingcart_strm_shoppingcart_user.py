# Generated by Django 4.1.7 on 2023-04-17 23:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedapp', '0009_schedule_approval_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingcart',
            name='strm',
            field=models.IntegerField(default=1228),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
