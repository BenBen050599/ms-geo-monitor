"""
Cloudflare GraphQL Analytics API client
获取 Global Perspectives 的实时分析数据
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

API_TOKEN = "cfut_p5CxD36LyxCBPGTNEXf8QEUlDx9BRN1rz5vNeeX94c6cb85b"
ZONE_ID = "6d4c0f4dc951584468d1df02f4161d3b"
GRAPHQL_URL = "https://api.cloudflare.com/client/v4/graphql"


def get_headers():
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }


def query_graphql(query):
    """执行 GraphQL 查询"""
    payload = {"query": query}
    r = requests.post(GRAPHQL_URL, json=payload, headers=get_headers(), timeout=30)
    return r.json()


def get_http_requests_analytics(days=1):
    """获取 HTTP 请求分析"""
    since = (datetime.now() - timedelta(days=days)).isoformat() + "Z"
    until = datetime.now().isoformat() + "Z"
    
    query = f"""
    query {{
      viewer {{
        zones(filter: {{zoneTag: "{ZONE_ID}"}}) {{
          httpRequests1dGroups(
            limit: 100
            filter: {{
              datetime_geq: "{since}"
              datetime_lt: "{until}"
            }}
          ) {{
            dimensions {{
              date
            }}
            sum {{
              requests
              bytes
              cachedBytes
              pageViews
              threats
            }}
            avg {{
              sslTLSVersion
              sslTLSProtocol
            }}
          }}
        }}
      }}
    }}
    """
    
    return query_graphql(query)


def get_bot_analytics(days=7):
    """获取 Bot 流量分析"""
    since = (datetime.now() - timedelta(days=days)).isoformat() + "Z"
    until = datetime.now().isoformat() + "Z"
    
    query = f"""
    query {{
      viewer {{
        zones(filter: {{zoneTag: "{ZONE_ID}"}}) {{
          httpRequests1dGroups(
            limit: 100
            filter: {{
              datetime_geq: "{since}"
              datetime_lt: "{until}"
            }}
          ) {{
            dimensions {{
              date
              botManagementVerifiedBotCategory
            }}
            sum {{
              requests
              bytes
            }}
          }}
        }}
      }}
    }}
    """
    
    return query_graphql(query)


def get_country_analytics(days=1):
    """获取按国家分布的流量"""
    since = (datetime.now() - timedelta(days=days)).isoformat() + "Z"
    until = datetime.now().isoformat() + "Z"
    
    query = f"""
    query {{
      viewer {{
        zones(filter: {{zoneTag: "{ZONE_ID}"}}) {{
          httpRequests1dGroups(
            limit: 100
            filter: {{
              datetime_geq: "{since}"
              datetime_lt: "{until}"
            }}
          ) {{
            dimensions {{
              date
              clientCountryName
            }}
            sum {{
              requests
              bytes
              pageViews
            }}
          }}
        }}
      }}
    }}
    """
    
    return query_graphql(query)


def get_cache_analytics(days=1):
    """获取缓存分析"""
    since = (datetime.now() - timedelta(days=days)).isoformat() + "Z"
    until = datetime.now().isoformat() + "Z"
    
    query = f"""
    query {{
      viewer {{
        zones(filter: {{zoneTag: "{ZONE_ID}"}}) {{
          httpRequests1dGroups(
            limit: 100
            filter: {{
              datetime_geq: "{since}"
              datetime_lt: "{until}"
            }}
          ) {{
            dimensions {{
              date
              cacheStatus
            }}
            sum {{
              requests
              bytes
              cachedBytes
            }}
          }}
        }}
      }}
    }}
    """
    
    return query_graphql(query)


def get_threat_analytics(days=7):
    """获取威胁分析"""
    since = (datetime.now() - timedelta(days=days)).isoformat() + "Z"
    until = datetime.now().isoformat() + "Z"
    
    query = f"""
    query {{
      viewer {{
        zones(filter: {{zoneTag: "{ZONE_ID}"}}) {{
          httpRequests1dGroups(
            limit: 100
            filter: {{
              datetime_geq: "{since}"
              datetime_lt: "{until}"
            }}
          ) {{
            dimensions {{
              date
              threatPathingThreatType
            }}
            sum {{
              threats
              requests
            }}
          }}
        }}
      }}
    }}
    """
    
    return query_graphql(query)


def save_analytics(data, filename=None):
    """保存分析数据"""
    if not filename:
        filename = f"cloudflare_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    output_dir = Path(__file__).parent.parent / "data" / "cloudflare"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = output_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved to {filepath}")
    return filepath


def print_summary(data):
    """打印数据摘要"""
    if data.get("errors"):
        print(f"❌ Error: {data['errors']}")
        return
    
    try:
        zones = data["data"]["viewer"]["zones"]
        if not zones:
            print("❌ No zone data found")
            return
        
        groups = zones[0]["httpRequests1dGroups"]
        
        print("\n📊 Cloudflare Analytics Summary")
        print("=" * 60)
        
        total_requests = 0
        total_bytes = 0
        total_cached = 0
        total_threats = 0
        
        for group in groups:
            total_requests += group["sum"]["requests"]
            total_bytes += group["sum"]["bytes"]
            total_cached += group["sum"]["cachedBytes"]
            total_threats += group["sum"]["threats"]
        
        print(f"\n📈 Total Requests: {total_requests:,}")
        print(f"📦 Total Bandwidth: {total_bytes / 1e9:.2f} GB")
        print(f"💾 Cached Bytes: {total_cached / 1e9:.2f} GB")
        print(f"🛡️  Total Threats Blocked: {total_threats:,}")
        
        # 缓存命中率
        if total_bytes > 0:
            cache_hit_rate = (total_cached / total_bytes) * 100
            print(f"\n⚡ Cache Hit Rate: {cache_hit_rate:.1f}%")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"❌ Error parsing response: {e}")
        print(f"Response: {json.dumps(data, indent=2)}")


if __name__ == "__main__":
    print("🔍 Fetching Cloudflare analytics via GraphQL...")
    
    # 获取 HTTP 请求分析
    print("\n1️⃣  HTTP Requests Analytics...")
    data = get_http_requests_analytics(days=1)
    print_summary(data)
    save_analytics(data, "http_requests.json")
    
    # 获取国家分布
    print("\n2️⃣  Country Analytics...")
    data = get_country_analytics(days=1)
    if not data.get("errors"):
        groups = data["data"]["viewer"]["zones"][0]["httpRequests1dGroups"]
        countries = {}
        for group in groups:
            country = group["dimensions"]["clientCountryName"]
            if country:
                if country not in countries:
                    countries[country] = {"requests": 0, "bytes": 0}
                countries[country]["requests"] += group["sum"]["requests"]
                countries[country]["bytes"] += group["sum"]["bytes"]
        
        print("\n🌍 Top Countries:")
        for country, stats in sorted(countries.items(), key=lambda x: x[1]["requests"], reverse=True)[:10]:
            print(f"  {country}: {stats['requests']:,} requests, {stats['bytes']/1e9:.2f} GB")
    
    # 获取缓存分析
    print("\n3️⃣  Cache Analytics...")
    data = get_cache_analytics(days=1)
    save_analytics(data, "cache_analytics.json")
    
    # 获取威胁分析
    print("\n4️⃣  Threat Analytics...")
    data = get_threat_analytics(days=7)
    save_analytics(data, "threat_analytics.json")
    
    print("\n✅ All analytics fetched!")
