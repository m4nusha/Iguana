# Generated by Django 5.1.2 on 2024-11-30 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0010_merge_0008_alter_tutor_subject_0009_student_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('student', 'Student'), ('tutor', 'Tutor')], default='student', max_length=10),
        ),
    ]
