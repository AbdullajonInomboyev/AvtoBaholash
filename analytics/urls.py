from django.urls import path
from . import views

app_name = 'analytics'
urlpatterns = [
    path('kafedra/', views.kafedra_analytics, name='kafedra'),
    path('teacher/', views.teacher_analytics, name='teacher'),
    path('student/', views.student_analytics, name='student'),
    path('admin/',   views.admin_analytics,   name='admin'),
    path('api/',     views.analytics_api,     name='api'),
]
