from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    # show owner's username (read-only)
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'unique_id', 'publish_year', 'copies_available', 'is_available', 'owner']
