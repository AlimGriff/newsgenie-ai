import feedparser
import requests
from datetime import datetime
from typing import List, Dict
import logging
from newspaper import Article
from config import NEWS_SOURCES, NEWS_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetch news from multiple sources."""
    
    def __init__(self):
        self.rss_feeds = NEWS_SOURCES["rss_feeds"]
        self.api_key = NEWS_API_KEY
    
    def fetch_from_rss(self, feed_url: str) -> List[Dict]:
        """Fetch articles from RSS feed."""
        try:
            feed = feedparser.parse(feed_url)
            articles = []
            
            for entry in feed.entries[:10]:  # Limit to 10 per feed
                article = {
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', ''),
                    'source': feed.feed.get('title', 'Unknown'),
                }
                articles.append(article)
            
            logger.info(f"Fetched {len(articles)} articles from {feed_url}")
            return articles
        
        except Exception as e:
            logger.error(f"Error fetching from {feed_url}: {e}")
            return []
    
    def fetch_from_newsapi(self, category: str = None) -> List[Dict]:
        """Fetch articles from News API."""
        if not self.api_key:
            logger.warning("News API key not configured")
            return []
        
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'apiKey': self.api_key,
                'language': 'en',
                'pageSize': 20
            }
            
            if category:
                params['category'] = category.lower()
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for item in data.get('articles', []):
                article = {
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'published': item.get('publishedAt', ''),
                    'summary': item.get('description', ''),
                    'source': item.get('source', {}).get('name', 'Unknown'),
                    'author': item.get('author', ''),
                    'image': item.get('urlToImage', '')
                }
                articles.append(article)
            
            logger.info(f"Fetched {len(articles)} articles from News API")
            return articles
        
        except Exception as e:
            logger.error(f"Error fetching from News API: {e}")
            return []
    
    def extract_full_article(self, url: str) -> Dict:
        """Extract full article content from URL."""
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            return {
                'text': article.text,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'top_image': article.top_image,
                'keywords': article.keywords
            }
        
        except Exception as e:
            logger.error(f"Error extracting article from {url}: {e}")
            return {}
    
    def fetch_all(self, category: str = None) -> List[Dict]:
        """Fetch articles from all sources."""
        all_articles = []
        
        # Fetch from RSS feeds
        for feed_url in self.rss_feeds:
            articles = self.fetch_from_rss(feed_url)
            all_articles.extend(articles)
        
        # Fetch from News API
        api_articles = self.fetch_from_newsapi(category)
        all_articles.extend(api_articles)
        
        # Remove duplicates based on title
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            title = article.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        logger.info(f"Total unique articles fetched: {len(unique_articles)}")
        return unique_articles
