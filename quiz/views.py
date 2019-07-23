from django.utils.datastructures import MultiValueDictKeyError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.views import generic
from django.utils import timezone
from .models import Question

def IndexView(request):    
    return render(request, 'quiz/index.html')

class DetailView(generic.DetailView):
    model = Question
    template_name = 'quiz/detail.html'

def VoteView(request, question_id):
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
        else:
            print('Wrong answer :(')
            
        next_question_id = question.id + 1
        next_question = Question.objects.filter(pk=next_question_id).count()
        if (next_question > 0):
            return HttpResponseRedirect(reverse('survey:detail', args=(next_question_id,)))
        else:
            return HttpResponseRedirect(reverse('survey:thanks',))

def ThanksView(request):
    template_name = 'quiz/thanks.html'
    return render(request, template_name,)