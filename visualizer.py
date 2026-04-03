import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import OUTPUT_DIR, ETFS
from processor import load_raw, compute_hourly_stats

# ---------------------------------------------------------------------------
# Style global
# ---------------------------------------------------------------------------

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 150
plt.rcParams["figure.figsize"] = (12, 5)


# ---------------------------------------------------------------------------
# Plot 1 — Spread intraday
# ---------------------------------------------------------------------------

def plot_intraday_spread(df: pd.DataFrame, isin: str) -> None:
    fig, ax = plt.subplots()

    ax.plot(
        df["timestamp_euronext"],
        df["spread_pct"],
        linewidth=1.2,
        color="steelblue",
    )

    ax.axhline(
        df["spread_pct"].mean(),
        color="tomato",
        linestyle="--",
        linewidth=1,
        label=f"Moyenne : {df['spread_pct'].mean():.4f}%",
    )

    ax.set_title(f"Spread bid/ask intraday — {isin}")
    ax.set_xlabel("Heure")
    ax.set_ylabel("Spread (%)")
    ax.legend()
    fig.autofmt_xdate()

    path = OUTPUT_DIR / f"{isin}_intraday_spread.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {path}")


# ---------------------------------------------------------------------------
# Plot 2 — Distribution du spread
# ---------------------------------------------------------------------------

def plot_spread_distribution(df: pd.DataFrame, isin: str) -> None:
    fig, ax = plt.subplots()

    sns.histplot(
        df["spread_pct"],
        kde=True,
        bins=30,
        color="steelblue",
        ax=ax,
    )

    ax.axvline(
        df["spread_pct"].mean(),
        color="tomato",
        linestyle="--",
        linewidth=1,
        label=f"Moyenne : {df['spread_pct'].mean():.4f}%",
    )

    ax.set_title(f"Distribution du spread bid/ask — {isin}")
    ax.set_xlabel("Spread (%)")
    ax.set_ylabel("Fréquence")
    ax.legend()

    path = OUTPUT_DIR / f"{isin}_spread_distribution.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {path}")


# ---------------------------------------------------------------------------
# Plot 3 — Spread moyen par heure
# ---------------------------------------------------------------------------

def plot_hourly_spread(df: pd.DataFrame, isin: str) -> None:
    hourly = compute_hourly_stats(df)

    fig, ax = plt.subplots()

    sns.barplot(
        data=hourly,
        x="hour",
        y="spread_pct_mean",
        color="steelblue",
        ax=ax,
    )

    ax.errorbar(
        x=range(len(hourly)),
        y=hourly["spread_pct_mean"],
        yerr=hourly["spread_pct_std"].fillna(0),
        fmt="none",
        color="tomato",
        capsize=3,
        linewidth=1,
    )

    ax.set_title(f"Spread moyen par heure — {isin}")
    ax.set_xlabel("Heure")
    ax.set_ylabel("Spread moyen (%)")

    path = OUTPUT_DIR / f"{isin}_hourly_spread.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(isin: str) -> None:
    df = load_raw(isin)
    plot_intraday_spread(df, isin)
    plot_spread_distribution(df, isin)
    plot_hourly_spread(df, isin)


if __name__ == "__main__":
    for isin in ETFS:
        run(isin)