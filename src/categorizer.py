from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np
from typing import List, Dict
import logging
from config import CATEGORIES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleCategorizer:
    """Categorize news articles into predefined categories."""
    
    def __init__(self):
        self.categories = CATEGORIES
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.classifier = MultinomialNB()
        self.is_trained = False
        
        # Category keywords for rule-based fallback
        self.category_keywords = {
            'Technology': ['tech', 'software', 'ai', 'computer', 'digital', 'internet', 'app', 'startup'],
            'Business': ['business', 'economy', 'market', 'stock', 'finance', 'company', 'trade'],
            'Politics': ['politics', 'government', 'election', 'president', 'congress', 'policy'],
            'Sports': ['sports', 'game', 'team', 'player', 'match', 'football', 'basketball'],
            'Entertainment': ['movie', 'music', 'celebrity', 'film', 'actor', 'entertainment'],
            'Health': ['health', 'medical', 'doctor', 'hospital', 'disease', 'patient'],
            'Science': ['science', 'research', 'study', 'scientist', 'discovery', 'experiment'],
            'World': ['world', 'international', 'country', 'global', 'nation'],
        }
    
    def categorize_by_keywords(self, text: str) -> str:
        """Categorize using keyword matching."""
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[category] = score
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return "General"
    
    def categorize_article(self, article: Dict) -> str:
        """Categorize a single article."""
        text = f"{article.get('title', '')} {article.get('summary', '')}"
        return self.categorize_by_keywords(text)
    
    def categorize_batch(self, articles: List[Dict]) -> List[Dict]:
        """Categorize multiple articles."""
        for article in articles:
            article['category'] = self.categorize_article(article)
        
        return articles
    
    def get_category_distribution(self, articles: List[Dict]) -> Dict[str, int]:
        """Get distribution of articles across categories."""
        distribution = {cat: 0 for cat in self.categories}
        distribution['General'] = 0
        
        for article in articles:
            category = article.get('category', 'General')
            distribution[category] = distribution.get(category, 0) + 1
        
        return distribution
