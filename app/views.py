from django.shortcuts import render
from django.http import JsonResponse
from .models import NewsArticle
from app.services.news_fetcher import fetch_news  # Import fetch_news
from app.services.sentiment_analyzer import analyze_sentiment

def index(request):
    """Retrieve news articles with AJAX filtering."""
    articles = NewsArticle.objects.all().order_by("-published_at")

    # Get filter values from request
    selected_category = request.GET.get("category", "")
    selected_sentiment = request.GET.get("sentiment", "")

    # Apply filters
    if selected_category:
        articles = articles.filter(category=selected_category)
    if selected_sentiment:
        articles = articles.filter(sentiment=selected_sentiment)

    # AJAX Request: Return JSON response for filtering
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        articles_data = [
            {
                "title": article.title,
                "url": article.url,
                "published_at": article.published_at.strftime("%B %d, %Y %I:%M %p"),
                "sentiment": article.sentiment,
                "category": article.category,
            }
            for article in articles
        ]
        return JsonResponse({"articles": articles_data})

    # Normal request: Render the page with all articles
    categories = sorted(set(NewsArticle.objects.values_list("category", flat=True)))
    sentiments = sorted(set(NewsArticle.objects.values_list("sentiment", flat=True)))

    return render(
        request,
        "index.html",
        {
            "articles": articles,
            "categories": categories,
            "sentiments": sentiments,
            "selected_category": selected_category,
            "selected_sentiment": selected_sentiment,
        },
    )

def refresh_articles(request):
    """Manually trigger the fetch_news function to get the latest articles."""
    fetch_news()  # Call the function to fetch the latest news articles
    analyze_sentiment()
    return JsonResponse({"status": "success", "message": "Articles refreshed!"})

def about(request):
    return render(request, "about.html")
