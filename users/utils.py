import random
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp):

    subject = "PhotoNest Email Verification"

    html_content = render_to_string(
        "emails/otp_email.html",
        {
            "otp": otp
        }
    )

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=f"Your OTP is {otp}",
        to=[email]
    )

    email_message.attach_alternative(
        html_content,
        "text/html"
    )

    email_message.send()


def send_reset_password_email(email, otp):

    subject = "PhotoNest Password Reset"

    html_content = render_to_string(
        "emails/reset_password_email.html",
        {
            "otp": otp
        }
    )

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=f"Your password reset OTP is {otp}",
        to=[email]
    )

    email_message.attach_alternative(
        html_content,
        "text/html"
    )

    email_message.send()


def send_welcome_email(email, username):

    subject = "Welcome to PhotoNest 🎉"

    html_content = render_to_string(
        "emails/welcome_email.html",
        {
            "username": username
        }
    )

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=f"Welcome to PhotoNest {username}",
        to=[email]
    )

    email_message.attach_alternative(
        html_content,
        "text/html"
    )

    email_message.send()