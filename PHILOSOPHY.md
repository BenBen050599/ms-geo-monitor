# GEO Monitor — Philosophy

## 🎯 Mission

Build a **free, open-source, zero-cost** daily GEO (Generative Engine Optimization) monitoring tool that helps website owners track whether AI search engines recommend their brand.

## 🧠 Core Beliefs

1. **AI search is the new SEO** — Users increasingly rely on AI answers. If AI doesn't mention you, you're invisible.
2. **Monitoring should be free** — GEO tools shouldn't cost money. Scraping + open-source tech is enough.
3. **Data over intuition** — Stop guessing whether AI recommends you. Measure it.
4. **Simplicity wins** — A tool that works today is better than a perfect tool shipped never.
5. **Transparency** — Every raw AI response should be saved. Don't just track numbers, track context.

## 🎯 Goals

### Primary
- Track daily whether AI engines mention `globalperspective.net`
- Identify which queries/keywords trigger brand mentions
- Monitor trends over time (30-day, 90-day, 1-year)
- Compare across multiple AI engines

### Secondary
- Track competitor mentions for the same queries
- Analyze how AI describes the brand (sentiment/context)
- Detect AI citation links to the website
- Alert on significant changes in mention rates

### Non-Goals
- ❌ Manipulating or gaming AI search results (ethical only)
- ❌ Paid API usage — must run on free infrastructure
- ❌ Real-time monitoring — daily snapshots are sufficient
- ❌ Enterprise dashboards — simple HTML reports + data files

## 📏 Principles

| Principle | Description |
|-----------|-------------|
| **Zero Cost** | Run entirely on GitHub Actions free tier. No paid APIs. |
| **Minimal Dependencies** | Python + Playwright. Nothing more. |
| **Data-First** | Save every raw response. Analysis can change, data shouldn't. |
| **Deterministic Queries** | Same questions every day. Consistency enables trend tracking. |
| **Multi-Engine** | Monitor 3+ AI engines from day one. |
| **Reproducible** | Anyone should be able to fork and run for their own brand. |
| **Non-Invasive** | We only read AI search results. We don't spam, click, or interact. |

## 🔍 What We Monitor

For each query × each engine × each day:

| Metric | Type | Description |
|--------|------|-------------|
| `mentioned` | bool | Is the brand name in the AI response? |
| `cited` | bool | Is the brand URL in the AI response? |
| `position` | string | Where: top / middle / bottom / not_found |
| `raw_response` | text | Full AI response (for analysis) |
| `response_length` | int | Length of AI response |
| `citation_urls` | list | All URLs cited by the AI |
| `competitor_mentions` | list | Other brands mentioned in the same response |

## 🤖 AI Engines (Priority Order)

1. **Perplexity** — No login required, easy to scrape
2. **DuckDuckGo AI Chat** — Free, no anti-bot
3. **Google AI Overview** — Most users, harder to scrape
4. **ChatGPT** — Requires login, but valuable data
5. **Claude** — Growing market share

## ⏱️ Frequency

- **Daily**: Run at 16:00 CST (08:00 UTC)
- **Per query**: 3 attempts (to account for AI non-determinism)
- **Total queries/day**: ~6 questions × 3 attempts × 3 engines = ~54 requests

## 📊 Success Metrics

- [ ] The tool runs automatically every day for 30 consecutive days
- [ ] We can see trend data on a simple HTML page
- [ ] We detect when mention rate changes significantly
- [ ] The project is reproducible — anyone can fork and use for their brand

---

*"If AI doesn't mention you, you don't exist."*
