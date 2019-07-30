import random
from django.utils.datastructures import MultiValueDictKeyError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.contrib import messages
from django.views import generic
from django.utils import timezone
from .models import Course, Question, Score
from .forms import CourseSelectForm
from quiz import settings as QuizSettings


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
                user_course_scores = Score.objects.filter(
                    user=request.user,
                    course_id=course_id,
                ).count()
                course_attempts = getattr(QuizSettings, 'COURSE_ATTEMPTS')
                if (user_course_scores >= course_attempts):
                    messages.add_message(request, messages.ERROR,
                             'You have already attempted the %s quiz %s times!' % (course_name, course_attempts))
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
        course_id = question.course_id
        next_question_id = getNextRandQuestion(course_id)

        # Check the limit for number of questions per quiz
        questions_limit = getattr(QuizSettings, 'QUIZ_QUESTIONS')
        print("questions_count", questions_count)
        if (questions_count < questions_limit):
            return HttpResponseRedirect(reverse('quiz:detail', args=(course_id, next_question_id), ))
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


def getNextRandQuestion(course_id):
    course_questions = list(Question.objects.filter(
        course=course_id).values_list('pk', flat=True))
    return random.choice(course_questions)
