from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm
from django.contrib import messages
from django.contrib.auth import get_user_model

Users = get_user_model()

@login_required
def show_profile(request):
    user = request.user

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        
        new_username = request.POST.get('username')
        if Users.objects.filter(username=new_username).exclude(pk=user.pk).exists():
            messages.error(request, 'Пользователь с таким именем уже существует.')
            return render(request, 'home_page/profile.html', {'form': form})
        
        new_email = request.POST.get('email')
        if Users.objects.filter(email=new_email).exclude(pk=user.pk).exists():
            messages.error(request, 'Пользователь с таким email уже существует.')
            return render(request, 'home_page/profile.html', {'form': form})
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'home_page/profile.html', {'form': form})