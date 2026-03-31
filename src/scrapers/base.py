"""
Base scraper class for AI search engines.
"""

from abc import ABC, abstractmethod
from typing import Optional
from playwright.sync_api import sync_playwright, Browser, Page, TimeoutError as PlaywrightTimeout


class BaseScraper(ABC):
    """Abstract base class for AI search engine scrapers."""
    
    name: str = "base"
    url: str = "https://example.com"
    
    def __init__(self, headless: bool = True, timeout: int = 30):
        """
        Initialize scraper.
        
        Args:
            headless: Run browser in headless mode
            timeout: Page load timeout in seconds
        """
        self.headless = headless
        self.timeout = timeout * 1000  # Convert to milliseconds
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    def __enter__(self):
        """Context manager entry."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def new_page(self) -> Page:
        """Create a new browser page."""
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use context manager.")
        return self.browser.new_page()
    
    def close(self):
        """Close browser and playwright."""
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
    
    @abstractmethod
    def search(self, query: str, page: Page) -> str:
        """
        Perform a search and return the AI response.
        
        Args:
            query: Search query
            page: Playwright page object
        
        Returns:
            Raw AI response text
        """
        pass
    
    def scrape(self, query: str) -> str:
        """
        Convenience method to scrape a query.
        
        Args:
            query: Search query
        
        Returns:
            Raw AI response text
        """
        with self as scraper:
            page = scraper.new_page()
            try:
                return scraper.search(query, page)
            except PlaywrightTimeout:
                return f"[TIMEOUT] Scraping {self.name} timed out for query: {query}"
            except Exception as e:
                return f"[ERROR] {str(e)}"
            finally:
                page.close()


class ScraperError(Exception):
    """Base exception for scraper errors."""
    pass


class LoginRequiredError(ScraperError):
    """Raised when login is required."""
    pass


class RateLimitError(ScraperError):
    """Raised when rate limited."""
    pass
