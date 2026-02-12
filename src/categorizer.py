from collections import Counter
import logging
import re

logger = logging.getLogger(__name__)


class ArticleCategorizer:
    
    def __init__(self):
        self.category_keywords = {
            'Technology': ['tech', 'technology', 'software', 'app', 'digital', 'ai', 'computer'],
            'Sports': ['sport', 'football', 'game', 'player', 'team', 'match'],
            'Business': ['business', 'company', 'corporate', 'ceo'],
            'Finance': ['finance', 'bank', 'stock', 'market', 'investment'],
            'Politics': ['politics', 'government', 'election', 'minister'],
            'Entertainment': ['entertainment', 'movie', 'music', 'celebrity'],
            'Health': ['health', 'medical', 'hospital', 'doctor'],
            'Science': ['science', 'research', 'study'],
            'World': ['international', 'global', 'world']
        }
    
    def categorize(self, article):
        text = article.get('title', '').lower()
        
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        return 'General'
    
    def categorize_batch(self, articles):
        for article in articles:
            article['category'] = self.categorize(article)
        return articles
    
    def get_category_distribution(self, articles):
        categories = [article.get('category', 'General') for article in articles]
        return dict(Counter(categories))
