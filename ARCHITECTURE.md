# GEO Monitor — Architecture

## Overview

```
┌─────────────────────────────────────────────────────────┐
│  GitHub Actions (cron: daily 08:00 UTC)                 │
│                                                         │
│  ┌───────────┐   ┌───────────┐   ┌───────────┐        │
│  │ Perplexity│   │   DDG AI  │   │ ChatGPT   │  ...  │
│  └─────┬─────┘   └─────┬─────┘   └─────┬─────┘        │
│        │                │                │              │
│        └────────────────┼────────────────┘              │
│                         ↓                                │
│              ┌─────────────────────┐                    │
│              │   Playwright Scraper  │                    │
│              └──────────┬──────────┘                    │
│                         ↓                                │
│              ┌─────────────────────┐                    │
│              │     Analyzer         │                    │
│              │  (brand detection)  │                    │
│              └──────────┬──────────┘                    │
│                         ↓                                │
│              ┌─────────────────────┐                    │
│              │     Storage          │                    │
│              │  (SQLite + JSON)    │                    │
│              └──────────┬──────────┘                    │
│                         ↓                                │
│              ┌─────────────────────┐                    │
│              │    Report Generator  │                    │
│              │   (HTML + Charts)  │                    │
│              └──────────┬──────────┘                    │
│                         ↓                                │
│              ┌─────────────────────┐                    │
│              │   GitHub Pages      │                    │
│              │   (dashboard.html)  │                    │
│              └─────────────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

```
geo-monitor/
├── .github/
│   └── workflows/
│       └── daily.yml          # GitHub Actions workflow
├── src/
│   ├── __init__.py
│   ├── main.py                # Entry point
│   ├── config.py              # Config (queries, brand, engines)
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py            # Abstract scraper class
│   │   ├── perplexity.py      # Perplexity scraper
│   │   ├── ddg_ai.py          # DuckDuckGo AI Chat scraper
│   │   ├── chatgpt.py         # ChatGPT scraper
│   │   └── google_aio.py       # Google AI Overview scraper
│   ├── analyzer.py            # Brand detection & analysis
│   ├── storage.py             # SQLite + JSON storage
│   ├── report.py              # HTML report generator
│   └── utils.py               # Helpers
├── data/                      # Data files (git-tracked)
│   ├── results.db             # SQLite database
│   └── raw_responses/         # Raw AI responses (JSON)
│       └── 2025-03-28/
│           ├── perplexity.json
│           └── chatgpt.json
├── dashboard/
│   └── index.html             # GitHub Pages dashboard
├── tests/
│   └── test_analyzer.py       # Unit tests
├── requirements.txt            # Python dependencies
├── Dockerfile                 # (optional) for local runs
└── README.md                  # Setup instructions
```

## Component Details

### 1. Config (`config.py`)

Central configuration. Edit this to change monitored brand/queries.

```python
BRAND = "globalperspective.net"
BRAND_ALIASES = ["Global Perspectives", "globalperspective"]
CITATION_PATTERNS = [
    f"https://{BRAND}",
    f"http://{BRAND}",
    BRAND,
]

QUERIES = [
    "What are the best AI news aggregation platforms?",
    "Tell me about Global Perspectives news",
    "Where can I find AI-curated global news?",
    "What is globalperspective.net?",
    "Best news aggregator with AI 2025",
    "Global perspectives AI news review",
]

ATTEMPTS_PER_QUERY = 3  # Run each query N times for consistency

ENGINES = ["perplexity", "ddg_ai", "chatgpt"]
```

### 2. Scrapers (`scrapers/`)

Base class:
```python
class BaseScraper:
    name: str  # e.g. "perplexity"
    url: str   # e.g. "https://perplexity.ai"

    def __init__(self, headless=True):
        self.browser = playwright.chromium.launch(headless=headless)

    async def search(self, query: str) -> str:
        """Returns the raw AI response text"""
        raise NotImplementedError

    async def close(self):
        self.browser.close()
