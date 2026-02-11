import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# API Keys (use environment variables in production)
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# News sources
NEWS_SOURCES = {
    "rss_feeds": [
        # General News
        "http://rss.cnn.com/rss/cnn_topstories.rss",
        "http://feeds.bbci.co.uk/news/rss.xml",
        "https://www.theguardian.com/world/rss",
        
        # Technology
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://www.wired.com/feed/rss",
        "https://arstechnica.com/feed/",
        
        # Sports
        "http://feeds.bbci.co.uk/sport/rss.xml",
        "https://www.espn.com/espn/rss/news",
        "https://www.skysports.com/rss/12040",
        "https://sports.yahoo.com/rss/",
        "https://www.theguardian.com/sport/rss",
        
        # Business
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.ft.com/?format=rss",
        
        # Entertainment
        "https://www.hollywoodreporter.com/feed/",
        "https://variety.com/feed/",
        
        # Health
        "https://www.medicalnewstoday.com/rss/news.xml",
        
        # Science
        "https://www.sciencedaily.com/rss/all.xml",
    ],
    "news_api_sources": [
        "bbc-news",
        "cnn",
        "the-verge",
        "techcrunch",
        "reuters",
        "espn",
        "bbc-sport"
    ]
}

# Categories
CATEGORIES = [
    "Technology",
    "Business",
    "Politics",
    "Sports",
    "Entertainment",
    "Health",
    "Science",
    "World",
    "General"
]

# Model configurations
SUMMARIZATION_MODEL = "simple"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# App settings
MAX_ARTICLES_PER_FETCH = 50
SUMMARY_MAX_LENGTH = 150
SUMMARY_MIN_LENGTH = 50
