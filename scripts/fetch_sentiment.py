import yfinance as yf
import requests
import json
import os
from datetime import datetime, timezone

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'data.json')

SYMBOLS = {
    "US": {"name": "美股 S&P 500", "symbol": "^GSPC"},
    "TW": {"name": "台股 加權指數", "symbol": "^TWII"},
    "JP": {"name": "日股 日經225", "symbol": "^N225"},
    "KR": {"name": "韓股 KOSPI", "symbol": "^KS11"},
}

def get_trend(change_pct):
    if change_pct > 0.5:
        return "up"
    elif change_pct < -0.5:
        return "down"
    return "neutral"

def fetch_market_data():
    markets = {}
    for key, info in SYMBOLS.items():
        try:
            ticker = yf.Ticker(info["symbol"])
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist["Close"].iloc[-2]
                current = hist["Close"].iloc[-1]
            elif len(hist) == 1:
                prev_close = hist["Open"].iloc[-1]
                current = hist["Close"].iloc[-1]
            else:
                raise ValueError("No data")

            change = current - prev_close
            change_pct = (change / prev_close) * 100

            markets[key] = {
                "name": info["name"],
                "symbol": info["symbol"],
                "price": round(float(current), 2),
                "change": round(float(change), 2),
                "change_pct": round(float(change_pct), 2),
                "trend": get_trend(change_pct),
            }
        except Exception as e:
            print(f"[WARN] {key} fetch failed: {e}")
            markets[key] = {
                "name": info["name"],
                "symbol": info["symbol"],
                "price": 0, "change": 0, "change_pct": 0, "trend": "neutral"
            }
    return markets

def fetch_fear_greed():
    """CNN Fear & Greed Index（免費，免 API Key）"""
    try:
        url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        score = int(data["fear_and_greed"]["score"])
        rating = data["fear_and_greed"]["rating"]
        return score, rating
    except Exception as e:
        print(f"[WARN] Fear & Greed fetch failed: {e}")
        return 0, "N/A"

def fetch_vix():
    try:
        ticker = yf.Ticker("^VIX")
        hist = ticker.history(period="1d")
        if not hist.empty:
            return round(float(hist["Close"].iloc[-1]), 2)
    except Exception as e:
        print(f"[WARN] VIX fetch failed: {e}")
    return 0

def main():
    print("Fetching market data...")
    markets = fetch_market_data()

    fg_score, fg_label = fetch_fear_greed()
    vix = fetch_vix()

    if "US" in markets:
        markets["US"]["vix"] = vix
        markets["US"]["fear_greed_index"] = fg_score
        markets["US"]["fear_greed_label"] = fg_label

    output = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "markets": markets
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Done. Data saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
