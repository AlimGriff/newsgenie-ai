from collections import Counter
import logging
import re

logger = logging.getLogger(__name__)


class ArticleCategorizer:
    
    def __init__(self):
        self.category_keywords = {
            'Technology': [
                'tech', 'technology', 'software', 'hardware', 'computer', 'ai', 
                'machine learning', 'algorithm', 'cyber', 'digital', 'app', 'smartphone',
                'internet', 'online', 'web', 'gadget', 'coding', 'programming', 
                'google', 'apple', 'microsoft', 'amazon', 'facebook', 'meta', 
                'robot', 'automation', 'blockchain', 'bitcoin', 'cloud', 'chip'
            ],
            'Sports': [
                'sport', 'football', 'soccer', 'basketball', 'tennis', 'golf', 
                'cricket', 'rugby', 'hockey', 'olympics', 'world cup', 'championship', 
                'league', 'tournament', 'match', 'game', 'player', 'team', 'coach', 
                'athlete', 'fifa', 'nba', 'nfl', 'premier league', 'medal', 'trophy'
            ],
            'Business': [
                'business', 'company', 'corporate', 'startup', 'entrepreneur', 
                'retail', 'sales', 'customer', 'brand', 'marketing', 'ceo', 
                'merger', 'acquisition', 'manufacturing', 'workforce', 'hiring'
            ],
            'Finance': [
                'finance', 'financial', 'economy', 'economic', 'market', 'stock', 
                'trading', 'investment', 'investor', 'wall street', 'bank', 'banking', 
                'interest rate', 'bonds', 'currency', 'profit', 'revenue', 'earnings', 
                'nasdaq', 'dow jones', 'ftse', 'inflation', 'recession', 'gdp'
            ],
            'Politics': [
                'politics', 'political', 'government', 'parliament', 'congress', 
                'election', 'vote', 'president', 'prime minister', 'minister', 
                'policy', 'law', 'legislation', 'party', 'conservative', 'labour', 
                'treaty', 'downing street', 'capitol'
            ],
            'Entertainment': [
                'entertainment', 'movie', 'film', 'cinema', 'actor', 'actress', 
                'celebrity', 'music', 'concert', 'album', 'singer', 'band', 
                'tv', 'show', 'netflix', 'disney', 'hollywood', 'oscar', 'grammy'
            ],
            'Health': [
                'health', 'medical', 'medicine', 'doctor', 'hospital', 'patient', 
                'disease', 'virus', 'vaccine', 'covid', 'pandemic', 'healthcare', 
                'drug', 'surgery', 'therapy', 'fitness', 'nutrition', 'cancer'
            ],
            'Science': [
                'science', 'scientific', 'research', 'study', 'discovery', 
                'experiment', 'physics', 'chemistry', 'biology', 'astronomy', 
                'space', 'nasa', 'planet', 'climate', 'environment', 'gene'
            ],
            'World': [
                'international', 'global', 'world', 'foreign', 'country', 
                'conflict', 'war', 'peace', 'united nations', 'refugee', 
                'migration', 'crisis', 'humanitarian'
            ]
        }
        
        self.exclusion_keywords = {
            'Technology': ['protest', 'demonstration', 'strike'],
            'Sports': ['sports bar', 'sports betting'],
        }
    
    def categorize(self, article):
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        source_url = article.get('url', '').lower()
        source = article.get('source', '').lower()
        title_lower = article.get('title', '').lower()
        
        if any(s in source_url or s in source for s in ['espn', 'skysports', '/sport/']):
            return 'Sports'
        if any(s in source_url or s in source for s in ['techcrunch', 'theverge', '/technology/']):
            return 'Technology'
        if any(s in source_url or s in source for s in ['/finance/', 'ft.com']):
            return 'Finance'
        if any(s in source_url or s in source for s in ['/business/']):
            return 'Business'
        
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, title_lower):
                    score += 3
                elif re.search(pattern, text):
                    score += 1
            
            excluded = False
            if category in self.exclusion_keywords:
                for exclusion in self.exclusion_keywords[category]:
                    if exclusion in text:
                        excluded = True
                        break
            
            if not excluded and score > 0:
                category_scores[category] = score
        
        if any(word in text for word in ['protest', 'demonstration', 'rally']):
            if 'Technology' in category_scores:
                category_scores['Technology'] = max(0, category_scores['Technology'] - 5)
            if 'Politics' in category_scores:
                category_scores['Politics'] += 3
            else:
                category_scores['Politics'] = 3
        
        if any(word in text for word in ['strike', 'union', 'workers']):
            if 'Technology' in category_scores:
                category_scores['Technology'] =

