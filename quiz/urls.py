from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views


app_name = 'quiz'
urlpatterns = [
    # use name for reverse function
    path('', views.IndexView.as_view(), name='index'),
    path('admin/', login_required(views.AdminView.as_view()),
         name='admin'),  # use name for reverse function
    path('start/', login_required(views.startQuiz), name='start'),
    path('admin/create_token/',
         login_required(views.CreateToken), name='create_token'),
    # path('<int:pk>/', login_required(views.DetailView.as_view()), name='detail'),
    path('course/<int:pk_course>/<int:pk>/',
         login_required(views.DetailView.as_view()), name='detail'),
    path('<int:question_id>/vote/', login_required(views.VoteView), name='vote'),
    path('thanks/', login_required(views.ThanksView), name='thanks'),
]
