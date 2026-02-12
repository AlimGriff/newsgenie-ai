from typing import List, Dict, Optional
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class ConversationalAgent:
    """Conversational AI agent for NewsGenie."""
    
    def __init__(self, articles: List[Dict]):
        self.articles = articles
        self.conversation_history = []
        
    def process_query(self, user_query: str) -> str:
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
    
    def _generate_response(self, query: str) -> str:
        """Generate response based on query intent."""
        
        # Greeting
        if any(word in query for word in ['hello', 'hi', 'hey', 'greetings']):
            return self._handle_greeting()
        
        # Help
        if any(word in query for word in ['help', 'what can you do', 'commands']):
            return self._handle_help()
        
        # Top stories
        if any(phrase in query for phrase in ['top stories', 'latest news', 'headlines', 'what\'s new']):
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
    
    def _handle_greeting(self) -> str:
        """Handle greeting queries."""
        return (
            "👋 Hello! I'm NewsGenie AI, your intelligent news assistant.\n\n"
            "I can help you:\n"
            "• Get latest headlines and top stories\n"
            "• Find news on specific topics\n"
            "• Analyze sentiment and trends\n"
            "• Summarize news by category\n"
            "• Answer questions about current events\n\n"
            "What would you like to know?"
        )
    
    def _handle_help(self) -> str:
        """Handle help queries."""
        return (
            "🤖 **Here's what I can do:**\n\n"
            "📰 **Get News:**\n"
            "• \"What are the top stories?\"\n"
            "• \"Show me sports news\"\n"
            "• \"Latest technology headlines\"\n\n"
            "🔍 **Search Topics:**\n"
            "• \"Tell me about climate change\"\n"
            "• \"Find articles about AI\"\n\n"
            "📊 **Analysis:**\n"
            "• \"What's trending?\"\n"
            "• \"What's the sentiment on politics?\"\n"
            "• \"Summarize the business news\"\n\n"
            "❓ **Ask Questions:**\n"
            "• \"How many sports articles are there?\"\n"
            "• \"What's the most positive news today?\"\n\n"
            "Just ask me anything about the news!"
        )
    
    def _handle_top_stories(self, limit: int = 5) -> str:
        """Return top stories."""
        if not self.articles:
            return "❌ No news articles available at the moment. Please refresh the page."
        
        top_articles = self.articles[:limit]
        
        response = f"📰 **Top {limit} Stories:**\n\n"
        
        for i, article in enumerate(top_articles, 1):
            title = article.get('title', 'No title')
            source = article.get('source', 'Unknown')
            category = article.get('category', 'General')
            sentiment = article.get('sentiment', {}).get('label', 'neutral')
            
            emoji = '🔴' if sentiment == 'negative' else '🟢' if sentiment == 'positive' else '🟡'
            
            response += f"{i}. **{title}**\n"
            response += f"   📂 {category} | 📰 {source} | {emoji} {sentiment.title()}\n\n"
        
        return response
    
    def _handle_category_query(self, category: str) -> str:
        """Handle category-specific queries."""
        category_title = category.title()
        
        category_articles = [
            a for a in self.articles 
            if a.get('category', '').lower() == category
        ]
        
        if not category_articles:
            return f"❌ No {category_title} articles found. Try a different category."
        
        count = len(category_articles)
        
        # Get sentiment distribution
        sentiments = [a.get('sentiment', {}).get('label', 'neutral') 
                     for a in category_articles]
        positive = sentiments.count('positive')
        negative = sentiments.count('negative')
        neutral = sentiments.count('neutral')
        
        response = f"📊 **{category_title} News Summary:**\n\n"
        response += f"Found **{count} articles** in {category_title}\n\n"
        response += f"**Sentiment Breakdown:**\n"
        response += f"🟢 Positive: {positive} ({positive/count*100:.0f}%)\n"
        response += f"🔴 Negative: {negative} ({negative/count*100:.0f}%)\n"
        response += f"🟡 Neutral: {neutral} ({neutral/count*100:.0f}%)\n\n"
        
        # Show top 3 headlines
        response += f"**Top Headlines:**\n\n"
        for i, article in enumerate(category_articles[:3], 1):
            title = article.get('title', 'No title')
            response += f"{i}. {title}\n"
        
        return response
    
    def _handle_sentiment_query(self, query: str) -> str:
        """Handle sentiment analysis queries."""
        if not self.articles:
            return "❌ No articles available for sentiment analysis."
        
        # Check if query mentions specific topic
        topic = self._extract_topic(query)
        
        if topic:
            relevant_articles = [
                a for a in self.articles
                if topic.lower() in a.get('title', '').lower() or 
                   topic.lower() in a.get('summary', '').lower()
            ]
            
            if not relevant_articles:
                return f"❌ No articles found about '{topic}' to analyze sentiment."
            
            articles_to_analyze = relevant_articles
            context = f"about **{topic}**"
        else:
            articles_to_analyze = self.articles
            context = "overall"
        
        # Calculate sentiment
        sentiments = [a.get('sentiment', {}).get('label', 'neutral') 
                     for a in articles_to_analyze]
        polarities = [a.get('sentiment', {}).get('polarity', 0) 
                     for a in articles_to_analyze]
        
        positive = sentiments.count('positive')
        negative = sentiments.count('negative')
        neutral = sentiments.count('neutral')
        total = len(sentiments)
        avg_polarity = sum(polarities) / len(polarities) if polarities else 0
        
        # Determine overall sentiment
        if avg_polarity > 0.1:
            overall = "positive 🟢"
        elif avg_polarity < -0.1:
            overall = "negative 🔴"
        else:
            overall = "neutral 🟡"
        
        response = f"📊 **Sentiment Analysis {context}:**\n\n"
        response += f"**Overall Sentiment:** {overall}\n"
        response += f"**Sentiment Score:** {avg_polarity:.2f} (-1 to +1)\n\n"
        response += f"**Distribution** (from {total} articles):\n"
        response += f"🟢 Positive: {positive} ({positive/total*100:.0f}%)\n"
        response += f"🔴 Negative: {negative} ({negative/total*100:.0f}%)\n"
        response += f"🟡 Neutral: {neutral} ({neutral/total*100:.0f}%)\n"
        
        return response
    
    def _handle_trending(self) -> str:
        """Handle trending topics queries."""
        from collections import Counter
        import re
        
        if not self.articles:
            return "❌ No articles available to analyze trends."
        
        # Extract keywords from all articles
        all_words = []
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                    'to', 'for', 'of', 'as', 'by', 'with', 'is', 'are', 'was',
                    'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does',
                    'did', 'will', 'would', 'could', 'should', 'may', 'might'}
        
        for article in self.articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            words = re.findall(r'\b[a-z]{4,}\b', text.lower())
            all_words.extend([w for w in words if w not in stopwords])
        
        # Get top keywords
        keyword_counts = Counter(all_words)
        top_keywords = keyword_counts.most_common(10)
        
        response = "🔥 **Trending Topics:**\n\n"
        
        for i, (keyword, count) in enumerate(top_keywords, 1):
            bar = '█' * min(count, 20)
            response += f"{i}. **{keyword.title()}** {bar} ({count})\n"
        
        return response
    
    def _handle_summarize(self, query: str) -> str:
        """Handle summarization requests."""
        # Check if specific category mentioned
        categories = ['technology', 'sports', 'business', 'finance', 'politics', 
                     'entertainment', 'health', 'science', 'world']
        
        category = None
        for cat in categories:
            if cat in query:
                category = cat
                break
        
        if category:
            return self._handle_category_query(category)
        else:
            return self._handle_top_stories()
    
    def _handle_topic_search(self, topic: str) -> str:
        """Search for articles about specific topic."""
        relevant_articles = [
            a for a in self.articles
            if topic.lower() in a.get('title', '').lower() or 
               topic.lower() in a.get('summary', '').lower()
        ]
        
        if not relevant_articles:
            return f"❌ No articles found about '{topic}'. Try a different search term."
        
        count = len(relevant_articles)
        
        response = f"🔍 **Found {count} articles about '{topic}':**\n\n"
        
        for i, article in enumerate(relevant_articles[:5], 1):
            title = article.get('title', 'No title')
            source = article.get('source', 'Unknown')
            category = article.get('category', 'General')
            sentiment = article.get('sentiment', {}).get('label', 'neutral')
            
            emoji = '🔴' if sentiment == 'negative' else '🟢' if sentiment == 'positive' else '🟡'
            
            response += f"{i}. **{title}**\n"
            response += f"   📂 {category} | 📰 {source} | {emoji} {sentiment.title()}\n\n"
        
        if count > 5:
            response += f"\n_...and {count - 5} more articles_"
        
        return response
    
    def _handle_count_query(self, query: str) -> str:
        """Handle counting queries."""
        total = len(self.articles)
        
        # Count by category
        from collections import Counter
        categories = [a.get('category', 'General') for a in self.articles]
        category_counts = Counter(categories)
        
        response = f"📊 **Article Statistics:**\n\n"
        response += f"**Total Articles:** {total}\n\n"
        response += f"**By Category:**\n"
        
        for category, count in category_counts.most_common():
            response += f"• {category}: {count}\n"
        
        return response
    
    def _handle_general_query(self, query: str) -> str:
        """Handle general queries with keyword search."""
        # Extract potential keywords (words longer than 3 chars)
        keywords = re.findall(r'\b[a-z]{4,}\b', query)
        
        if not keywords:
            return (
                "🤔 I'm not sure what you're asking. Try:\n"
                "• 'Show me the top stories'\n"
                "• 'Tell me about [topic]'\n"
                "• 'What's trending?'\n"
                "• Type 'help' for more options"
            )
        
        # Search using first keyword
        return self._handle_topic_search(keywords[0])
    
    def _extract_topic(self, query: str) -> Optional[str]:
        """Extract topic from query."""
        # Patterns like "about X", "on X", "regarding X"
        patterns = [
            r'about\s+([a-z\s]+)',
            r'on\s+([a-z\s]+)',
            r'regarding\s+([a-z\s]+)',
            r'find\s+([a-z\s]+)',
            r'search\s+([a-z\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                topic = match.group(1).strip()
                # Remove trailing words like "news", "articles"
                topic = re.sub(r'\s+(news|articles|stories)$', '', topic)
                return topic
        
        return None
    
    def get_conversation_history(self) -> List[Dict]:
        """Return conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
