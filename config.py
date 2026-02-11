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
        "http://rss.cnn.com/rss/cnn_topstories.rss",
        "http://feeds.bbci.co.uk/news/rss.xml",
        "https://www.theguardian.com/world/rss",
        "https://www.reddit.com/r/news/.rss",
        "https://techcrunch.com/feed/",
    ],
    "news_api_sources": [
        "bbc-news",
        "cnn",
        "the-verge",
        "techcrunch",
        "reuters"
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
