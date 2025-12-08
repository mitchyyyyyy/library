from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from datetime import date
from .models import Book, BorrowRecord, UserProfile


# HOME PAGE
def index(request):
    """Homepage"""
    
    context = {
        'total_books': Book.objects.count(),
        'available_books': Book.objects.filter(available_copies__gt=0).count(),
        'total_users': User.objects.count(),
        'total_borrowed': BorrowRecord.objects.filter(status='borrowed').count(),
    }
    return render(request, 'index.html', context)


# REGISTER
def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Account created! Please login.')
        return redirect('login')
    
    return render(request, 'registration.html')


# LOGIN
def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome, {username}!')
            return redirect('index')
        else:
            messages.error(request, 'Invalid credentials!')
    
    return render(request, 'login.html')


# LOGOUT
def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'Logged out!')
    return redirect('index')


# BOOK LIST
def book_list(request):
    """Browse books"""
    search_query = request.GET.get('search', '')
    category = request.GET.get('category', '')

    books = Book.objects.all()

    if search_query:
        books = books.filter(title__icontains=search_query)
    if category:
        books = books.filter(category=category)

    context = {
        'books': books,
        'search_query': search_query,
        'category': category,
    }
    return render(request, 'book_list.html', context)


# BOOK DETAIL
def book_detail(request, book_id):
    """Book details"""
    book = {'id': book_id, 'title': 'Sample Book'}
    return render(request, 'book_detail.html', {'book': book})


# BORROW BOOK
@login_required(login_url='login')
def borrow_book(request, book_id):
    """Borrow book"""
    messages.success(request, 'Book borrowed!')
    return redirect('book_list')


#BORROWED BOOKS
@login_required
def borrowed_books(request):
    records = BorrowRecord.objects.filter(user=request.user, status='borrowed')
    return render(request, 'borrowed_books.html', {'records': records})


# RETURN BOOK
@login_required(login_url='login')
def return_book(request, borrow_id):
    """Return book"""
    messages.success(request, 'Book returned!')
    return redirect('index')


# DASHBOARD
@login_required(login_url='login')
def dashboard(request):
    """User dashboard"""
    return render(request, 'book_list.html')


# LIBRARIAN DASHBOARD
@login_required(login_url='login')
def librarian_dashboard(request):
    """Admin dashboard"""
    return render(request, 'book_list.html')


# ADD BOOK
@login_required(login_url='login')
def add_book(request):
    """Add new book"""
    return render(request, 'book_list.html')
