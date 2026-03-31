# Global Perspectives - GEO Optimization Plan

## Goal

Improve GEO (Generative Engine Optimization) rankings for globalperspective.net so AI search engines (Perplexity, ChatGPT, Groq, etc.) mention the brand more frequently.

---

## Current Status

### GEO Monitor Results (Day 1)
| Metric | Value |
|--------|-------|
| Brand queries ("Global Perspectives") | 100% ✅ |
| Product queries ("AI news aggregator") | 0% ❌ |
| Competitor queries ("Google News alternative") | 0% ❌ |

**Problem:** AI knows the brand exists, but doesn't recommend it for product-related searches.

---

## Competitive Analysis

### Main Competitors

| Competitor | What They Do | GEO Advantage |
|------------|--------------|---------------|
| **Perplexity** | AI search engine | Has content source list, crawls 100K+ sites |
| **Finvy** | AI finance news | Partnerships with Bloomberg, Reuters |
| **Arc Search** | AI browser | Apple ecosystem integration |
| **Klu** | AI news assistant | Multi-source aggregation |
| **Particle** | News AI | Media partnerships |

### Why Competitors Rank Higher

| Factor | Competitors | Global Perspectives |
|--------|-------------|---------------------|
| Content positioning | "AI investment news" clearly stated | ❌ Not clear |
| Media partnerships | Bloomberg, Reuters | ❌ None |
| Community presence | Active on Reddit, Twitter | ❌ None |
| Content marketing | Deep analysis articles | ❌ None |
| SEO optimization | Backlinks from authority sites | ❌ None |
| Schema markup | Structured data implemented | ❌ None |

---

## Technical Optimizations

### 1. Add Schema.org Structured Data 🔴 HIGH PRIORITY

Add to `<head>` section of all pages:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "NewsMediaOrganization",
  "name": "Global Perspectives",
  "alternateName": ["GlobalPerspective", "GP News"],
  "description": "AI-powered global news aggregation platform for country-level risk analysis and geopolitical intelligence",
  "url": "https://globalperspective.net",
  "keywords": "AI news aggregator, country risk analysis, geopolitical news, global intelligence, news tracker",
  "sameAs": [
    "https://twitter.com/globalperspect",
    "https://linkedin.com/company/globalperspectives"
  ],
  "publishes": {
    "@type": "DataFeed",
    "dataFeedElement": {
      "@type": "NewsArticle",
      "about": "Global news with country risk analysis"
    }
  }
}
</script>
```

**Why:** Helps AI understand what type of website this is and what content it publishes.

---

### 2. Optimize Cloudflare Cache Settings 🟡 MEDIUM

Current cache hit rate: **42%** (should be 70%+)

**Cloudflare Dashboard Settings:**

| Resource Type | Cache Duration | Status |
|---------------|-----------------|--------|
| Images (jpg, png, gif) | 30 days | Set |
| CSS, JS | 7 days | Set |
| HTML pages | 1 hour | Set |
| API responses | No cache | Set |

**Steps:**
1. Go to Cloudflare → Caching → Configuration
2. Set "Browser Cache TTL" to "Respect Existing Headers"
3. Create Page Rules for specific paths

---

### 3. Generate sitemap.xml 📋 REQUIRED

Create `sitemap.xml` with all important pages:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://globalperspective.net/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://globalperspective.net/news</loc>
    <changefreq>hourly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://globalperspective.net/analysis</loc>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

**Why:** AI crawlers use sitemaps to discover content.

---

### 4. Add OpenGraph + Twitter Cards 📋 REQUIRED

```html
<!-- OpenGraph (for Facebook, LinkedIn) -->
<meta property="og:type" content="website">
<meta property="og:title" content="Global Perspectives - AI News Intelligence">
<meta property="og:description" content="AI-powered global news aggregation for country-level risk analysis">
<meta property="og:url" content="https://globalperspective.net">
<meta property="og:image" content="https://globalperspective.net/og-image.jpg">

