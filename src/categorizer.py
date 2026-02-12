from collections import Counter
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleCategorizer:
    """Categorize news articles using keyword-based classification."""
    
    def __init__(self):
        self.category_keywords = {
            'Technology': [
                'tech', 'technology', 'software', 'hardware', 'computer', 'ai', 'artificial intelligence',
                'machine learning', 'algorithm', 'data', 'cyber', 'digital', 'app', 'smartphone',
                'internet', 'online', 'web', 'startup', 'silicon valley', 'gadget', 'innovation',
                'coding', 'programming', 'developer', 'google', 'apple', 'microsoft', 'amazon',
                'facebook', 'meta', 'twitter', 'robot', 'automation', 'blockchain',
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
                'finance', 'financial', 'economy', 'economic', 'market', 'stock', 'stocks', 'share',
                'shares', 'trading', 'trader', 'investment', 'investor', 'investing', 'portfolio',
                'wall street', 'bank', 'banking', 'central bank', 'federal reserve', 'interest rate',
                'bonds', 'treasury', 'equity', 'commodities', 'forex', 'currency', 'exchange rate',
                'profit', 'revenue', 'earnings', 'dividend', 'bull market', 'bear market',
                'nasdaq', 'dow jones', 'ftse', 'inflation', 'deflation', 'gdp',
                'recession', 'depression', 'fiscal', 'monetary', 'credit', 'debt', 'loan',
                'mortgage', 'pension', 'hedge fund', 'mutual fund', 'etf',
                'asset', 'capital', 'valuation', 'analyst', 'rating', 'index', 'benchmark'
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
                'scientist', 'breakthrough', 'telescope', 'microscope', 'species'
            ],
            'World': [
                'international', 'global', 'world', 'foreign', 'country', 'nation', 'conflict',
                'war', 'peace', 'united nations', 'refugee', 'migration', 'border', 'crisis',
                'embassy', 'ambassador', 'sanctions', 'humanitarian', 'geopolitical'
            ]
        }
        
        self.exclusion_keywords = {
            'Technology': ['food tech', 'med tech', 'health tech', 'protest', 'demonstration', 'strike'],
            'Sports': ['sports bar', 'sports betting', 'esports'],
            'Finance': ['finance minister', 'finance committee'],
        }
    
    def categorize(self, article):
        """Categorize a single article."""
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        source_url = article.get('url', '').lower()
        source = article.get('source', '').lower()
        
        if any(sport in source_url or sport in source for sport in ['espn', 'skysports', 'bbc-sport', 'sports.yahoo', '/sport/']):
            return 'Sports'
        if any(tech in source_url or tech in source for tech in ['techcrunch', 'theverge', 'wired', 'arstechnica', '/technology/']):
            return 'Technology'
        if any(fin in source_url or fin in source for fin in ['reuters/markets', 'marketwatch', 'investing.com', '/finance/', 'ft.com']):
            return 'Finance'
        if any(biz in source_url or biz in source for biz in ['reuters/business', '/business/']):
            return 'Business'
        
        category_scores = {}
        title_lower = article.get('title', '').lower()
        
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
        
        if any(word in text for word in ['protest', 'demonstration', 'rally', 'march', 'activist']):
            if 'Technology' in category_scores:
                category_scores['Technology'] = max(0, category_scores['Technology'] - 5)
            if 'Politics' in category_scores:
                category_scores['Politics'] += 3
            else:
                category_scores['Politics'] = 3
        
        if any(word in text for word in ['strike', 'union', 'workers', 'employees']):
            if 'Technology' in category_scores:
                category_scores['Technology'] = max(0, category_scores['Technology'] - 5)
            if 'Business' in category_scores:
                category_scores['Business'] += 2
        
        if 'Finance' in category_scores and 'Business' in category_scores:
            finance_specific = ['stock', 'market', 'trading', 'investment', 'bank', 'currency', 
                              'inflation', 'interest rate', 'profit', 'earnings', 'revenue']
            has_finance_specific = any(term in text for term in finance_specific)
            
            if has_finance_specific:
                category_scores['Finance'] += 3
        
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            min_threshold = 1 if best_category in ['Finance', 'Sports', 'Politics'] else 2
            
            if category_scores[best_category] >= min_threshold:
                return best_category
        
        return 'General'
    
    def categorize_batch(self, articles):
        """Categorize multiple articles."""
        for article in articles:
            article['category'] = self.categorize(article)
        return articles
    
    def get_category_distribution(self, articles):
        """Get distribution of articles across categories."""
        categories = [article.get('category', 'General') for article in articles]
        return dict(Counter(categories))
