from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils.timezone import now
from app.models import NewsArticle
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Deletes news articles older than a week"

    def handle(self, *args, **kwargs):
        one_week_ago = now() - timedelta(days=7)
        old_articles = NewsArticle.objects.filter(published_at__lt=one_week_ago)

        if old_articles.exists():
            count = old_articles.count()
            old_articles.delete()
            logger.info(f"🗑️ Deleted {count} old news articles older than 7 days.")
            self.stdout.write(self.style.SUCCESS(f"Deleted {count} old news articles"))
        else:
            logger.info("✅ No old news articles to delete.")
            self.stdout.write(self.style.SUCCESS("No old news articles to delete."))
