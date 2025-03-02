from celery import shared_task
from app.services.news_fetcher import fetch_news
from app.models import NewsArticle
from django.utils.timezone import now
from datetime import timedelta

@shared_task
def fetch_and_store_news():
    """Fetches and stores news articles."""
    fetch_news()
    print("✅ News fetched successfully.")

@shared_task
def delete_old_articles():
    """Deletes news articles older than 2 weeks."""
    threshold_date = now() - timedelta(weeks=2)
    deleted_count, _ = NewsArticle.objects.filter(published_at__lt=threshold_date).delete()
    print(f"🗑 Deleted {deleted_count} old articles.")
