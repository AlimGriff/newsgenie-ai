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


@st.cache_data(ttl=3600)
def fetch_and_process_news(category=None):
    """Fetch and process news articles."""
    fetcher = NewsFetcher()
    summarizer, categorizer, sentiment_analyzer, trend_analyzer = load_models()
    
    articles = fetcher.fetch_all(category)
    
    if not articles:
        return []
    
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
    st.markdown('<h1 class="main-header">📰 NewsGenie AI</h1>', unsafe_allow_html=True)
    st.markdown("### Your Intelligent News Aggregator & Analyzer")
    
    with st.sidebar:
        st.markdown("## 📰 NewsGenie AI")
        st.markdown("---")
        
        st.header("⚙️ Settings")
        
        selected_category = st.selectbox(
            "Select Category",
            ["All"] + CATEGORIES
        )
        
        num_articles = st.slider("Number of articles to display", 5, 50, 20)
        
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
    
    with st.spinner("Loading news..."):
        category_filter = None if selected_category == "All" else selected_category
        articles = fetch_and_process_news(category_filter)
    
    if not articles:
        st.warning("No articles found. Please try again later or check your API configuration.")
        st.info("💡 **Tip:** Get a free News API key from https://newsapi.org to access more news sources!")
        return
    
    if selected_category != "All":
        articles = [a for a in articles if a.get('category') == selected_category]
    
    articles = articles[:num_articles]
    
    tab1, tab2, tab3, tab4 = st.tabs(["📰 News Feed", "📊 Analytics", "🔥 Trends", "🔍 Search"])
    
    with tab1:
        st.header("Latest News")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            sentiment_filter = st.multiselect(
                "Filter by Sentiment",
                ["positive", "negative", "neutral"],
                default=["positive", "negative", "neutral"]
            )
        
        filtered_articles = [
            a for a in articles 
            if a.get('sentiment', {}).get('label', 'neutral') in sentiment_filter
        ]
        
        st.write(f"Showing {len(filtered_articles)} articles")
        
        if filtered_articles:
            for article in filtered_articles:
                display_article(article)
        else:
            st.info("No articles match your filters. Try adjusting the sentiment filter.")
    
    with tab2:
        st.header("News Analytics")
        
        if articles:
            _, categorizer, sentiment_analyzer, trend_analyzer = load_models()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Category Distribution")
                cat_dist = categorizer.get_category_distribution(articles)
                df_cat = pd.DataFrame(list(cat_dist.items()), columns=['Category', 'Count'])
                df_cat = df_cat[df_cat['Count'] > 0].sort_values('Count', ascending=False)
                
                if not df_cat.empty:
                    fig_cat = px.bar(df_cat, x='Category', y='Count', 
                                    color='Count', color_continuous_scale='Blues')
                    fig_cat.update_layout(showlegend=False)
                    st.plotly_chart(fig_cat, use_container_width=True)
                else:
                    st.info("No category data available")
            
            with col2:
                st.subheader("Sentiment Distribution")
                sent_dist = sentiment_analyzer.get_sentiment_distribution(articles)
                df_sent = pd.DataFrame(list(sent_dist.items()), columns=['Sentiment', 'Count'])
                
                if not df_sent.empty:
                    colors = {'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#6c757d'}
                    fig_sent = px.pie(df_sent, values='Count', names='Sentiment',
                                     color='Sentiment', color_discrete_map=colors)
                    st.plotly_chart(fig_sent, use_container_width=True)
                else:
                    st.info("No sentiment data available")
            
            st.subheader("Top News Sources")
            source_dist = trend_analyzer.get_source_distribution(articles)
            if source_dist:
                df_source = pd.DataFrame(list(source_dist.items()), columns=['Source', 'Count'])
                
                fig_source = px.bar(df_source, x='Source', y='Count', orientation='v')
                fig_source.update_layout(showlegend=False)
                st.plotly_chart(fig_source, use_container_width=True)
            else:
                st.info("No source data available")
            
            st.subheader("Sentiment by Category")
            sentiment_by_cat = []
            for article in articles:
                sentiment_by_cat.append({
                    'Category': article.get('category', 'General'),
                    'Sentiment': article.get('sentiment', {}).get('label', 'neutral'),
                    'Polarity': article.get('sentiment', {}).get('polarity', 0)
                })
            
            df_sent_cat = pd.DataFrame(sentiment_by_cat)
            if not df_sent_cat.empty and len(df_sent_cat) > 0:
                fig_sent_cat = px.box(df_sent_cat, x='Category', y='Polarity', color='Category')
                fig_sent_cat.update_layout(showlegend=False)
                st.plotly_chart(fig_sent_cat, use_container_width=True)
            else:
                st.info("Not enough data for sentiment analysis by category")
        else:
            st.info("No articles to analyze")
    
    with tab3:
        st.header("Trending Topics")
        
        if articles:
            _, _, _, trend_analyzer = load_models()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔥 Hot Keywords")
                trending = trend_analyzer.get_trending_topics(articles, top_n=15)
                
                if trending:
                    df_trend = pd.DataFrame(trending, columns=['Keyword', 'Frequency'])
                    fig_trend = px.bar(df_trend, x='Frequency', y='Keyword', 
                                      orientation='h', color='Frequency',
                                      color_continuous_scale='Reds')
                    fig_trend.update_layout(showlegend=False)
                    st.plotly_chart(fig_trend, use_container_width=True)
                else:
                    st.info("No trending keywords found")
            
            with col2:
                st.subheader("📈 Category Trends")
                cat_trends = trend_analyzer.analyze_category_trends(articles)
                
                if cat_trends:
                    for category, data in cat_trends.items():
                        if data['count'] > 0:
                            with st.expander(f"{category} ({data['count']} articles)"):
                                keywords = data.get('keywords', [])
                                if keywords:
                                    st.write("Top keywords:")
                                    for kw, freq in keywords[:5]:
                                        st.write(f"- **{kw}** ({freq})")
                                else:
                                    st.write("No keywords available")
                else:
                    st.info("No category trends available")
        else:
            st.info("No articles to analyze for trends")
    
    with tab4:
        st.header("Search Articles")
        
        search_query = st.text_input("🔍 Search for articles", placeholder="Enter keywords...")
        
        if search_query:
            search_results = []
            query_lower = search_query.lower()
            
            for article in articles:
                title = article.get('title', '').lower()
                summary = article.get('summary', '').lower()
                
                if query_lower in title or query_lower in summary:
                    search_results.append(article)
            
            st.write(f"Found {len(search_results)} results for '{search_query}'")
            
            if search_results:
                for article in search_results:
                    display_article(article)
            else:
                st.info("No articles found matching your search. Try different keywords.")
        else:
            st.info("Enter a search term to find relevant articles")


if __name__ == "__main__":
    main()
