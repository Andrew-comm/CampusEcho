# Generated by Django 5.0.3 on 2024-03-13 22:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('campusEcho', '0016_feedback_student_phone_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedback',
            name='student_phone_number',
        ),
    ]
