from newsapi import NewsApiClient
from datetime import datetime
from django.utils.timezone import make_aware
from django.core.cache import cache
from app.models import NewsArticle
import os
import time
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("NEWSAPI_KEY")

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=API_KEY)

# Define categories to fetch
CATEGORIES = ["technology", "business", "sports", "entertainment", "health", "science", "general"]

# Cache expiration time (6 hours)
CACHE_TIMEOUT = 6 * 60 * 60

def fetch_news():
    """Fetches news articles from NewsAPI and stores them in the database with caching and error handling."""
    
    cache_key = "latest_news_fetched"
    last_fetch_time = cache.get(cache_key)

    if last_fetch_time:
        logger.info("✅ Using cached news, skipping API request")
        print("Using Cache")
        return  # Skip fetching if cache is valid

    new_articles = []  # List to hold new articles for bulk insert

    for category in CATEGORIES:
        logger.info(f"📡 Fetching {category.capitalize()} news...")

        try:
            top_headlines = newsapi.get_top_headlines(
                category=category,
                language="en",
                country="us"
            )

            if "articles" not in top_headlines or not top_headlines["articles"]:
                logger.warning(f"⚠️ No articles found for {category}!")
                continue

            for article in top_headlines["articles"]:
                title = article["title"]
                url = article["url"]
                source = article["source"]["name"]
                published_at = datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
                published_at = make_aware(published_at)  # Convert to timezone-aware

                # Prevent duplicate entries by checking URL existence
                if not NewsArticle.objects.filter(url=url).exists():
                    new_articles.append(NewsArticle(
                        title=title,
                        source=source,
                        url=url,
                        published_at=published_at,
                        category=category.capitalize()
                    ))

            if new_articles:
                NewsArticle.objects.bulk_create(new_articles)  # Bulk insert new articles
                logger.info(f"✅ {len(new_articles)} new articles added for {category.capitalize()}!")
            else:
                logger.info(f"⚠️ No new articles for {category.capitalize()}.")

        except Exception as e:
            logger.error(f"❌ Error fetching {category} news: {str(e)}")
            time.sleep(5)  # If error occurs, wait 5 seconds before retrying next request

    # ✅ Set cache to prevent excessive API requests
    cache.set(cache_key, datetime.now(), CACHE_TIMEOUT)
    logger.info("✅ News fetch completed & cached for 6 hours")
