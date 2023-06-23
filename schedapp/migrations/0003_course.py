# Generated by Django 4.1.6 on 2023-03-16 00:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedapp', '0002_alter_user_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('subject', models.CharField(max_length=10)),
                ('catalog_number', models.CharField(max_length=20)),
                ('class_section', models.CharField(max_length=20)),
                ('class_number', models.IntegerField(primary_key=True, serialize=False)),
                ('class_title', models.CharField(max_length=250)),
                ('class_topic_formal_desc', models.CharField(max_length=600)),
                ('instructor', models.CharField(max_length=200)),
                ('enrollment_capacity', models.IntegerField()),
                ('meeting_days', models.CharField(max_length=10)),
                ('meeting_time_start', models.CharField(max_length=10)),
                ('meeting_time_end', models.CharField(max_length=10)),
                ('term', models.CharField(max_length=10)),
                ('term_desc', models.CharField(max_length=20)),
            ],
        ),
    ]