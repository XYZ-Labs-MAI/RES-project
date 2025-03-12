from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def home_page_show(request):
    return render(request, 'home_page/general_page.html')


@login_required
def profile_view(request):
    return render(request, 'authenticate\\login_page.html', {'user': request.user}) # путь до профиля
