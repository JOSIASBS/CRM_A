from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import CustomUser


class PerfilForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'avatar']

        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'phone': 'Teléfono',
            'address': 'Dirección',
            'avatar': 'Avatar',
        }


        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Teléfono'}),
            'address': forms.TextInput(attrs={'placeholder': 'Dirección'}),
        }
