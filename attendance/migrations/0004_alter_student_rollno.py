# Generated by Django 5.1.3 on 2025-01-16 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0003_alter_attendance_subject_alter_student_rollno'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='rollno',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
