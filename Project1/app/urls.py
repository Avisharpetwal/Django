from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.book_list, name='book-list'),      # GET all, POST new
    path('books/<int:pk>/', views.book_detail, name='book-detail'),  # GET one, PUT, DELETE
]
