from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "phone", "address", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Русские labels для всех полей
        self.fields['username'].label = 'Имя пользователя'
        self.fields['email'].label = 'Электронная почта'
        self.fields['phone'].label = 'Телефон'
        self.fields['address'].label = 'Адрес'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'
        
        # Русские help_text
        self.fields['username'].help_text = 'Не более 150 символов. Только буквы, цифры и @/./+/-/_.'
        self.fields['password1'].help_text = '''
            <ul>
                <li>Ваш пароль не должен быть слишком похож на другую вашу личную информацию.</li>
                <li>Ваш пароль должен содержать как минимум 8 символов.</li>
            </ul>
        '''
        self.fields['password2'].help_text = 'Для подтверждения, введите пароль ещё раз.'
        
        # Добавляем классы к полям
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
            self.fields[field_name].widget.attrs['placeholder'] = f'Введите {self.fields[field_name].label.lower()}'