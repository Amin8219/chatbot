# authentication/forms.py
from django import forms
from django.contrib.auth.models import User

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    mobile = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']