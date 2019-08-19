import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from uuid import uuid4


class Course(models.Model):
    course_name = models.CharField(max_length=300)

    def __str__(self):
        return self.course_name


class Chapter(models.Model):
    chapter_name = models.CharField(max_length=300)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.course.course_name, self.chapter_name)


class Question(models.Model):
    question_text = models.CharField(max_length=300)
    question_choice_1 = models.CharField(max_length=300)
    question_choice_2 = models.CharField(max_length=100)
    question_choice_3 = models.CharField(max_length=100)
    question_choice_4 = models.CharField(max_length=100)
    question_answer = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(4)])
    pub_date = models.DateTimeField('Date published', default=timezone.now)

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Score(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='User',
                             on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField('Quiz Date', default=timezone.now)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username + " - score: " + str(self.score)


class TokenManager(models.Manager):
    def get_queryset(self):
        now = timezone.now()
        week_ago = now - datetime.timedelta(days=7)
        return super(TokenManager, self).get_queryset().filter(date__gte=week_ago)


class QuizToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default='1')

    objects = models.Manager()
    active = TokenManager()

    def still_active(self):
        now = timezone.now()
        return self.date + datetime.timedelta(days=7) >= now

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid4()
        return super(QuizToken, self).save(*args, **kwargs)


# def retrieve_token(request, token=''):
#     access_token = UserAccessToken.objects.filter(token=token, used=False)
#     if access_token:
#         # Replace queryset with model instance
#         access_token = access_token[0]
#         access_token.used = True
#         access_token.save()
#         response = HttpResponse(access_token.download,
#                                 content_type='text/plain')
#         response['Content-Disposition'] = 'attachment; filename=download.zip'
#         return response
#     else:
#         return HttpResponse(status_code=404)
