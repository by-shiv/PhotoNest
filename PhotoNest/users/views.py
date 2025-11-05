from django.shortcuts import render, redirect
from django.contrib.auth.views import LogoutView
from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as django_login

def auth_view(request):
    # If already logged in, always redirect to gallery/dashboard
    if request.user.is_authenticated:
        return redirect('gallery_home')  # Use the name of your dashboard view

    login_form = AuthenticationForm()
    register_form = SignUpForm()

    if request.method == 'POST':
        if 'login_submit' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                django_login(request, user)
                return redirect('gallery_home')  # Redirect to gallery/dashboard

        elif 'register_submit' in request.POST:
            register_form = SignUpForm(request.POST)
            if register_form.is_valid():
                register_form.save()
                return redirect('root_auth')  # Stay on same page to allow login

    return render(request, 'users/auth.html', {
        'login_form': login_form,
        'register_form': register_form
    })

class CustomLogoutView(LogoutView):
    next_page = 'root_auth'  # Redirect to the login/register after logout
