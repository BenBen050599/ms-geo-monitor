"""
Tests for report.py - dashboard data generation.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


def test_generate_dashboard_data():
    """Test generating dashboard data from database."""
    import storage as storage_module
    import report as report_module
    from datetime import datetime
    
    # Setup temp DB
    test_dir = tempfile.mkdtemp()
    storage_module.DB_FILE = os.path.join(test_dir, "test.db")
    storage_module.RAW_RESPONSES_DIR = os.path.join(test_dir, "raw_responses")
    storage_module.init_db()
    
    # Use today's date so it's within 30 days
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Save some test data
    analysis = {
        "mentioned": True,
        "cited": True,
        "position": "top",
        "citation_urls": ["https://example.com"],
        "competitor_mentions": ["Google News"],
        "competitor_count": 1,
        "response_length": 500,
    }
    
    storage_module.save_result(
        date=today,
        engine="groq",
        query="test query 1",
        attempt=1,
        analysis=analysis,
        raw_response="Test response"
    )
    
    storage_module.save_result(
        date=today,
        engine="groq",
        query="test query 2",
        attempt=1,
        analysis=analysis,
        raw_response="Another test"
    )
    
    # Generate dashboard data
    data = report_module.generate_dashboard_data()
    
    # Verify structure
    assert "total" in data
    assert "mention_rate" in data
    assert "cited" in data
    assert "days" in data
    assert "trend" in data
    assert "by_engine" in data
    assert "recent" in data
    
    # Verify values (should be >= 2 since we saved 2 results)
    assert data["total"] >= 2, f"Expected >= 2, got {data['total']}"
    assert data["mention_rate"] > 0
    assert data["cited"] >= 2
    
    # Verify recent results
    assert len(data["recent"]) >= 2
    
    shutil.rmtree(test_dir)
    print("✅ test_generate_dashboard_data")


def test_save_dashboard_json():
    """Test saving dashboard data to JSON."""
    import storage as storage_module
    import report as report_module
    from datetime import datetime
    
    # Setup
    test_dir = tempfile.mkdtemp()
    storage_module.DB_FILE = os.path.join(test_dir, "test.db")
    storage_module.RAW_RESPONSES_DIR = os.path.join(test_dir, "raw_responses")
    storage_module.init_db()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Save data
    analysis = {
        "mentioned": True,
        "cited": False,
        "position": "top",
        "citation_urls": [],
        "competitor_mentions": [],
        "competitor_count": 0,
        "response_length": 100,
    }
    
    storage_module.save_result(
        date=today,
        engine="groq",
        query="test",
        attempt=1,
        analysis=analysis,
        raw_response="Test"
    )
    
    # Check data is valid JSON
    import json
    data = report_module.generate_dashboard_data()
    json_str = json.dumps(data)
    parsed = json.loads(json_str)
    assert parsed["total"] >= 1
    
    shutil.rmtree(test_dir)
    print("✅ test_save_dashboard_json")


def test_dashboard_data_empty_db():
    """Test dashboard generation with empty database."""
    import storage as storage_module
    import report as report_module
    
    # Setup
    test_dir = tempfile.mkdtemp()
    storage_module.DB_FILE = os.path.join(test_dir, "test.db")
    storage_module.RAW_RESPONSES_DIR = os.path.join(test_dir, "raw_responses")
    storage_module.init_db()
    
    # Generate with empty DB
    data = report_module.generate_dashboard_data()
    
    # Should return empty results
    assert data["total"] == 0
    assert data["mention_rate"] == 0
    assert data["cited"] == 0
    assert data["days"] == 0
    assert len(data["trend"]) == 0
    assert len(data["recent"]) == 0
    
    shutil.rmtree(test_dir)
    print("✅ test_dashboard_data_empty_db")


def test_dashboard_recent_format():
    """Test that recent results are formatted correctly."""
    import storage as storage_module
    import report as report_module
    
    # Setup
    test_dir = tempfile.mkdtemp()
    storage_module.DB_FILE = os.path.join(test_dir, "test.db")
    storage_module.RAW_RESPONSES_DIR = os.path.join(test_dir, "raw_responses")
    storage_module.init_db()
    
    # Save data with known values
    analysis = {
        "mentioned": True,
        "cited": True,
        "position": "middle",
        "citation_urls": ["https://test.com"],
        "competitor_mentions": ["Google"],
        "competitor_count": 1,
        "response_length": 500,
    }
    
    storage_module.save_result(
        date="2025-03-29",
        engine="groq",
        query="AI news aggregator",
        attempt=1,
        analysis=analysis,
        raw_response="Test"
    )
    
    data = report_module.generate_dashboard_data()
    
    # Check recent format
    recent = data["recent"][0]
    assert "date" in recent
    assert "engine" in recent
    assert "query" in recent
    assert "mentioned" in recent
    assert "position" in recent
    
    # Check types
    assert isinstance(recent["mentioned"], bool)
    assert isinstance(recent["query"], str)
    assert isinstance(recent["position"], str)
    
    shutil.rmtree(test_dir)
    print("✅ test_dashboard_recent_format")


if __name__ == "__main__":
    tests = [
        test_generate_dashboard_data,
        test_save_dashboard_json,
        test_dashboard_data_empty_db,
        test_dashboard_recent_format,
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
