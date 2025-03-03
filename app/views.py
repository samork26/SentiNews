from django.shortcuts import render
from django.http import JsonResponse
from .models import NewsArticle, LocalNews
from app.services.news_fetcher import fetch_news, fetch_local_news
from app.services.sentiment_analyzer import analyze_sentiment

def index(request):
    """Retrieve global news articles with AJAX filtering."""
    articles = NewsArticle.objects.all().order_by("-published_at")

    selected_category = request.GET.get("category", "")
    selected_sentiment = request.GET.get("sentiment", "")

    if selected_category:
        articles = articles.filter(category=selected_category)
    if selected_sentiment:
        articles = articles.filter(sentiment=selected_sentiment)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"articles": [
            {
                "title": article.title,
                "url": article.url,
                "published_at": article.published_at.strftime("%B %d, %Y %I:%M %p"),
                "sentiment": article.sentiment,
                "category": article.category,
            }
            for article in articles
        ]})

    categories = sorted(set(NewsArticle.objects.values_list("category", flat=True)))
    sentiments = sorted(set(NewsArticle.objects.values_list("sentiment", flat=True)))

    return render(request, "index.html", {
        "articles": articles,
        "categories": categories,
        "sentiments": sentiments,
        "selected_category": selected_category,
        "selected_sentiment": selected_sentiment,
    })

def refresh_articles(request):
    """Refresh both global and local news dynamically using the user's location."""
    fetch_news()  # Refresh global news

    lat = request.GET.get("lat")
    lon = request.GET.get("lon")

    if lat and lon:
        try:
            lat, lon = float(lat), float(lon)
            fetch_local_news(lat, lon)  # Refresh local news dynamically
            location_status = f"Local news refreshed for {lat}, {lon}."
        except ValueError:
            location_status = "❌ Invalid location data. Refreshing only global news."
    else:
        location_status = "⚠️ No location provided. Refreshing only global news."

    analyze_sentiment()  # Update sentiment scores

    return JsonResponse({"status": "success", "message": f"Global & Local articles refreshed! {location_status}"})


def fetch_local_news_view(request):
    """Retrieve existing local news articles with filtering."""
    articles = LocalNews.objects.all().order_by("-published_at")

    selected_category = request.GET.get("category", "")

    if selected_category:
        articles = articles.filter(category=selected_category)

    return JsonResponse({"articles": [
        {
            "title": article.title,
            "url": article.url,
            "published_at": article.published_at.strftime("%B %d, %Y %I:%M %p"),
            "sentiment": article.sentiment,
            "category": article.category,
            "location": article.location,
        }
        for article in articles
    ]})

def about(request):
    return render(request, "about.html")
