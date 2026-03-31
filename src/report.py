"""
Generate dashboard data from SQLite database.
Run this after main.py to update the dashboard.
"""

import sys
import json
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from storage import load_results, get_summary_stats


def generate_dashboard_data():
    """Generate dashboard data from database."""
    
    # Get stats
    stats = get_summary_stats(days=30)
    
    # Get ALL recent results (not just 20)
    recent = load_results(limit=200)
    
    # Load raw responses for each result
    recent_with_raw = []
    for r in recent:
        raw_response = load_raw_response(r.get("raw_file"))
        recent_with_raw.append({
            "date": r["date"],
            "engine": r["engine"],
            "query": r["query"],
            "mentioned": bool(r["mentioned"]),
            "cited": bool(r["cited"]),
            "position": r["position"],
            "sentiment": r.get("sentiment", "neutral"),
            "response_length": r.get("response_length", 0),
            "raw_response": raw_response
        })
    
    # Group by query for query performance
    query_performance = {}
    for r in recent_with_raw:
        query = r["query"]
        if query not in query_performance:
            query_performance[query] = {"mentioned": 0, "total": 0, "cited": 0}
        query_performance[query]["total"] += 1
        if r["mentioned"]:
            query_performance[query]["mentioned"] += 1
        if r["cited"]:
            query_performance[query]["cited"] += 1
    
    # Format query performance
    query_stats = [
        {
            "query": q,
            "mentioned": s["mentioned"],
            "total": s["total"],
            "cited": s["cited"],
            "rate": round(s["mentioned"] / s["total"] * 100, 1) if s["total"] > 0 else 0
        }
        for q, s in query_performance.items()
    ]
    query_stats.sort(key=lambda x: x["rate"], reverse=True)
    
    # Format for dashboard
    data = {
        "generated_at": "auto",
        "total": stats["total"],
        "mention_rate": stats["mention_rate"],
        "cited": stats["cited"],
        "days": len(stats["daily_trend"]),
        "trend": stats["daily_trend"],
        "by_engine": stats["by_engine"],
        "query_performance": query_stats,
        "recent": recent_with_raw
    }
    
    return data


def load_raw_response(raw_file):
    """Load raw response from file."""
    if not raw_file:
        return None
    
    try:
        # raw_file is relative to project root
        base_dir = Path(__file__).parent.parent
        full_path = base_dir / raw_file
        
        if full_path.exists():
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("response", "")
    except Exception:
        pass
    
    return None


def save_dashboard_json():
    """Save dashboard data to JSON file."""
    data = generate_dashboard_data()
    
    output_path = Path(__file__).parent.parent / "dashboard" / "data.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Dashboard data saved to {output_path}")
    return data


if __name__ == "__main__":
    data = save_dashboard_json()
    print(f"\n📊 Summary:")
    print(f"   Total queries: {data['total']}")
    print(f"   Mention rate: {data['mention_rate']}%")
    print(f"   Days tracked: {data['days']}")
    print(f"   Recent results: {len(data['recent'])}")
