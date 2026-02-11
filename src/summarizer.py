from typing import List, Dict
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleSummarizer:
    """Summarize news articles using extractive summarization."""
    
    def __init__(self, model_name: str = None):
        # Simple extractive summarization - no heavy models needed
        logger.info("Initialized simple summarizer")
    
    def summarize(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """Generate summary using simple extractive method."""
        if not text:
            return ""
        
        try:
            # Split into sentences
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return text[:max_length] + "..."
            
            # Take first 2-3 sentences as summary
            summary_sentences = []
            current_length = 0
            
            for sentence in sentences[:5]:  # Check first 5 sentences
                if current_length + len(sentence) <= max_length:
                    summary_sentences.append(sentence)
                    current_length += len(sentence)
                else:
                    break
            
            if not summary_sentences:
                summary_sentences = [sentences[0]]
            
            summary = '. '.join(summary_sentences)
            if not summary.endswith('.'):
                summary += '.'
            
            return summary
        
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text
    
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
