from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import Teacher, Student, Subject, Grade, Parent
from .forms import LoginForm
from datetime import date
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.db.models import Avg


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

            try:
                student = Student.objects.get(student_id=user_id, password=password)
                user = student.user
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
                return redirect('student_dashboard')
            except Student.DoesNotExist:
                pass


            try:
                parent = Parent.objects.get(parent_id=user_id, password=password)
                user = parent.user
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
                return redirect('parent_dashboard')
            except Parent.DoesNotExist:
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

    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return redirect('home')

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

    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        return redirect('home')

    students_in_classes = Student.objects.filter(class_field__in=teacher.classes.all()).select_related('user',
                                                                                                       'class_field')
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

            grade_int = int(grade_value)
            if grade_int < 1 or grade_int > 10:
                messages.error(request, 'Оценка должна быть от 1 до 10')
                return redirect('add_grade')

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


@login_required
def student_dashboard(request):

    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return redirect('home')

    grades = Grade.objects.filter(student=student).order_by('-date')

    subjects_dict = defaultdict(list)

    for grade in grades:
        subjects_dict[grade.subject].append(grade)

    subjects_grades_data = []
    total_grades_count = 0
    all_grades_sum = 0
    grade_stats = {i: 0 for i in range(1, 11)}

    for subject, subject_grades in subjects_dict.items():
        subject_grades_count = len(subject_grades)
        subject_grades_sum = sum(grade.grade for grade in subject_grades)
        subject_average = subject_grades_sum / subject_grades_count if subject_grades_count > 0 else 0

        for grade in subject_grades:
            if 1 <= grade.grade <= 10:
                grade_stats[grade.grade] = grade_stats.get(grade.grade, 0) + 1

        subjects_grades_data.append({
            'subject': subject,
            'grades': subject_grades,
            'average': subject_average,
            'count': subject_grades_count
        })

        total_grades_count += subject_grades_count
        all_grades_sum += subject_grades_sum

    average_grade = all_grades_sum / total_grades_count if total_grades_count > 0 else 0

    context = {
        'student': student,
        'subjects_grades_data': subjects_grades_data,
        'total_grades_count': total_grades_count,
        'average_grade': average_grade,
        'grade_stats': grade_stats,
    }
    return render(request, 'student_dashboard.html', context)


@login_required
def parent_dashboard(request):

    try:
        parent = request.user.parent_profile
    except Parent.DoesNotExist:
        return redirect('home')

    children = parent.students.all().select_related('user', 'class_field')

    children_with_grades = []
    for child in children:
        grades = Grade.objects.filter(student=child).select_related('subject').order_by('-date')

        subjects_data = []
        for subject in Subject.objects.all():
            subject_grades = grades.filter(subject=subject)
            if subject_grades.exists():
                avg = subject_grades.aggregate(avg=Avg('grade'))['avg']
                subjects_data.append({
                    'subject': subject,
                    'grades': list(subject_grades),
                    'average': round(avg, 2) if avg else 0
                })

        children_with_grades.append({
            'child': child,
            'grades': grades,
            'subjects_data': subjects_data
        })

    context = {
        'parent': parent,
        'children': children,
        'children_with_grades': children_with_grades,
    }
    return render(request, 'parent_dashboard.html', context)