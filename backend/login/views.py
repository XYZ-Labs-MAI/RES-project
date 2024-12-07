from django.shortcuts import render

# Create your views here.

def login_page_show(request):
    return render(request, 'login_page/login_page.html')