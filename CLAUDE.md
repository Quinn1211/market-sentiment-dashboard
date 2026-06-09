# Project: Global Market Sentiment Dashboard (美/台/日/韓)
## 專案概述
本專案旨在建立一個輕量化、響應式（Responsive）的單網頁 HTML 儀表板，用於追蹤並視覺化全球四大市場（美股、台股、日股、韓股）的每日市場情緒與關鍵指標。
此網頁將託管於 GitHub Pages，支援電腦 Safari 瀏覽與手機 iOS/Android 加入主畫面（Web App 體驗）。
## 核心功能需求
1. **多市場情緒看板**：涵蓋美股、台股、日股、韓股，顯示當日漲跌、技術指標或情緒狀態（如：貪婪與恐懼、多空排列比例、VIX 等）。
2. **自動數據更新機制**：
   - 方案 A（優先）：利用 **GitHub Actions** 每天定時執行 Python/Node.js 爬蟲指令碼，抓取最新數據，產生靜態 `data.json` 並自動 Commit 回推。
   - 方案 B：網頁端前端 JavaScript 透過免費且免金鑰的 API（如 Yahoo Finance API 轉接、Fear and Greed API）在載入時即時抓取。
3. **跨平台極致體驗**：
   - 支援 PWA（Progressive Web App）基本設定（Manifest.json, Apple Touch Icon），使其可完美「加入主畫面」全螢幕開啟。
   - 採用 Clean & Dark Mode（深色模式）優先的 UI 設計，適合手機快速瀏覽。
## 技術堆疊
- **前端 UI**：單一 `index.html` + Tailwind CSS (CDN) + Lucide Icons (CDN)
- **資料視覺化**：Chart.js 或 ApexCharts (CDN)
- **自動化/資料端**：GitHub Actions + Python (yfinance, requests) 產生 `data.json`
## 專案結構
```text
├── .github/
│   └── workflows/
│       └── update_data.yml    # 每天定時執行爬蟲與更新的自動化腳本
├── assets/
│   └── icon.png               # 手機主畫面圖示 (192x192 & 512x512)
├── scripts/
│   └── fetch_sentiment.py     # 抓取美台日韓市場數據的 Python 腳本
├── index.html                 # 儀表板前端核心網頁
├── manifest.json              # 讓手機可以辨識為 App 的設定檔
└── data.json                  # 爬蟲產生的最新市場數據（由 Actions 自動更新）
```
