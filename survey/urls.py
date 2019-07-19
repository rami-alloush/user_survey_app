from django.urls import path
from . import views


app_name = 'survey'
urlpatterns = [
    # ex: /survey/
    path('', views.index, name='index'),
    # ex: /survey/5/
    path('<int:question_id>/', views.detail, name='detail'),
    # ex: /survey/5/results/
    path('<int:question_id>/results/', views.results, name='results'),
    # ex: /survey/5/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),
]