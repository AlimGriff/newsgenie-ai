import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from pathlib import Path

from src.news_fetcher import NewsFetcher
from src.summarizer import ArticleSummarizer
from src.categorizer import ArticleCategorizer
from src.sentiment_analyzer import SentimentAnalyzer
from src.trend_analyzer import TrendAnalyzer
from config import CATEGORIES, DATA_DIR

# Download NLTK data on first run
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# Page configuration
st.set_page_config(
    page_title="NewsGenie AI",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1E88E5;
        margin-bottom: 2rem;
    }
    .article-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
        border-left: 4px solid #1E88E5;
    }
    .sentiment-positive {
        color: #28a745;
        font-weight: bold;
    }
    .sentiment-negative {
        color: #dc3545;
        font-weight: bold;
    }
    .sentiment-neutral {
        color: #6c757d;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def load_models():
    """Load all AI models."""
    summarizer = ArticleSummarizer()
    categorizer = ArticleCategorizer()
    sentiment_analyzer = SentimentAnalyzer()
    trend_analyzer = TrendAnalyzer()
    return summarizer, categorizer, sentiment_analyzer, trend_analyzer


@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_and_process_news(category=None):
    """Fetch and process news articles."""
    fetcher = NewsFetcher()
    summarizer, categorizer, sentiment_analyzer, trend_analyzer = load_models()
    
    # Fetch articles
    articles = fetcher.fetch_all(category)
    
    if not articles:
        return []
    
    # Process articles
    articles = categorizer.categorize_batch(articles)
    articles = sentiment_analyzer.analyze_batch(articles)
    
    return articles


def display_article(article, show_summary=True):
    """Display a single article card."""
    sentiment = article.get('sentiment', {})
    sentiment_label = sentiment.get('label', 'neutral')
    sentiment_class = f"sentiment-{sentiment_label}"
    
    st.markdown(f"""
    <div class="article-card">
        <h3>{article.get('title', 'No Title')}</h3>
        <p><strong>Source:</strong> {article.get('source', 'Unknown')} | 
           <strong>Category:</strong> {article.get('category', 'General')} | 
           <span class="{sentiment_class}">Sentiment: {sentiment_label.upper()}</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if show_summary:
        summary = article.get('ai_summary', article.get('summary', ''))
        if summary:
            st.write(summary)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if article.get('url'):
            st.link_button("Read Full Article", article['url'])


def main():
    # Header
    st.markdown('<h1 class="main-header">📰 NewsGenie AI</h1>', unsafe_allow_html=True)
    st.markdown("### Your Intelligent News Aggregator & Analyzer")
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📰 NewsGenie AI")
        st.markdown("---")
        
        st.header("⚙️ Settings")
        
        # Category filter
        selected_category = st.selectbox(
            "Select Category",
            ["All"] + CATEGORIES
        )
        
        # Number of articles
        num_articles = st.slider("Number of articles to display", 5, 50, 20)
        
        # Refresh button
        if st.button("🔄 Refresh News", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### About")
        st.info(
            "NewsGenie AI aggregates news from multiple sources, "
            "analyzes sentiment, categorizes content, and identifies trends "
            "using advanced AI models."
        )
    
    # Main content
    with st.spinner("Loading news..."):
        # Fetch and process news
        category_filter = None if selected_category == "All" else selected_category
        articles = fetch_and_process_news(category_filter)
    
    if not articles:
        st.warning("No articles found. Please try again later or check your API configuration.")
        st.info("💡 **Tip:** Get a free News API key from https://newsapi.org to access more news sources!")

