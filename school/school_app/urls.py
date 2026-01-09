from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/add-grade/', views.add_grade, name='add_grade'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('parent/dashboard/', views.parent_dashboard, name='parent_dashboard')
]