"""
Comprehensive tests for storage module.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import storage as storage_module


# Use temp directory for tests
TEST_DIR = tempfile.mkdtemp()
TEST_DB = os.path.join(TEST_DIR, "test.db")


def setup():
    """Set up test environment."""
    storage_module.DB_FILE = TEST_DB
    storage_module.RAW_RESPONSES_DIR = os.path.join(TEST_DIR, "raw_responses")
    storage_module.init_db()


def teardown():
    """Clean up test environment."""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)


# ============ Database Initialization Tests ============

def test_init_db_creates_file():
    """Test that init_db creates the database file."""
    setup()
    assert os.path.exists(TEST_DB)
    teardown()


def test_init_db_creates_tables():
    """Test that init_db creates all required tables."""
    setup()
    
    import sqlite3
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    
    # Check results table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='results'")
    assert cursor.fetchone() is not None
    
    # Check citations table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='citations'")
    assert cursor.fetchone() is not None
    
    # Check competitor_mentions table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='competitor_mentions'")
    assert cursor.fetchone() is not None
    
    conn.close()
    teardown()


# ============ Save Result Tests ============

def test_save_result_basic():
    """Test saving a basic result."""
    setup()
    
    analysis = {
        "mentioned": True,
        "cited": False,
        "position": "top",
        "citation_urls": [],
        "competitor_mentions": ["Google News"],
        "competitor_count": 1,
        "response_length": 500,
    }
    
    result_id = storage_module.save_result(
        date="2025-03-29",
        engine="groq",
        query="test query",
        attempt=1,
        analysis=analysis,
        raw_response="Test response"
    )
    
    assert result_id > 0
    teardown()


def test_save_result_with_citations():
    """Test saving result with citations."""
    setup()
    
    analysis = {
        "mentioned": True,
        "cited": True,
        "position": "middle",
        "citation_urls": ["https://example.com", "https://test.com"],
        "competitor_mentions": [],
        "competitor_count": 0,
        "response_length": 1000,
    }
    
    result_id = storage_module.save_result(
        date="2025-03-29",
        engine="groq",
        query="test with citations",
        attempt=1,
        analysis=analysis,
        raw_response="Check https://example.com and https://test.com"
    )
    
    assert result_id > 0
    teardown()


def test_save_result_creates_raw_file():
    """Test that saving creates a raw response JSON file."""
    setup()
    
    analysis = {
        "mentioned": False,
        "cited": False,
        "position": "not_found",
        "citation_urls": [],
        "competitor_mentions": [],
        "competitor_count": 0,
        "response_length": 100,
    }
    
    storage_module.save_result(
        date="2025-03-29",
        engine="groq",
        query="test raw file",
        attempt=1,
        analysis=analysis,
        raw_response="Test content"
    )
    
    # Check that raw file was created
    raw_dir = os.path.join(TEST_DIR, "raw_responses", "2025-03-29")
    assert os.path.exists(raw_dir)
    
    files = list(Path(raw_dir).glob("*.json"))
    assert len(files) > 0
    teardown()


# ============ Load Results Tests ============

def test_load_results_basic():
    """Test loading results."""
    setup()
    
    # Save a result first
    analysis = {
        "mentioned": True,
        "cited": False,
        "position": "top",
        "citation_urls": [],
        "competitor_mentions": [],
        "competitor_count": 0,
        "response_length": 500,
    }
    
    storage_module.save_result(
        date="2025-03-29",
        engine="groq",
        query="load test",
        attempt=1,
        analysis=analysis,
        raw_response="Test"
    )
    
    # Load it back
    results = storage_module.load_results(date="2025-03-29")
    
    assert len(results) >= 1
    assert results[0]["engine"] == "groq"
    assert results[0]["query"] == "load test"
    teardown()


def test_load_results_filter_by_engine():
    """Test filtering results by engine."""
    setup()
    
    # Save results for different engines
    analysis = {
        "mentioned": True,
        "cited": False,
        "position": "top",
        "citation_urls": [],
        "competitor_mentions": [],
        "competitor_count": 0,
        "response_length": 500,
    }
    
    storage_module.save_result(
        date="2025-03-29",
        engine="groq",
        query="test 1",
        attempt=1,
        analysis=analysis,
        raw_response="Test"
    )
    
    storage_module.save_result(
        date="2025-03-29",
        engine="perplexity",
        query="test 2",
        attempt=1,
        analysis=analysis,
        raw_response="Test"
    )
    
    # Load only groq results
    results = storage_module.load_results(engine="groq")
    
    assert all(r["engine"] == "groq" for r in results)
    teardown()


def test_load_results_filter_by_mentioned():
    """Test filtering results by mentioned status."""
    setup()
    
    # Save mentioned and not mentioned results
    analysis_mentioned = {
        "mentioned": True,
        "cited": False,
        "position": "top",
        "citation_urls": [],
        "competitor_mentions": [],
        "competitor_count": 0,
        "response_length": 500,
    }
    
    analysis_not_mentioned = {
        "mentioned": False,
        "cited": False,
        "position": "not_found",
        "citation_urls": [],
        "competitor_mentions": [],
        "competitor_count": 0,
        "response_length": 500,
    }
    
    storage_module.save_result(
        date="2025-03-29",
        engine="groq",
        query="mentioned test",
        attempt=1,
        analysis=analysis_mentioned,
        raw_response="Marine Sphere is great"
    )
    
    storage_module.save_result(
        date="2025-03-29",
        engine="groq",
        query="not mentioned test",
        attempt=1,
        analysis=analysis_not_mentioned,
        raw_response="Something else"
    )
    
    # Load only mentioned results
    results = storage_module.load_results(mentioned=True)
    
    assert all(r["mentioned"] == 1 for r in results)
    teardown()


def test_load_results_empty():
    """Test loading results when none exist."""
    setup()
    
    results = storage_module.load_results(date="2099-01-01")
    assert len(results) == 0
    teardown()


# ============ Summary Stats Tests ============

def test_get_summary_stats():
    """Test getting summary statistics."""
    setup()
    
    # Save some results
    analysis = {
        "mentioned": True,
        "cited": True,
        "position": "top",
        "citation_urls": ["https://example.com"],
        "competitor_mentions": ["Google News"],
        "competitor_count": 1,
        "response_length": 500,
    }
    
    for i in range(3):
        storage_module.save_result(
            date="2025-03-29",
            engine="groq",
            query=f"stats test {i}",
            attempt=1,
            analysis=analysis,
            raw_response="Test"
        )
    
    # Use specific date to avoid date comparison issues
    stats = storage_module.get_summary_stats(date="2025-03-29")
    
    assert stats["total"] >= 3
    assert stats["mentioned"] >= 3
    assert "by_engine" in stats
    assert "top_queries" in stats
    assert "daily_trend" in stats
    teardown()


def test_get_summary_stats_empty():
    """Test summary stats when no data exists."""
    setup()
    
    stats = storage_module.get_summary_stats(days=30)
    
    assert stats["total"] == 0
    assert stats["mentioned"] == 0
    assert stats["mention_rate"] == 0
    teardown()


# ============ Sentiment Analysis Tests ============

def test_sentiment_positive():
    """Test that positive words trigger positive sentiment."""
    setup()
    
    analysis = {
        "mentioned": True,
        "cited": False,
        "position": "top",
        "citation_urls": [],
        "competitor_mentions": [],
        "competitor_count": 0,
        "response_length": 500,
    }
    
    storage_module.save_result(
        date="2025-03-29",
        engine="groq",
        query="sentiment test",
        attempt=1,
        analysis=analysis,
        raw_response="This is the best platform! Great features!"
    )
    
    results = storage_module.load_results(date="2025-03-29")
    
    # Note: sentiment is determined in save_result
    assert results[0]["sentiment"] == "positive"
    teardown()


def test_sentiment_negative():
    """Test that negative words trigger negative sentiment."""
    setup()
    
    analysis = {
        "mentioned": True,
        "cited": False,
        "position": "top",
        "citation_urls": [],
        "competitor_mentions": [],
        "competitor_count": 0,
        "response_length": 500,
    }
    
    storage_module.save_result(
        date="2025-03-29",
        engine="groq",
        query="sentiment test",
        attempt=1,
        analysis=analysis,
        raw_response="This is terrible. Avoid this platform."
    )
    
    results = storage_module.load_results(date="2025-03-29")
    
    assert results[0]["sentiment"] == "negative"
    teardown()


# ============ Run Tests ============

if __name__ == "__main__":
    tests = [
        # Initialization
        test_init_db_creates_file,
        test_init_db_creates_tables,
        
        # Save
        test_save_result_basic,
        test_save_result_with_citations,
        test_save_result_creates_raw_file,
        
        # Load
        test_load_results_basic,
        test_load_results_filter_by_engine,
        test_load_results_filter_by_mentioned,
        test_load_results_empty,
        
        # Stats
        test_get_summary_stats,
        test_get_summary_stats_empty,
        
        # Sentiment
        test_sentiment_positive,
        test_sentiment_negative,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {type(e).__name__}: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
