from textblob import TextBlob
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyze sentiment of news articles."""
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text."""
        if not text:
            return {'polarity': 0.0, 'subjectivity': 0.0, 'label': 'neutral'}
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Classify sentiment
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'polarity': round(polarity, 3),
                'subjectivity': round(subjectivity, 3),
                'label': label
            }
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {'polarity': 0.0, 'subjectivity': 0.0, 'label': 'neutral'}
    
    def analyze_batch(self, articles: List[Dict]) -> List[Dict]:
        """Analyze sentiment for multiple articles."""
        for article in articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            article['sentiment'] = self.analyze_sentiment(text)
        
        return articles
    
    def get_sentiment_distribution(self, articles: List[Dict]) -> Dict[str, int]:
        """Get distribution of sentiments."""
        distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for article in articles:
            label = article.get('sentiment', {}).get('label', 'neutral')
            distribution[label] += 1
        
        return distribution
