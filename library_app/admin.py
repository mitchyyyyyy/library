from django.contrib import admin
from .models import Book, UserProfile, BorrowRecord

# Register your models here.

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'available_copies', 'total_copies', 'category')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('category', 'publication_date')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'library_card_number', 'is_librarian', 'membership_date')
    search_fields = ('user__username', 'library_card_number')


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrow_date', 'due_date', 'status')
    search_fields = ('user__username', 'book__title')
    list_filter = ('status', 'borrow_date')