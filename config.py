from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data" / "raw"
OUTPUT_DIR = ROOT_DIR / "output"

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# ETFs suivis
# ---------------------------------------------------------------------------
ETFS = {
    "IE0002XZSHO1": {
        "name": "iShares MSCI World Swap PEA UCITS ETF",
        "ticker": "WPEA",
        "mic": "XPAR",
        "currency": "EUR",
    },
}

# ---------------------------------------------------------------------------
# Collecte
# ---------------------------------------------------------------------------
POLL_INTERVAL_SECONDS = 30
TIMEZONE      = "Europe/Paris"

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
EURONEXT_QUOTE_URL = (
    "https://live.euronext.com/en/ajax/getDetailedQuote/{isin}-{mic}"
)