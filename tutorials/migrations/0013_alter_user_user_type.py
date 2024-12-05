# Generated by Django 5.1.2 on 2024-12-03 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0012_alter_user_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('student', 'Student'), ('tutor', 'Tutor')], default='student', max_length=10),
        ),
    ]
