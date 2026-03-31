"""
DuckDuckGo AI Chat scraper.
DuckDuckGo has a free AI Chat feature that doesn't require login.
"""

import time
from .base import BaseScraper
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout


class DDGAIChatScraper(BaseScraper):
    """Scraper for DuckDuckGo AI Chat."""
    
    name = "ddg_ai"
    url = "https://duckduckgo.com/?q=AI+Chat&ia=chat"
    
    def search(self, query: str, page: Page) -> str:
        """
        Search DuckDuckGo AI Chat and get AI response.
        
        Args:
            query: Search query
            page: Playwright page object
        
        Returns:
            AI response text
        """
        # Navigate to DuckDuckGo with AI Chat
        # Format: https://duckduckgo.com/?q=QUERY&ia=chat
        encoded_query = query.replace(" ", "+")
        search_url = f"https://duckduckgo.com/?q={encoded_query}&ia=chat"
        
        page.goto(search_url, wait_until="networkidle", timeout=self.timeout)
        
        # Wait for AI chat to load
        try:
            # Look for AI response container
            page.wait_for_selector(
                '[data-testid="ai-chat-response"]',
                timeout=15000
            )
        except PlaywrightTimeout:
            # Try alternative
            try:
                page.wait_for_selector(
                    '.ai-chat-message',
                    timeout=10000
                )
            except PlaywrightTimeout:
                pass
        
        # Wait longer for response to generate
        time.sleep(30)
        
        # Try multiple selectors
        answer_selectors = [
            '[data-testid="ai-chat-response"]',
            '.ai-chat-message',
            '.message-ai',
            '[class*="ai-response"]',
            '.result-message',
        ]
        
        answer_text = None
        for selector in answer_selectors:
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    # Get text from all matching elements
                    texts = [el.inner_text() for el in elements]
                    answer_text = "\n".join(texts)
                    if answer_text and len(answer_text) > 50:
                        break
            except:
                continue
        
        # Fallback: get main content
        if not answer_text or len(answer_text) < 50:
            try:
                main = page.query_selector("main")
                if main:
                    answer_text = main.inner_text()
            except:
                pass
        
        # Clean up
        if answer_text:
            answer_text = "\n".join(line.strip() for line in answer_text.split("\n") if line.strip())
        
        return answer_text or "[NO_RESPONSE] Could not extract response from DuckDuckGo AI Chat"


# For easy importing
scraper = DDGAIChatScraper
