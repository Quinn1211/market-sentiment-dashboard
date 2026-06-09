import requests
import json
import os
from datetime import datetime, timezone

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data.json')

SYMBOLS = {
    "US": {"name": "美股 S&P 500",  "symbol": "%5EGSPC"},
    "JP": {"name": "日股 日經225",   "symbol": "%5EN225"},
    "KR": {"name": "韓股 KOSPI",    "symbol": "%5EKS11"},
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
}

def get_trend(pct):
    if pct > 0.5:  return "up"
    if pct < -0.5: return "down"
    return "neutral"

def fetch_yahoo(encoded_symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded_symbol}?range=5d&interval=1d"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        data = r.json()
        result = data["chart"]["result"][0]
        closes = result["indicators"]["quote"][0]["close"]
        closes = [c for c in closes if c is not None]
        if len(closes) < 2:
            raise ValueError("Not enough data")
        prev, curr = closes[-2], closes[-1]
        change = curr - prev
        pct = (change / prev) * 100
        return round(curr, 2), round(change, 2), round(pct, 2)
    except Exception as e:
        print(f"[WARN] Yahoo fetch failed for {encoded_symbol}: {e}")
        return 0, 0, 0

def fetch_twse():
    """台灣證交所官方 API 抓加權指數"""
    try:
        url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_t00.tw&json=1&delay=0"
        r = requests.get(url, headers=HEADERS, timeout=15)
        data = r.json()
        info = data["msgArray"][0]
        price = float(info["z"]) if info["z"] != "-" else float(info["y"])
        prev  = float(info["y"])
        change = round(price - prev, 2)
        pct    = round((change / prev) * 100, 2)
        return round(price, 2), change, pct
    except Exception as e:
        print(f"[WARN] TWSE fetch failed: {e}")
        # fallback to Yahoo
        return fetch_yahoo("%5ETWII")

def fetch_vix():
    try:
        price, _, _ = fetch_yahoo("%5EVIX")
        return price
    except:
        return 0

def fetch_fear_greed():
    try:
        url = "https://fear-and-greed-index.p.rapidapi.com/v1/fgi"
        # fallback: use alternative.me crypto F&G as placeholder
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
        data = r.json()
        score = int(data["data"][0]["value"])
        label = data["data"][0]["value_classification"]
        return score, label
    except Exception as e:
        print(f"[WARN] Fear & Greed fetch failed: {e}")
        return 0, "N/A"

def main():
    print("Fetching market data...")
    markets = {}

    for key, info in SYMBOLS.items():
        price, change, pct = fetch_yahoo(info["symbol"])
        markets[key] = {
            "name": info["name"],
            "symbol": info["symbol"],
            "price": price, "change": change,
            "change_pct": pct, "trend": get_trend(pct),
        }

    # 台股用證交所 API
    tw_price, tw_change, tw_pct = fetch_twse()
    markets["TW"] = {
        "name": "台股 加權指數", "symbol": "^TWII",
        "price": tw_price, "change": tw_change,
        "change_pct": tw_pct, "trend": get_trend(tw_pct),
    }

    vix = fetch_vix()
    fg_score, fg_label = fetch_fear_greed()
    markets["US"]["vix"] = vix
    markets["US"]["fear_greed_index"] = fg_score
    markets["US"]["fear_greed_label"] = fg_label

    output = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "markets": markets,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Done. Data saved.")

if __name__ == "__main__":
    main()
