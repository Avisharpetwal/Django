# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Book
# from .serializers import BookSerializer

# @api_view(['GET', 'POST'])
# def book_list(request):
#     if request.method == 'GET':   # Read all books
#         books = Book.objects.all()
#         serializer = BookSerializer(books, many=True)
#         return Response(serializer.data)

#     elif request.method == 'POST':   # Create a new book
#         serializer = BookSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
# def book_detail(request, pk):
#     try:
#         book = Book.objects.get(pk=pk)
#     except Book.DoesNotExist:
#         return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'GET':   # Read one book
#         serializer = BookSerializer(book)
#         return Response(serializer.data)

#     elif request.method == 'PUT':   # Update (all fields required)
#         serializer = BookSerializer(book, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     elif request.method == 'PATCH':   # Partial update (only some fields)
#         serializer = BookSerializer(book, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     elif request.method == 'DELETE':   # Delete
#         book.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Book
from .serializers import BookSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def book_list(request):
    """GET -> list books owned by request.user
       POST -> create book, owner set to request.user
    """
    if request.method == 'GET':
        books = Book.objects.filter(owner=request.user)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)  # set owner automatically
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)

    # allow access if owner or staff
    if book.owner != request.user and not request.user.is_staff:
        return Response({"detail": "You don't have permission to access this book."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = BookSerializer(book)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save(owner=book.owner)  # preserve owner
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PATCH':
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(owner=book.owner)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

import pandas as pd
from django.http import HttpResponse
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import parser_classes

from .models import Book
from .serializers import BookSerializer

# ---------- 1. Download Book entries as Excel ----------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_books_excel(request):
    books = Book.objects.all()  # or filter(owner=request.user) if needed
    data = []
    for book in books:
        data.append({
            "title": book.title,
            "author": book.author,
            "unique_id": book.unique_id,
            "publish_year": book.publish_year,
            "copies_available": book.copies_available,
            "is_available": book.is_available,
            "owner": book.owner.username if book.owner else None
        })
    
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=books.xlsx'
    df.to_excel(response, index=False)
    return response

# ---------- 2. Upload Excel file ----------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_books_excel(request):
    """
    Just upload the file and read its content. Don't save yet.
    """
    file = request.FILES.get('file')
    if not file:
        return Response({"error": "No file uploaded."}, status=400)
    
    try:
        df = pd.read_excel(file)
    except Exception as e:
        return Response({"error": f"Invalid Excel file. {str(e)}"}, status=400)
    
    # Convert to JSON-like records to preview
    records = df.to_dict(orient='records')
    return Response({"uploaded_data": records})

# ---------- 3. Save valid entries from uploaded Excel ----------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def save_books_from_excel(request):
    file = request.FILES.get('file')
    if not file:
        return Response({"error": "No file uploaded."}, status=400)
    
    try:
        df = pd.read_excel(file)
    except Exception as e:
        return Response({"error": f"Invalid Excel file. {str(e)}"}, status=400)
    
    saved_books = []
    errors = []

    for idx, row in df.iterrows():
        serializer = BookSerializer(data={
            "title": row.get("title"),
            "author": row.get("author"),
            "unique_id": row.get("unique_id"),
            "publish_year": row.get("publish_year"),
            "copies_available": row.get("copies_available", 1),
            "is_available": row.get("is_available", True),
        })
        if serializer.is_valid():
            serializer.save(owner=request.user)
            saved_books.append(serializer.data)
        else:
            errors.append({"row": idx + 2, "errors": serializer.errors})  # row+2 for Excel indexing

    return Response({"saved": saved_books, "errors": errors})




