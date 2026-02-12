from collections import Counter
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class ConversationalAgent:
    
    def __init__(self, articles):
        self.articles = articles
        self.conversation_history = []
        
    def process_query(self, user_query):
        query_lower = user_query.lower().strip()
        
        self.conversation_history.append({
            'role': 'user',
            'content': user_query,
            'timestamp': datetime.now()
        })
        
        response = self._generate_response(query_lower)
        
        self.conversation_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now()
        })
        
        return response
    
    def _generate_response(self, query):
        
        if any(word in query for word in ['hello', 'hi', 'hey']):
            return self._handle_greeting()
        
        if any(word in query for word in ['help', 'what can you do']):
            return self._handle_help()
        
        if any(phrase in query for phrase in ['uk news', 'british news', 'latest uk']):
            return self._handle_uk_news()
        
        if any(phrase in query for phrase in ['top stories', 'latest news', 'headlines']):
            return self._handle_top_stories()
        
        categories = ['technology', 'sports', 'business', 'finance', 'politics']
        for category in categories:
            if category in query:
                return self._handle_category_query(category)
        
        if 'sentiment' in query:
            return self._handle_sentiment_query(query)
        
        if any(word in query for word in ['trending', 'popular']):
            return self._handle_trending()
        
        if 'about' in query or 'find' in query:
            topic = self._extract_topic(query)
            if topic:
                return self._handle_topic_search(topic)
        
        if any(word in query for word in ['how many', 'count']):
            return self._handle_count_query()
        
        return self._handle_general_query(query)
    
    def _handle_greeting(self):
        return (
            "Hello! I'm NewsGenie AI, your intelligent news assistant.\n\n"
            "I can help you:\n"
            "- Get latest headlines\n"
            "- Find news on topics\n"
            "- Analyze sentiment\n"
            "- Show trending news\n\n"
            "What would you like to know?"
        )
    
    def _handle_help(self):
        return (
            "**Here's what I can do:**\n\n"
            "**Get News:**\n"
            "- What are the top stories?\n"
            "- Show me sports news\n"
            "- What's the latest UK news?\n\n"
            "**Search:**\n"
            "- Tell me about climate change\n"
            "- Find articles about AI\n\n"
            "**Analysis:**\n"
            "- What's trending?\n"
            "- What's the sentiment?\n"
            "- How many articles?\n"
        )
    
    def _handle_uk_news(self):
        uk_sources = ['BBC', 'Sky News', 'The Guardian', 'Independent', 'Telegraph']
        
        uk_articles = [
            a for a in self.articles
            if any(source in a.get('source', '') for source in uk_sources)
        ]
        
        if not](#)

