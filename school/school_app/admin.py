from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Teacher, Subject, SchoolClass, Student, Parent


class TeacherAdminForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')

    class Meta:
        model = Teacher
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        teacher = super().save(commit=False)

        if not teacher.user:
            teacher.save()
            user = teacher.create_user(
                self.cleaned_data['first_name'],
                self.cleaned_data['last_name']
            )
            teacher.user = user

        else:
            teacher.user.first_name = self.cleaned_data['first_name']
            teacher.user.last_name = self.cleaned_data['last_name']
            teacher.user.save()

        if commit:
            teacher.save()

        return teacher


class TeacherInline(admin.StackedInline):
    model = Teacher
    form = TeacherAdminForm
    can_delete = False
    verbose_name_plural = 'Профиль учителя'
    fields = ['teacher_id', 'password', 'subjects', 'classes', 'first_name', 'last_name']
    readonly_fields = ['teacher_id', 'password']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    form = TeacherAdminForm
    list_display = ['teacher_id', 'get_full_name', 'password']
    search_fields = ['teacher_id', 'user__first_name', 'user__last_name']
    readonly_fields = ['teacher_id', 'password', 'user']
    filter_horizontal = ['subjects', 'classes']

    fieldsets = (
        ('Личные данные', {
            'fields': ('first_name', 'last_name')
        }),
        ('Преподавание', {
            'fields': ('subjects', 'classes')
        }),
        ('Системная информация', {
            'fields': ('teacher_id', 'password', 'user'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        if obj.user:
            return f'{obj.user.first_name} {obj.user.last_name}'
        return 'Без имени'

    get_full_name.short_description = 'ФИО'


class UserAdmin(BaseUserAdmin):
    inlines = [TeacherInline]

    def get_inline_instances(self, request, obj=None):
        if obj:
            if hasattr(obj, 'teacher_profile'):
                return [TeacherInline(self.model, self.admin_site)]
        return []


class SubjectAdminForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = '__all__'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    form = SubjectAdminForm
    list_display = ['name', 'get_teacher_count']
    search_fields = ['name']
    filter_horizontal = ['classes']

    def get_teacher_count(self, obj):
        return obj.teachers.count()

    get_teacher_count.short_description = 'Учителя'


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ['number_class', 'letter_class', 'full_name', 'get_subject_count']
    list_filter = ['number_class']
    search_fields = ['number_class', 'letter_class']

    def full_name(self, obj):
        return f'{obj.number_class} {obj.letter_class}'

    full_name.short_description = 'Класс'

    def get_subject_count(self, obj):
        return obj.subjects.count()

    get_subject_count.short_description = 'Предметы'


class StudentAdminForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')

    class Meta:
        model = Student
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        student = super().save(commit=False)

        if not student.user:
            student.save()
            user = student.create_user_with_name(
                self.cleaned_data['first_name'],
                self.cleaned_data['last_name']
            )
            student.user = user
        else:

            student.user.first_name = self.cleaned_data['first_name']
            student.user.last_name = self.cleaned_data['last_name']
            student.user.save()

        if commit:
            student.save()

        return student


class StudentInline(admin.StackedInline):
    model = Student
    form = StudentAdminForm
    can_delete = False
    verbose_name_plural = 'Профиль ученика'
    fields = ['student_id', 'password', 'class_field', 'first_name', 'last_name']
    readonly_fields = ['student_id', 'password']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = ['student_id', 'get_full_name', 'class_field', 'password']
    list_filter = ['class_field']
    search_fields = ['student_id', 'user__first_name', 'user__last_name']
    readonly_fields = ['student_id', 'password', 'user']

    fieldsets = (
        ('Личные данные', {
            'fields': ('first_name', 'last_name', 'class_field')
        }),
        ('Системная информация', {
            'fields': ('student_id', 'password', 'user'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        if obj.user:
            return f"{obj.user.last_name} {obj.user.first_name}"
        return "Без имени"

    get_full_name.short_description = 'ФИО'


class ParentAdminForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="Имя")
    last_name = forms.CharField(max_length=30, required=True, label="Фамилия")

    class Meta:
        model = Parent
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        parent = super().save(commit=False)

        if not parent.user:

            parent.save()
            user = parent.create_user_with_name(
                self.cleaned_data['first_name'],
                self.cleaned_data['last_name']
            )
            parent.user = user
        else:

            parent.user.first_name = self.cleaned_data['first_name']
            parent.user.last_name = self.cleaned_data['last_name']
            parent.user.save()

        if commit:
            parent.save()

        return parent


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    form = ParentAdminForm
    list_display = ['parent_id', 'get_full_name', 'password', 'children_count']
    search_fields = ['parent_id', 'user__first_name', 'user__last_name']
    readonly_fields = ['parent_id', 'password', 'user']
    filter_horizontal = ['students']

    fieldsets = (
        ('Личные данные', {
            'fields': ('first_name', 'last_name')
        }),
        ('Дети', {
            'fields': ('students',)
        }),
        ('Системная информация', {
            'fields': ('parent_id', 'password', 'user'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        if obj.user:
            return f"{obj.user.last_name} {obj.user.first_name}"
        return "Без имени"

    get_full_name.short_description = 'ФИО'

    def children_count(self, obj):
        return obj.students.count()

    children_count.short_description = 'Количество детей'