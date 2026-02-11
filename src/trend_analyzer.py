from collections import Counter
from typing import List, Dict
import re
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Analyze trends in news articles."""
    
    def __init__(self):
        # Common words to filter out
        self.stop_words = set([
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'says', 'said', 'after', 'new', 'over', 'more', 'their', 'this', 'that'
        ])
    
    def extract_keywords(self, text: str, top_n: int = 20) -> List[tuple]:
        """Extract important keywords from text."""
        # Clean and tokenize
        text = text.lower()
        words = re.findall(r'\b[a-z]{3,}\b', text)
        
        # Filter stop words
        words = [w for w in words if w not in self.stop_words]
        
        # Count frequencies
        word_freq = Counter(words)
        
        return word_freq.most_common(top_n)
    
    def get_trending_topics(self, articles: List[Dict], top_n: int = 10) -> List[tuple]:
        """Identify trending topics across articles."""
        all_text = " ".join([
            f"{article.get('title', '')} {article.get('summary', '')}"
            for article in articles
        ])
        
        keywords = self.extract_keywords(all_text, top_n)
        return keywords
    
    def get_source_distribution(self, articles: List[Dict]) -> Dict[str, int]:
        """Get distribution of articles by source."""
        sources = [article.get('source', 'Unknown') for article in articles]
        return dict(Counter(sources).most_common(10))
    
    def get_temporal_trends(self, articles: List[Dict]) -> Dict[str, int]:
        """Analyze article publication trends over time."""
        dates = []
        
        for article in articles:
            pub_date = article.get('published', '')
            if pub_date:
                try:
                    # Parse various date formats
                    if isinstance(pub_date, str):
                        date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    else:
                        date_obj = pub_date
                    
                    dates.append(date_obj.date())
                except:
                    pass
        
        if dates:
            date_counts = Counter(dates)
            return {str(date): count for date, count in sorted(date_counts.items())}
        
        return {}
    
    def analyze_category_trends(self, articles: List[Dict]) -> Dict:
        """Analyze trends within each category."""
        category_trends = {}
        
        # Group articles by category
        by_category = {}
        for article in articles:
            category = article.get('category', 'General')
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(article)
        
        # Get top keywords for each category
        for category, cat_articles in by_category.items():
            category_text = " ".join([
                f"{article.get('title', '')} {article.get('summary', '')}"
                for article in cat_articles
            ])
            keywords = self.extract_keywords(category_text, 5)
            category_trends[category] = {
                'count': len(cat_articles),
                'keywords': keywords
            }
        
        return category_trends
