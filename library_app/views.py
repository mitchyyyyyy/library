from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from datetime import date
from .models import Book, BorrowRecord, UserProfile
from .forms import BookSearchForm

# Create your views here.

# HOME PAGE
def index(request):
    total_books = Book.objects.count()
    available_books = Book.objects.filter(available_copies__gt=0).count()
    total_users = User.objects.count()
    total_borrowed = BorrowRecord.objects.filter(status='borrowed').count()
    
    context = {
        'total_books': total_books,
        'available_books': available_books,
        'total_users': total_users,
        'total_borrowed': total_borrowed,
    }
    return render(request, 'index.html', context)


# REGISTRATION
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, '❌ Passwords do not match!')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '❌ Username already exists!')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '❌ Email already exists!')
            return redirect('register')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user, library_card_number=f"LIB{user.id:05d}")
        
        messages.success(request, '✅ Account created! Please login.')
        return redirect('login')
    
    return render(request, 'register.html')


# LOGIN
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'✅ Welcome back, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, '❌ Invalid username or password!')
    
    return render(request, 'login.html')


# LOGOUT
def logout_view(request):
    logout(request)
    messages.success(request, '✅ You have been logged out.')
    return redirect('index')


# BOOK LIST
def book_list(request):
    books = Book.objects.all()
    search_query = request.GET.get('search', '')
    category = request.GET.get('category', '')
    
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    if category:
        books = books.filter(category=category)
    
    categories = Book.CATEGORY_CHOICES
    context = {'books': books, 'search_query': search_query, 'category': category, 'categories': categories}
    return render(request, 'book_list.html', context)


# BOOK DETAIL
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'book_detail.html', {'book': book})


# BORROW BOOK
@login_required(login_url='login')
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if not book.is_available():
        messages.error(request, '❌ This book is not available!')
        return redirect('book_detail', book_id=book_id)
    
    if BorrowRecord.objects.filter(user=request.user, book=book, status='borrowed').exists():
        messages.warning(request, '⚠️ You already borrowed this book!')
        return redirect('book_detail', book_id=book_id)
    
    BorrowRecord.objects.create(user=request.user, book=book)
    book.available_copies -= 1
    book.save()
    
    messages.success(request, f'✅ Successfully borrowed "{book.title}"!')
    return redirect('dashboard')


# RETURN BOOK
@login_required(login_url='login')
def return_book(request, borrow_id):
    borrow = get_object_or_404(BorrowRecord, id=borrow_id, user=request.user)
    
    borrow.return_date = date.today()
    borrow.status = 'returned'
    borrow.save()
    
    book = borrow.book
    book.available_copies += 1
    book.save()
    
    messages.success(request, f'✅ "{book.title}" returned successfully!')
    return redirect('dashboard')


# DASHBOARD
@login_required(login_url='login')
def dashboard(request):
    borrowed_books = BorrowRecord.objects.filter(user=request.user, status='borrowed').select_related('book')
    returned_books = BorrowRecord.objects.filter(user=request.user, status='returned').select_related('book')[:10]
    
    for record in borrowed_books:
        if record.is_overdue():
            record.status = 'overdue'
            record.save()
    
    context = {'borrowed_books': borrowed_books, 'returned_books': returned_books}
    return render(request, 'dashboard.html', context)


# LIBRARIAN DASHBOARD
@login_required(login_url='login')
def librarian_dashboard(request):
    try:
        if not request.user.userprofile.is_librarian:
            messages.error(request, '❌ Access denied!')
            return redirect('dashboard')
    except:
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    
    total_books = Book.objects.count()
    borrowed_books = BorrowRecord.objects.filter(status='borrowed').count()
    overdue_books = BorrowRecord.objects.filter(status='overdue').count()
    
    context = {'total_books': total_books, 'borrowed_books': borrowed_books, 'overdue_books': overdue_books}
    return render(request, 'librarian_dashboard.html', context)


# ADD BOOK
@login_required(login_url='login')
def add_book(request):
    try:
        if not request.user.userprofile.is_librarian:
            messages.error(request, '❌ Access denied!')
            return redirect('dashboard')
    except:
        messages.error(request, '❌ Access denied!')
        return redirect('dashboard')
    
    if request.method == 'POST':
        Book.objects.create(
            title=request.POST.get('title'),
            author=request.POST.get('author'),
            isbn=request.POST.get('isbn'),
            description=request.POST.get('description'),
            category=request.POST.get('category'),
            total_copies=int(request.POST.get('total_copies', 1)),
            available_copies=int(request.POST.get('total_copies', 1)),
            publication_date=request.POST.get('publication_date'),
            pages=request.POST.get('pages'),
        )
        messages.success(request, '✅ Book added successfully!')
        return redirect('librarian_dashboard')
    
    categories = Book.CATEGORY_CHOICES
    return render(request, 'add_book.html', {'categories': categories})
    