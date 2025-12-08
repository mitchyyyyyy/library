from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, date
# Create your models here.

class Book(models.Model):
    CATEGORY_CHOICES = [
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('technology', 'Technology'),
        ('history', 'History'),
        ('biography', 'Biography'),
        ('mystery', 'Mystery'),
        ('romance', 'Romance'),
    ]
    
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='fiction')
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    publication_date = models.DateField()
    pages = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(available_copies__lte=models.F('total_copies')), name='available_not_exceed_total')
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def is_available(self):
        return self.available_copies > 0


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    library_card_number = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    membership_date = models.DateField(auto_now_add=True)
    is_librarian = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} ({self.library_card_number})"


class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_records')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='borrowed')
    
    class Meta:
        ordering = ['-borrow_date']
    
    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"
    
    def is_overdue(self):
        if self.return_date is None and date.today() > self.due_date:
            return True
        return False
    
    def save(self, *args, **kwargs):
        # If new record and status is borrowed → reduce available copies
        if not self.pk and self.status == 'borrowed':
            if self.book.available_copies > 0:
                self.book.available_copies -= 1
                self.book.save()

        # If existing record and status changed to returned → increase available copies
        elif self.pk:
            old_status = BorrowRecord.objects.get(pk=self.pk).status
            if old_status != self.status and self.status == 'returned':
                if self.book.available_copies < self.book.total_copies:
                    self.book.available_copies += 1
                    self.book.save()

        # Auto-set due date if missing
        if not self.due_date:
            self.due_date = (self.borrow_date + timedelta(days=14)).date()

        super().save(*args, **kwargs)