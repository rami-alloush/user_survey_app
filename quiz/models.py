import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Course(models.Model):
    course_name = models.CharField(max_length=300)

    def __str__(self):
        return self.course_name


class Question(models.Model):
    question_text = models.CharField(max_length=300)
    question_choice_1 = models.CharField(max_length=300)
    question_choice_2 = models.CharField(max_length=100)
    question_choice_3 = models.CharField(max_length=100)
    question_choice_4 = models.CharField(max_length=100)
    question_answer = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(4)])
    pub_date = models.DateTimeField('Date published', default=timezone.now)

    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Score(models.Model):
    user = models.ForeignKey(User, verbose_name='User',
                             on_delete=models.CASCADE)
    date = models.DateTimeField('Quiz Date', default=timezone.now)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username + " - score: " + str(self.score)

