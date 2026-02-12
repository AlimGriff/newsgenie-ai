from collections import Counter
from datetime import datetime
import re


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
        
        response = self.generate_response(query_lower)
        
        self.conversation_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now()
        })
        
        return response
    
    def generate_response(self, query):
        if 'hello' in query or 'hi' in query:
            return "Hello! I'm NewsGenie AI. Ask me about the news!"
        
        if 'help' in query:
            return "I can help you find news, analyze sentiment, and show trending topics."
        
        if 'uk news' in query or 'british' in query:
            return self.get_uk_news()
        
        if 'top stories' in query or 'headlines' in query:
            return self.get_top_stories()
        
        if 'trending' in query:
            return self.get_trending()
        
        if 'how many' in query:
            return self.get_count()
        
        return "Try asking: 'What are the top stories?' or 'What's trending?'"
    
    def get_uk_news(self):
        uk_sources = ['BBC', 'Sky News', 'The Guardian', 'Independent']
        uk_articles = [a for a in self.articles if any(s in a.get('source', '') for s in uk_sources)]
        
        if not uk_articles:
            return "No UK news available. Try refreshing."
        
        response = f"Latest UK News ({len(uk_articles)} articles):\n\n"
        for i, article in enumerate(uk_articles[:5], 1):
            response += f"{i}. {article.get('title', 'No title')}\n"
        return response
    
    def get_top_stories(self):
        if not self.articles:
            return "No articles available."
        
        response = "Top Stories:\n\n"
        for i, article in enumerate(self.articles[:5], 1):
            title = article.get('title', 'No title')
            source = article.get('source', 'Unknown')
            response += f"{i}. {title} ({source})\n"
        return response
    
    def get_trending(self):
        if not self.articles:
            return "No articles available."
        
        words = []
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to'}
        
        for article in self.articles:
            text = article.get('title', '').lower()
            words.extend([w for w in re.findall(r'\b[a-z]{4,}\b', text) if w not in stopwords])
        
        counts = Counter(words)
        response = "Trending Topics:\n\n"
        for i, (word, count) in enumerate(counts.most_common(10), 1):
            response += f"{i}. {word.title()} ({count})\n"
        return response
    
    def get_count(self):
        total = len(self.articles)
        categories = Counter([a.get('category', 'General') for a in self.articles])
        
        response = f"Total Articles: {total}\n\n"
        for category, count in categories.most_common():
            response += f"{category}: {count}\n"
        return response
    
    def clear_history(self):
        self.conversation_history = []
    
    def get_conversation_history(self):
        return self.conversation_history
