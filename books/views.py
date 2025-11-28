from django.shortcuts import render

# Create your views here.

def base(request):
    return render(request, 'base.html')

def index(request):
    return render(request, 'index.html')

def book_detail(request):
    return render(request, 'book_detail.html')

def book_list(request):
    return render(request, 'book_list.html')

def registration(request):
    return render(request, 'registration.html')

def login(request):
    return render(request, 'login.html')
    