from django.shortcuts import render


def home_page_show(request):
    return render(request, 'home_page/home_page.html')
