from textblob import TextBlob
from app.models import NewsArticle

# Expanded keyword lists for better accuracy
POSITIVE_WORDS = {
    "profit", "growth", "success", "win", "record", "innovation", "strong", "rise", 
    "optimistic", "gains", "increase", "improve", "advancement", 
    "stunner", "comeback", "clutch", "dominant", "amazing", "upset", "pull off", "stable", "good health", "good", "fix", "new"
}

NEGATIVE_WORDS = {
    "crash", "decline", "loss", "fail", "drop", "problem", "risk", "cut", "pessimistic", 
    "downturn", "plummet", "reduce", "collapse", "hope is fading", "no hope", "hopeless", "fatal", "suing"
}

def analyze_sentiment():
    """Improved sentiment analysis with sports & category adjustments."""
    articles = NewsArticle.objects.all()  # Analyze all articles

    for article in articles:
        if not article.title:  # Ignore empty titles
            continue
        
        # Analyze with TextBlob
        analysis = TextBlob(article.title)
        polarity = analysis.sentiment.polarity

        # Convert title to lowercase for keyword matching
        words = set(article.title.lower().split())

        # Category-based sentiment adjustment
        is_sports = article.category.lower() == "sports"

        # Check for strong sentiment-boosting keywords
        if words & POSITIVE_WORDS:
            sentiment = "Positive"
        elif words & NEGATIVE_WORDS:
            sentiment = "Negative"
        else:
            # If no strong keywords, rely on polarity score with adjusted thresholds
            if polarity > 0.05 or (is_sports and polarity >= 0):  # Sports bias → Neutral becomes Positive
                sentiment = "Positive"
            elif polarity < -0.05:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

        # Update the database
        article.sentiment = sentiment
        article.save()

    print("✅ Sentiment analysis updated with category-based bias!")
