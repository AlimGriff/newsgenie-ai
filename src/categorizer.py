    def categorize(self, article):
        """Categorize a single article with improved accuracy."""
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        # Check source URL for category hints
        source_url = article.get('url', '').lower()
        source = article.get('source', '').lower()
        
        # Direct source matching (most reliable)
        if any(sport in source_url or sport in source for sport in ['espn', 'skysports', 'bbc-sport', 'sports.yahoo', '/sport/']):
            return 'Sports'
        if any(tech in source_url or tech in source for tech in ['techcrunch', 'theverge', 'wired', 'arstechnica', '/technology/']):
            return 'Technology'
        if any(fin in source_url or fin in source for fin in ['reuters/markets', 'marketwatch', 'investing.com', '/finance/', 'ft.com']):
            return 'Finance'
        if any(biz in source_url or biz in source for biz in ['reuters/business', '/business/']):
            return 'Business'
        
        # Score each category with weighted keywords
        category_scores = {}
        
        # Check title first (more weight)
        title_lower = article.get('title', '').lower()
        
        for category, keywords in self.category_keywords.items():
            score = 0
            matches = []
            
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                
                # Title matches get triple weight
                if re.search(pattern, title_lower):
                    score += 3
                    matches.append(keyword)
                # Summary matches get single weight
                elif re.search(pattern, text):
                    score += 1
                    matches.append(keyword)
            
            # Check exclusions
            excluded = False
            if category in self.exclusion_keywords:
                for exclusion in self.exclusion_keywords[category]:
                    if exclusion in text:
                        excluded = True
                        break
            
            if not excluded and score > 0:
                category_scores[category] = score
        
        # Special rules to prevent miscategorization
        
        # If "protest" or "demonstration" mentioned, likely Politics or World
        if any(word in text for word in ['protest', 'demonstration', 'rally', 'march', 'activist']):
            if 'Technology' in category_scores:
                category_scores['Technology'] = max(0, category_scores['Technology'] - 5)
            if 'Politics' in category_scores:
                category_scores['Politics'] += 3
            else:
                category_scores['Politics'] = 3
        
        # If "strike" or "union" mentioned, likely Business or Politics
        if any(word in text for word in ['strike', 'union', 'workers', 'employees']):
            if 'Technology' in category_scores:
                category_scores['Technology'] = max(0, category_scores['Technology'] - 5)
            if 'Business' in category_scores:
                category_scores['Business'] += 2
        
        # Special handling for Finance vs Business disambiguation
        if 'Finance' in category_scores and 'Business' in category_scores:
            finance_specific = ['stock', 'market', 'trading', 'investment', 'bank', 'currency', 
                              'inflation', 'interest rate', 'profit', 'earnings', 'revenue']
            has_finance_specific = any(term in text for term in finance_specific)
            
            if has_finance_specific:
                category_scores['Finance'] += 3
        
        # Return category with highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            
            # Require minimum threshold based on category
            min_threshold = 1 if best_category in ['Finance', 'Sports', 'Politics'] else 2
            
            if category_scores[best_category] >= min_threshold:
                logger.info(f"Categorized '{article.get('title', 'Unknown')[:50]}...' as {best_category} (score: {category_scores[best_category]})")
                return best_category
        
        # Default to General if no clear match
        logger.info(f"Categorized '{article.get('title', 'Unknown')[:50]}...' as General (no clear match)")
        return 'General'
