from opencage.geocoder import OpenCageGeocode
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
GEOCODING_API_KEY = os.getenv("GEOCODING_API_KEY")  # OpenCage API Key

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

newsapi = NewsApiClient(api_key=API_KEY)
geocoder = OpenCageGeocode(GEOCODING_API_KEY)  # OpenCage client

CATEGORIES = ["technology", "business", "sports", "entertainment", "health", "science", "general"]
CACHE_TIMEOUT = 6 * 60 * 60  # 6 hours

def fetch_news():
    """Fetches global news articles and stores them in the database with caching."""
    cache_key = "latest_news_fetched"
    if cache.get(cache_key):
        logger.info("✅ Using cached news, skipping API request")
        return

    logger.info("📡 Starting news fetch...")

    for category in CATEGORIES:
        logger.info(f"🔍 Fetching {category.capitalize()} news...")
        try:
            top_headlines = newsapi.get_top_headlines(category=category, language="en", country="us")

            if not top_headlines.get("articles"):
                logger.warning(f"⚠️ No articles found for {category}!")
                continue

            for article in top_headlines["articles"]:
                obj, created = NewsArticle.objects.get_or_create(
                    url=article["url"],
                    defaults={
                        "title": article["title"],
                        "source": article["source"]["name"],
                        "published_at": make_aware(
                            datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
                        ),
                        "category": category.capitalize(),
                    },
                )
                logger.info(f"✅ Added: {article['title']}" if created else f"🔹 Skipped: {article['title']}")

        except Exception as e:
            logger.error(f"❌ Error fetching {category} news: {str(e)}")
            time.sleep(5)

    cache.set(cache_key, datetime.now(), CACHE_TIMEOUT)
    logger.info(f"✅ News fetch completed & cached for {CACHE_TIMEOUT // 3600} hours")

def reverse_geocode(lat, lon):
    """Converts latitude and longitude to a city or region name using OpenCage API."""
    try:
        results = geocoder.reverse_geocode(lat, lon)

        if results:
            components = results[0]["components"]
            city = components.get("city") or components.get("town") or components.get("village")
            county = components.get("county")
            state = components.get("state")
            country = components.get("country")

            if city:
                location_name = f"{city}, {state}" if state else city
                logger.info(f"📍 Identified Location: {location_name}, {country}")
                return location_name
            elif county:
                location_name = f"{county}, {state}" if state else county
                logger.info(f"📍 Using county as fallback: {location_name}, {country}")
                return location_name
            elif state:
                logger.info(f"📍 Using state as fallback: {state}, {country}")
                return state
            else:
                logger.warning("⚠️ No valid city, county, or state found.")
                return None

        logger.warning("⚠️ No geocoding results found.")
        return None

    except Exception as e:
        logger.error(f"❌ Error in reverse geocoding: {str(e)}")
        return None

def fetch_local_news(lat, lon):
    """Fetches local news based on user's latitude & longitude by converting them into a city name."""
    cache_key = "latest_news_fetched"
    if cache.get(cache_key):
        logger.info("✅ Using cached news, skipping API request")
        return
    
    city_name = reverse_geocode(lat, lon)
    
    if not city_name:
        logger.warning("⚠️ No city found for the given coordinates, using 'local news' query.")
        query = "local news"
    else:
        query = city_name

    logger.info(f"📡 Fetching local news for location: {query}...")

    try:
        top_headlines = newsapi.get_everything(q=query, language="en")

        if not top_headlines.get("articles"):
            logger.warning("⚠️ No local articles found!")
            return []

        local_articles = []
        for article in top_headlines["articles"]:
            obj, created = NewsArticle.objects.get_or_create(
                url=article["url"],
                defaults={
                    "title": article["title"],
                    "source": article["source"]["name"],
                    "published_at": make_aware(
                        datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
                    ),
                    "category": "Local",
                },
            )
            if created:
                local_articles.append(obj)

        logger.info(f"✅ {len(local_articles)} new local news articles added.")
        return local_articles

    except Exception as e:
        logger.error(f"❌ Error fetching local news: {str(e)}")
        return []
