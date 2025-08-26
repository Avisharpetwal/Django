from django.db import models

class Book(models.Model):
    title=models.CharField(max_length=100)
    author=models.CharField(max_length=50)
    unique_id=models.CharField(max_length=20,unique=True)
    publish_year=models.IntegerField()
    copies_available=models.IntegerField(default=1)
    is_available=models.BooleanField(default=True)


    def __str__(self):
        return f"{self.title} ({self.author})"
