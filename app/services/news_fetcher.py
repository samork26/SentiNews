from newsapi import NewsApiClient
from datetime import datetime
from django.utils.timezone import make_aware
from app.models import NewsArticle
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("NEWSAPI_KEY")

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=API_KEY)

# Define categories to fetch
CATEGORIES = ["technology", "business", "sports", "entertainment", "health", "science", "general"]

def fetch_news():
    """Fetches news articles from NewsAPI for multiple categories and stores them in the database."""
    for category in CATEGORIES:
        print(f"📡 Fetching {category.capitalize()} news...")

        top_headlines = newsapi.get_top_headlines(
            category=category,
            language="en",
            country="us"
        )

        if "articles" not in top_headlines:
            print(f"⚠️ No articles found for {category}!")
            continue

        new_articles_count = 0  # Initialize counter for new articles

        for article in top_headlines["articles"]:
            title = article["title"]
            url = article["url"]
            source = article["source"]["name"]
            published_at = datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")

            # Convert naive datetime to timezone-aware
            published_at = make_aware(published_at)

            # Prevent duplicate entries
            if not NewsArticle.objects.filter(url=url).exists():
                NewsArticle.objects.create(
                    title=title,
                    source=source,
                    url=url,
                    published_at=published_at,
                    category=category.capitalize()
                )
                new_articles_count += 1  # Increment counter for new articles

        if new_articles_count > 0:
            print(f"✅ {new_articles_count} new articles fetched for {category.capitalize()}!")
        else:
            print(f"⚠️ No new articles for {category.capitalize()}.")

