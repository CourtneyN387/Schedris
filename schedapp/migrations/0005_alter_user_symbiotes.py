# Generated by Django 4.1.6 on 2023-03-16 18:31

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedapp', '0004_schedule_courses'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='symbiotes',
            field=models.ManyToManyField(blank=True, related_name='symbiotes_of', to=settings.AUTH_USER_MODEL),
        ),
    ]
