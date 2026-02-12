import feedparser
import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging
from config import NEWS_SOURCES, NEWS_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsFetcher:
    """Fetch news from multiple sources including News API and RSS feeds."""
    
    def __init__(self):
        self.news_api_key = NEWS_API_KEY
        self.news_api_url = 'https://newsapi.org/v2/top-headlines'
        self.rss_feeds = NEWS_SOURCES.get('rss_feeds', [])
        self.seen_urls = set()
        
        logger.info(f"Initialized NewsFetcher with {len(self.rss_feeds)} RSS feeds")
    
    def fetch_from_news_api(self, category: str = None) -> List[Dict]:
        """
        Fetch news from News API.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of article dictionaries
        """
        if not self.news_api_key:
            logger.warning("News API key not configured")
            return []
        
        try:
            params = {
                'apiKey': self.news_api_key,
                'country': 'gb',
                'language': 'en',
                'pageSize': 50,
            }
            
            if category and category.lower() != 'all':
                params['category'] = category.lower()
            
            response = requests.get(
                self.news_api_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'ok':
                logger.error(f"News API error: {data.get('message', 'Unknown error')}")
                return []
            
            articles = []
            for item in data.get('articles', []):
                try:
                    article = {
                        'title': item.get('title', ''),
                        'summary': item.get('description', ''),
                        'url': item.get('url', ''),
                        'source': item.get('source', {}).get('name', 'Unknown'),
                        'published': item.get('publishedAt', datetime.now().isoformat()),
                        'image': item.get('urlToImage', ''),
                        'author': item.get('author', ''),
                    }
                    
                    if article['url'] and article['url'] not in self.seen_urls:
                        articles.append(article)
                        self.seen_urls.add(article['url'])
                
                except Exception as e:
                    logger.warning(f"Error parsing News API article: {e}")
                    continue
            
            logger.info(f"Fetched {len(articles)} articles from News API")
            return articles
        
        except requests.exceptions.RequestException as e:
            logger.error(f"News API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching from News API: {e}")
            return []
    
    def fetch_from_rss(self, feed_url: str) -> List[Dict]:
        """
        Fetch news from an RSS feed.
        
        Args:
            feed_url: URL of the RSS feed
            
        Returns:
            List of article dictionaries
        """
        try:
            feed = feedparser.parse(feed_url)
            
            if feed.bozo and not feed.entries:
                logger.warning(f"Failed to parse RSS feed: {feed_url}")
                return []
            
            articles = []
            
            for entry in feed.entries[:20]:
                try:
                    url = entry.get('link', '')
                    
                    if not url or url in self.seen_urls:

