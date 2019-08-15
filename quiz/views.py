import random
import datetime
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail, EmailMessage
from django.views import generic
from django.utils import timezone
from .models import Course, Question, Score, QuizToken
from .forms import CourseSelectForm
from quiz import settings as QuizSettings
from django.conf import settings

User = get_user_model()


def startQuiz(request):
    # Reset quiz session
    request.session['score'] = 0
    request.session['count'] = 0

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CourseSelectForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            course_id = form['course_name'].value()
            course_name = form.cleaned_data['course_name']

            # Check if user can still take quiz for this course
            if request.user.is_authenticated:

                # Check for Previous Attemps
                user_course_scores = Score.objects.filter(
                    user=request.user,
                    course_id=course_id,
                ).count()
                course_attempts = getattr(QuizSettings, 'COURSE_ATTEMPTS')
                # Fail for Attempts Limit
                if (user_course_scores >= course_attempts):
                    messages.add_message(request, messages.ERROR,
                                         'You have already attempted the %s quiz %s times!' % (course_name, course_attempts))
                    return HttpResponseRedirect('/quiz/')

                # Check for Last Attempt time
                yesterday = timezone.now() - datetime.timedelta(days=1)
                user_recent_attempts = Score.objects.filter(
                    user=request.user,
                    course_id=course_id,
                    date__gte=yesterday,
                ).count()
                # Fail for recent Attempt
                if (user_recent_attempts > 0):
                    messages.add_message(request, messages.ERROR,
                                         'You must wait 24 hrs to access the quiz for this course again :/')
                    return HttpResponseRedirect('/quiz/')

                # Check for Tokens
                user_active_tokens_count = QuizToken.active.filter(
                    user=request.user).count()
                # Fail for no active token
                if (user_active_tokens_count < 1):
                    messages.add_message(request, messages.ERROR,
                                         'You don\'t have active tokens to access the quiz :/')
                    return HttpResponseRedirect('/quiz/')

            next_question_id = getNextRandQuestion(course_id)
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('quiz:detail', args=(course_id, next_question_id,)))

    # if a GET (or any other method)
    else:
        messages.add_message(request, messages.ERROR,
                             'You are not allowed to access this page!')
        return HttpResponseRedirect('/quiz/')


class IndexView(generic.ListView):
    model = Score
    template_name = 'quiz/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context.update({
            'form': CourseSelectForm(),
        })
        return context

    def get_queryset(self):
        """
        Return the current users scores
        """
        # Enforce quiz session reset
        self.request.session['score'] = 0
        self.request.session['count'] = 0

        user = self.request.user
        if user.is_authenticated:
            return Score.objects.filter(
                user=self.request.user
            )
        else:
            return None


class DetailView(generic.DetailView):
    model = Question
    template_name = 'quiz/detail.html'


def VoteView(request, question_id):
    # Check for valid choice
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = int(request.POST['choice'])
    except (KeyError, MultiValueDictKeyError):
        # Redisplay the question voting form.
        return render(request, 'quiz/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        # Check if answer is correct and update score
        if question.question_answer == selected_choice:
            print('Correct answer :)')
            request.session['score'] = request.session['score'] + 1
        else:
            print('Wrong answer :(')

        # Increase questions count
        questions_count = request.session['count'] + 1
        request.session['count'] = questions_count

        # Decide the next question and redirect
        chapter_id = question.chapter_id
        course_id = question.chapter.course.id
        next_question_id = getNextRandQuestion(chapter_id)

        # Check the limit for number of questions per quiz
        questions_limit = getattr(QuizSettings, 'QUIZ_QUESTIONS')
        print("questions_count", questions_count)
        if (questions_count < questions_limit):
            return HttpResponseRedirect(reverse('quiz:detail', args=(chapter_id, next_question_id), ))
        else:
            # Last page, save score
            if request.user.is_authenticated:
                score = Score(user=request.user,
                              course_id=course_id,
                              score=request.session['score'])
                score.save()
            return HttpResponseRedirect(reverse('quiz:thanks',))


def ThanksView(request):
    template_name = 'quiz/thanks.html'
    return render(request, template_name,)


class AdminView(generic.ListView):
    model = User
    template_name = 'quiz/admin.html'

    def get_context_data(self, **kwargs):
        context = super(AdminView, self).get_context_data(**kwargs)
        context.update({
            'form': None,
        })
        return context


def CreateToken(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        data = request.POST
        user = User.objects.get(id=data['user_id'])
        new_token = QuizToken(user=user)
        new_token.save()
        domain = request.META['HTTP_HOST']
        sendTokenEmail(new_token, user, domain)

        messages.add_message(request, messages.INFO,
                             'Token created and email sent for user with ID: %s' % user.id)
        return HttpResponseRedirect('/quiz/admin')

    # if a GET (or any other method)
    else:
        messages.add_message(request, messages.ERROR,
                             'You are not allowed to access this page!')
        return HttpResponseRedirect('/quiz/admin')


def sendTokenEmail(token, user, domain):
    # send_mail(
    #     'You can access the quiz now!',
    #     'Hi,\nYou now have access to the quiz using this link: ' + str(token.token) + '\nYour access will expire after 7 days on: ' + str(timezone.now() + datetime.timedelta(days=7)),
    #     'Nora@rmasoft.com',
    #     [user.email],
    #     # fail_silently=False,
    # )

    # send as HTML
    msg = EmailMessage('You can access the quiz now!',
                       'Hi,<br>You now have access to the quiz using ' +
                       '<a href="http://' + domain + '/quiz?token=' + str(token.token) + '">this link</a>' +
                       '<br>Your access will expire after 7 days on: ' +
                       str(timezone.now() + datetime.timedelta(days=7)) +
                       '<br><br>Best Regards,',
                       'Nora@example.com',
                       [user.email]
                       )
    msg.content_subtype = "html"
    msg.send()


def getNextRandQuestion(course_id):
    # Filter with chapter
    course_questions = list(Question.objects.filter(
        chapter=course_id).values_list('pk', flat=True))
    return random.choice(course_questions)
