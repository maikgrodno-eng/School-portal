from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import Teacher, Student, Subject, Grade
from .forms import LoginForm
from datetime import date
from collections import defaultdict
from django.contrib.auth.decorators import login_required


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


@login_required
def teacher_dashboard(request):
    """Личный кабинет учителя"""
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return redirect('home')

    # Получаем предметы и классы учителя
    subjects = teacher.subjects.all()
    classes = teacher.classes.all()

    context = {
        'teacher': teacher,
        'subjects': subjects,
        'classes': classes,
    }
    return render(request, 'teacher_dashboard.html', context)



@login_required
def add_grade(request):
    """Добавление оценки (для учителя) - 10-балльная система"""
    try:
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return redirect('home')

    # Получаем всех учеников из классов учителя
    students_in_classes = Student.objects.filter(class_field__in=teacher.classes.all()).select_related('user',
                                                                                                       'class_field')

    # Группируем учеников по классам для удобства
    students_by_class = defaultdict(list)

    for student in students_in_classes:
        if student.class_field:
            students_by_class[student.class_field].append(student)

    if request.method == 'POST':
        student_id = request.POST.get('student')
        subject_id = request.POST.get('subject')
        grade_value = request.POST.get('grade')
        date_str = request.POST.get('date')

        try:
            student = Student.objects.get(id=student_id)
            subject = Subject.objects.get(id=subject_id)

            # Проверяем оценку (1-10)
            grade_int = int(grade_value)
            if grade_int < 1 or grade_int > 10:
                messages.error(request, 'Оценка должна быть от 1 до 10')
                return redirect('add_grade')

            # Проверяем, ведет ли учитель этот предмет у этого класса
            if (subject in teacher.subjects.all() and
                    student.class_field in teacher.classes.all()):

                Grade.objects.create(
                    student=student,
                    subject=subject,
                    grade=grade_value,
                    date=date_str
                )
                messages.success(request,
                                 f'✅ Оценка {grade_value} по предмету "{subject.name}" успешно добавлена ученику {student.user.last_name} {student.user.first_name}'
                                 )
                return redirect('add_grade')
            else:
                messages.error(request, '❌ У вас нет прав на добавление оценки по этому предмету или для этого класса')

        except ValueError:
            messages.error(request, '❌ Оценка должна быть числом от 1 до 10')
        except Student.DoesNotExist:
            messages.error(request, '❌ Ученик не найден')
        except Subject.DoesNotExist:
            messages.error(request, '❌ Предмет не найден')
        except Exception as e:
            messages.error(request, f'❌ Ошибка: {str(e)}')

    context = {
        'teacher': teacher,
        'students_by_class': dict(students_by_class),
        'subjects': teacher.subjects.all(),
        'today': date.today().strftime('%Y-%m-%d'),
    }
    return render(request, 'add_grade.html', context)