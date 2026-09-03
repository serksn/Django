from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from account.forms import UserProfileForm, CustomUserCreationForm
from django.contrib import messages


def register_views(request):
    if request.user.is_authenticated:
        return redirect('profile')
   
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f'Добро пожаловать, {user.get_full_name()}! Ваш аккаунт успешно создан.'
            )
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = CustomUserCreationForm()
   
    return render(request, 'register.html', {'form': form})

def login_views(request):
    if request.user.is_authenticated:
        return redirect('profile')
   
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
       
        user = authenticate(request, email=email, password=password)
       
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'profile')
            messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверный email или пароль')
   
    return render(request, 'login.html')

@login_required
def logout_views(request):
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы')
    return redirect('home')

@login_required
def profile_views(request):
    return render(request, 'profile.html', {'user': request.user})


@login_required
def edit_profile_views(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
   
    return render(request, 'edit_profile.html', {'form': form})