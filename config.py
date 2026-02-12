import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# API Keys (use environment variables in production)
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

NEWS_SOURCES = {
    'news_api': {
        'base_url': 'https://newsapi.org/v2/top-headlines',
        'categories': ['general', 'business', 'technology', 'sports', 'entertainment', 'health', 'science']
    },
    'rss_feeds': [
        # BBC News (UK)
        'http://feeds.bbci.co.uk/news/rss.xml',
        'http://feeds.bbci.co.uk/news/uk/rss.xml',
        'http://feeds.bbci.co.uk/news/world/rss.xml',
        'http://feeds.bbci.co.uk/news/business/rss.xml',
        'http://feeds.bbci.co.uk/news/technology/rss.xml',
        'http://feeds.bbci.co.uk/sport/rss.xml',
        
        # The Guardian (UK)
        'https://www.theguardian.com/uk/rss',
        'https://www.theguardian.com/world/rss',
        'https://www.theguardian.com/business/rss',
        'https://www.theguardian.com/technology/rss',
        'https://www.theguardian.com/sport/rss',
        
        # Sky News (UK)
        'https://feeds.skynews.com/feeds/rss/uk.xml',
        'https://feeds.skynews.com/feeds/rss/world.xml',
        'https://feeds.skynews.com/feeds/rss/business.xml',
        'https://feeds.skynews.com/feeds/rss/technology.xml',
        
        # Reuters (International)
        'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best',
        'https://www.reuters.com/rssfeed/businessNews',
        'https://www.reuters.com/rssfeed/technologyNews',
        'https://www.reuters.com/rssfeed/worldNews',
        
        # Independent (UK)
        'https://www.independent.co.uk/news/uk/rss',
        'https://www.independent.co.uk/news/world/rss',
        'https://www.independent.co.uk/news/business/rss',
        'https://www.independent.co.uk/sport/rss',
        
        # Financial Times (UK - Business/Finance)
        'https://www.ft.com/?format=rss',
        
        # Al Jazeera (International)
        'https://www.aljazeera.com/xml/rss/all.xml',
        
        # CNN (International)
        'http://rss.cnn.com/rss/edition.rss',
        'http://rss.cnn.com/rss/edition_world.rss',
        'http://rss.cnn.com/rss/edition_technology.rss',
        
        # Bloomberg (Business/Finance)
        'https://feeds.bloomberg.com/markets/news.rss',
        
        # TechCrunch (Technology)
        'https://techcrunch.com/feed/',
        
        # The Verge (Technology)
        'https://www.theverge.com/rss/index.xml',
        
        # ESPN (Sports)
        'https://www.espn.com/espn/rss/news',
    ]
}

# Categories
CATEGORIES = [
    "Technology",
    "Business",
    "Finance",
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
