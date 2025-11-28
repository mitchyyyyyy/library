from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('base/', views.base, name='base'),
  path('book_detail/', views.book_detail, name='book_detail'),
  path('book_list/', views.book_list, name='book_list'),
  path('registration/', views.registration, name='registration'),
  path('login/', views.login, name='login'),

    
]