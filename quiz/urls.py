from django.urls import path
from . import views


app_name = 'quiz'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),  # use name for reverse function
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:question_id>/vote/', views.VoteView, name='vote'),
    path('thanks/', views.ThanksView, name='thanks'),
]
