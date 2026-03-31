"""
Perplexity AI search scraper.
Perplexity doesn't require login for basic searches.
"""

import time
from .base import BaseScraper, ScraperError
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout


class PerplexityScraper(BaseScraper):
    """Scraper for Perplexity AI search."""
    
    name = "perplexity"
    url = "https://www.perplexity.ai"
    
    def search(self, query: str, page: Page) -> str:
        """
        Search Perplexity and get AI response.
        
        Args:
            query: Search query
            page: Playwright page object
        
        Returns:
            AI response text
        """
        # Navigate to Perplexity
        page.goto(self.url, wait_until="networkidle", timeout=self.timeout)
        
        # Wait for search box to be ready
        try:
            search_box = page.wait_for_selector(
                'input[placeholder*="Ask"]',
                timeout=10000
            )
        except PlaywrightTimeout:
            # Try alternative selector
            search_box = page.wait_for_selector(
                'input[type="text"]',
                timeout=10000
            )
        
        # Type query
        search_box.fill(query)
        
        # Press Enter to submit
        search_box.press("Enter")
        
        # Wait for AI response to start appearing
        # Perplexity shows "thinking" then actual answer
        try:
            # Wait for the answer container to appear
            page.wait_for_selector(
                '[data-testid="answer"]',
                timeout=self.timeout
            )
        except PlaywrightTimeout:
            # Try alternative - look for any answer text
            pass
        
        # Wait longer for full response (up to 30 seconds)
        time.sleep(30)
        
        # Try multiple selectors to get the answer
        answer_selectors = [
            '[data-testid="answer"]',
            '.answer-content',
            '.prose',
            '.result-main',
            'main article',
            '[class*="answer"]',
        ]
        
        answer_text = None
        for selector in answer_selectors:
            try:
                element = page.query_selector(selector)
                if element:
                    answer_text = element.inner_text()
                    if answer_text and len(answer_text) > 50:
                        break
            except:
                continue
        
        # If no structured answer, get the main content
        if not answer_text or len(answer_text) < 50:
            # Fallback: get the main content area
            try:
                main = page.query_selector("main")
                if main:
                    answer_text = main.inner_text()
            except:
                pass
        
        # Last resort: get entire body text
        if not answer_text or len(answer_text) < 50:
            answer_text = page.inner_text("body")
        
        # Clean up the response
        if answer_text:
            # Remove extra whitespace
            answer_text = "\n".join(line.strip() for line in answer_text.split("\n") if line.strip())
        
        return answer_text or "[NO_RESPONSE] Could not extract answer from Perplexity"


# For easy importing
scraper = PerplexityScraper
