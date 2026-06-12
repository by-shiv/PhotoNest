from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser


class SignUpForm(UserCreationForm):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Choose a username"
            }
        )
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Enter your email"
            }
        )
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Create a password",
                "id": "password1",
                "data-password-field": "true"
            }
        )
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Confirm password",
                "id": "password2",
                "data-password-field": "true"
            }
        )
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "password1",
            "password2"
        ]

    def clean_email(self):

        email = self.cleaned_data.get("email")

        verified_user_exists = CustomUser.objects.filter(
            email__iexact=email,
            email_verified=True
        ).exists()

        if verified_user_exists:

            raise ValidationError(
                "An account with this email already exists. Please login instead."
            )

        return email