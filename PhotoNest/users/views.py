from django.shortcuts import render, redirect
from django.contrib.auth.views import LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as django_login
from django.utils import timezone
from datetime import timedelta
from .forms import SignUpForm
from django import forms
from .models import CustomUser
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .utils import generate_otp, send_otp_email, send_reset_password_email, send_welcome_email
from django.contrib import messages

class LoginForm(forms.Form):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Username or Email"
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "auth-input",
                "placeholder": "Password",
                "id": "login-password",
                "data-password-field": "true"
            }
        )
    )


def auth_view(request):

    # If user is already logged in
    if request.user.is_authenticated:
        return redirect('gallery_home')

    login_form = LoginForm()
    register_form = SignUpForm()

    if request.method == 'POST':

        # LOGIN FORM
        if 'login_submit' in request.POST:

            username_or_email = request.POST.get('username')
            password = request.POST.get('password')

            user_obj = None

            # Find user by email
            try:
                user_obj = CustomUser.objects.get(
                    email__iexact=username_or_email
                )

            except CustomUser.DoesNotExist:

                # Find user by username
                try:
                    user_obj = CustomUser.objects.get(
                        username=username_or_email
                    )

                except CustomUser.DoesNotExist:
                    user_obj = None

            # Reset lock automatically if lock period has expired
            if (
                user_obj
                and user_obj.account_locked_until
                and timezone.now() >= user_obj.account_locked_until
            ):

                user_obj.failed_login_attempts = 0
                user_obj.account_locked_until = None
                user_obj.save()

            # Check lock BEFORE authenticate
            if (
                user_obj
                and user_obj.account_locked_until
                and timezone.now() < user_obj.account_locked_until
            ):

                remaining_minutes = (
                    (
                        user_obj.account_locked_until
                        - timezone.now()
                    ).seconds // 60
                ) + 1

                messages.error(
                    request,
                    f"Account locked. Try again in {remaining_minutes} minute(s)."
                )

                return redirect('root_auth')

            user = None

            if user_obj:

                # Handle unverified users
                if not user_obj.email_verified:

                    password_correct = user_obj.check_password(
                        password
                    )

                    if password_correct:

                        messages.warning(
                            request,
                            "This account is not verified. Please verify your OTP or register again to receive a new OTP."
                        )

                        return redirect('root_auth')

                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=password
                )

            # SUCCESSFUL LOGIN
            if user is not None:

                user.failed_login_attempts = 0
                user.account_locked_until = None

                user.save()

                django_login(
                    request,
                    user
                )

                return redirect('gallery_home')

            # FAILED LOGIN
            else:

                if user_obj:

                    user_obj.failed_login_attempts += 1

                    if user_obj.failed_login_attempts >= 5:

                        user_obj.account_locked_until = (
                            timezone.now()
                            + timedelta(minutes=15)
                        )

                        messages.error(
                            request,
                            "Too many failed login attempts. Account locked for 15 minutes."
                        )

                    else:

                        remaining_attempts = (
                            5 -
                            user_obj.failed_login_attempts
                        )

                        messages.error(
                            request,
                            f"Invalid credentials. {remaining_attempts} attempt(s) remaining."
                        )

                    user_obj.save()

                else:

                    messages.error(
                        request,
                        "Invalid credentials."
                    )

                login_form = LoginForm()

        # REGISTRATION FORM
        elif 'register_submit' in request.POST:

            register_form = SignUpForm(request.POST)

            if register_form.is_valid():

                email = register_form.cleaned_data['email']

                # Delete old unverified account if it exists
                existing_user = CustomUser.objects.filter(
                    email__iexact=email,
                    email_verified=False
                ).first()

                if existing_user:
                    existing_user.delete()

                user = register_form.save(commit=False)

                otp = generate_otp()

                current_time = timezone.now()

                user.is_active = False
                user.email_verified = False

                user.otp = otp
                user.otp_created_at = current_time
                user.last_otp_sent_at = current_time

                user.save()

                send_otp_email(
                    user.email,
                    otp
                )

                return redirect(
                    'verify_otp',
                    user_id=user.id
                )

            else:

                print(
                    "FORM ERRORS:",
                    register_form.errors
                )

    return render(
        request,
        'users/auth.html',
        {
            'login_form': login_form,
            'register_form': register_form
        }
    )



def verify_otp(request, user_id):

    try:
        user = CustomUser.objects.get(id=user_id)

    except CustomUser.DoesNotExist:

        messages.error(
            request,
            "Your verification session has expired. Please register again."
        )

        return redirect('root_auth')

    if request.method == 'POST':

        entered_otp = request.POST.get('otp')

        otp_expired = (
            timezone.now() >
            user.otp_created_at + timedelta(minutes=5)
        )

        if otp_expired:

            messages.warning(
                request,
                "OTP has expired. Please request a new OTP."
            )

            return redirect(
                'verify_otp',
                user_id=user.id
            )

        if entered_otp == user.otp:

            user.email_verified = True
            user.is_active = True
            user.otp = None

            user.save()

            send_welcome_email(
                user.email,
                user.username
            )

            user.backend = (
                'django.contrib.auth.backends.ModelBackend'
            )

            django_login(
                request,
                user
            )

            return redirect(
                'gallery_home'
            )

        messages.error(
            request,
            "Invalid OTP"
        )

        return redirect(
            'verify_otp',
            user_id=user.id
        )

    remaining_seconds = 0

    if user.last_otp_sent_at:

        elapsed = (
            timezone.now() -
            user.last_otp_sent_at
        ).seconds

        remaining_seconds = max(
            0,
            60 - elapsed
        )

    return render(
        request,
        'users/verify_otp.html',
        {
            'user': user,
            'remaining_seconds': remaining_seconds
        }
    )


