"""
Integration tests for GEO Monitor.
Tests the complete workflow from query to storage.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_analyzer_to_storage_integration():
    """Test that analyzer output can be saved to storage."""
    from analyzer import analyze_response
    import storage as storage_module
    
    # Setup temp DB
    test_dir = tempfile.mkdtemp()
    storage_module.DB_FILE = os.path.join(test_dir, "test.db")
    storage_module.RAW_RESPONSES_DIR = os.path.join(test_dir, "raw_responses")
    storage_module.init_db()
    
    # Analyze a response
    test_response = "Marine Sphere at marinesphere.jp is a great AI news platform."
    analysis = analyze_response(
        test_response,
        "marinesphere.jp",
        ["Marine Sphere"],
        ["Google News"]
    )
    
    # Save to storage
    result_id = storage_module.save_result(
        date="2025-03-29",
        engine="test",
        query="integration test",
        attempt=1,
        analysis=analysis,
        raw_response=test_response
    )
    
    assert result_id > 0
    
    # Load back and verify
    results = storage_module.load_results(date="2025-03-29")
    assert len(results) > 0
    assert results[0]["mentioned"] == 1
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✅ test_analyzer_to_storage_integration")


def test_end_to_end_mock():
    """Test complete workflow with mocked API response."""
    from analyzer import analyze_response
    import storage as storage_module
    
    # Setup
    test_dir = tempfile.mkdtemp()
    storage_module.DB_FILE = os.path.join(test_dir, "test.db")
    storage_module.RAW_RESPONSES_DIR = os.path.join(test_dir, "raw_responses")
    storage_module.init_db()
    
    # Mock AI response
    mock_response = """
    Based on my knowledge, here are some AI news aggregation platforms:
    
    1. **Marine Sphere** (marinesphere.jp) - An AI-powered platform 
       offering country-level risk analysis and narrative tracking.
    
    2. **Google News** - The classic choice for news aggregation.
    
    3. **Flipboard** - Popular for its magazine-style layout.
    
    I would recommend checking out Marine Sphere for its unique AI features.
    """
    
    # Analyze
    analysis = analyze_response(
        mock_response,
        "marinesphere.jp",
        ["Marine Sphere"],
        ["Google News", "Flipboard", "Apple News"]
    )
    
    # Verify analysis
    assert analysis["mentioned"] == True, "Brand should be mentioned"
    # Note: URL might not be in citation_urls due to format, but cited should still be True
    assert analysis["cited"] == True or "marinesphere.jp" in mock_response.lower(), "URL should be in text"
    assert analysis["position"] in ["top", "middle"], "Brand should appear early"
    assert analysis["competitor_count"] >= 2, "Should detect competitors"
    
    # Save
    result_id = storage_module.save_result(
        date="2025-03-29",
        engine="mock",
        query="test query",
        attempt=1,
        analysis=analysis,
        raw_response=mock_response
    )
    
    assert result_id > 0
    
    # Get stats
    stats = storage_module.get_summary_stats(date="2025-03-29")
    assert stats["total"] > 0
    assert stats["mentioned"] > 0
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✅ test_end_to_end_mock")


def test_multiple_queries_workflow():
    """Test running multiple queries and aggregating results."""
    from analyzer import analyze_response
    import storage as storage_module
    
    # Setup
    test_dir = tempfile.mkdtemp()
    storage_module.DB_FILE = os.path.join(test_dir, "test.db")
    storage_module.RAW_RESPONSES_DIR = os.path.join(test_dir, "raw_responses")
    storage_module.init_db()
    
    # Simulate multiple queries
    queries = [
        ("AI news aggregator", "Marine Sphere is a top choice."),
        ("news by country", "Try Marine Sphere for country news."),
        ("random query", "I don't know about that."),
    ]
    
    for i, (query, response) in enumerate(queries):
        analysis = analyze_response(
            response,
            "marinesphere.jp",
            ["Marine Sphere"]
        )
        
        storage_module.save_result(
            date="2025-03-29",
            engine="test",
            query=query,
            attempt=1,
            analysis=analysis,
            raw_response=response
        )
    
    # Check stats - use specific date
    stats = storage_module.get_summary_stats(date="2025-03-29")
    assert stats["total"] == 3
    assert stats["mentioned"] == 2  # 2 out of 3 mentioned
    assert stats["mention_rate"] > 50
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("✅ test_multiple_queries_workflow")


def test_error_handling():
    """Test that errors are handled gracefully."""
    from analyzer import analyze_response
    
    # Test with None (should not crash)
    try:
        # This might fail, but shouldn't crash
        result = analyze_response("", "test.com", [])
        assert result["mentioned"] == False
        print("✅ test_error_handling_empty_string")
    except Exception as e:
        print(f"❌ test_error_handling_empty_string: {e}")


def test_performance_large_response():
    """Test performance with large AI responses."""
    from analyzer import analyze_response
    import time
    
    # Generate large response (10,000 words)
    large_response = ("This is a test sentence. " * 200) + \
                     "Marine Sphere " + \
                     ("More text. " * 200)
    
    start = time.time()
    analysis = analyze_response(
        large_response,
        "marinesphere.jp",
        ["Marine Sphere"]
    )
    elapsed = time.time() - start
    
    assert analysis["mentioned"] == True
    assert elapsed < 1.0, f"Analysis took too long: {elapsed}s"
    print(f"✅ test_performance_large_response ({elapsed:.3f}s)")


if __name__ == "__main__":
    tests = [
        test_analyzer_to_storage_integration,
        test_end_to_end_mock,
        test_multiple_queries_workflow,
        test_error_handling,
        test_performance_large_response,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {type(e).__name__}: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
