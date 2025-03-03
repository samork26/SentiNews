from textblob import TextBlob
from app.models import NewsArticle, LocalNews

# Expanded keyword lists for better accuracy
POSITIVE_WORDS = {
    "profit", "growth", "success", "win", "record", "innovation", "strong", "rise", 
    "optimistic", "gains", "increase", "improve", "advancement", 
    "stunner", "comeback", "clutch", "dominant", "amazing", "upset", "pull off", 
    "stable", "good health", "good", "fix", "new"
}

NEGATIVE_WORDS = {
    "crash", "decline", "loss", "fail", "drop", "problem", "risk", "cut", "pessimistic", 
    "downturn", "plummet", "reduce", "collapse", "hope is fading", "no hope", 
    "hopeless", "fatal", "suing"
}

def analyze_sentiment():
    """Improved sentiment analysis for both Global and Local news articles."""
    
    # Process global news
    process_sentiment(NewsArticle.objects.all(), NewsArticle)

    # Process local news
    process_sentiment(LocalNews.objects.all(), LocalNews)

    print("✅ Sentiment analysis updated for both Global & Local news!")


def process_sentiment(articles, model_class):
    """Processes sentiment for a queryset of news articles."""
    bulk_updates = []

    for article in articles:
        if not article.title:  # Ignore empty titles
            continue

        # Analyze sentiment with TextBlob
        analysis = TextBlob(article.title)
        polarity = analysis.sentiment.polarity

        # Convert title to lowercase for keyword matching
        words = set(article.title.lower().split())

        # Category-based sentiment adjustment
        is_sports = article.category.lower() == "sports"

        # Determine sentiment
        if words & POSITIVE_WORDS:
            sentiment = "Positive"
        elif words & NEGATIVE_WORDS:
            sentiment = "Negative"
        else:
            # If no strong keywords, rely on polarity score with adjusted thresholds
            if polarity > 0.05 or (is_sports and polarity >= 0):  
                sentiment = "Positive"  # Sports articles often get a positive bias
            elif polarity < -0.05:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

        # Update sentiment only if it has changed
        if article.sentiment != sentiment:
            article.sentiment = sentiment
            bulk_updates.append(article)

    # Bulk update all changed articles at once for efficiency
    if bulk_updates:
        model_class.objects.bulk_update(bulk_updates, ["sentiment"])
