    def fetch_all(self, category: str = None) -> List[Dict]:
        """
        Fetch news from all available sources with better distribution.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of article dictionaries
        """
        all_articles = []
        
        # Fetch from News API first (if available)
        try:
            api_articles = self.fetch_from_news_api(category)
            if api_articles:
                all_articles.extend(api_articles)
                logger.info(f"Fetched {len(api_articles)} articles from News API")
        except Exception as e:
            logger.warning(f"News API unavailable: {e}")
        
        # Fetch from RSS feeds (always do this for variety)
        logger.info(f"Fetching from {len(self.rss_feeds)} RSS feeds...")
        
        for i, feed_url in enumerate(self.rss_feeds):
            try:
                rss_articles = self.fetch_from_rss(feed_url)
                if rss_articles:
                    all_articles.extend(rss_articles)
                    logger.info(f"Fetched {len(rss_articles)} articles from feed {i+1}/{len(self.rss_feeds)}")
            except Exception as e:
                logger.warning(f"Failed to fetch from {feed_url}: {e}")
                continue
        
        if not all_articles:
            logger.warning("No articles fetched from any source")
            return []
        
        # Deduplicate articles
        all_articles = self._deduplicate(all_articles)
        
        # Sort by published date (newest first)
        all_articles.sort(
            key=lambda x: x.get('published', ''), 
            reverse=True
        )
        
        logger.info(f"Total unique articles after deduplication: {len(all_articles)}")
        
        # Return up to 100 articles for variety
        return all_articles[:100]
