from django.urls import path
from . import views


app_name = 'survey'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('thanks/', views.ThanksView, name='thanks'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:question_id>/vote/', views.VoteView, name='vote'),
]
