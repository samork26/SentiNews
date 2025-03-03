from opencage.geocoder import OpenCageGeocode
from newsapi import NewsApiClient
from datetime import datetime
from django.utils.timezone import make_aware
from django.core.cache import cache
from app.models import NewsArticle, LocalNews
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
                if created:
                    logger.info(f"✅ Added: {article['title']}")
                else:
                    logger.info(f"🔹 Skipped duplicate: {article['title']}")

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
    """Fetches local news based on user's latitude & longitude."""
    
    # Round lat/lon to prevent floating-point mismatches in cache keys
    lat, lon = round(float(lat), 4), round(float(lon), 4)

    cache_key = f"local_news_fetched_{lat}_{lon}"
    if cache.get(cache_key):
        logger.info(f"✅ Using cached local news for {lat}, {lon}, skipping API request")
        return

    city_name = reverse_geocode(lat, lon)
    
    if not city_name:
        logger.warning("⚠️ No city found, using 'local news' query.")
        query = "local news"
    else:
        query = city_name

    logger.info(f"📡 Fetching local news for location: {query}...")

    try:
        local_articles = []
        for category in CATEGORIES:
            logger.info(f"🔍 Fetching {category.capitalize()} local news...")
            
            # Use location + category in the query for better results
            top_headlines = newsapi.get_everything(q=f"{query} {category}", language="en")

            if not top_headlines.get("articles"):
                logger.warning(f"⚠️ No articles found for {category} in {query}!")
                continue

            for article in top_headlines["articles"]:
                obj, created = LocalNews.objects.get_or_create(
                    url=article["url"],
                    defaults={
                        "title": article["title"],
                        "source": article["source"]["name"],
                        "published_at": make_aware(
                            datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
                        ),
                        "category": category.capitalize(),
                        "location": city_name,
                    },
                )
                if created:
                    local_articles.append(obj)
                    logger.info(f"✅ Added: {article['title']} ({category})")
                else:
                    logger.info(f"🔹 Skipped duplicate: {article['title']}")

        if local_articles:
            logger.info(f"✅ Successfully added {len(local_articles)} local articles for {query}")

    except Exception as e:
        logger.error(f"❌ Error fetching local news: {str(e)}")
        return []

    # ✅ Set cache AFTER successful fetch
    cache.set(cache_key, True, CACHE_TIMEOUT)
    logger.info(f"✅ Local news fetch completed & cached for {CACHE_TIMEOUT // 3600} hours")
