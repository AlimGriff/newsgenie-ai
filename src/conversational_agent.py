    def handle_llm_query(self, query):
        """Use LLM to answer complex questions."""
        try:
            context = self.build_context()
            
            prompt = f"""You are a helpful news assistant. Answer the user's question based on the available news articles.

Available articles context:
{context}

User question: {query}

Provide a helpful and concise answer:"""
            
            response = self.llm_handler.generate_response(prompt, max_length=400)
            
            # If LLM returns None or empty, use fallback
            if not response or response.strip() == "":
                logger.warning("LLM returned empty response, using fallback")
                return self.fallback_response(query)
            
            return response
        
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return self.fallback_response(query)
    
    def fallback_response(self, query):
        """Fallback when LLM fails."""
        keywords = re.findall(r'\b[a-z]{4,}\b', query.lower())
        
        if 'uk' in query.lower() or 'british' in query.lower():
            return self.get_uk_news()
        elif 'news' in query.lower() or 'latest' in query.lower():
            return self.get_top_stories()
        elif keywords:
            return self.search_articles(keywords[0])
        else:
            return "I'm having trouble understanding. Try: 'Show me UK news' or 'What are the top stories?'"
