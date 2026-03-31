"""
Tests for config.py - configuration validation.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_config_import():
    """Test that config imports correctly."""
    import config
    
    assert hasattr(config, "BRAND")
    assert hasattr(config, "BRAND_ALIASES")
    assert hasattr(config, "ENGINES")
    assert hasattr(config, "ALL_QUERIES")
    assert hasattr(config, "ATTEMPTS_PER_QUERY")
    
    print("✅ test_config_import")


def test_config_values():
    """Test that config values are valid."""
    import config
    
    # Brand should be set
    assert config.BRAND != ""
    assert "marinesphere" in config.BRAND.lower() or len(config.BRAND) > 0
    
    # Aliases should be a list
    assert isinstance(config.BRAND_ALIASES, list)
    assert len(config.BRAND_ALIASES) > 0
    
    # Engines should be a list
    assert isinstance(config.ENGINES, list)
    assert len(config.ENGINES) > 0
    
    # All queries should be a list
    assert isinstance(config.ALL_QUERIES, list)
    assert len(config.ALL_QUERIES) > 0
    
    # Attempts should be positive
    assert config.ATTEMPTS_PER_QUERY > 0
    
    print("✅ test_config_values")


def test_queries_not_empty():
    """Test that all query categories have content."""
    import config
    
    # Check each query category
    assert len(config.BRAND_QUERIES) >= 1, "Should have at least 1 brand query"
    assert len(config.CATEGORY_QUERIES) >= 1, "Should have at least 1 category query"
    assert len(config.COMPETITOR_QUERIES) >= 1, "Should have at least 1 competitor query"
    
    # All queries should be non-empty strings
    for query in config.ALL_QUERIES:
        assert isinstance(query, str)
        assert len(query) > 0
    
    print("✅ test_queries_not_empty")


def test_engines_valid():
    """Test that all engines are valid."""
    import config
    
    valid_engines = ["groq", "perplexity", "ddg_ai"]
    
    for engine in config.ENGINES:
        assert engine in valid_engines, f"Unknown engine: {engine}"
    
    print("✅ test_engines_valid")


def test_citation_patterns():
    """Test that citation patterns are valid."""
    import config
    
    # Should contain brand URL
    assert any(config.BRAND.replace("www.", "") in p for p in config.CITATION_PATTERNS)
    
    print("✅ test_citation_patterns")


def test_all_queries_combined():
    """Test that ALL_QUERIES is the combination of categories."""
    import config
    
    expected_all = config.BRAND_QUERIES + config.CATEGORY_QUERIES + config.COMPETITOR_QUERIES
    
    assert len(config.ALL_QUERIES) == len(expected_all)
    
    print("✅ test_all_queries_combined")


def test_query_categories_mapping():
    """Test that QUERY_CATEGORIES is properly structured."""
    import config
    
    assert "brand" in config.QUERY_CATEGORIES
    assert "category" in config.QUERY_CATEGORIES
    assert "competitor" in config.QUERY_CATEGORIES
    
    # Each category should have queries
    for category, queries in config.QUERY_CATEGORIES.items():
        assert isinstance(queries, list)
        assert len(queries) > 0
    
    print("✅ test_query_categories_mapping")


if __name__ == "__main__":
    tests = [
        test_config_import,
        test_config_values,
        test_queries_not_empty,
        test_engines_valid,
        test_citation_patterns,
        test_all_queries_combined,
        test_query_categories_mapping,
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
