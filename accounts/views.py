from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User

from students.models import StudentProfile
from partners.models import PartnerProfile
from .forms import RegisterForm

def main_page(request):
    return render(request, 'accounts/main_page.html')

def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )

            if form.cleaned_data['role'] == 'student':
                StudentProfile.objects.create(user=user)
            else:
                PartnerProfile.objects.create(user=user)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('main_page')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    error = None

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('main_page')
        else:
            error = 'Неверный логин или пароль'

    return render(request, 'accounts/login.html', {'error': error})


def user_logout(request):
    logout(request)
    return redirect('login')