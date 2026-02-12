# NewsGenie AI - Workflow & Error Handling Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [News Fetching Workflow](#news-fetching-workflow)
3. [Query Processing Pipeline](#query-processing-pipeline)
4. [LLM Integration & Fallback Mechanisms](#llm-integration--fallback-mechanisms)
5. [Error Handling Strategy](#error-handling-strategy)
6. [API Integration Details](#api-integration-details)
7. [Caching Strategy](#caching-strategy)
8. [Performance Optimization](#performance-optimization)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface (Streamlit)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Chat   │  │   News   │  │Analytics │  │  Trends  │   │
│  │   Tab    │  │   Feed   │  │   Tab    │  │   Tab    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer (app.py)                │
│  • Session Management                                        │
│  • Cache Management                                          │
│  • Component Orchestration                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Processing Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Conversational│  │  Categorizer │  │  Sentiment   │     │
│  │    Agent      │  │              │  │  Analyzer    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ LLM Handler  │  │ Summarizer   │  │   Trend      │     │
│  │ (Optional)   │  │              │  │  Analyzer    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     Data Acquisition Layer                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  News API    │  │  RSS Feeds   │  │  Deduplicator│     │
│  │  (Optional)  │  │  (Primary)   │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## News Fetching Workflow

### 1. **Initial Fetch Process**

```python
# Location: src/news_fetcher.py -> fetch_all()

STEP 1: Initialize NewsFetcher
├── Load RSS feed URLs from config (40+ sources)
├── Initialize seen_urls set for deduplication
└── Set timeout parameters

STEP 2: Fetch from News API (Optional)
├── IF API key available:
│   ├── Construct request with parameters (country='gb', language='en')
│   ├── Send HTTP GET request with 10s timeout
│   ├── Parse JSON response
│   ├── Extract articles (title, summary, url, source, published, image)
│   ├── Add to seen_urls for deduplication
│   └── RETURN articles list
├── ELSE:
│   ├── Log warning: "News API key not configured"
│   └── Continue to RSS feeds
└── ON ERROR:
    ├── Log error with details
    ├── Continue without News API data
    └── No user-facing error (graceful degradation)

STEP 3: Fetch from RSS Feeds (Primary Source)
├── FOR EACH feed_url in rss_feeds:
│   ├── Parse RSS feed using feedparser
│   ├── IF feed.bozo AND no entries:
│   │   ├── Log warning
│   │   └── CONTINUE to next feed
│   ├── FOR EACH entry in feed.entries[:20]:
│   │   ├── Check if URL already seen
│   │   ├── Parse published date (ISO format)
│   │   ├── Extract and clean summary (remove HTML tags)
│   │   ├── Create article dictionary
│   │   ├── Add to articles list
│   │   └── Add URL to seen_urls
│   └── ON ERROR:
│       ├── Log warning with feed URL
│       └── CONTINUE to next feed
└── Log total articles fetched per feed

STEP 4: Deduplication
├── Initialize seen_urls and seen_titles sets
├── FOR EACH article:
│   ├── Check URL against seen_urls
│   ├── Create title_key (first 10 words)
│   ├── Check title_key against seen_titles
│   ├── IF duplicate: SKIP
│   └── ELSE: Add to unique_articles
├── Log number of duplicates removed
└── RETURN unique_articles

STEP 5: Sorting and Limiting
├── Sort by published date (newest first)
├── Limit to top 100 articles
└── RETURN processed articles
```

### 2. **Article Processing Pipeline**

```python
# Location: app.py -> fetch_and_process_news()

STEP 1: Fetch Raw Articles
├── Call NewsFetcher.fetch_all(category)
└── IF empty: RETURN []

STEP 2: Categorization
├── Load ArticleCategorizer
├── FOR EACH article:
│   ├── Extract title and summary
│   ├── Check source URL for category hints
│   ├── Score against category keywords
│   ├── Apply exclusion rules (e.g., protest → Politics not Technology)
│   ├── Assign best matching category or "General"
│   └── Add category to article dictionary
└── RETURN categorized articles

STEP 3: Sentiment Analysis
├── Load SentimentAnalyzer
├── FOR EACH article:
│   ├── Combine title and summary
│   ├── Calculate polarity score (-1 to +1)
│   ├── Calculate subjectivity score (0 to 1)
│   ├── Classify as positive/negative/neutral
│   └── Add sentiment data to article
└── RETURN analyzed articles

STEP 4: Caching
├── Cache result with 5-minute TTL (300 seconds)
├── Store in Streamlit cache_data
└── RETURN processed articles
```

---

## Query Processing Pipeline

### 3. **Conversational Agent Query Flow**

```python
# Location: src/conversational_agent.py -> process_query()

USER INPUT: "What's the latest UK news today?"
│
├── STEP 1: Preprocessing
│   ├── Convert to lowercase
│   ├── Strip whitespace
│   └── Store in conversation history
│
├── STEP 2: Intent Detection (Rule-Based - Fast Path)
│   ├── CHECK: Greeting? ['hello', 'hi', 'hey']
│   │   └── IF YES: RETURN greeting message → END
│   │
│   ├── CHECK: Help request? ['help', 'what can you do']
│   │   └── IF YES: RETURN help message → END
│   │
│   ├── CHECK: UK news? ['uk news', 'british news', 'latest uk', 'uk today']
│   │   └── IF YES: CALL get_uk_news() → END
│   │
│   ├── CHECK: Top stories? ['top stories', 'headlines', 'latest news']
│   │   └── IF YES: CALL get_top_stories() → END
│   │
│   ├── CHECK: Trending? ['trending', 'popular', 'hot']
│   │   └── IF YES: CALL get_trending() → END
│   │
│   ├── CHECK: Sentiment? ['sentiment', 'feeling', 'mood']
│   │   └── IF YES: CALL get_sentiment() → END
│   │
│   ├── CHECK: Count/statistics? ['how many', 'count', 'number']
│   │   └── IF YES: CALL get_count() → END
│   │
│   └── CHECK: Category query? [technology, sports, business, etc.]
│       └── IF YES: CALL get_category_news(category) → END
│
├── STEP 3: Keyword Extraction (Fallback)
│   ├── Extract words 4+ characters long
│   ├── Filter out stopwords ['the', 'news', 'show', 'tell', etc.]
│   ├── IF keywords found:
│   │   └── CALL search_articles(keyword) → END
│   └── ELSE: CONTINUE
│
├── STEP 4: LLM Processing (Optional - Complex Queries)
│   ├── IF llm_handler available AND use_llm enabled:
│   │   ├── Build context from top 10 articles
│   │   ├── Construct prompt with context and query
│   │   ├── Call llm_handler.generate_response()
│   │   ├── IF response valid: RETURN response → END
│   │   └── ELSE: CONTINUE to fallback
│   └── ELSE: SKIP
│
└── STEP 5: Final Fallback
    ├── RETURN generic help message
    └── Suggest example queries
```

### 4. **Specific Query Handlers**

#### **UK News Handler**

```python
# Location: src/conversational_agent.py -> get_uk_news()

INPUT: User asks for UK news
│
├── STEP 1: Filter by Source
│   ├── UK sources: ['BBC', 'Sky News', 'The Guardian', 'Independent', 'Telegraph']
│   ├── Filter articles where source contains any UK source name
│   └── IF no UK articles:
│       ├── RETURN message: "No UK news available"
│       └── Suggest: "Try clicking 'Refresh News'"
│
├── STEP 2: Format Response
│   ├── Create header with article count
│   ├── FOR EACH article (limit 5):
│   │   ├── Extract title, source, category
│   │   ├── Format as numbered list with markdown
│   │   └── Add to response string
│   └── IF more than 5 articles:
│       └── Add footer: "...and X more UK articles available"
│
└── RETURN formatted response
```

#### **Trending Topics Handler**

```python
# Location: src/conversational_agent.py -> get_trending()

INPUT: User asks for trending topics
│
├── STEP 1: Extract Keywords
│   ├── Initialize stopwords list
│   ├── FOR EACH article:
│   │   ├── Extract title
│   │   ├── Find all words 4+ characters
│   │   ├── Filter out stopwords
│   │   └── Add to words list
│   └── IF no words found:
│       └── RETURN "No articles available"
│
├── STEP 2: Count Frequencies
│   ├── Use Counter to count word occurrences
│   ├── Get top 10 most common words
│   └── Sort by frequency
│
├── STEP 3: Format Response
│   ├── Create header "Trending Topics"
│   ├── FOR EACH (word, count):
│   │   ├── Capitalize word
│   │   ├── Create visual bar (= symbols, max 20)
│   │   ├── Format: "1. **Word** ===== (5)"
│   │   └── Add to response
│   └── RETURN formatted response
│
└── RETURN response to user
```

---

## LLM Integration & Fallback Mechanisms

### 5. **LLM Handler Workflow**

```python
# Location: src/llm_handler.py

INITIALIZATION (Once per app session - cached)
│
├── STEP 1: Model Selection
│   ├── Primary: "google/flan-t5-small" (300MB)
│   ├── Fallback: "distilgpt2" (80MB)
│   └── Set device=-1 (CPU mode for Streamlit Cloud)
│
├── STEP 2: Model Loading
│   ├── TRY:
│   │   ├── Show loading message to user
│   │   ├── Initialize transformers pipeline
│   │   ├── Load model weights (2-3 minutes first time)
│   │   ├── Set max_length=256, temperature=0.7
│   │   ├── Show success message
│   │   └── RETURN llm_handler instance
│   └── ON ERROR:
│       ├── Log error details
│       ├── Show warning to user: "LLM not available"
│       ├── Set llm_handler = None
│       └── App continues with rule-based responses
│
└── Cache in Streamlit session (only loads once)

QUERY PROCESSING
│
├── INPUT: Complex user query
│
├── STEP 1: Build Context
│   ├── Extract top 10 articles
│   ├── Format: "[Category] Title - Summary (Source)"
│   ├── Concatenate with newlines
│   └── Limit total context to ~1000 characters
│
├── STEP 2: Construct Prompt
│   ├── System message: "You are a helpful news assistant"
│   ├── Add context: "Available articles context: ..."
│   ├── Add user query: "User question: ..."
│   └── Add instruction: "Provide a helpful and concise answer:"
│
├── STEP 3: Generate Response
│   ├── TRY:
│   │   ├── Call llm.generate()
│   │   ├── Set max_length=256-400
│   │   ├── Set do_sample=False for deterministic output
│   │   ├── Extract generated_text from response
│   │   └── IF response empty or None:
│   │       └── TRIGGER fallback
│   └── ON ERROR:
│       ├── Log error
│       └── TRIGGER fallback
│
└── STEP 4: Fallback Mechanism
    ├── Use rule-based response
    ├── Extract keywords from query
    ├── Match to handler (UK news, top stories, search)
    └── RETURN rule-based result
```

### 6. **Hybrid Response Strategy**

```
┌─────────────────────────────────────────────────────────┐
│                    Query Analysis                        │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                     ↓
┌───────────────┐                   ┌───────────────┐
│  Simple Query │                   │ Complex Query │
│  (Pattern     │                   │ (Natural      │
│   Match)      │                   │  Language)    │
└───────────────┘                   └───────────────┘
        ↓                                     ↓
┌───────────────┐                   ┌───────────────┐
│  Rule-Based   │                   │  LLM Attempt  │
│   Response    │                   │               │
│  ⚡ Instant   │                   └───────────────┘
└───────────────┘                            ↓
        ↓                           ┌────────┴────────┐
        │                           ↓                 ↓
        │                   ┌─────────────┐   ┌─────────────┐
        │                   │  LLM Success│   │  LLM Failed │
        │                   │  🤖 2-5s    │   │             │
        │                   └─────────────┘   └─────────────┘
        │                           ↓                 ↓
        │                           │         ┌─────────────┐
        │                           │         │  Rule-Based │
        │                           │         │  Fallback   │
        │                           │         │  ⚡ Instant │
        │                           │         └─────────────┘
        │                           │                 ↓
        └───────────────────────────┴─────────────────┘
                                    ↓
                          ┌───────────────────┐
                          │  User Response    │
                          └───────────────────┘
```

**Performance Characteristics:**

| Query Type | Method | Response Time | Accuracy |
|------------|--------|---------------|----------|
| "Show UK news" | Rule-based | <100ms | 100% |
| "What's trending?" | Rule-based | <500ms | 95% |
| "Top stories" | Rule-based | <100ms | 100% |
| "Compare UK vs US sentiment" | LLM → Fallback | 2-5s → <500ms | 85% → 80% |
| "Summarize main themes" | LLM → Fallback | 2-5s → <1s | 85% → 70% |

---

## Error Handling Strategy

### 7. **Error Classification and Handling**

#### **Level 1: Critical Errors (App Cannot Function)**

```python
ERROR: Unable to import core modules
├── CAUSE: Missing dependencies, syntax errors
├── DETECTION: Import statement failure
├── HANDLING:
│   ├── Streamlit displays error page
│   ├── Error logged to Streamlit Cloud logs
│   └── User sees: "App encountered an error"
└── RESOLUTION: Fix code and redeploy

ERROR: No articles fetched from any source
├── CAUSE: All API/RSS feeds failed, network issues
├── DETECTION: fetch_and_process_news() returns []
├── HANDLING:
│   ├── Show warning message to user
│   ├── Display: "No articles found. Please try again later"
│   ├── Suggest: Check API configuration
│   └── Log details to console
└── RESOLUTION: User clicks "Refresh News" or waits
```

#### **Level 2: Feature Degradation (App Functions with Limitations)**

```python
ERROR: News API unavailable
├── CAUSE: No API key, rate limit exceeded, API down
├── DETECTION: requests.exceptions.RequestException
├── HANDLING:
│   ├── Log warning with details
│   ├── Continue to RSS feeds (primary source)
│   ├── NO user-facing error message
│   └── Graceful degradation
└── IMPACT: Fewer articles, but app fully functional

ERROR: LLM initialization failed
├── CAUSE: Memory constraints, model download failed
├── DETECTION: Exception in LLMHandler.__init__()
├── HANDLING:
│   ├── Set llm_handler = None
│   ├── Display warning: "LLM not available. Using rule-based responses."
│   ├── Continue with rule-based conversational agent
│   └── Log error details
└── IMPACT: Complex queries use fallback, simple queries unaffected

ERROR: RSS feed parse failure
├── CAUSE: Invalid feed, timeout, feed temporarily down
├── DETECTION: feedparser.bozo = True
├── HANDLING:
│   ├── Log warning with feed URL
│   ├── Skip to next feed
│   ├── NO user-facing error
│   └── Continue with other feeds
└── IMPACT: Slightly fewer articles from that source
```

#### **Level 3: Minor Errors (Single Operation Fails)**

```python
ERROR: Article categorization failure
├── CAUSE: Missing title/summary, encoding issues
├── DETECTION: Exception in categorize()
├── HANDLING:
│   ├── Catch exception
│   ├── Assign category = "General"
│   ├── Log warning
│   └── Continue processing other articles
└── IMPACT: One article miscategorized, rest normal

ERROR: Sentiment analysis failure
├── CAUSE: Invalid text, encoding issues
├── DETECTION: Exception in analyze()
├── HANDLING:
│   ├── Catch exception
│   ├── Assign default sentiment: {'label': 'neutral', 'polarity': 0}
│   ├── Log warning
│   └── Continue processing
└── IMPACT: One article has neutral sentiment, rest normal

ERROR: Cache expiration during session
├── CAUSE: TTL expired (5 minutes)
├── DETECTION: Cache miss on fetch_and_process_news()
├── HANDLING:
│   ├── Automatically refetch and reprocess
│   ├── Show spinner: "Loading news..."
│   └── Update cache with fresh data
└── IMPACT: 10-30 second delay, then fresh data
```

### 8. **Error Handling Code Patterns**

**Pattern 1: Try-Catch with Fallback**

```python
def fetch_from_news_api(self, category=None):
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        # Process response
        return articles
    except requests.exceptions.Timeout:
        logger.error("News API timeout")
        return []  # Graceful degradation
    except requests.exceptions.RequestException as e:
        logger.error(f"News API request failed: {e}")
        return []  # Continue with RSS feeds
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return []
```

**Pattern 2: Validation with Default Values**

```python
def categorize(self, article):
    # Validate input
    if not article:
        return 'General'
    
    title = article.get('title', '')
    summary = article.get('summary', '')
    
    # Validate data exists
    if not title and not summary:
        logger.warning("Article has no title or summary")
        return 'General'
    
    # Process normally
    # ...
```

**Pattern 3: Progressive Enhancement**

```python
def __init__(self, articles, llm_handler=None):
    self.articles = articles
    self.llm_handler = llm_handler
    self.use_llm = llm_handler is not None  # Feature flag
    
def generate_response(self, query):
    # Try enhanced features first
    if self.use_llm and self.llm_handler:
        llm_response = self.handle_llm_query(query)
        if llm_response:  # LLM succeeded
            return llm_response
    
    # Fall back to core features
    return self.rule_based_response(query)
```

---

## API Integration Details

### 9. **News API Integration**

**Configuration:**
```python
# Location: config.py
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')

# Location: .streamlit/secrets.toml (Streamlit Cloud)
NEWS_API_KEY = "your_api_key_here"
```

**Request Specification:**
```python
Endpoint: https://newsapi.org/v2/top-headlines

Parameters:
├── apiKey: Required authentication
├── country: 'gb' (United Kingdom focus)
├── language: 'en' (English articles)
├── pageSize: 50 (max articles per request)
└── category: Optional (business, technology, sports, etc.)

Headers:
└── User-Agent: NewsGenie AI/1.0

Timeout: 10 seconds

Rate Limits:
├── Free tier: 100 requests/day
├── Developer tier: 1000 requests/day
└── Business tier: 100,000 requests/day
```

**Response Handling:**
```python
SUCCESS (200 OK):
{
  "status": "ok",
  "totalResults": 38,
  "articles": [
    {
      "source": {"name": "BBC News"},
      "title": "Article title",
      "description": "Article summary",
      "url": "https://...",
      "urlToImage": "https://...",
      "publishedAt": "2025-02-12T10:30:00Z",
      "author": "John Smith"
    }
  ]
}

ERROR (Various):
├── 401: Invalid API key
├── 429: Rate limit exceeded
├── 500: Server error
└── Network timeout
```

**Fallback Strategy:**
```
News API Request
       ↓
  ┌────┴────┐
  ↓         ↓
SUCCESS   FAILURE
  ↓         ↓
Use data  Log error
  ↓         ↓
  └────┬────┘
       ↓
Continue to RSS feeds
```

### 10. **RSS Feed Integration**

**Feed Sources (40+ feeds):**
```python
UK Sources (Primary):
├── BBC News (6 feeds): news, uk, world, business, technology, sport
├── Sky News (4 feeds): home, uk, world, business
├── The Guardian (5 feeds): uk, world, business, technology, sport
├── Independent (4 feeds): uk, world, business, sport
└── Telegraph (1 feed): main feed

International Sources:
├── Reuters (4 feeds): best topics, business, technology, world
├── CNN (3 feeds): world, technology, sport
├── Al Jazeera (1 feed): all news
└── Bloomberg (1 feed): markets

Specialized Sources:
├── TechCrunch (1 feed): technology
├── The Verge (1 feed): technology
└── ESPN (1 feed): sports
```

**Feed Processing:**
```python
FOR EACH feed_url:
│
├── STEP 1: Parse Feed
│   ├── Use feedparser.parse(feed_url)
│   ├── Check feed.bozo (error indicator)
│   └── IF error: Skip to next feed
│
├── STEP 2: Extract Entries
│   ├── Limit to first 20 entries per feed
│   ├── Extract: link, title, summary, published, author
│   └── Parse published date to ISO format
│
├── STEP 3: Clean Data
│   ├── Remove HTML tags from summary
│   ├── Truncate summary to 500 characters
│   ├── Validate URL format
│   └── Skip if URL already seen
│
├── STEP 4: Add to Collection
│   ├── Create article dictionary
│   ├── Add to articles list
│   └── Mark URL as seen
│
└── ON ERROR:
    ├── Log warning with feed URL
    ├── Continue to next feed
    └── No user-facing error
```

**Error Tolerance:**
- **Single feed failure:** App continues normally
- **Multiple feed failures:** Reduced article count
- **All feeds fail:** Show warning to user

---

## Caching Strategy

### 11. **Multi-Layer Caching**

```
┌──────────────────────────────────────────────────────┐
│              Layer 1: Model Cache                     │
│  @st.cache_resource                                   │
│  • LLM model (300MB) - Persistent across sessions    │
│  • Categorizer, Sentiment Analyzer - Loaded once     │
│  • TTL: Infinite (until app restart)                 │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│              Layer 2: Data Cache                      │
│  @st.cache_data(ttl=300)                             │
│  • Fetched articles - 5 minute TTL                   │
│  • Processed articles (categorized + sentiment)      │
│  • Shared across all users                           │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│              Layer 3: Session State                   │
│  st.session_state                                     │
│  • Conversational agent instance - Per user          │
│  • Chat history - Per user                           │
│  • User preferences - Per user                        │
└──────────────────────────────────────────────────────┘
```

**Cache Invalidation:**
```python
Manual Invalidation:
├── User clicks "Refresh News" button
│   ├── Calls: st.cache_data.clear()
│   ├── Clears: fetch_and_process_news() cache
│   ├── Deletes: session_state.chat_agent
│   └── Deletes: session_state.messages
└── Forces: Fresh fetch from all sources

Automatic Invalidation:
├── TTL expiration (5 minutes)
│   ├── Triggers: Background refetch
│   ├── User sees: Brief spinner
│   └── Updates: Cache with fresh data
└── App restart
    ├── Clears: All caches
    └── Reloads: Models and data
```

---

## Performance Optimization

### 12. **Optimization Strategies**

**Strategy 1: Lazy Loading**
```python
# Load heavy models only once
@st.cache_resource
def load_models():
    # Models loaded first time, cached thereafter
    return summarizer, categorizer, sentiment_analyzer, trend_analyzer, llm_handler

# Articles cached for 5 minutes
@st.cache_data(ttl=300)
def fetch_and_process_news(category=None):
    # Network calls and processing cached
    return articles
```

**Strategy 2: Parallel Processing Potential**
```python
# Current: Sequential RSS feed fetching
# Future enhancement: Parallel fetching with ThreadPoolExecutor

from concurrent.futures import ThreadPoolExecutor

def fetch_all_parallel(self):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(self.fetch_from_rss, url) for url in self.rss_feeds]
        results = [f.result() for f in futures]
    # Could reduce fetch time from 20s to 5s
```

**Strategy 3: Response Streaming (LLM)**
```python
# Future enhancement: Stream LLM responses
# Current: Wait for complete response
# Enhanced: Show response as it's generated

def stream_response(self, prompt):
    for chunk in self.llm.stream(prompt):
        yield chunk
    # Improves perceived performance
```

**Strategy 4: Progressive Data Loading**
```python
# Load essential data first, enhance later
STEP 1: Fetch articles (fast)
STEP 2: Show articles immediately
STEP 3: Process categorization in background
STEP 4: Update UI when ready
# User sees content faster
```

**Performance Metrics:**

| Operation | Current Time | Optimized Target |
|-----------|-------------|------------------|
| First app load | 30-60s | 20-30s |
| Model loading | 120-180s | 60-90s (smaller model) |
| News fetch | 15-25s | 5-10s (parallel) |
| Categorization | 2-3s | 1-2s (vectorized) |
| Rule-based query | <100ms | <50ms |
| LLM query | 2-5s | 1-3s (streaming) |
| Cache hit | <50ms | <50ms |

---

## Summary

### Key Design Principles

1. **Graceful Degradation**: App functions with reduced features when components fail
2. **Progressive Enhancement**: Core features always work, advanced features optional
3. **Fail-Safe Defaults**: Every error has a sensible default behavior
4. **User Transparency**: Users informed of limitations but not overwhelmed with errors
5. **Comprehensive Logging**: Errors logged for debugging without user disruption
6. **Performance First**: Fast paths for common queries, LLM only for complex cases
7. **Multi-Source Resilience**: 40+ RSS feeds ensure news availability
8. **Smart Caching**: Balance between freshness and performance

### Error Recovery Hierarchy

```
ERROR DETECTED
      ↓
┌─────┴─────┐
↓           ↓
Component   Data
Level       Level
↓           ↓
Use         Use
Fallback    Cached
Component   Data
↓           ↓
└─────┬─────┘
      ↓
Inform User
(if needed)
      ↓
Log Details
      ↓
Continue
Operation
```

---

## Appendix: Configuration Files

### A. Environment Variables
```bash
# .env (local development)
NEWS_API_KEY=your_api_key_here

# .streamlit/secrets.toml (Streamlit Cloud)
NEWS_API_KEY = "your_api_key_here"
```

### B. Dependencies
```txt
# requirements.txt
streamlit>=1.28.0
feedparser>=6.0.10
textblob>=0.17.1
requests>=2.31.0
pandas>=2.0.0
plotly>=5.14.0
python-dateutil>=2.8.2
nltk>=3.8.1
transformers>=4.30.0  # Optional: LLM support
torch>=2.0.0          # Optional: LLM support
sentencepiece>=0.1.99 # Optional: LLM support
accelerate>=0.20.0    # Optional: LLM support
```

### C. Monitoring & Logging
```python
# Enable detailed logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Monitor in Streamlit Cloud:
# 1. Go to app dashboard
# 2. Click "Manage app"
# 3. Click "Logs"
# 4. View real-time logs
```

---

**Document Version:** 2.0  
**Last Updated:** 2025-02-12  
**Status:** Production Ready  
**Maintained by:** NewsGenie AI Development Team
