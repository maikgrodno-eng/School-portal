from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import Teacher, Student, Subject, Grade, Parent
from .forms import LoginForm
from datetime import date, datetime
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
        teacher = request.user.teacher_profile
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
        teacher = request.user.teacher_profile
    except Teacher.DoesNotExist:
        return redirect('home')

    students_in_classes = Student.objects.filter(
        class_field__in=teacher.classes.all()).select_related('user','class_field')

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

            if  not (subject in teacher.subjects.all() and
                    student.class_field in teacher.classes.all()):
                messages.error(request, '❌ Нет прав')

                return redirect('add_grade')

            if not subject.classes.filter(id=student.class_field.id).exists():
                messages.error(request,
                               f'❌ Предмет "{subject.name}" не преподается в классе {student.class_field.name_class}')
                return redirect('add_grade')

            existing_grade = Grade.objects.filter(
                student=student,
                subject=subject,
                date=date_str,
            ).exists()

            grade_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            day_of_week = grade_date.weekday()

            if day_of_week == 5 or day_of_week==6:
                messages.error(request,
                               f'❌ Нельзя поставить оценку ({grade_date.strftime("%d.%m.%Y")}) - это выходной день'
                               )
                return redirect('add_grade')

            holidays_2025_2026 = [
                date(2025, 11, 7),
                date(2025, 12, 25),
                date(2026, 1, 1),
                date(2026, 1, 2),
                date(2026, 1, 7),
                date(2026, 3, 8),
                date(2026, 5, 1),
                date(2026, 5, 9),
            ]

            if grade_date in holidays_2025_2026:

                messages.error(request,
                               f'❌ Нельзя поставить оценку ({grade_date.strftime("%d.%m.%Y")}) - праздничный день'
                               )
                return redirect('add_grade')

            if existing_grade:
                messages.error(request, f'❌ У этого ученика уже есть оценка по предмету "{subject.name}" на {date_str}.'
                                        f'Используйте другую дату.')
                return redirect('add_grade')

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


@login_required
def student_grades_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    grades = Grade.objects.filter(student=student).select_related('subject')

    subjects_grades = {}
    total_grades_count = 0
    total_grades_sum = 0

    for grade in grades:
        if grade.subject not in subjects_grades:
            subjects_grades[grade.subject] = []
        subjects_grades[grade.subject].append(grade)
        total_grades_count += 1
        total_grades_sum += grade.grade

    subject_averages = {}
    for subject, grade_list in subjects_grades.items():
        subject_sum = sum(grade.grade for grade in grade_list)
        subject_averages[subject.id] = round(subject_sum / len(grade_list), 2)

    average_grade = round(total_grades_sum / total_grades_count, 2) if total_grades_count > 0 else 0

    context = {
        'student': student,
        'subjects_grades': subjects_grades,
        'grades': grades,
        'subject_averages': subject_averages,
        'average_grade': average_grade,
        'total_grades_count': total_grades_count,
    }

    return render(request, 'student_grades_view.html', context)