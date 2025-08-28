from django.db import models
from django.conf import settings

class Book(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='books',
        null=True, blank=True   # 👈 allows empty owner
    )
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    unique_id = models.CharField(max_length=20, unique=True)
    publish_year = models.IntegerField()
    copies_available = models.IntegerField(default=1)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        if self.owner:
            return f"{self.title} ({self.author}) - owner: {self.owner.username}"
        return f"{self.title} ({self.author}) - owner: None"
