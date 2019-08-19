from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.views import generic
from django.utils import timezone
from .models import Question, Choice


class IndexView(generic.ListView):
    template_name = 'survey/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


def ThanksView(request):
    template_name = 'survey/thanks.html'
    return render(request, template_name,)


class DetailView(generic.DetailView):
    model = Question
    template_name = 'survey/detail.html'

    def get_queryset(self):
        """ Exclude any unpublished questions. """
        return Question.objects.filter(pub_date__lte=timezone.now())

    # def render_to_response(self, context):
    #     print("render_to_response")
    #     if len(self.model.objects.all()) == 0:
    #         return HttpResponseRedirect(reverse('survey:detail', args=(11,)))
    #     return super().render_to_response(context)


def VoteView(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'survey/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        next_question_id = question.id + 1
        next_question = Question.objects.filter(pk=next_question_id).count()
        if (next_question > 0):
            return HttpResponseRedirect(reverse('survey:detail', args=(next_question_id,)))
        else:
            return HttpResponseRedirect(reverse('survey:thanks',))
