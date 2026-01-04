from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Teacher, Subject

from .forms import LoginForm


def home(request):

    return render(request, 'home.html')

def user_login(request):

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            password = form.cleaned_data['password']

            try:
                teacher = Teacher.objects.get(teacher_id=user_id, password=password)
                user = teacher.user
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
                return redirect('teacher_dashboard')
            except Teacher.DoesNotExist:
                pass

            messages.error(request, 'Неверный ID или пароль')

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def user_logout(request):
    
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('home')