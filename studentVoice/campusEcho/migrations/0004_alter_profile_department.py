# Generated by Django 5.0.3 on 2024-03-09 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campusEcho', '0003_alter_faculty_name_alter_profile_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='department',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
