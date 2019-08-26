import random
import datetime
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.core.mail import send_mail, EmailMessage
from django.views import generic
from django.utils import timezone
from .models import Course, Question, Score, QuizToken
from .forms import CourseSelectForm
from quiz import settings as QuizSettings
from django.conf import settings

User = get_user_model()
questions_limit = getattr(QuizSettings, 'QUIZ_QUESTIONS')
course_attempts = getattr(QuizSettings, 'COURSE_ATTEMPTS')
quiz_duration = getattr(QuizSettings, 'QUIZ_DURATION_MINUTES')
pass_score = getattr(QuizSettings, 'PASS_SCORE')


def startQuiz(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CourseSelectForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            course_id = form['course_name'].value()
            request.session['course_id'] = course_id
            course_name = form.cleaned_data['course_name']

            # Check if user can still take quiz for this course
            if request.user.is_authenticated:

                # Check for Previous Attemps
                user_course_scores = Score.objects.filter(
                    user=request.user,
                    course_id=course_id,
                ).count()
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
                    user=request.user,
                    course_id=course_id,
                ).count()
                # Fail for no active token
                if (user_active_tokens_count < 1):
                    messages.add_message(request, messages.ERROR,
                                         'You don\'t have active tokens to access the quiz of this course :/')
                    return HttpResponseRedirect('/quiz/')

                # Check for enough questions in course
                course_questions = Question.objects.all().values(
                    'chapter__course').filter(
                    chapter__course=course_id).annotate(
                    total=Count('chapter__course'))
                course_questions_total = course_questions[0]['total']
                # Fail for not enough questions
                if (course_questions_total < questions_limit):
                    messages.add_message(request, messages.ERROR,
                                         'There are no enough questions in the DB for this course!')
                    return HttpResponseRedirect(reverse('quiz:index', ))

                # Everythong is OK, start quiz session
                request.session['active_quiz'] = True
                request.session['result'] = ''
                request.session['seen_questions'] = []
                request.session['seen_questions_scores'] = []
                # Set Quiz End Time
                now = timezone.now()
                end_time = now + datetime.timedelta(minutes=quiz_duration)
                request.session['quiz_start'] = end_time.strftime(
                    '%b %d, %Y %H:%M:%S')  # UTC time

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
        self.request.session['active_quiz'] = False
        self.request.session['result'] = ''
        self.request.session['seen_questions'] = []
        self.request.session['seen_questions_scores'] = []

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

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        question_id = context['object'].id
        seen_questions = self.request.session['seen_questions']
        seen_questions_scores = self.request.session['seen_questions_scores']
        # Check if new question
        if not question_id in seen_questions:
            # New Question
            # add current question to seen questions
            seen_questions.append(question_id)
            self.request.session['seen_questions'] = seen_questions
            seen_questions_scores.append(None)
            self.request.session['seen_questions_scores'] = seen_questions_scores

        print(seen_questions)
        print(seen_questions_scores)

        question_index = seen_questions.index(question_id)
        try:
            question_score = seen_questions_scores[question_index]
            # Check if answered before
            if question_score is not None:
                context['send'] = True
        except:
            pass

        # Send start time with context
        context['quiz_start'] = self.request.session['quiz_start']
        # Send questions progress with context
        context['current_question'] = question_index + 1
        context['total_questions'] = questions_limit
        if question_index > 0:
            context['previous'] = True
        if question_index + 1 < questions_limit:
            context['next'] = True
        if len(seen_questions) == questions_limit and not None in seen_questions_scores:
            context['can_submit'] = True
        return context


def VoteView(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    course_id = question.chapter.course.id
    seen_questions = request.session['seen_questions']
    seen_questions_scores = request.session['seen_questions_scores']
    # Get clicked button
    if request.POST.get("send"):
        # Check if first time question
        selected_choice = int(request.POST['choice'])
        question_id_index = seen_questions.index(question_id)
        # Check if answer is correct and update score
        if question.question_answer == selected_choice:
            print('Correct answer :)')
            seen_questions_scores[question_id_index] = 1
        else:
            print('Wrong answer :(')
            seen_questions_scores[question_id_index] = 0

        # Update session
        request.session['seen_questions_scores'] = seen_questions_scores
        return HttpResponseRedirect(reverse('quiz:detail', args=(course_id, question_id), ))

    else:
        # No answer submitted
        current_question_id_index = seen_questions.index(question_id)
        if request.POST.get("previous"):
            previous_question_id = seen_questions[current_question_id_index - 1]
            return HttpResponseRedirect(reverse('quiz:detail', args=(course_id, previous_question_id), ))

        if request.POST.get("next"):
            # check if seen next question exist
            try:
                next_question_id = seen_questions[current_question_id_index + 1]
                return HttpResponseRedirect(reverse('quiz:detail', args=(course_id, next_question_id), ))
            except:
                # Create new question
                if (len(seen_questions) < questions_limit):
                    next_question_id = getNextRandQuestion(
                        course_id, seen_questions)
                    return HttpResponseRedirect(reverse('quiz:detail', args=(course_id, next_question_id), ))
                else:
                    # No Next btn should be visible
                    return HttpResponseRedirect(reverse('quiz:thanks', ))

        if request.POST.get("submit_quiz"):
            return HttpResponseRedirect(reverse('quiz:thanks', ))


def ThanksView(request):
    # Last page, save score
    score_total = sum(request.session['seen_questions_scores'])
    if request.user.is_authenticated:
        if request.session['active_quiz']:
            score = Score(user=request.user,
                          course_id=request.session['course_id'],
                          score=score_total)
            score.save()

            # Determine result
            if (score.score >= pass_score):
                request.session['result'] = "Pass"
            else:
                request.session['result'] = "Fail"
            request.session['active_quiz'] = False
        else:
            return HttpResponseRedirect(reverse('quiz:index', ))

    template_name = 'quiz/thanks.html'
    return render(request, template_name, {'score': score_total})


class AdminView(generic.ListView):
    model = User
    template_name = 'quiz/admin.html'

    def get_context_data(self, **kwargs):
        context = super(AdminView, self).get_context_data(**kwargs)
        context.update({
            'courses': Course.objects.all(),
        })
        return context


def CreateToken(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        data = request.POST
        user = User.objects.get(id=data['user_id'])
        course = Course.objects.get(id=data['course_id'])
        new_token = QuizToken(user=user, course=course)
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


def getNextRandQuestion(course_id, seen_questions=[]):
    # Filter with chapter
    try:
        course_questions = list(Question.objects.filter(
            chapter__course_id=course_id).exclude(id__in=seen_questions).values_list('pk', flat=True))
        return random.choice(course_questions)
    except (ValueError, IndexError) as err:
        print("No Enough Questions in DB:", err.args)
