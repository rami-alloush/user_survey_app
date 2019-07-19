from django.db import models


class Question(models.Model):
    question_text = models.CharField(max_length=300)
    pub_date = models.DateTimeField('Date published')


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)