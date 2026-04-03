import pandas as pd
from pathlib import Path
from config import DATA_DIR, OUTPUT_DIR, ETFS

# ---------------------------------------------------------------------------
# Chargement
# ---------------------------------------------------------------------------

def load_raw(isin: str) -> pd.DataFrame:
    files = sorted(DATA_DIR.glob(f"{isin}_*.csv"))
    if not files:
        raise FileNotFoundError(f"Aucun fichier CSV trouvé pour {isin}")
    
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    
    df["timestamp_euronext"] = pd.to_datetime(df["timestamp_euronext"], utc=True)
    df["timestamp_local"] = pd.to_datetime(df["timestamp_local"], utc=True)
    
    # Dédoublonnage sur timestamp_euronext — garder la première occurrence
    df = df.drop_duplicates(subset="timestamp_euronext")
    df = df.sort_values("timestamp_euronext").reset_index(drop=True)
    
    return df


# ---------------------------------------------------------------------------
# Métriques agrégées
# ---------------------------------------------------------------------------

def compute_hourly_stats(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["hour"] = df["timestamp_euronext"].dt.hour
    
    stats = df.groupby("hour").agg(
        spread_pct_mean=("spread_pct", "mean"),
        spread_pct_min=("spread_pct", "min"),
        spread_pct_max=("spread_pct", "max"),
        spread_pct_std=("spread_pct", "std"),
        n_observations=("spread_pct", "count"),
    ).reset_index()
    
    return stats


def compute_session_stats(df: pd.DataFrame) -> dict:
    return {
        "spread_pct_mean": round(df["spread_pct"].mean(), 4),
        "spread_pct_min": round(df["spread_pct"].min(), 4),
        "spread_pct_max": round(df["spread_pct"].max(), 4),
        "spread_pct_std": round(df["spread_pct"].std(), 4),
        "spread_abs_mean": round(df["spread_abs"].mean(), 6),
        "n_observations": len(df),
        "date_start": str(df["timestamp_euronext"].min()),
        "date_end": str(df["timestamp_euronext"].max()),
    }


def compute_daily_stats(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = df["timestamp_euronext"].dt.date
    
    stats = df.groupby("date").agg(
        spread_pct_mean=("spread_pct", "mean"),
        spread_pct_min=("spread_pct", "min"),
        spread_pct_max=("spread_pct", "max"),
        n_observations=("spread_pct", "count"),
    ).reset_index()
    
    return stats


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def save_stats(isin: str) -> dict:
    df = load_raw(isin)
    
    session = compute_session_stats(df)
    hourly = compute_hourly_stats(df)
    daily = compute_daily_stats(df)
    
    hourly.to_csv(OUTPUT_DIR / f"{isin}_hourly_stats.csv", index=False)
    daily.to_csv(OUTPUT_DIR / f"{isin}_daily_stats.csv", index=False)
    
    print(f"=== Stats session {isin} ===")
    for k, v in session.items():
        print(f"  {k}: {v}")
    
    print(f"\n=== Stats horaires ===")
    print(hourly.to_string(index=False))
    
    return session


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    for isin in ETFS:
        save_stats(isin)