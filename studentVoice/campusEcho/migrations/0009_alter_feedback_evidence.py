# Generated by Django 5.0.3 on 2024-03-10 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campusEcho', '0008_user_is_staff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='evidence',
            field=models.ImageField(blank=True, null=True, upload_to='feedback_evidence/'),
        ),
    ]
