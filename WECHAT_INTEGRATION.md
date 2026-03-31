# WeChat Public Account Integration Plan

## Overview

Integrate WeChat Official Account (公众号) with Global Perspectives platform to:
- Auto-publish daily news briefs in Chinese to WeChat followers
- Drive traffic from WeChat to globalperspective.net
- Track engagement data (reads, shares, follower growth)

---

## Architecture

```
globalperspective.net (news data)
         ↓
Groq API (generate Chinese summary)
         ↓
WeChat API (publish article)
         ↓
Followers receive daily brief
         ↓
Click → globalperspective.net
```

---

## Credentials Needed

| Key | Value | Status |
|-----|-------|--------|
| `WECHAT_APPID` | TBD | ⏳ Pending registration |
| `WECHAT_APPSECRET` | TBD | ⏳ Pending registration |
| `WECHAT_TOKEN` | Set by you | ⏳ Pending |
| `GROQ_API_KEY` | Already set | ✅ Done |

---

## File Structure

```
geo-monitor/
├── src/
│   ├── wechat/
│   │   ├── __init__.py
│   │   ├── auth.py          # Access token management
│   │   ├── publisher.py     # Article publishing
│   │   ├── stats.py         # Analytics data fetching
│   │   └── translator.py    # English → Chinese summary (Groq)
│   └── main.py              # Updated to include WeChat push
├── .github/workflows/
│   └── daily.yml            # Add WeChat publish step
└── dashboard/
    └── index.html           # Add WeChat stats section
```

---

## Step 1: Auth Module (`src/wechat/auth.py`)

```python
import requests
import json
import time
from pathlib import Path

APPID = os.environ.get("WECHAT_APPID")
APPSECRET = os.environ.get("WECHAT_APPSECRET")
TOKEN_CACHE = Path("data/wechat_token.json")

def get_access_token():
    """
    Get WeChat access token (valid 2 hours, cached locally).
    """
    # Check cache
    if TOKEN_CACHE.exists():
        with open(TOKEN_CACHE) as f:
            cache = json.load(f)
        if cache["expires_at"] > time.time() + 60:
            return cache["access_token"]
    
    # Fetch new token
    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": APPID,
        "secret": APPSECRET
    }
    r = requests.get(url, params=params, timeout=15)
    data = r.json()
    
    if "access_token" not in data:
        raise Exception(f"Failed to get token: {data}")
    
    # Cache token
    TOKEN_CACHE.parent.mkdir(exist_ok=True)
    with open(TOKEN_CACHE, "w") as f:
        json.dump({
            "access_token": data["access_token"],
            "expires_at": time.time() + data["expires_in"]
        }, f)
    
    return data["access_token"]
```

---

## Step 2: Translator (`src/wechat/translator.py`)

```python
from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_chinese_summary(title_en: str, content_en: str) -> dict:
    """
    Use Groq to generate Chinese title + summary for WeChat.
    Returns: { title_cn, summary_cn, content_cn }
    """
    prompt = f"""
    You are a professional news editor. 
    Translate and summarize the following English news for Chinese WeChat readers.
    
    Original Title: {title_en}
    Original Content: {content_en[:2000]}
    
    Return JSON with:
    - title_cn: Chinese title (max 30 chars)
    - summary_cn: Chinese summary (max 120 chars, for article digest)
    - content_cn: Full Chinese article (500-800 chars)
    
    Keep it professional and engaging for business/investment audience.
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)
```

---

## Step 3: Publisher (`src/wechat/publisher.py`)

```python
import requests
from .auth import get_access_token

def upload_thumb_image(image_url: str) -> str:
    """Upload cover image to WeChat, return media_id."""
    token = get_access_token()
    
    # Download image
    img_data = requests.get(image_url).content
    
    # Upload to WeChat
    url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type=image"
    r = requests.post(url, files={"media": img_data})
    return r.json()["media_id"]


def publish_article(articles: list) -> dict:
    """
    Publish articles to WeChat followers.
    
    articles: list of dicts with keys:
        - title: Chinese title
        - thumb_media_id: cover image media_id
        - author: author name
        - digest: short summary (120 chars)
        - content: full HTML content
        - content_source_url: link to original English article
    """
    token = get_access_token()
    
    # Step 1: Upload as draft
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    payload = {"articles": articles}
    r = requests.post(url, json=payload)
    media_id = r.json()["media_id"]
    
    # Step 2: Publish draft
    url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={token}"
    r = requests.post(url, json={"media_id": media_id})
    
    return r.json()


def send_daily_brief(news_items: list):
    """
    Main function: take news items, translate, publish to WeChat.
    """
    from .translator import generate_chinese_summary
    
    articles = []
    for item in news_items[:3]:  # Max 3 articles per push
        # Generate Chinese content
        cn = generate_chinese_summary(item["title"], item["content"])
        
        articles.append({
            "title": cn["title_cn"],
            "thumb_media_id": "DEFAULT_THUMB_ID",  # Set after uploading default cover
            "author": "Global Perspectives",
            "digest": cn["summary_cn"],
            "content": f"""
                <p>{cn['content_cn']}</p>
                <p><a href="{item['url']}">Read full article in English →</a></p>
            """,
            "content_source_url": item["url"],
            "need_open_comment": 0
        })
    
    return publish_article(articles)
```

