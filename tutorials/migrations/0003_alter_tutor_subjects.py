# Generated by Django 5.1.2 on 2024-12-12 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0002_alter_tutor_subjects'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutor',
            name='subjects',
            field=models.ManyToManyField(related_name='tutors', to='tutorials.subject'),
        ),
    ]
