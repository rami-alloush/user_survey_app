# Generated by Django 2.1.1 on 2019-08-19 16:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0007_auto_20190815_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiztoken',
            name='course',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='quiz.Course'),
        ),
    ]