def resend_otp(request, user_id):

    try:
        user = CustomUser.objects.get(id=user_id)

    except CustomUser.DoesNotExist:
        return redirect('root_auth')

    current_time = timezone.now()

    if (
        user.last_otp_sent_at
        and
        (current_time - user.last_otp_sent_at).seconds < 60
    ):

        messages.warning(
           request,
           "Please wait before requesting another OTP."
        )

        return redirect(
           'verify_otp',
           user_id=user.id
        )

    otp = generate_otp()

    user.otp = otp
    user.otp_created_at = current_time
    user.last_otp_sent_at = current_time

    user.save()

    send_otp_email(
        user.email,
        otp
    )

    messages.success(
       request,
       "A new OTP has been sent."
    )

    return redirect(
      'verify_otp',
      user_id=user.id
    )

def resend_reset_otp(request, user_id):

    try:
        user = CustomUser.objects.get(id=user_id)

    except CustomUser.DoesNotExist:
        return redirect('root_auth')

    current_time = timezone.now()

    if (
        user.last_otp_sent_at
        and
        (current_time - user.last_otp_sent_at).seconds < 60
    ):

        messages.warning(
            request,
            "Please wait before requesting another OTP."
        )

        return redirect(
            'reset_password',
            user_id=user.id
        )

    otp = generate_otp()

    user.otp = otp
    user.otp_created_at = current_time
    user.last_otp_sent_at = current_time

    user.save()

    send_reset_password_email(
        user.email,
        otp
    )

    messages.success(
        request,
        "A new OTP has been sent."
    )

    return redirect(
        'reset_password',
        user_id=user.id
    )

def forgot_password(request):

    if request.method == 'POST':

        email = request.POST.get('email')

        try:

            user = CustomUser.objects.get(
                email=email
            )

            otp = generate_otp()

            current_time = timezone.now()
            user.otp = otp
            user.otp_created_at = current_time
            user.last_otp_sent_at = current_time

            user.save()

            send_reset_password_email(user.email, otp)

            return redirect(
                'reset_password',
                user_id=user.id
            )

        except CustomUser.DoesNotExist:

            messages.error(
                request,
                "No account found with this email."
            )

            return redirect(
                'forgot_password'
            )

    return render(
        request,
        'users/forgot_password.html'
    )

def verify_existing_account(request):

    if request.method == 'POST':

        email = request.POST.get('email')

        try:

            user = CustomUser.objects.get(
                email__iexact=email
            )

            if user.email_verified:

                messages.info(
                    request,
                    "Your account is already verified. Please login."
                )

                return redirect(
                    'root_auth'
                )

            otp = generate_otp()

            current_time = timezone.now()

            user.otp = otp
            user.otp_created_at = current_time
            user.last_otp_sent_at = current_time

            user.save()

            send_otp_email(
                user.email,
                otp
            )

            messages.success(
                request,
                "A new verification OTP has been sent."
            )

            return redirect(
                'verify_otp',
                user_id=user.id
            )

        except CustomUser.DoesNotExist:

            messages.error(
                request,
                "No account found with this email."
            )

            return redirect(
                'verify_account'
            )

    return render(
        request,
        'users/verify_account.html'
    )

def reset_password(request, user_id):

    try:
        user = CustomUser.objects.get(id=user_id)

    except CustomUser.DoesNotExist:
        return redirect('root_auth')

    if request.method == 'POST':

        entered_otp = request.POST.get('otp')

        new_password = request.POST.get(
            'password'
        )

        confirm_password = request.POST.get(
            'confirm_password'
        )

        # Password Match Validation
        if new_password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect(
                'reset_password',
                user_id=user.id
            )

        # OTP Expiry Check
        otp_expired = (
            timezone.now() >
            user.otp_created_at + timedelta(minutes=5)
        )

        if otp_expired:

            messages.warning(
                request,
                "OTP has expired."
            )

            return redirect(
                'reset_password',
                user_id=user.id
            )

        # OTP Verification
        if entered_otp == user.otp:

            user.set_password(
                new_password
            )

            user.otp = None

            user.save()

            messages.success(
                request,
                "Password reset successful. Please login."
            )

            return redirect(
                'root_auth'
            )

        messages.error(
            request,
            "Invalid OTP"
        )

        return redirect(
            'reset_password',
            user_id=user.id
        )

    # Resend OTP Cooldown Timer
    remaining_seconds = 0

    if user.last_otp_sent_at:

        elapsed = (
            timezone.now() -
            user.last_otp_sent_at
        ).seconds

        remaining_seconds = max(
            0,
            60 - elapsed
        )

    return render(
        request,
        'users/reset_password.html',
        {
            'user': user,
            'remaining_seconds': remaining_seconds
        }
    )


class CustomLogoutView(LogoutView):
    next_page = 'root_auth'