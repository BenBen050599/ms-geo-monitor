"""
GEO Monitor - Main entry point.
Runs all queries through AI engines and saves results.
"""

import sys
import time
import os
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import BRAND, BRAND_ALIASES, ENGINES, ALL_QUERIES, ATTEMPTS_PER_QUERY
from analyzer import analyze_response
from storage import save_result

# Competitors to track
COMPETITORS = ["Google News", "Flipboard", "Apple News", "Microsoft News", "SmartNews"]


def run_query_groq(query: str, attempt: int) -> dict:
    """Run query using Groq API (free, reliable)."""
    try:
        from scrapers.groq_api import GroqAPIScraper
        scraper = GroqAPIScraper()
        raw_response = scraper.search(query)
        
        analysis = analyze_response(raw_response, BRAND, BRAND_ALIASES, COMPETITORS)
        
        return {"success": True, "response": raw_response, "analysis": analysis}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_query_scraping(engine: str, query: str, attempt: int) -> dict:
    """Run query using web scraping."""
    from scrapers.perplexity import PerplexityScraper
    from scrapers.ddg_ai import DDGAIChatScraper
    
    scrapers = {
        "perplexity": PerplexityScraper,
        "ddg_ai": DDGAIChatScraper,
    }
    
    scraper_class = scrapers.get(engine)
    if not scraper_class:
        return {"success": False, "error": f"Unknown engine: {engine}"}
    
    try:
        scraper = scraper_class(headless=True, timeout=60)
        raw_response = scraper.scrape(query)
        
        analysis = analyze_response(raw_response, BRAND, BRAND_ALIASES, COMPETITORS)
        
        return {"success": True, "response": raw_response, "analysis": analysis}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_query(engine: str, query: str, attempt: int) -> dict:
    """Run a single query on a single engine."""
    print(f"  [{engine}] Attempt {attempt}: {query[:50]}...")
    
    if engine == "groq":
        return run_query_groq(query, attempt)
    else:
        return run_query_scraping(engine, query, attempt)


def main():
    """Main function to run all monitoring."""
    print("=" * 60)
    print(f"GEO Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Brand: {BRAND}")
    print(f"Engines: {ENGINES}")
    print(f"Queries: {len(ALL_QUERIES)}")
    print(f"Attempts per query: {ATTEMPTS_PER_QUERY}")
    print("=" * 60)
    
    # Check for API keys
    if "groq" in ENGINES and not os.getenv("GROQ_API_KEY"):
        print("\n⚠️  GROQ_API_KEY not set!")
        print("Get free key at: https://console.groq.com")
        print("Set it: export GROQ_API_KEY='your-key-here'\n")
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    total_success = 0
    total_failed = 0
    
    for engine_name in ENGINES:
        print(f"\n🔍 Engine: {engine_name}")
        
        for query in ALL_QUERIES:
            for attempt in range(1, ATTEMPTS_PER_QUERY + 1):
                result = run_query(engine_name, query, attempt)
                
                if result.get("success"):
                    save_result(
                        date=today,
                        engine=engine_name,
                        query=query,
                        attempt=attempt,
                        analysis=result["analysis"],
                        raw_response=result["response"]
                    )
                    total_success += 1
                    
                    mentioned = result["analysis"]["mentioned"]
                    cited = result["analysis"]["cited"]
                    print(f"    ✅ Mentioned: {mentioned}, Cited: {cited}")
                else:
                    total_failed += 1
                    print(f"    ❌ {result.get('error', 'Unknown error')}")
                
                time.sleep(1)  # Be nice to servers
    
    print("\n" + "=" * 60)
    print(f"✅ Done! Success: {total_success}, Failed: {total_failed}")
    print(f"📊 Data saved to: data/results.db")
    print("=" * 60)


if __name__ == "__main__":
    main()