---

## Step 4: Stats (`src/wechat/stats.py`)

```python
import requests
from .auth import get_access_token
from datetime import datetime, timedelta

def get_article_stats(days=7) -> dict:
    """Fetch article read/share stats from WeChat."""
    token = get_access_token()
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    url = f"https://api.weixin.qq.com/datacube/getarticlesummary?access_token={token}"
    payload = {
        "begin_date": start_date,
        "end_date": end_date
    }
    
    r = requests.post(url, json=payload)
    return r.json()
    # Returns: int_page_read_count, ori_page_read_count, share_count, etc.


def get_follower_stats(days=7) -> dict:
    """Fetch follower growth stats."""
    token = get_access_token()
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    url = f"https://api.weixin.qq.com/datacube/getusersummary?access_token={token}"
    payload = {
        "begin_date": start_date,
        "end_date": end_date
    }
    
    r = requests.post(url, json=payload)
    return r.json()
    # Returns: new_user, cancel_user, cumulate_user per day
```

---

## Step 5: GitHub Actions Update

Add to `.github/workflows/daily.yml`:

```yaml
- name: Publish to WeChat
  env:
    WECHAT_APPID: ${{ secrets.WECHAT_APPID }}
    WECHAT_APPSECRET: ${{ secrets.WECHAT_APPSECRET }}
    GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
  run: |
    python3 src/wechat/publisher.py
```

Add GitHub Secrets:
- `WECHAT_APPID` → your AppID
- `WECHAT_APPSECRET` → your AppSecret

---

## Step 6: Dashboard Update

Add WeChat metrics to `dashboard/data.json`:

```json
{
  "wechat": {
    "followers": 0,
    "articles_published": 0,
    "total_reads": 0,
    "avg_read_rate": 0,
    "daily_trend": []
  }
}
```

---

## Content Strategy

### Daily Brief Format (Chinese)

```
标题: 【全球简报】今日国际风险速览 - 3月30日

摘要: 今日重点：美联储政策动向、中东局势更新、亚太市场分析

正文:
📌 [新闻标题中文版]
[120字中文摘要]
→ 阅读英文原文

📌 [新闻标题中文版]  
[120字中文摘要]
→ 阅读英文原文

---
🌐 更多分析请访问 globalperspective.net
```

---

## Language Strategy

| Content | Language | Reason |
|---------|----------|--------|
| WeChat article title | Chinese | Lower barrier for Chinese readers |
| WeChat article body | Chinese | Engagement |
| "Read more" link | → English site | Drive traffic to globalperspective.net |
| Website | English | Keep original positioning |

---

## TODO Checklist

- [ ] Register WeChat Official Account at https://mp.weixin.qq.com
- [ ] Get AppID and AppSecret from 设置 → 基本配置
- [ ] Add WECHAT_APPID to GitHub Secrets
- [ ] Add WECHAT_APPSECRET to GitHub Secrets
- [ ] Upload default cover image, get thumb_media_id
- [ ] Test auth.py locally
- [ ] Test translator.py (Chinese summary generation)
- [ ] Test publisher.py with one article
- [ ] Add WeChat stats to dashboard
- [ ] Set up daily auto-publish in GitHub Actions

---

## API Reference

| API | Endpoint | Docs |
|-----|----------|------|
| Get Token | `GET /cgi-bin/token` | [Link](https://developers.weixin.qq.com/doc/offiaccount/Basic_Information/Get_access_token.html) |
| Upload Draft | `POST /cgi-bin/draft/add` | [Link](https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Add_draft.html) |
| Publish | `POST /cgi-bin/freepublish/submit` | [Link](https://developers.weixin.qq.com/doc/offiaccount/Publish/Publish.html) |
| Article Stats | `POST /datacube/getarticlesummary` | [Link](https://developers.weixin.qq.com/doc/offiaccount/Analytics/Article_summary.html) |
| Follower Stats | `POST /datacube/getusersummary` | [Link](https://developers.weixin.qq.com/doc/offiaccount/Analytics/User_Analysis_Data_Interface.html) |

---

## Notes

- WeChat access token expires every 2 hours → always use cached token
- Subscription accounts (订阅号) can push **1 article per day**
- Article content must be HTML format
- Images must be uploaded to WeChat CDN first (can't use external URLs)
- Stats API only available after account verification (认证)
