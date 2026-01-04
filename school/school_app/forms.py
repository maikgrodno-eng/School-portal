from django import forms
from django.contrib.auth.models import User
from .models import Teacher


class LoginForm(forms.Form):
    user_id = forms.CharField(max_length=10,
                              label='ID пользователя',
                              widget=forms.TextInput(attrs={
                                  'placeholder': 'Введите Ваш ID',
                                  'class': 'form-control',
                                  'autocomplete': 'off',
                              })
    )
    password = forms.CharField(max_length=6,
                               label='Пароль',
                               widget=forms.PasswordInput(attrs={
                                   'placeholder': '6-значный пароль',
                                   'class': 'form-control',
                                   'autocomplete': 'off',
                               })
    )

class TeacherAdminForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30,
                                 required=True,
                                 label='Имя',
                                 widget=forms.TextInput(attrs={'class': 'vTextField'})
    )
    last_name = forms.CharField(max_length=30,
                                required=True,
                                label="Фамилия",
                                widget=forms.TextInput(attrs={'class': 'vTextField'})
    )

    class Meta:
        model = Teacher
        fields = ['subjects', 'classes']
        widgets = {
            'subject': forms.SelectMultiple(attrs={'class': 'vSelectMultiple'}),
            'classes': forms.SelectMultiple(attrs={'class': 'vSelectMultiple'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        teacher = super().save(commit=False)

        if not teacher.user:
            user_name = f'teacher_{teacher.teacher_id}'
            user = User.objects.create_user(username=user_name,
                                            password=teacher.password,
                                            first_name=self.cleaned_data['first_name'],
                                            last_name=self.cleaned_data['last_name'],
                                            is_active=True,
            )
            teacher.user = user

        else:
            teacher.user.first_name = self.cleaned_data['first_name']
            teacher.user.last_name = self.cleaned_data['last_name']
            teacher.user.save()

        if commit:
            teacher.save()
            self.save_m2m()


        return teacher