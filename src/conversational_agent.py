from collections import Counter
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class ConversationalAgent:
    
    def __init__(self, articles, llm_handler=None):
        self.articles = articles
        self.llm_handler = llm_handler
        self.conversation_history = []
        self.use_llm = llm_handler is not None
        
    def process_query(self, user_query):
        query_lower = user_query.lower().strip()
        
        self.conversation_history.append({
            'role': 'user',
            'content': user_query,
            'timestamp': datetime.now()
        })
        
        response = self.generate_response(query_lower, user_query)
        
        self.conversation_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now()
        })
        
        return response
    
    def generate_response(self, query_lower, original_query):
        if any(word in query_lower for word in ['hello', 'hi', 'hey']):
            return self.handle_greeting()
        
        if 'help' in query_lower:
            return self.handle_help()
        
        if any(phrase in query_lower for phrase in ['uk news', 'british news', 'latest uk', 'news uk', 'uk today']):
            return self.get_uk_news()
        
        if any(phrase in query_lower for phrase in ['top stories', 'top news', 'latest news', 'headlines', 'news today']):
            return self.get_top_stories()
        
        if any(word in query_lower for word in ['trending', 'popular']):
            return self.get_trending()
        
        if 'sentiment' in query_lower:
            return self.get_sentiment()
        
        if any(phrase in query_lower for phrase in ['how many', 'count']):
            return self.get_count()
        
        categories = ['technology', 'sports', 'business', 'finance', 'politics', 'health', 'science']
        for category in categories:
            if category in query_lower:
                return self.get_category_news(category)
        
        if 'summarize' in query_lower or 'summary' in query_lower:
            return self.get_top_stories()
        
        keywords = re.findall(r'\b[a-z]{4,}\b', query_lower)
        stopwords = {'the', 'news', 'tell', 'show', 'what', 'latest', 'today', 'about', 'find'}
        keywords = [k for k in keywords if k not in stopwords]
        
        if keywords:
            return self.search_articles(keywords[0])
        
        return "Try asking: 'Show me UK news' or 'What are the top stories?'"
    
    def handle_greeting(self):
        return (
            "Hello! I'm NewsGenie AI, your intelligent news assistant.\n\n"
            "I can help you:\n"
            "- Get latest headlines and UK news\n"
            "- Find news on specific topics\n"
            "- Analyze sentiment and trends\n"
            "- Answer questions about the news\n\n"
            "What would you like to know?"
        )
    
    def handle_help(self):
        return (
            "**Here's what I can do:**\n\n"
            "**Get News:**\n"
            "- What are the top stories?\n"
            "- Show me UK news\n"
            "- Latest sports/technology/business news\n\n"
            "**Search & Analyze:**\n"
            "- Tell me about [topic]\n"
            "- What's trending?\n"
            "- What's the sentiment?\n\n"
            "**Statistics:**\n"
            "- How many articles are there?\n"
        )
    
    def get_uk_news(self):
        uk_sources = ['BBC', 'Sky News', 'The Guardian', 'Independent', 'Telegraph']
        uk_articles = [a for a in self.articles if any(s in a.get('source', '') for s in uk_sources)]
        
        if not uk_articles:
            return "No UK news available right now. Try clicking 'Refresh News' in the sidebar."
        
        response = f"**Latest UK News** ({len(uk_articles)} articles):\n\n"
        for i, article in enumerate(uk_articles[:5], 1):
            title = article.get('title', 'No title')
            source = article.get('source', 'Unknown')
            category = article.get('category', 'General')
            response += f"{i}. **{title}**\n   {category} | {source}\n\n"
        
        if len(uk_articles) > 5:
            response += f"...and {len(uk_articles) - 5} more UK articles available"
        
        return response
    
    def get_top_stories(self):
        if not self.articles:
            return "No articles available."
        
        response = "**Top Stories:**\n\n"
        for i, article in enumerate(self.articles[:5], 1):
            title = article.get('title', 'No title')
            source = article.get('source', 'Unknown')
            category = article.get('category', 'General')
            sentiment = article.get('sentiment', {}).get('label', 'neutral')
            response += f"{i}. **{title}**\n   {category} | {source} | Sentiment: {sentiment}\n\n"
        return response
    
    def get_category_news(self, category):
        category_title = category.title()
        category_articles = [a for a in self.articles if a.get('category', '').lower() == category]
        
        if not category_articles:
            return f"No {category_title} articles found."
        
        response = f"**{category_title} News** ({len(category_articles)} articles):\n\n"
        for i, article in enumerate(category_articles[:5], 1):
            title = article.get('title', 'No title')
            source = article.get('source', 'Unknown')
            response += f"{i}. {title} ({source})\n"
        
        return response
    
    def get_trending(self):
        if not self.articles:
            return "No articles available."
        
        words = []
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'is', 'are', 'says'}
        
        for article in self.articles:
            text = article.get('title', '').lower()
            words.extend([w for w in re.findall(r'\b[a-z]{4,}\b', text) if w not in stopwords])
        
        counts = Counter(words)
        response = "**Trending Topics:**\n\n"
        for i, (word, count) in enumerate(counts.most_common(10), 1):
            bar = '=' * min(count, 20)
            response += f"{i}. **{word.title()}** {bar} ({count})\n"
        return response
    
    def get_sentiment(self):
        if not self.articles:
            return "No articles available."
        
        sentiments = [a.get('sentiment', {}).get('label', 'neutral') for a in self.articles]
        positive = sentiments.count('positive')
        negative = sentiments.count('negative')
        neutral = sentiments.count('neutral')
        total = len(sentiments)
        
        response = "**Overall Sentiment Analysis:**\n\n"
        response += f"Positive: {positive} ({positive*100//total}%)\n"
        response += f"Negative: {negative} ({negative*100//total}%)\n"
        response += f"Neutral: {neutral} ({neutral*100//total}%)\n"
        
        return response
    
    def get_count(self):
        total = len(self.articles)
        categories = Counter([a.get('category', 'General') for a in self.articles])
        
        response = f"**Article Statistics:**\n\nTotal: {total} articles\n\n**By Category:**\n"
        for category, count in categories.most_common():
            response += f"{category}: {count}\n"
        return response
    
    def search_articles(self, keyword):
        results = [a for a in self.articles if keyword.lower() in a.get('title', '').lower()]
        
        if not results:
            return f"No articles found about '{keyword}'."
        
        response = f"**Found {len(results)} articles about '{keyword}':**\n\n"
        for i, article in enumerate(results[:5], 1):
            title = article.get('title', 'No title')
            response += f"{i}. {title}\n"
        return response
    
    def clear_history(self):
        self.conversation_history = []
    
    def get_conversation_history(self):
        return self.conversation_history
