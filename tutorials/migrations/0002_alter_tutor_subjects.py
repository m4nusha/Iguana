# Generated by Django 5.1.2 on 2024-12-12 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutor',
            name='subjects',
            field=models.ManyToManyField(default='python', related_name='tutors', to='tutorials.subject'),
        ),
    ]