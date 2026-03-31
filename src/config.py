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

# ── ブランド直接 ──────────────────────────────────
BRAND_QUERIES = [
    "Marine Sphere 海洋デジタル化",
    "マリンスフィア 養殖",
    "marinesphere.jp",
    "Marine Sphere aquaculture",
    "Marine Sphere ICTコンサルティング",
    "マリンスフィア 水産業DX",
]

# ── 養殖・水産業 DX ───────────────────────────────
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
    "養殖 データ管理 クラウド",
    "水産業 センサー IoT 管理",
    "陸上養殖 デジタル化",
    "land-based aquaculture technology",
    "aquaculture management software Japan",
]

# ── コンサルティング・IT ──────────────────────────
CONSULTING_QUERIES = [
    "水産業 ITコンサルティング",
    "SAP 水産業 導入",
    "海洋産業 DXコンサル",
    "ICTガバナンス 水産",
    "デジタルビジネス変革 日本",
    "aquaculture IT consulting Japan",
    "fishery industry digital consulting",
    "水産業 ERP 導入",
    "水産業 業務改革 コンサル",
    "ICT導入 水産 中小企業",
    "プロジェクト管理 水産業 IT",
    "aquaculture ERP system",
    "fishery business transformation consulting",
]

# ── 海洋テック・ブルーエコノミー ──────────────────
OCEAN_TECH_QUERIES = [
    "海洋デジタルフロンティア",
    "ブルーエコノミー テクノロジー 日本",
    "海洋資源 デジタル化",
    "ocean digitization Japan",
    "blue economy technology",
    "marine tech startup Japan",
    "海洋産業 スタートアップ 日本",
    "ocean tech company Japan",
    "blue economy startup Asia",
    "海洋 クラウドサービス",
]

# ── 競合・IT 供給者比較 ───────────────────────────
# 水産・海洋 IT 分野の主要プレイヤーとの比較クエリ
COMPETITOR_QUERIES = [
    # 国内競合・関連企業との比較
    "NTTデータ 水産業 DX",
    "富士通 水産業 IoT",
    "日立 水産業 デジタル化",
    "NEC 水産業 スマート化",
    "パナソニック 養殖 IoT",
    "水産業 DX 日本 IT企業 比較",
    "養殖 IT ソリューション 比較",

    # グローバル競合
    "Aquabyte aquaculture AI",
    "Observe Technologies fish farming",
    "XpertSea aquaculture software",
    "Innovasea fish tracking",
    "aquaculture software companies comparison",
    "best aquaculture management platform",
    "aquaculture technology vendors Japan",

    # SAP / ERP 競合
    "SAP alternative water industry",
    "SAP 水産業 代替 ソリューション",
    "水産業 基幹システム クラウド",

    # クラウドファンディング・投資プラットフォーム比較
    "養殖 クラウドファンディング プラットフォーム",
    "aquaculture crowdfunding platform",
    "水産業 投資 プラットフォーム 日本",
    "production funding aquaculture network",

    # ワークログ・業務記録系
    "水産業 ワークログ 自動化",
    "universal work logger fishery",
    "養殖 作業記録 デジタル",
    "fishery work log automation",
]

# ── DNV GL / パートナー関連 ───────────────────────
PARTNER_QUERIES = [
    "DNV GL 水産業 日本",
    "DNV aquaculture Japan partner",
    "Hauge Aqua Japan",
    "ハウゲアクア 日本",
    "DNV GL maritime Japan IT partner",
]

# All queries to run
ALL_QUERIES = (
    BRAND_QUERIES
    + AQUACULTURE_QUERIES
    + CONSULTING_QUERIES
    + OCEAN_TECH_QUERIES
    + COMPETITOR_QUERIES
    + PARTNER_QUERIES
)

# Query categories for analysis
QUERY_CATEGORIES = {
    "brand": BRAND_QUERIES,
    "aquaculture": AQUACULTURE_QUERIES,
    "consulting": CONSULTING_QUERIES,
    "ocean_tech": OCEAN_TECH_QUERIES,
    "competitor": COMPETITOR_QUERIES,
    "partner": PARTNER_QUERIES,
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
