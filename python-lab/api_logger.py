# api_logger.py — FlowCraft Base (robust fetch + JSONL logging)
import requests
import json
from datetime import datetime

# Try CoinDesk first; fallback to GitHub public API
CANDIDATE_URLS = [
    "https://api.coindesk.com/v1/bpi/currentprice.json",
    "https://api.github.com"
]

def fetch_from(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        # return None on failure (we'll try next)
        return None

def fetch_price():
    """Try known APIs; return a dict with time and price if available."""
    for url in CANDIDATE_URLS:
        data = fetch_from(url)
        if not data:
            continue
        # CoinDesk shape: has top-level 'bpi' -> USD -> rate
        if isinstance(data, dict) and "bpi" in data:
            usd_rate = data["bpi"].get("USD", {}).get("rate")
            return {"time": datetime.utcnow().isoformat(), "source": "coindesk", "usd_rate": usd_rate}
        # GitHub or other API: record some summary (safe fallback)
        if isinstance(data, dict):
            # pick a small representative field if available
            sample_keys = list(data.keys())
            sample = {k: data.get(k) for k in sample_keys[:3]}
            return {"time": datetime.utcnow().isoformat(), "source": "github_or_other", "sample": sample, "usd_rate": None}
    # if all failed
    return {"time": datetime.utcnow().isoformat(), "source": "none", "usd_rate": None}

def log_price(entry, filename="api_log.jsonl"):
    """Append fetched data into a JSONL log file."""
    with open(filename, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def main():
    entry = fetch_price()
    log_price(entry)
    print("✅ Logged record to:", entry)

if __name__ == "__main__":
    main()
