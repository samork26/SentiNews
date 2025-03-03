from django.db import models
class NewsArticle(models.Model):
    title = models.CharField(max_length=500)
    source = models.CharField(max_length=100)
    url = models.URLField(unique=True)  # Ensures no duplicate articles
    published_at = models.DateTimeField()
    category = models.CharField(max_length=50, choices=[
        ('Technology', 'Technology'),
        ('Business', 'Business'),
        ('Sports', 'Sports'),
        ('Entertainment', 'Entertainment'),
        ('Health', 'Health'),
        ('Science', 'Science'),
        ('General', 'General'),
    ])
    sentiment = models.CharField(max_length=20, choices=[
        ('Positive', 'Positive'),
        ('Negative', 'Negative'),
        ('Neutral', 'Neutral'),
    ], default="Neutral")

class LocalNews(models.Model):
    """Stores local news articles separately from global news."""
    title = models.CharField(max_length=255)
    url = models.URLField(unique=True)
    source = models.CharField(max_length=100)
    published_at = models.DateTimeField()
    category = models.CharField(max_length=50)  # Technology, Business, etc.
    sentiment = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100)  # City or region

    def __str__(self):
        return f"{self.title} - {self.location}"


class Meta:
    ordering = ["-published_at"]  # Order articles by latest news first

    def __str__(self):
        return f"{self.title} - {self.source}"

