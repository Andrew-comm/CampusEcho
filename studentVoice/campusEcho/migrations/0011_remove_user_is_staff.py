# Generated by Django 5.0.3 on 2024-03-11 16:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campusEcho', '0010_feedback_solution'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_staff',
        ),
    ]
