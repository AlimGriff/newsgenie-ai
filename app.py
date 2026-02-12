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
from src.conversational_agent import ConversationalAgent
from config import CATEGORIES, DATA_DIR

import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

st.set_page_config(
    page_title="NewsGenie AI",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .stChatMessage {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def load_models():
    summarizer = ArticleSummarizer()
    categorizer = ArticleCategorizer()
    sentiment_analyzer = SentimentAnalyzer()
    trend_analyzer = TrendAnalyzer()
    return summarizer, categorizer, sentiment_analyzer, trend_analyzer


@st.cache_data(ttl=3600)
def fetch_and_process_news(category=None):
    fetcher = NewsFetcher()
    summarizer, categorizer, sentiment_analyzer, trend_analyzer = load_models()
    
    articles = fetcher.fetch_all(category)
    
    if not articles:
        return []
    
    articles = categorizer.categorize_batch(articles)
    articles = sentiment_analyzer.analyze_batch(articles)
    
    return articles


def display_article(article, show_summary=True):
    sentiment = article.get('sentiment', {})
    sentiment_label = sentiment.get('label', 'neutral')
    sentiment_class = f"sentiment-{sentiment_label}"
    
    st.markdown(f"""
    <div class="article-card">
        <h3>{article.get('title', 'No Title')}</h3>
        <p><strong>Source:</strong> {article.get('source', 'Unknown')} | 
           <strong>Category:</strong> {article.get('category', 'General')} | 
           <span class="{sentiment_class}">Sentiment: {sentiment_label.upper

