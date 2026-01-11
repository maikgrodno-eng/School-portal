from django import forms


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