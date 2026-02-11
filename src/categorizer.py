from typing import List, Dict
from collections import Counter
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleCategorizer:
    """Categorize news articles using keyword-based classification."""
    
    def __init__(self):
        # Enhanced keyword mapping with more specific terms
        self.category_keywords = {
            'Technology': [
                'tech', 'technology', 'software', 'hardware', 'computer', 'ai', 'artificial intelligence',
                'machine learning', 'algorithm', 'data', 'cyber', 'digital', 'app', 'smartphone',
                'internet', 'online', 'web', 'startup', 'silicon valley', 'gadget', 'innovation',
                'coding', 'programming', 'developer', 'google', 'apple', 'microsoft', 'amazon',
                'facebook', 'meta', 'twitter', 'tesla', 'spacex', 'robot', 'automation', 'blockchain',
                'cryptocurrency', 'bitcoin', 'cloud computing', '5g', 'virtual reality', 'vr', 'ar',
                'tech giant', 'tech company', 'chip', 'semiconductor', 'processor', 'gaming'
            ],
            'Sports': [
                'sport', 'football', 'soccer', 'basketball', 'baseball', 'tennis', 'golf', 'cricket',
                'rugby', 'hockey', 'olympics', 'world cup', 'championship', 'league', 'tournament',
                'match', 'game', 'player', 'team', 'coach', 'athlete', 'fifa', 'nba', 'nfl', 'mlb',
                'premier league', 'champions league', 'medal', 'trophy', 'score', 'goal', 'win',
                'defeat', 'boxing', 'mma', 'ufc', 'formula 1', 'f1', 'racing', 'marathon', 'swimming',
                'super bowl', 'world series', 'final', 'semifinal', 'playoff', 'stadium', 'arena'
            ],
            'Business': [
                'business', 'company', 'corporate', 'startup', 'entrepreneur', 'industry', 'retail',
                'e-commerce', 'sales', 'customer', 'brand', 'marketing', 'ceo', 'executive',
                'merger', 'acquisition', 'venture capital', 'ipo', 'partnership', 'deal',
                'supply chain', 'manufacturing', 'production', 'workforce', 'employment',
                'hiring', 'layoff', 'expansion', 'growth strategy', 'business model'
            ],
            'Finance': [
                # Core finance terms
                'finance', 'financial', 'economy', 'economic', 'market', 'stock', 'stocks', 'share',
                'shares', 'trading', 'trader', 'investment', 'investor', 'investing', 'portfolio',
                
                # Banking
                'bank', 'banking', 'banker', 'central bank', 'federal reserve', 'interest rate',
                'lloyds', 'barclays', 'hsbc', 'natwest', 'santander', 'citibank', 'jpmorgan',
                
                # Markets
                'wall street', 'bonds', 'treasury', 'equity', 'commodities', 'forex', 'currency',
                'exchange rate', 'bull market', 'bear market', 'nasdaq', 'dow jones', 'ftse',
                's&p 500', 's&p', 'dow', 'index', 'benchmark',
                
                # Economic indicators
                'inflation', 'deflation', 'gdp', 'recession', 'depression', 'fiscal', 'monetary',
                'unemployment', 'employment', 'wage', 'salary',
                
                # Financial products
                'credit', 'debt', 'loan', 'mortgage', 'pension', 'hedge fund', 'mutual fund',
                'etf', 'asset', 'capital', 'valuation', 'ipo', 'dividend',
                
                # Crypto (if not tech-focused)
                'cryptocurrency', 'bitcoin', 'ethereum', 'crypto', 'blockchain finance', 'fintech',
                
                # Financial activities
                'profit', 'revenue', 'earnings', 'loss', 'turnover', 'quarter', 'quarterly',
                'annual report', 'balance sheet', 'cash flow', 'analyst', 'rating',
                
                # Financial institutions
                'wealth management', 'insurance', 'pension fund', 'sovereign wealth',
                'investment bank', 'retail bank', 'commercial bank',
                
                # Money-related
                'money', 'cash', 'pound', 'dollar', 'euro', 'yen', 'price', 'cost',
                'spending', 'savings', 'budget', 'tax', 'taxation'
            ],
            'Politics': [
                'politics', 'political', 'government', 'parliament', 'congress', 'senate', 'election',
                'vote', 'democracy', 'president', 'prime minister', 'minister', 'policy', 'law',
                'legislation', 'campaign', 'party', 'republican', 'democrat', 'conservative', 'labour',
                'diplomatic', 'treaty', 'summit', 'white house', 'downing street', 'capitol',
                'senator', 'representative', 'governor', 'mayor', 'referendum', 'ballot'
            ],
            'Entertainment': [
                'entertainment', 'movie', 'film', 'cinema', 'actor', 'actress', 'celebrity', 'music',
                'concert', 'album', 'song', 'singer', 'band', 'tv', 'television', 'show', 'series',
                'netflix', 'disney', 'hollywood', 'bollywood', 'oscar', 'grammy', 'emmy', 'theater',
                'theatre', 'performance', 'artist', 'fashion', 'style', 'streaming', 'premiere',
                'box office', 'red carpet', 'awards', 'nomination', 'soundtrack'
            ],
            'Health': [
                'health', 'medical', 'medicine', 'doctor', 'hospital', 'patient', 'disease', 'virus',
                'vaccine', 'covid', 'coronavirus', 'pandemic', 'epidemic', 'healthcare', 'treatment',
                'drug', 'pharmaceutical', 'surgery', 'therapy', 'mental health', 'fitness', 'wellness',
                'nutrition', 'diet', 'obesity', 'cancer', 'diabetes', 'research', 'clinical trial',
                'symptom', 'diagnosis', 'cure', 'prevention', 'immune', 'prescription'
            ],
            'Science': [
                'science', 'scientific', 'research', 'study', 'university', 'discovery', 'experiment',
                'physics', 'chemistry', 'biology', 'astronomy', 'space', 'nasa', 'planet', 'climate',
                'environment', 'evolution', 'gene', 'dna', 'laboratory', 'professor', 'academic',
                'scientist', 'breakthrough', 'innovation', 'telescope', 'microscope', 'species'
            ],
            'World': [
                'international', 'global', 'world', 'foreign', 'country', 'nation', 'conflict',
                'war', 'peace', 'united nations', 'refugee', 'migration', 'border', 'crisis',
                'embassy', 'ambassador', 'sanctions', 'humanitarian', 'geopolitical'
            ]
        }
        
        # Anti-keywords to prevent miscategorization
        self.exclusion_keywords = {
            'Technology': ['food tech', 'med tech', 'health tech'],
            'Sports': ['sports bar', 'sports betting', 'esports'],
        }
    
    def categorize(self, article: Dict) -> str:
        """Categorize a single article with improved accuracy."""
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        # Check source URL for category hints
        source_url = article.get('url', '').lower()
        source = article.get('source', '').lower()
        
        # Direct source matching (most reliable)
        if any(sport in source_url or sport in source for sport in ['espn', 'skysports', 'bbc-sport', 'sports.yahoo', '/sport/']):
            return 'Sports'
        if any(tech in source_url or tech in source for tech in ['techcrunch', 'theverge', 'wired', 'arstechnica']):
            return 'Technology'
        if any(biz in source_url or biz in source for biz in ['reuters/business', 'ft.com', 'bloomberg']):
            return 'Business'
        if any(fin in source_url or fin in source for fin in ['reuters/markets', 'marketwatch', 'investing.com']):
            return 'Finance'
        
        # Score each category
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            matches = []
            
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text):
                    score += 1
                    matches.append(keyword)
            
            # Check exclusions
            excluded = False
            if category in self.exclusion_keywords:
                for exclusion in self.exclusion_keywords[category]:
                    if exclusion in text:
                        excluded = True
                        break
            
            if not excluded and score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            
            # Require minimum threshold
            if category_scores[best_category] >= 2:
                logger.info(f"Categorized '{article.get('title', 'Unknown')}' as {best_category} (score: {category_scores[best_category]})")
                return best_category
        
        # Default to General if no clear match
        logger.info(f"Categorized '{article.get('title', 'Unknown')}' as General (no clear match)")
        return 'General'
    
    def categorize_batch(self, articles: List[Dict]) -> List[Dict]:
        """Categorize multiple articles."""
        for article in articles:
            article['category'] = self.categorize(article)
        
        return articles
    
    def get_category_distribution(self, articles: List[Dict]) -> Dict[str, int]:
        """Get distribution of articles across categories."""
        categories = [article.get('category', 'General') for article in articles]
        return dict(Counter(categories))
