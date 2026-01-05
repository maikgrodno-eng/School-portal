import string
from itertools import count
from django.db import models
from django.contrib.auth.models import User
import random, secrets


class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название предмета')
    classes = models.ManyToManyField('SchoolClass',
                                     related_name='subjects',
                                     blank=True,
                                     verbose_name='Классы, в которых преподается'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

class SchoolClass(models.Model):
    number_class = models.IntegerField(verbose_name='Номер класса')
    letter_class = models.CharField(max_length=1, verbose_name='Буква класса')

    @property
    def name_class(self):
        return f'{self.number_class}-{self.letter_class}'

    def __str__(self):
        return self.name_class

    class Meta:
        verbose_name = 'Класс'
        verbose_name_plural = 'Классы'

class Teacher(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                verbose_name='Пользователь',
                                related_name='teacher_profile',
                                blank=True,
                                null=True
    )
    subjects = models.ManyToManyField(Subject,
                                 verbose_name='Предметы',
                                 related_name='teachers'
    )
    classes = models.ManyToManyField(SchoolClass,
                                     verbose_name='Классы',
                                     related_name='teachers'
    )
    teacher_id = models.CharField(max_length=10,
                                  unique=True,
                                  verbose_name='ID учителя',
                                  null=True,
                                  blank=True,
                                  editable=False
    )
    password = models.CharField(max_length=6,
                                verbose_name='Пароль для входа',
                                null=True,
                                blank=True,
                                editable=False
    )
    def save(self, *args, **kwargs):

        if not self.teacher_id:
            self.teacher_id = self.generate_teacher_id()

        if not self.password:
            self.password = self.generate_password()

        super().save(*args, **kwargs)

    def create_user(self, first_name, last_name):
        username = f'teacher_{self.teacher_id}'

        counter = 1
        original_user_name = username

        while User.objects.filter(username=username).exists():
            username = f'{original_user_name}_{counter}'
            counter += 1

        user= User.objects.create_user(
                   username=username,
                   password=self.password,
                   first_name=first_name,
                   last_name=last_name,
                   is_active=True
        )

        return user

    def generate_teacher_id(self):

        while True:
            number = str(random.randint(100000, 999999))
            teacher_id = f't{number}'
            if not Teacher.objects.filter(teacher_id=teacher_id).exists():
                return teacher_id

    def generate_password(self):

        return ''.join(secrets.choice(string.digits) for _ in range(6))

    def __str__(self):
        if self.user:
            return f'{self.user.first_name} {self.user.last_name} (ID: {self.teacher_id})'
        return f'Учитель (ID: {self.teacher_id})'

    class   Meta:
        verbose_name = 'Учитель'
        verbose_name_plural = 'Учителя'

