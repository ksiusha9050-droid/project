from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import WorkSession
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username']
class StartSessionForm(forms.ModelForm):
    class Meta:
        model = WorkSession
        fields = ['task']
        widgets = {
            'task': forms.TextInput(attrs={'placeholder': 'Например: делаю домашку по Python'}),
        }
class CheckForm(forms.Form):
    code = forms.CharField(label='Код', max_length=4,
                           widget=forms.TextInput(attrs={'placeholder': '0000', 'autocomplete': 'off'}))
