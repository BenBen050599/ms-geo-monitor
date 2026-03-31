"""
Storage layer for GEO Monitor - SQLite + JSON for raw responses.
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import DB_FILE, RAW_RESPONSES_DIR


def init_db():
    """Initialize SQLite database with schema."""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Main results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            engine TEXT NOT NULL,
            query TEXT NOT NULL,
            attempt INTEGER NOT NULL,
            mentioned INTEGER NOT NULL,
            cited INTEGER NOT NULL,
            position TEXT NOT NULL,
            sentiment TEXT DEFAULT 'neutral',
            competitor_count INTEGER DEFAULT 0,
            response_length INTEGER DEFAULT 0,
            raw_file TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Citations table (separate for normalization)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            result_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            FOREIGN KEY (result_id) REFERENCES results(id)
        )
    """)
    
    # Competitors table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS competitor_mentions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            result_id INTEGER NOT NULL,
            competitor TEXT NOT NULL,
            FOREIGN KEY (result_id) REFERENCES results(id)
        )
    """)
    
    # Indexes for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON results(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_engine ON results(engine)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_query ON results(query)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mentioned ON results(mentioned)")
    
    conn.commit()
    conn.close()


def save_result(
    date: str,
    engine: str,
    query: str,
    attempt: int,
    analysis: Dict[str, Any],
    raw_response: str
) -> int:
    """
    Save a single result to the database.
    
    Args:
        date: ISO date string (YYYY-MM-DD)
        engine: AI engine name (e.g., "perplexity")
        query: The query that was asked
        attempt: Attempt number (1, 2, 3...)
        analysis: Dict from analyzer.analyze_response()
        raw_response: Raw AI response text
    
    Returns:
        Result ID
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Determine sentiment (simple heuristic)
    sentiment = "neutral"
    if any(word in raw_response.lower() for word in ["best", "great", "excellent", "recommend", "love"]):
        sentiment = "positive"
    elif any(word in raw_response.lower() for word in ["bad", "worst", "avoid", "hate", "terrible"]):
        sentiment = "negative"
    
    # Save raw response to JSON file
    raw_file = save_raw_response(date, engine, query, attempt, raw_response)
    
    # Insert main result
    cursor.execute("""
        INSERT INTO results (
            date, engine, query, attempt, mentioned, cited, position,
            sentiment, competitor_count, response_length, raw_file
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        date,
        engine,
        query,
        attempt,
        1 if analysis["mentioned"] else 0,
        1 if analysis["cited"] else 0,
        analysis["position"],
        sentiment,
        analysis["competitor_count"],
        analysis["response_length"],
        raw_file
    ))
    
    result_id = cursor.lastrowid
    
    # Save citations
    for url in analysis.get("citation_urls", []):
        cursor.execute(
            "INSERT INTO citations (result_id, url) VALUES (?, ?)",
            (result_id, url)
        )
    
    # Save competitor mentions
    for competitor in analysis.get("competitor_mentions", []):
        cursor.execute(
            "INSERT INTO competitor_mentions (result_id, competitor) VALUES (?, ?)",
            (result_id, competitor)
        )
    
    conn.commit()
    conn.close()
    
    return result_id


def save_raw_response(
    date: str,
    engine: str,
    query: str,
    attempt: int,
    response: str
) -> str:
    """
    Save raw response to a JSON file.
    
    Args:
        date: ISO date string
        engine: AI engine name
        query: The query asked
        attempt: Attempt number
        response: Raw response text
    
    Returns:
        Relative path to the saved file
    """
    # Create directory: data/raw_responses/2025-03-28/
    date_dir = Path(RAW_RESPONSES_DIR) / date
    date_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitize query for filename
    query_hash = str(abs(hash(query)))[:8]
    filename = f"{engine}_{query_hash}_{attempt}.json"
    filepath = date_dir / filename
    
    data = {
        "date": date,
        "engine": engine,
        "query": query,
        "attempt": attempt,
        "response": response,
        "saved_at": datetime.now().isoformat()
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Return relative path
    return str(Path("data") / "raw_responses" / date / filename)


def load_results(
    date: Optional[str] = None,
    engine: Optional[str] = None,
    query: Optional[str] = None,
    mentioned: Optional[bool] = None,
    limit: int = 1000
) -> List[Dict[str, Any]]:
    """
    Load results from database with optional filters.
    
    Args:
        date: Filter by date (YYYY-MM-DD)
        engine: Filter by engine
        query: Filter by query (partial match)
        mentioned: Filter by mentioned status
        limit: Maximum results to return
    
    Returns:
        List of result dictionaries
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    sql = "SELECT * FROM results WHERE 1=1"
    params = []
    
    if date:
        sql += " AND date = ?"
        params.append(date)
    
    if engine:
        sql += " AND engine = ?"
        params.append(engine)
    
    if query:
        sql += " AND query LIKE ?"
        params.append(f"%{query}%")
    
    if mentioned is not None:
        sql += " AND mentioned = ?"
        params.append(1 if mentioned else 0)
    
    sql += " ORDER BY date DESC, engine, query, attempt LIMIT ?"
    params.append(limit)
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    
    results = [dict(row) for row in rows]
    
    conn.close()
    
    return results


def get_summary_stats(date: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
    """
    Get summary statistics for the dashboard.
    
    Args:
        date: Specific date, or None for latest
        days: Number of days to look back
    
    Returns:
        Dictionary with summary statistics
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Date filter - use date comparison that works with string dates
    date_filter = ""
    if date:
        date_filter = f"AND date = '{date}'"
    elif days:
        # For string dates in YYYY-MM-DD format, compare with current date
        from datetime import datetime, timedelta
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        date_filter = f"AND date >= '{start_date}'"
    
    # Total queries
    cursor.execute(f"""
        SELECT COUNT(*) as total FROM results WHERE 1=1 {date_filter}
    """)
    total = cursor.fetchone()[0]
    
    # Mentioned count
    cursor.execute(f"""
        SELECT COUNT(*) as mentioned FROM results WHERE mentioned=1 {date_filter}
    """)
    mentioned = cursor.fetchone()[0]
    
    # Cited count
    cursor.execute(f"""
        SELECT COUNT(*) as cited FROM results WHERE cited=1 {date_filter}
    """)
    cited = cursor.fetchone()[0]
    
    # By engine
    cursor.execute(f"""
        SELECT engine, 
               COUNT(*) as total,
               SUM(mentioned) as mentioned,
               SUM(cited) as cited
        FROM results WHERE 1=1 {date_filter}
        GROUP BY engine
    """)
    by_engine = []
    for row in cursor.fetchall():
        by_engine.append({
            "engine": row[0],
            "total": row[1],
            "mentioned": row[2],
            "cited": row[3],
            "mention_rate": round(row[2] / row[1] * 100, 1) if row[1] > 0 else 0
        })
    
    # By query category
    cursor.execute(f"""
        SELECT query, 
               COUNT(*) as total,
               SUM(mentioned) as mentioned
        FROM results WHERE 1=1 {date_filter}
        GROUP BY query
        ORDER BY mentioned DESC
        LIMIT 10
    """)
    top_queries = []
    for row in cursor.fetchall():
        top_queries.append({
            "query": row[0],
            "total": row[1],
            "mentioned": row[2],
            "mention_rate": round(row[2] / row[1] * 100, 1) if row[1] > 0 else 0
        })
    
    # Daily trend
    cursor.execute(f"""
        SELECT date,
               COUNT(*) as total,
               SUM(mentioned) as mentioned
        FROM results WHERE 1=1 {date_filter}
        GROUP BY date
        ORDER BY date DESC
        LIMIT 30
    """)
    daily_trend = []
    for row in cursor.fetchall():
        daily_trend.append({
            "date": row[0],
            "total": row[1],
            "mentioned": row[2],
            "mention_rate": round(row[2] / row[1] * 100, 1) if row[1] > 0 else 0
        })
    
    conn.close()
    
    return {
        "total": total,
        "mentioned": mentioned,
        "cited": cited,
        "mention_rate": round(mentioned / total * 100, 1) if total > 0 else 0,
        "by_engine": by_engine,
        "top_queries": top_queries,
        "daily_trend": daily_trend
    }


# Initialize on import
init_db()