```

Each scraper inherits `BaseScraper` and implements `search()`.

### 3. Analyzer (`analyzer.py`)

Pure functions — no side effects.

```python
def detect_brand(response: str, brand: str, aliases: list[str]) -> bool
def detect_citation(response: str, url: str) -> bool
def estimate_position(response: str, brand: str) -> str  # top/middle/bottom/not_found
def extract_citations(response: str) -> list[str]  # extract all URLs from response
def detect_competitors(response: str, competitors: list[str]) -> list[str]
def analyze_sentiment(response: str) -> str  # positive/neutral/negative
```

### 4. Storage (`storage.py`)

SQLite for structured data, JSON files for raw responses.

```python
# SQLite schema
CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,           -- ISO date: "2025-03-28"
    engine TEXT,         -- "perplexity"
    query TEXT,          -- the search query
    attempt INTEGER,     -- 1, 2, or 3
    mentioned INTEGER,    -- 0 or 1
    cited INTEGER,        -- 0 or 1
    position TEXT,       -- "top" / "middle" / "bottom" / "not_found"
    sentiment TEXT,       -- "positive" / "neutral" / "negative"
    competitor_count INTEGER,
    response_length INTEGER,
    raw_file TEXT,       -- path to raw JSON file
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE citations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER,
    url TEXT,
    FOREIGN KEY (result_id) REFERENCES results(id)
);
```

### 5. Report Generator (`report.py`)

Generates `dashboard/index.html` with:
- Daily summary table
- 30-day trend chart (using Chart.js)
- Per-engine breakdown
- Per-query breakdown
- Recent raw responses (collapsible)

```python
def generate_dashboard(data_dir: Path, output: Path):
    results = load_results(data_dir / "results.db")
    chart_data = aggregate_trends(results, days=30)
    competitors = aggregate_competitors(results)
    html = render_template("dashboard.html", ...)
    write(output, html)
```

### 6. GitHub Actions Workflow (`.github/workflows/daily.yml`)

```yaml
name: Daily GEO Monitor
on:
  schedule:
    - cron: '0 8 * * *'  # 08:00 UTC = 16:00 CST
  workflow_dispatch:       # Manual trigger

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run GEO monitor
        run: python -m src.main
      - name: Commit and push data
        run: |
          git config user.name "GEO Bot"
          git add data/
          git commit -m "Update GEO data $(date +%Y-%m-%d)" || exit 0
          git push
```

## Data Flow

```
1. main.py reads config.QUERIES
         ↓
2. For each engine in config.ENGINES:
         ↓
3. For each query in QUERIES:
         ↓
4. Run scraper.search(query) × ATTEMPTS_PER_QUERY times
         ↓
5. For each raw response:
         ↓
6. analyzer.analyze(response) → metrics dict
         ↓
7. Save raw response to data/raw_responses/{date}/{engine}_{query_hash}.json
         ↓
8. Write metrics to SQLite
         ↓
9. report.generate_dashboard() → dashboard/index.html
         ↓
10. GitHub Actions commits + pushes data + dashboard
         ↓
11. GitHub Pages serves dashboard/index.html
```

## Key Design Decisions

| Decision | Reason |
|----------|--------|
| **Playwright** (not requests/httpx) | AI search pages are JS-heavy. Need real browser. |
| **SQLite** (not PostgreSQL) | Single file, git-tracked, no server needed. |
| **JSON for raw responses** | Full responses for future analysis. Easy to diff. |
| **No async/await in main** | GitHub Actions has 6-hour timeout. Sync is fine. |
| **Per-attempt storage** | Raw data preserved. Can re-analyze later with new logic. |
| **Dashboard = static HTML** | No server. GitHub Pages free hosting. Chart.js for charts. |

## Running Locally

```bash
# Clone
git clone https://github.com/YOUR_USER/geo-monitor.git
cd geo-monitor

# Install
pip install -r requirements.txt
playwright install chromium

# Run once
python -m src.main

# Serve dashboard locally
cd dashboard && python -m http.server 8080
```

## Environment Variables (for local runs)

```bash
export CHATGPT_SESSION_TOKEN="your-session-token"  # For ChatGPT scraping
export PERPLEXITY_COOKIES="..."                   # If needed
```

---

*Last updated: 2025-03-28*
