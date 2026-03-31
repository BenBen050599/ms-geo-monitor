"""
Groq API scraper - Free LLM API.
Get your free API key at: https://console.groq.com
"""

import os
from typing import Optional
from .base import BaseScraper, ScraperError


class GroqAPIScraper(BaseScraper):
    """Scraper using Groq's free API."""
    
    name = "groq"
    url = "https://console.groq.com"
    
    # Free models available on Groq
    MODELS = [
        "llama-3.3-70b-versatile",  # Best quality
        "llama-3.1-8b-instant",      # Fastest
        "mixtral-8x7b-32768",        # Good balance
    ]
    
    def __init__(self, api_key: Optional[str] = None, model: str = None):
        """
        Initialize Groq API scraper.
        
        Args:
            api_key: Groq API key (or set GROQ_API_KEY env var)
            model: Model to use (default: llama-3.1-8b-instant for token efficiency)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ScraperError("GROQ_API_KEY not set. Get free key at https://console.groq.com")
        
        # Use 8b-instant by default: ~4x fewer tokens than 70b, same free tier limit
        self.model = model or "llama-3.1-8b-instant"
    
    def search(self, query: str) -> str:
        """
        Query Groq API and get response.
        
        Args:
            query: Search query
        
        Returns:
            AI response text
        """
        try:
            from groq import Groq
        except ImportError:
            raise ScraperError("groq package not installed. Run: pip install groq")
        
        client = Groq(api_key=self.api_key)
        
        # Format query as a question
        prompt = f"""You are a helpful AI assistant. Please answer the following question comprehensively:

{query}

Provide a detailed answer, and if you mention any websites or services, include their URLs when possible."""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that provides detailed, informative answers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800,  # Reduced for token efficiency
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise ScraperError(f"Groq API error: {str(e)}")
    
    def scrape(self, query: str) -> str:
        """Convenience method matching BaseScraper interface."""
        return self.search(query)


# For easy importing
scraper = GroqAPIScraper
