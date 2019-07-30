from django.utils.datastructures import MultiValueDictKeyError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.views import generic
from django.utils import timezone
from .models import Course, Question, Score
from .forms import CourseSelectForm


def startQuiz(request):
    request.session['score'] = 0
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CourseSelectForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            course_id = form['course_name'].value()
            # redirect to a new URL:
            # return HttpResponseRedirect('/quiz/thanks/')
            return HttpResponseRedirect(reverse('quiz:detail', args=(course_id,1),))

    # if a GET (or any other method)
    else:
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
        self.request.session['score'] = 0
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
    # Reset score on start
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
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        if question.question_answer == selected_choice:
            print('Correct answer :)')
            request.session['score'] = request.session['score'] + 1
        else:
            print('Wrong answer :(')

        next_question_id = question.id + 1
        next_question = Question.objects.filter(pk=next_question_id).count()
        if (next_question > 0):
            return HttpResponseRedirect(reverse('quiz:detail', args=(next_question_id,), ))
        else:
            # Last page, save score
            if request.user.is_authenticated:
                score = Score(user=request.user,
                              score=request.session['score'])
                score.save()
            return HttpResponseRedirect(reverse('quiz:thanks',))


def ThanksView(request):
    template_name = 'quiz/thanks.html'
    return render(request, template_name,)
