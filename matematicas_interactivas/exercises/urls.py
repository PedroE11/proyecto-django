from django.urls import path
from . import views

urlpatterns = [
    path('config/', views.exercise_config, name='exercise_config'),
    path('solve/', views.exercise_solve, name='exercise_solve'),
    path('results/<int:session_id>/', views.exercise_results, name='exercise_results'),
    path('history/', views.exercise_history, name='exercise_history'),
]