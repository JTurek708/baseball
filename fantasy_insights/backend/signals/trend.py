"""
signals/trend.py
Detects players whose underlying metrics are shifting between a recent window
and a baseline. Two comparisons run in parallel:
  - 15-day window vs. season-to-date baseline
  - 15-day window vs. last-30-days baseline
A player flagged by either comparison surfaces; flagged by both = stronger signal.
"""
from datetime import date
import pandas as pd
from backend.data_sources import statcast
from backend.config import (
    TREND_RECENT_DAYS, TREND_BASELINE_RECENT_DAYS,
    TREND_HITTER_BARREL, TREND_HITTER_HH, TREND_HITTER_K, TREND_HITTER_BB,
    TREND_HITTER_XWOBA_CON,
    TREND_PITCHER_K, TREND_PITCHER_BB, TREND_PITCHER_WHIFF,
    TREND_PITCHER_CSW, TREND_PITCHER_VELO,
    TRENDS_LIST_SIZE,
)

# Season start — used for the season baseline. Tweak per year.
SEASON_START = "2026-03-27"


# ── Hitter metrics ────────────────────────────────────────────────────────────

# (metric, threshold, direction_for_buy, label)
# direction_for_buy: +1 means rising = good (e.g. barrel%); -1 means rising = bad (e.g. K%)
HITTER_METRICS = [
    ("barrel_pct",   TREND_HITTER_BARREL,    +1, "Barrel%"),
    ("hard_hit_pct", TREND_HITTER_HH,        +1, "HH%"),
    ("xwoba_con",    TREND_HITTER_XWOBA_CON, +1, "xwOBA/con"),
    ("k_pct",        TREND_HITTER_K,         -1, "K%"),
    ("bb_pct",       TREND_HITTER_BB,        +1, "BB%"),
]

PITCHER_METRICS = [
    ("whiff_pct", TREND_PITCHER_WHIFF, +1, "Whiff%"),
    ("csw_pct",   TREND_PITCHER_CSW,   +1, "CSW%"),
    ("k_pct",     TREND_PITCHER_K,     +1, "K%"),
    ("bb_pct",    TREND_PITCHER_BB,    -1, "BB%"),
    ("avg_velo",  TREND_PITCHER_VELO,  +1, "Velo"),
]


# ── Core comparison ───────────────────────────────────────────────────────────

def _compare_windows(
    recent: pd.DataFrame,
    baseline: pd.DataFrame,
    id_col: str,
    metrics: list,
    baseline_label: str,
    sample_col: str,
) -> list[dict]:
    """Return one record per (player, metric) where |delta| crosses the threshold.
    Each record carries direction, magnitude, the baseline_label, and prose reasoning."""
    if recent.empty or baseline.empty:
        return []

    merged = recent.merge(
        baseline, on=id_col, suffixes=("_r", "_b"), how="inner"
    )

    signals = []
    for col, threshold, sign, label in metrics:
        r_col, b_col = f"{col}_r", f"{col}_b"
        if r_col not in merged.columns or b_col not in merged.columns:
            continue

        for _, row in merged.iterrows():
            r_val = row.get(r_col)
            b_val = row.get(b_col)
            if pd.isna(r_val) or pd.isna(b_val):
                continue

            delta = r_val - b_val
            if abs(delta) < threshold:
                continue

            # Direction: rising metric * sign == +1 means buy, -1 means sell
            direction = "buy" if (delta > 0) == (sign > 0) else "sell"
            name = row.get("player_name_r") or row.get("player_name_b") or str(row[id_col])
            sample = row.get(f"{sample_col}_r", 0)

            # Magnitude scales with both change-size and sample. We weight sample
            # aggressively (squared) so a 30pp shift on 10 PA doesn't outrank a
            # 5pp shift on 60 PA. Floor at zero — single-PA noise should drop.
            raw_magnitude = abs(delta) / threshold
            sample_target = 60   # PA/TBF where confidence reaches full weight
            sample_weight = min(sample / sample_target, 1.0) ** 2 if sample else 0
            magnitude = raw_magnitude * sample_weight

            name = row.get("player_name_r") or row.get("player_name_b") or str(row[id_col])
            sample = row.get(f"{sample_col}_r", 0)

            unit = "" if col == "xwoba_con" else ("mph" if col == "avg_velo" else "pp")
            fmt = ".3f" if col == "xwoba_con" else ".1f"

            reasoning = (
                f"{label} {r_val:{fmt}} (last {TREND_RECENT_DAYS}d, {int(sample)} {sample_col.upper()}) "
                f"vs {b_val:{fmt}} ({baseline_label}) — Δ {delta:+{fmt}}{unit}"
            )

            signals.append({
                "player_name": name,
                "metric":      col,
                "label":       label,
                "direction":   direction,
                "magnitude":   round(magnitude, 2),
                "delta":       round(delta, 4),
                "recent":      round(r_val, 4),
                "baseline":    round(b_val, 4),
                "baseline_window": baseline_label,
                "sample":      int(sample),
                "reasoning":   reasoning,
            })

    return signals


