from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    path('books/', views.book_list, name='book-list'),      # GET all, POST new
    path('books/<int:pk>/', views.book_detail, name='book-detail'),  # GET one, PUT, DELETE
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('books/download/', views.download_books_excel, name='books-download'),
    path('books/upload/', views.upload_books_excel, name='books-upload'),
    path('books/save-excel/', views.save_books_from_excel, name='books-save-excel'),

    
]

