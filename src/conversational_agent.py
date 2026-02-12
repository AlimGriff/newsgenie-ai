from typing import List, Dict, Optional
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class ConversationalAgent:
    """Conversational AI agent for NewsGenie."""
    
    def __init__(self, articles):
        self.articles = articles
        self.conversation_history = []
        
    def process_query(self, user_query):
        """
        Process user query and return conversational response.
        
        Supported queries:
        - "What are the top stories today?"
        - "Tell me about [topic]"
        - "What's the sentiment on [topic]?"
        - "Show me sports news"
        - "Summarize the technology news"
        - "What's trending?"
        """
        query_lower = user_query.lower().strip()
        
        # Store in history
        self.conversation_history.append({
            'role': 'user',
            'content': user_query,
            'timestamp': datetime.now()
        })
        
        # Intent detection
        response = self._generate_response(query_lower)
        
        # Store response
        self.conversation_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now()
        })
        
        return response
    
    def _generate_response(self, query):
        """Generate response based on query intent."""
        
        # Greeting
        if any(word in query for word in ['hello', 'hi', 'hey', 'greetings']):
            return self._handle_greeting()
        
        # Help
        if any(word in query for word in ['help', 'what can you do', 'commands']):
            return self._handle_help()
        
        # UK-specific queries
        if any(phrase in query for phrase in ['uk news', 'british news', 'britain', 'united kingdom', 'england', 'scotland', 'wales', 'latest uk']):
            return self._handle_uk_news()
        
        # Top stories
        if any(phrase in query for phrase in ['top stories', 'latest news', 'headlines', 'what\'s new', 'whats new']):
            return self._handle_top_stories()
        
        # Category-specific
        categories = ['technology', 'sports', 'business', 'finance', 'politics', 
                     'entertainment', 'health', 'science', 'world']
        for category in categories:
            if category in query:
                return self._handle_category_query(category)
        
        # Sentiment queries
        if 'sentiment' in query or 'feeling' in query or 'mood' in query:
            return self._handle_sentiment_query(query)
        
        # Trending/popular
        if any(word in query for word in ['trending', 'popular', 'hot', 'viral']):
            return self._handle_trending()
        
        # Summarize
        if 'summarize' in query or 'summary' in query or 'brief' in query:
            return self._handle_summarize(query)
        
        # Search for topic
        if 'about' in query or 'find' in query or 'search' in query:
            topic = self._extract_topic(query)
            if topic:
                return self._handle_topic_search(topic)
        
        # Count queries
        if any(word in query for word in ['how many', 'number of', 'count']):
            return self._handle_count_query(query)
        
        # Default: Try topic search
        return self._handle_general_query(query)
    
    def _handle_greeting(self):
        """Handle greeting queries."""
        return (
            "Hello! I'm NewsGenie AI, your intelligent news assistant.\n\n"
            "I can help you:\n"
            "- Get latest headlines and top stories\n"
            "- Find news on specific topics\n"
            "- Analyze sentiment and trends\n"
            "- Summarize news by category\n"
            "- Answer questions about current events\n\n"
            "What would you like to know?"
        )
    
    def _handle_help(self):
        """Handle help queries."""
        return (
            "**Here's what I can do:**\n\n"
            "**Get News:**\n"
            "- What are the top stories?\n"
            "- Show me sports news\n"
            "- Latest technology headlines\n"
            "- What's the latest UK news?\n\n"
            "**Search Topics:**\n"
            "- Tell me about climate change\n"
            "- Find articles about AI\n\n"
            "**Analysis:**\n"
            "- What's trending?\n"
            "- What's the sentiment on politics?\n"
            "- Summarize the

