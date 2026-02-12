from transformers import pipeline
import logging

logger = logging.getLogger(__name__)


class LLMHandler:
    
    def __init__(self):
        self.model_name = "google/flan-t5-small"
        self.llm = None
        self._initialize_model()
    
    def _initialize_model(self):
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.llm = pipeline(
                "text2text-generation",
                model=self.model_name,
                max_length=256,
                device=-1
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.llm = None
    
    def generate_response(self, prompt, max_length=256):
        if not self.llm:
            return None
        
        try:
            response = self.llm(
                prompt,
                max_length=max_length,
                num_return_sequences=1,
                do_sample=False
            )
            return response[0]['generated_text']
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None