# ── Public: build the full trends list ────────────────────────────────────────

def build_trends() -> dict:
    """Compute hitter + pitcher trends across both baseline windows.
    Returns a dict with 'buys' and 'sells' lists, deduplicated and sorted by
    aggregate magnitude (a player flagged by multiple metrics floats higher)."""

    today = date.today()
    recent_start, recent_end = statcast.window_dates(TREND_RECENT_DAYS, end=today)
    base30_start, base30_end = statcast.window_dates(TREND_BASELINE_RECENT_DAYS, end=today)
    season_start, season_end = SEASON_START, statcast._iso(today)

    # Pull all three windows. Cached after first call.
    print("[trend] pulling recent window...")
    h_recent = statcast.hitters_window(recent_start, recent_end)
    p_recent = statcast.pitchers_window(recent_start, recent_end)

    print("[trend] pulling 30d baseline...")
    h_base30 = statcast.hitters_window(base30_start, base30_end)
    p_base30 = statcast.pitchers_window(base30_start, base30_end)

    print("[trend] pulling season baseline...")
    h_season = statcast.hitters_window(season_start, season_end)
    p_season = statcast.pitchers_window(season_start, season_end)

    raw_signals = []
    # Hitters
    raw_signals += _compare_windows(h_recent, h_base30, "batter", HITTER_METRICS,
                                     baseline_label="vs prior 30d", sample_col="pa")
    raw_signals += _compare_windows(h_recent, h_season, "batter", HITTER_METRICS,
                                     baseline_label="vs season", sample_col="pa")
    # Pitchers
    raw_signals += _compare_windows(p_recent, p_base30, "pitcher", PITCHER_METRICS,
                                     baseline_label="vs prior 30d", sample_col="tbf")
    raw_signals += _compare_windows(p_recent, p_season, "pitcher", PITCHER_METRICS,
                                     baseline_label="vs season", sample_col="tbf")

    # Group signals by (player, direction) so a player with multiple flags shows them together
    grouped: dict[tuple, dict] = {}
    for s in raw_signals:
        key = (s["player_name"], s["direction"])
        if key not in grouped:
            grouped[key] = {
                "name":       s["player_name"],
                "direction":  s["direction"],
                "magnitude":  0.0,
                "signal_count": 0,
                "reasoning":  [],
                "metrics":    [],
            }
        g = grouped[key]
        g["magnitude"]    += s["magnitude"]
        g["signal_count"] += 1
        g["reasoning"].append(s["reasoning"])
        g["metrics"].append({
            "label":     s["label"],
            "delta":     s["delta"],
            "recent":    s["recent"],
            "baseline":  s["baseline"],
            "window":    s["baseline_window"],
            "sample":    s["sample"],
        })

    # Bonus: if a player is flagged by both windows for the same metric direction,
    # boost magnitude (the corroboration matters)
    for g in grouped.values():
        windows = {m["window"] for m in g["metrics"]}
        if len(windows) > 1:
            g["magnitude"] *= 1.25
        g["magnitude"] = round(g["magnitude"], 2)

    # Split into buys and sells, sort by magnitude
    all_grouped = list(grouped.values())
    buys  = sorted([g for g in all_grouped if g["direction"] == "buy"],
                   key=lambda x: -x["magnitude"])[:TRENDS_LIST_SIZE]
    sells = sorted([g for g in all_grouped if g["direction"] == "sell"],
                   key=lambda x: -x["magnitude"])[:TRENDS_LIST_SIZE]

    return {"buys": buys, "sells": sells}