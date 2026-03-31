"""
Configuration for Marine Sphere GEO Monitor
marinesphere.jp — 海洋デジタル化・水産業DX・ICTコンサルティング
"""

# Brand to monitor
BRAND = "marinesphere.jp"
BRAND_ALIASES = [
    "Marine Sphere",
    "マリンスフィア",
    "Marine Sphere Co., Ltd.",
    "マリンスフィア株式会社",
]

# Patterns to check for citations
CITATION_PATTERNS = [
    f"https://{BRAND}",
    f"http://{BRAND}",
    BRAND,
    "marinesphere",
    "マリンスフィア",
]

# ============ QUERIES ============

# Brand queries (直接ブランド検索)
BRAND_QUERIES = [
    "Marine Sphere 海洋デジタル化",
    "マリンスフィア 養殖",
    "marinesphere.jp",
    "Marine Sphere aquaculture",
]

# 養殖・水産業 DX クエリ
AQUACULTURE_QUERIES = [
    "養殖業 デジタル化 日本",
    "水産業 DX ソリューション",
    "スマート養殖 IoT",
    "養殖 ICT 導入",
    "水産テック 日本企業",
    "aquaculture digitization Japan",
    "smart aquaculture technology",
    "aquaculture IoT platform",
    "fish farming digital transformation",
    "parametric aquaculture",
]

# コンサルティング・IT クエリ
CONSULTING_QUERIES = [
    "水産業 ITコンサルティング",
    "SAP 水産業 導入",
    "海洋産業 DXコンサル",
    "ICTガバナンス 水産",
    "デジタルビジネス変革 日本",
    "aquaculture IT consulting Japan",
    "fishery industry digital consulting",
]

# 海洋テック・ブルーエコノミー クエリ
OCEAN_TECH_QUERIES = [
    "海洋デジタルフロンティア",
    "ブルーエコノミー テクノロジー 日本",
    "海洋資源 デジタル化",
    "ocean digitization Japan",
    "blue economy technology",
    "marine tech startup Japan",
]

# 競合・カテゴリ クエリ
COMPETITOR_QUERIES = [
    "養殖 クラウドファンディング プラットフォーム",
    "水産業 ワークログ 自動化",
    "aquaculture crowdfunding platform",
    "universal work logger fishery",
]

# All queries to run
ALL_QUERIES = (
    BRAND_QUERIES
    + AQUACULTURE_QUERIES
    + CONSULTING_QUERIES
    + OCEAN_TECH_QUERIES
    + COMPETITOR_QUERIES
)

# Query categories for analysis
QUERY_CATEGORIES = {
    "brand": BRAND_QUERIES,
    "aquaculture": AQUACULTURE_QUERIES,
    "consulting": CONSULTING_QUERIES,
    "ocean_tech": OCEAN_TECH_QUERIES,
    "competitor": COMPETITOR_QUERIES,
}

# ============ ENGINES ============

ENGINES = ["groq"]

ATTEMPTS_PER_QUERY = 2

# ============ SETTINGS ============

DATA_DIR = "data"
RAW_RESPONSES_DIR = f"{DATA_DIR}/raw_responses"
DB_FILE = f"{DATA_DIR}/results.db"
DASHBOARD_FILE = "dashboard/index.html"
SCRAPE_TIMEOUT = 90
