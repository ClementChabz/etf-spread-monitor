import time
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

from config import (
    ETFS,
    POLL_INTERVAL_SECONDS,
    SESSION_START,
    SESSION_END,
    TIMEZONE,
    EURONEXT_QUOTE_URL,
    DATA_DIR,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_market_open() -> bool:
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    start = now.replace(
        hour=int(SESSION_START.split(":")[0]),
        minute=int(SESSION_START.split(":")[1]),
        second=0, microsecond=0
    )
    end = now.replace(
        hour=int(SESSION_END.split(":")[0]),
        minute=int(SESSION_END.split(":")[1]),
        second=0, microsecond=0
    )
    return start <= now <= end and now.weekday() < 5


def fetch_quote(isin: str, mic: str):
    url = EURONEXT_QUOTE_URL.format(isin=isin, mic=mic)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Referer": "https://live.euronext.com/",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Requête échouée : {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Last price
    last_tag = soup.find(id="header-instrument-price")
    last = float(last_tag.text.strip()) if last_tag else None

    # Bid / Ask — dans les <h5> du bloc head_detail_bottom
    h5_tags = soup.select("div.head_detail_bottom h5")
    bid, ask = None, None
    for h5 in h5_tags:
        label = h5.find("span", class_="data-12")
        value = h5.find("span", class_=lambda c: c != "data-12" if c else True)
        if label and value:
            text = label.text.strip().lower()
            try:
                val = float(value.text.strip())
            except ValueError:
                continue
            if "bid" in text:
                bid = val
            elif "ask" in text:
                val = float(value.text.strip())
                ask = val

    if bid is None or ask is None:
        print("[WARN] Bid/Ask non trouvés dans la réponse")
        return None

    midprice = (bid + ask) / 2
    spread_abs = round(ask - bid, 6)
    spread_pct = round((ask - bid) / midprice * 100, 4)

    tz = pytz.timezone(TIMEZONE)
    timestamp = datetime.now(tz).isoformat()

    return {
        "timestamp": timestamp,
        "isin": isin,
        "bid": bid,
        "ask": ask,
        "last": last,
        "midprice": round(midprice, 6),
        "spread_abs": spread_abs,
        "spread_pct": spread_pct,
    }


def get_csv_path(isin: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    return DATA_DIR / f"{isin}_{today}.csv"


def write_row(path, row: dict) -> None:
    file_exists = path.exists()
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run():
    print("=== ETF Spread Monitor démarré ===")
    while True:
        if not is_market_open():
            print("[INFO] Marché fermé, attente...")
            time.sleep(60)
            continue

        for isin, meta in ETFS.items():
            quote = fetch_quote(isin, meta["mic"])
            if quote:
                path = get_csv_path(isin)
                write_row(path, quote)
                print(
                    f"[{quote['timestamp']}] "
                    f"bid={quote['bid']} ask={quote['ask']} "
                    f"spread={quote['spread_pct']}%"
                )

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()