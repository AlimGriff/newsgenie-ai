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


@st.cache_resource
def load_models():
    """Load all AI models (cached)."""
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
    with st.spinner("Fetching latest news..."):
        articles = fetcher.fetch_all(category)
    
    if not articles:
        return []
    
    # Process articles
    with st.spinner("Analyzing articles..."):
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
        st.image("https://via.placeholder.com/200x100?text=NewsGenie", use_column_width=True)
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
    
    # Fetch and process news
    category_filter = None if selected_category == "All" else selected_category
    articles = fetch_and_process_news(category_filter)
    
    if not articles:
        st.warning("No articles found. Please try again later or check your API configuration.")
        return
    
    # Filter by selected category if "All" is not selected
    if selected_category != "All":
        articles = [a for a in articles if a.get('category') == selected_category]
    
    # Limit number of articles
    articles = articles[:num_articles]
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📰 News Feed", "📊 Analytics", "🔥 Trends", "🔍 Search"])
    
    with tab1:
        st.header("Latest News")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            sentiment_filter = st.multiselect(
                "Filter by Sentiment",
                ["positive", "negative", "neutral"],
                default=["positive", "negative", "neutral"]
            )
        
        # Display articles
        filtered_articles = [
            a for a in articles 
            if a.get('sentiment', {}).get('label', 'neutral') in sentiment_filter
        ]
        
        st.write(f"Showing {len(filtered_articles)} articles")
        
        for article in filtered_articles:
            display_article(article)
    
    with tab2:
        st.header("News Analytics")
        
        if articles:
            # Load analyzers
            _, categorizer, sentiment_analyzer, trend_analyzer = load_models()
            
            # Category distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Category Distribution")
                cat_dist = categorizer.get_category_distribution(articles)
                df_cat = pd.DataFrame(list(cat_dist.items()), columns=['Category', 'Count'])
                df_cat = df_cat[df_cat['Count'] > 0].sort_values('Count', ascending=False)
                
                fig_cat = px.bar(df_cat, x='Category', y='Count', 
                                color='Count', color_continuous_scale='Blues')
                st.plotly_chart(fig_cat, use_container_width=True)
            
            with col2:
                st.subheader("Sentiment Distribution")
                sent_dist = sentiment_analyzer.get_sentiment_distribution(articles)
                df_sent = pd.DataFrame(list(sent_dist.items()), columns=['Sentiment', 'Count'])
                
                colors = {'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#6c757d'}
                fig_sent = px.pie(df_sent, values='Count', names='Sentiment',
                                 color='Sentiment', color_discrete_map=colors)
                st.plotly_chart(fig_sent, use_container_width=True)
            
            # Source distribution
            st.subheader("Top News Sources")
            source_dist = trend_analyzer.get_source_distribution(articles)
            df_source = pd.DataFrame(list(source_dist.items()), columns=['Source', 'Count'])
            
            fig_source = px.bar(df_source, x='Source', y='Count', orientation='v')
            st.plotly_chart(fig_source, use_container_width=True)
            
            # Sentiment by category
            st.subheader("Sentiment by Category")
            sentiment_by_cat = []
            for article in articles:
                sentiment_by_cat.append({
                    'Category': article.get('category', 'General'),
                    'Sentiment': article.get('sentiment', {}).get('label', 'neutral'),
                    'Polarity': article.get('sentiment', {}).get('polarity', 0)
                })
            
            df_sent_cat = pd.DataFrame(sentiment_by_cat)
            fig_sent_cat = px.box(df_sent_cat, x='Category', y='Polarity', color='Category')
            st.plotly_chart(fig_sent_cat, use_container_width=True)
    
    with tab3:
        st.header("Trending Topics")
        
        if articles:
            _, _, _, trend_analyzer = load_models()
            
            # Trending keywords
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔥 Hot Keywords")
                trending = trend_analyzer.get_trending_topics(articles, top_n=15)
                
                if trending:
                    df_trend = pd.DataFrame(trending, columns=['Keyword', 'Frequency'])
                    fig_trend = px.bar(df_trend, x='Frequency', y='Keyword', 
                                      orientation='h', color='Frequency',
                                      color_continuous_scale='Reds')
                    st.plotly_chart(fig_trend, use_container_width=True)
            
            with col2:
                st.subheader("📈 Category Trends")
                cat_trends = trend_analyzer.analyze_category_trends(articles)
                
                for category, data in cat_trends.items():
                    if data['count'] > 0:
                        with st.expander(f"{category} ({data['count']} articles)"):
                            keywords = data.get('keywords', [])
                            if keywords:
                                st.write("Top keywords:")
                                for kw, freq in keywords[:5]:
                                    st.write(f"- **{kw}** ({freq})")
    
    with tab4:
        st.header("Search Articles")
        
        search_query = st.text_input("🔍 Search for articles", placeholder="Enter keywords...")
        
        if search_query:
            # Simple keyword search
            search_results = []
            query_lower = search_query.lower()
            
            for article in articles:
                title = article.get('title', '').lower()
                summary = article.get('summary', '').lower()
                
                if query_lower in title or query_lower in summary:
                    search_results.append(article)
            
            st.write(f"Found {len(search_results)} results for '{search_query}'")
            
            for article in search_results:
                display_article(article)
        else:
            st.info("Enter a search term to find relevant articles")


if __name__ == "__main__":
    main()
