from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views


app_name = 'quiz'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),  # use name for reverse function
    path('admin/', login_required(views.AdminView.as_view()), name='admin'),  # use name for reverse function
    path('start/', login_required(views.startQuiz), name='start'),
    # path('<int:pk>/', login_required(views.DetailView.as_view()), name='detail'),
    path('course/<int:pk_course>/<int:pk>/', login_required(views.DetailView.as_view()), name='detail'),
    path('<int:question_id>/vote/', login_required(views.VoteView), name='vote'),
    path('thanks/', login_required(views.ThanksView), name='thanks'),
]