<!-- Twitter Cards -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Global Perspectives">
<meta name="twitter:description" content="AI news intelligence platform">
<meta name="twitter:image" content="https://globalperspective.net/og-image.jpg">
```

---

## Content Optimizations

### 5. Add FAQ Schema 📋 REQUIRED

AI engines love FAQ content because it matches common search queries.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is Global Perspectives?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Global Perspectives is an AI-powered news aggregation platform that provides country-level risk analysis and geopolitical intelligence for investors and analysts."
      }
    },
    {
      "@type": "Question", 
      "name": "How does Global Perspectives track country risk?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Our AI analyzes news from thousands of sources daily to identify emerging risks and trends affecting specific countries and regions."
      }
    },
    {
      "@type": "Question",
      "name": "Is Global Perspectives free to use?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, Global Perspectives offers a free tier for basic news tracking. Premium features include advanced risk analysis and custom alerts."
      }
    }
  ]
}
</script>
```

---

### 6. Update Homepage with Clear Value Proposition 📋 REQUIRED

**Add this content to the homepage (in English):**

```html
<section class="value-proposition">
  <h1>Global Perspectives - AI News Intelligence</h1>
  <p>
    Global Perspectives is an <strong>AI-powered global news aggregation platform</strong> 
    designed for <strong>country-level risk analysis</strong> and 
    <strong>geopolitical intelligence</strong>.
  </p>
  <p>
    We help <strong>investors, analysts, and businesses</strong> stay ahead of 
    global trends with real-time AI-curated news from thousands of sources.
  </p>
  
  <h2>Key Features:</h2>
  <ul>
    <li>AI-powered news aggregation</li>
    <li>Country risk analysis</li>
    <li>Geopolitical intelligence</li>
    <li>Real-time alerts</li>
    <li>Multi-source coverage</li>
  </ul>
  
  <h2>Use Cases:</h2>
  <ul>
    <li>Alternative to Google News for business users</li>
    <li>Investment research tool</li>
    <li>Country risk monitoring</li>
    <li>Geopolitical trend analysis</li>
  </ul>
</section>
```

**Why:** AI needs to see these keywords in your content to recommend you for related queries.

---

## Authority Building (Off-Site)

### 7. Apply to AI Content Sources 🔴 HIGH PRIORITY

**Perplexity Publisher Program:**
- URL: https://perplexity.com/publishers
- Apply to be included in Perplexity's content sources
- This directly improves GEO ranking on Perplexity

### 8. Build Social Presence 🟡 MEDIUM

| Platform | Action |
|----------|--------|
| **LinkedIn** | Create company page, post daily news insights |
| **Twitter/X** | Share daily global news summaries |
| **Reddit** | Participate in r/geopolitics, r/investing |

### 9. Get Media Mentions 🟡 MEDIUM

| Strategy | How |
|----------|-----|
| Press release | Announce new features |
| Guest posts | Write for fintech/investment blogs |
| Directory submission | AlternativeTo, Product Hunt |

---

## Priority Checklist

### Immediate (Week 1)
- [ ] **HIGH** Add Schema.org NewsMediaOrganization to `<head>`
- [ ] **HIGH** Add FAQ Schema
- [ ] **HIGH** Generate sitemap.xml
- [ ] **HIGH** Add OpenGraph/Twitter meta tags
- [ ] **HIGH** Apply to Perplexity Publisher Program
- [ ] **HIGH** Update homepage with clear value proposition and keywords

### Short-term (Week 2-4)
- [ ] **MEDIUM** Optimize Cloudflare cache settings
- [ ] **MEDIUM** Create LinkedIn company page
- [ ] **MEDIUM** Set up Twitter/X account
- [ ] **MEDIUM** Submit to Product Hunt

### Long-term (Month 2-3)
- [ ] **LOW** Get 3-5 media mentions
- [ ] **LOW** Guest post on 2-3 industry blogs
- [ ] **LOW** Build 10+ backlinks

---

## Expected Results

| Timeline | Goal |
|----------|------|
| 1-2 weeks | Product queries mention rate: 10-20% (after Schema + Perplexity application) |
| 1 month | Product queries mention rate: 30%+ |
| 3 months | Competitor queries mention rate: 20%+ |

---

## Resources

- Schema.org Validator: https://validator.schema.org/
- Google Rich Results Test: https://search.google.com/test/rich-results
- Cloudflare Cache Docs: https://developers.cloudflare.com/cache/
- Perplexity Publishers: https://perplexity.com/publishers

---

## Monitoring

Track progress at:
- GEO Dashboard: https://benben050599.github.io/gp-geo-monitor/
- Cloudflare Analytics: https://dash.cloudflare.com

Update GEO dashboard daily to measure improvement.
