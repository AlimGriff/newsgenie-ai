from collections import Counter
import re


class ArticleCategorizer:
    
    def __init__(self):
        self.category_keywords = {
            'Technology': [
                'tech', 'technology', 'software', 'hardware', 'computer', 'ai', 
                'digital', 'app', 'smartphone', 'internet', 'online', 'web', 
                'google', 'apple', 'microsoft', 'amazon', 'facebook', 'meta'
            ],
            'Sports': [
                'sport', 'football', 'soccer', 'basketball', 'tennis', 'golf', 
                'cricket', 'rugby', 'hockey', 'olympics', 'championship', 
                'league', 'tournament', 'match', 'game', 'player', 'team'
            ],
            'Business': [
                'business', 'company', 'corporate', 'startup', 'entrepreneur', 
                'retail', 'sales', 'customer', 'brand', 'ceo'
            ],
            'Finance': [
                'finance', 'financial', 'economy', 'market', 'stock', 
                'trading', 'investment', 'bank', 'banking', 'profit', 
                'revenue', 'earnings', 'inflation'
            ],
            'Politics': [
                'politics', 'political', 'government', 'parliament', 'election', 
                'vote', 'president', 'minister', 'policy', 'law'
            ],
            'Entertainment': [
                'entertainment', 'movie', 'film', 'music', 'celebrity', 
                'actor', 'actress', 'concert', 'show', 'netflix'
            ],
            'Health': [
                'health', 'medical', 'medicine', 'doctor', 'hospital', 
                'patient', 'disease', 'vaccine', 'covid'
            ],
            'Science': [
                'science', 'scientific', 'research', 'study', 'discovery', 
                'space', 'nasa', 'climate', 'environment'
            ],
            'World': [
                'international', 'global', 'world', 'foreign', 'country', 
                'conflict', 'war', 'peace'
            ]
        }
    
    def categorize(self, article):
        text = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        full_text = text + ' ' + summary
        
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 3
                elif keyword in full_text:
                    score += 1
            
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
