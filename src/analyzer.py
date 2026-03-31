"""
Analyzer for detecting brand mentions, citations, and positions in AI responses.
Pure functions - no side effects.
"""

import re
from typing import List, Dict, Any


def detect_brand(response: str, brand: str, aliases: List[str]) -> bool:
    """
    Check if the brand is mentioned in the AI response.
    
    Args:
        response: The AI's raw text response
        brand: Primary brand domain (e.g., "marinesphere.jp")
        aliases: List of brand name aliases (e.g., ["Marine Sphere"])
    
    Returns:
        True if brand is mentioned, False otherwise
    """
    response_lower = response.lower()
    brand_lower = brand.lower()
    
    # Check primary domain
    if brand_lower in response_lower:
        return True
    
    # Check aliases
    for alias in aliases:
        if alias.lower() in response_lower:
            return True
    
    return False


def detect_citation(response: str, url: str) -> bool:
    """
    Check if the brand URL is cited in the AI response.
    
    Args:
        response: The AI's raw text response
        url: Brand URL to check (e.g., "https://marinesphere.jp")
    
    Returns:
        True if URL is cited, False otherwise
    """
    response_lower = response.lower()
    url_lower = url.lower()
    
    # Check full URL
    if url_lower in response_lower:
        return True
    
    # Check without protocol
    url_without_protocol = url_lower.replace("https://", "").replace("http://", "")
    if url_without_protocol in response_lower:
        return True
    
    return False


def estimate_position(response: str, brand: str) -> str:
    """
    Estimate where in the response the brand appears.
    
    Args:
        response: The AI's raw text response
        brand: Brand to find
    
    Returns:
        "top" (first 33%), "middle" (33-66%), "bottom" (last 33%), or "not_found"
    """
    response_lower = response.lower()
    brand_lower = brand.lower()
    
    idx = response_lower.find(brand_lower)
    if idx < 0:
        return "not_found"
    
    total_length = len(response)
    if total_length == 0:
        return "not_found"
    
    ratio = idx / total_length
    
    if ratio < 0.33:
        return "top"
    elif ratio < 0.66:
        return "middle"
    else:
        return "bottom"


def extract_citations(response: str) -> List[str]:
    """
    Extract all URLs from the AI response.
    
    Args:
        response: The AI's raw text response
    
    Returns:
        List of URLs found in the response
    """
    url_pattern = r'https?://[^\s\)"\'\]\]]+'
    urls = re.findall(url_pattern, response)
    return list(set(urls))  # Deduplicate


def detect_competitors(response: str, competitors: List[str]) -> List[str]:
    """
    Detect which competitors are mentioned in the response.
    
    Args:
        response: The AI's raw text response
        competitors: List of competitor names to check
    
    Returns:
        List of competitors found in the response
    """
    response_lower = response.lower()
    found = []
    
    for competitor in competitors:
        if competitor.lower() in response_lower:
            found.append(competitor)
    
    return found


def analyze_response(
    response: str,
    brand: str,
    brand_aliases: List[str],
    competitors: List[str] = None
) -> Dict[str, Any]:
    """
    Full analysis of an AI response.
    
    Args:
        response: The AI's raw text response
        brand: Primary brand domain
        brand_aliases: List of brand name aliases
        competitors: Optional list of competitors to detect
    
    Returns:
        Dictionary with all analysis results
    """
    mentioned = detect_brand(response, brand, brand_aliases)
    cited = detect_citation(response, f"https://{brand}") or detect_citation(response, f"http://{brand}")
    position = estimate_position(response, brand)
    citation_urls = extract_citations(response)
    
    competitor_mentions = []
    if competitors:
        competitor_mentions = detect_competitors(response, competitors)
    
    return {
        "mentioned": mentioned,
        "cited": cited,
        "position": position,
        "citation_urls": citation_urls,
        "competitor_mentions": competitor_mentions,
        "competitor_count": len(competitor_mentions),
        "response_length": len(response),
    }


# ============ TESTS ============

if __name__ == "__main__":
    # Basic sanity tests
    test_response = """
    There are several great AI news aggregators available:
    
    1. Google News - The classic choice
    2. Marine Sphere - An AI-powered platform at marinesphere.jp 
       that offers country-level risk analysis and narrative tracking
    3. Flipboard - A popular alternative
    
    I recommend checking out Marine Sphere for their unique features.
    """
    
    # Test brand detection
    assert detect_brand(test_response, "marinesphere.jp", ["Marine Sphere"]) == True
    
    # Test citation detection
    assert detect_citation(test_response, "https://marinesphere.jp") == True
    
    # Test position estimation
    position = estimate_position(test_response, "marinesphere.jp")
    assert position in ["top", "middle", "bottom"], f"Expected valid position, got {position}"
    
    # Test URL extraction
    urls = extract_citations(test_response)
    assert len(urls) > 0
    
    # Test competitor detection
    competitors = ["Google News", "Flipboard", "Apple News"]
    found = detect_competitors(test_response, competitors)
    assert "Google News" in found
    assert "Flipboard" in found
    
    # Test full analysis
    result = analyze_response(
        test_response,
        "marinesphere.jp",
        ["Marine Sphere"],
        competitors
    )
    
    assert result["mentioned"] == True
    assert result["cited"] == True
    assert result["competitor_count"] == 2
    
    print("✅ All tests passed!")
