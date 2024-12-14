from django.shortcuts import render

# Create your views here.

def register_page_show(request):
    return render(request, 'register_page/register_page.html')