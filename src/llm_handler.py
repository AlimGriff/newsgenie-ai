from transformers import pipeline
import logging

logger = logging.getLogger(__name__)


class LLMHandler:
    """Handle LLM interactions using HuggingFace models."""
    
    def __init__(self):
        self.model_name = "google/flan-t5-base"
        self.llm = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the HuggingFace model."""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.llm = pipeline(
                "text2text-generation",
                model=self.model_name,
                max_length=512,
                device=-1
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.llm = None
    
    def generate_response(self, prompt, max_length=256):
        """Generate response from LLM."""
        if not self.llm:
            return "LLM not available. Using fallback responses."
        
        try:
            response = self.llm(
                prompt,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7
            )
            return response[0]['generated_text']
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I encountered an error. Please try again."
    
    def answer_question(self, question, context):
        """Answer a question based on context."""
        prompt = f"Question: {question}\n\nContext: {context}\n\nAnswer:"
        return self.generate_response(prompt)
    
    def summarize_articles(self, articles, max_articles=5):
        """Summarize multiple articles."""
        if not articles:
            return "No articles to summarize."
        
        articles_text = "\n\n".join([
            f"Title: {a.get('title', '')}\nSummary: {a.get('summary', '')[:200]}"
            for a in articles[:max_articles]
        ])
        
        prompt = f"Summarize these news articles:\n\n{articles_text}\n\nSummary:"
        return self.generate_response(prompt, max_length=300)
