import feedparser
import requests
from typing import List, Dict, Optional
from datetime import datetime
import logging
import re

from config import NEWS_SOURCES, NEWS_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False


class NewsFetcher:
    """Fetch news from multiple sources including News API and RSS feeds."""
    
    def __init__(self):
        self.news_api_key = NEWS_API_KEY
        self.news_api_url = 'https://newsapi.org/v2/top-headlines'
        self.rss_feeds = NEWS_SOURCES.get('rss_feeds', [])
        self.seen_urls = set()
        
        logger.info(f"Initialized NewsFetcher with {len(self.rss_feeds)} RSS feeds")
    
    def fetch_from_news_api(self, category=None):
        """Fetch news from News API."""
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
    
    def fetch_from_rss(self, feed_url):
        """Fetch news from an RSS feed."""
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
                        continue
                    
                    published = entry.get('published', entry.get('updated', ''))
                    if published:
                        try:
                            from dateutil import parser
                            published = parser.parse(published).isoformat()
                        except:
                            published = datetime.now().isoformat()
                    else:
                        published = datetime.now().isoformat()
                    
                    summary = entry.get('summary', entry.get('description', ''))
                    if hasattr(summary, 'value'):
                        summary = summary.value
                    
                    summary = re.sub(r'<[^>]+>', '', str(summary))
                    
                    article = {
                        'title': entry.get('title', 'No Title'),
                        'summary': summary[:500],
                        'url': url,
                        'source': feed.feed.get('title', 'RSS Feed'),
                        'published': published,
                        'image': '',
                        'author': entry.get('author', ''),
                    }
                    
                    articles.append(article)
                    self.seen_urls.add(url)
                
                except Exception as e:
                    logger.warning(f"Error parsing RSS entry from {feed_url}: {e}")
                    continue
            
            if articles:
                logger.info(f"Fetched {len(articles)} articles from {feed.feed.get('title', feed_url)}")
            
            return articles
        
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
            return []
    
    def fetch_all(self, category=None):
        """Fetch news from all available sources."""
        all_articles = []
        self.seen_urls = set()
        
        logger.info("Starting to fetch news from all sources...")
        
        try:
            api_articles = self.fetch_from_news_api(category)
            if api_articles:
                all_articles.extend(api_articles)
                logger.info(f"News API: {len(api_articles)} articles")
        except Exception as e:
            logger.warning(f"News API unavailable: {e}")
        
        logger.info(f"Fetching from {len(self.rss_feeds)} RSS feeds...")
        
        for i, feed_url in enumerate(self.rss_feeds, 1):
            try:
                rss_articles = self.fetch_from_rss(feed_url)
                if rss_articles:
                    all_articles.extend(rss_articles)
                    logger.info(f"RSS Feed {i}/{len(self.rss_feeds)}: {len(rss_articles)} articles")
            except Exception as e:
                logger.warning(f"RSS feed {i} failed: {e}")
                continue
        
        if not all_articles:
            logger.warning("No articles fetched from any source")
            return []
        
        all_articles = self._deduplicate(all_articles)
        
        all_articles.sort(key=lambda x: x.get('published', ''), reverse=True)
        
        logger.info(f"Total unique articles: {len(all_articles)}")
        
        return all_articles[:100]
    
    def _deduplicate(self, articles):
        """Remove duplicate articles based on URL and title similarity."""
        seen_urls = set()
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('url', '')
            title = article.get('title', '').lower().strip()
            
            if url and url in seen_urls:
                continue
            
            title_key = ''.join(title.split()[:10])
            if title_key in seen_titles:
                continue
            
            if url:
                seen_urls.add(url)
            if title:
                seen_titles.add(title_key)
            
            unique_articles.append(article)
        
        removed = len(articles) - len(unique_articles)
        if removed > 0:
            logger.info(f"Removed {removed} duplicate articles")
        
        return unique_articles
    
    def extract_full_article(self, url):
        """Extract full article content from URL."""
        if not NEWSPAPER_AVAILABLE:
            logger.warning("newspaper3k not available")
            return {}
        
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
