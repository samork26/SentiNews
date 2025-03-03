from django.contrib import admin
from .models import NewsArticle, LocalNews

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "category", "sentiment", "published_at")
    list_filter = ("category", "sentiment", "source")
    search_fields = ("title", "source")

@admin.register(LocalNews)
class LocalNewsAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "category", "sentiment", "published_at")
    list_filter = ("category", "sentiment", "source")
    search_fields = ("title", "source")