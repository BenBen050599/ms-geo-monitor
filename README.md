# Marine Sphere GEO Monitor 🌊

AI 検索エンジンにおける **[Marine Sphere](https://marinesphere.jp/)** のブランド露出を自動追跡するツール。

## 概要

ChatGPT・Perplexity・Gemini などの AI 検索エンジンが「養殖デジタル化」「水産業 DX」「海洋テック」などのクエリに回答する際、Marine Sphere が言及・引用されているかを毎日自動計測します。

## 監視対象クエリ（35件）

| カテゴリ | 例 |
|---|---|
| ブランド直接 | `Marine Sphere 海洋デジタル化`, `マリンスフィア 養殖` |
| 養殖・水産 DX | `養殖業 デジタル化 日本`, `スマート養殖 IoT`, `aquaculture digitization Japan` |
| コンサルティング | `水産業 ITコンサルティング`, `SAP 水産業 導入` |
| 海洋テック | `海洋デジタルフロンティア`, `blue economy technology` |
| 競合比較 | `養殖 クラウドファンディング プラットフォーム` |

## ダッシュボード

📊 **[Live Dashboard](https://benben050599.github.io/ms-geo-monitor/)**

## 仕組み

```
GitHub Actions (毎日 09:00 JST)
    ↓
Groq API (llama-3.3-70b) に各クエリを投げる
    ↓
Marine Sphere の言及・URL引用を検出
    ↓
SQLite に保存 → dashboard/data.json 更新
    ↓
GitHub Pages に自動デプロイ
```

## セットアップ

```bash
git clone https://github.com/BenBen050599/ms-geo-monitor
cd ms-geo-monitor
pip install -r requirements.txt

# .env に GROQ_API_KEY を設定
export GROQ_API_KEY=your_key_here

python -m src.main
python -m src.report
```

## GitHub Secrets

| Secret | 説明 |
|---|---|
| `GROQ_API_KEY` | Groq API キー（無料）|

## ライセンス

MIT
