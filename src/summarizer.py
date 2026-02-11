from transformers import pipeline
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleSummarizer:
    """Summarize news articles using transformer models."""
    
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        try:
            self.summarizer = pipeline("summarization", model=model_name)
            logger.info(f"Loaded summarization model: {model_name}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.summarizer = None
    
    def summarize(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """Generate summary for a single text."""
        if not self.summarizer or not text:
            return text[:200] + "..." if len(text) > 200 else text
        
        try:
            # Split long texts into chunks
            max_chunk_size = 1024
            if len(text) > max_chunk_size:
                text = text[:max_chunk_size]
            
            summary = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            
            return summary[0]['summary_text']
        
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return text[:200] + "..." if len(text) > 200 else text
    
    def summarize_batch(self, articles: List[Dict]) -> List[Dict]:
        """Summarize multiple articles."""
        for article in articles:
            content = article.get('text', article.get('summary', ''))
            if content:
                article['ai_summary'] = self.summarize(content)
        
        return articles
    
    def generate_multi_article_summary(self, articles: List[Dict], topic: str) -> str:
        """Generate a summary across multiple articles about a topic."""
        if not articles:
            return f"No articles found about {topic}"
        
        # Combine summaries
        combined_text = " ".join([
            article.get('ai_summary', article.get('summary', ''))
            for article in articles[:5]  # Limit to 5 articles
        ])
        
        if combined_text:
            return self.summarize(combined_text, max_length=200, min_length=100)
        
        return f"Multiple articles discuss {topic}..."
