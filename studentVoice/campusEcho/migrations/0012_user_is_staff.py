# Generated by Django 5.0.3 on 2024-03-11 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campusEcho', '0011_remove_user_is_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
    ]
