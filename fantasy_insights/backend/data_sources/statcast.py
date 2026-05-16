"""
data_sources/statcast.py
Pitch-by-pitch Statcast data via pybaseball, aggregated to per-player rate stats
over a date range. Caches the aggregated result, not the raw pitch data.
"""
from datetime import date, timedelta
import pandas as pd
from pybaseball import statcast, playerid_reverse_lookup
from backend.data_sources import cache


# ── Date helpers ──────────────────────────────────────────────────────────────

def _iso(d: date) -> str:
    return d.strftime("%Y-%m-%d")


def window_dates(days: int, end: date | None = None) -> tuple[str, str]:
    """Return (start, end) ISO date strings for a rolling window ending at `end`."""
    end = end or date.today()
    start = end - timedelta(days=days)
    return _iso(start), _iso(end)


# ── Raw pull (cached) ─────────────────────────────────────────────────────────

def _pull_pitches(start: str, end: str) -> pd.DataFrame:
    """Wraps pybaseball.statcast with a quiet retry. Slow on first call."""
    print(f"[statcast] Pulling pitch data {start} → {end} (this can take a minute)...")
    df = statcast(start_dt=start, end_dt=end)
    print(f"[statcast]   got {len(df):,} pitches")
    return df


# ── Aggregations ──────────────────────────────────────────────────────────────

def aggregate_hitters(df: pd.DataFrame) -> pd.DataFrame:
    """Per-batter rate stats from pitch-level data."""
    if df.empty:
        return pd.DataFrame()

    # PA-level: rows where 'events' is set (last pitch of a PA)
    pa = df[df["events"].notna()].copy()
    by_pa = pa.groupby("batter", as_index=False).agg(
        pa=("events", "count"),
        k=("events", lambda x: (x == "strikeout").sum()),
        bb=("events", lambda x: (x == "walk").sum()),
    )

    # Batted-ball-level: rows with launch_speed (ball hit into play)
    bbe = df[df["launch_speed"].notna()].copy()
    by_bbe = bbe.groupby("batter", as_index=False).agg(
        batted_balls=("launch_speed", "count"),
        hard_hit=("launch_speed", lambda x: (x >= 95).sum()),
        barrels=("launch_speed_angle", lambda x: (x == 6).sum()),
        avg_ev=("launch_speed", "mean"),
        xwoba_con=("estimated_woba_using_speedangle", "mean"),
    )

    out = by_pa.merge(by_bbe, on="batter", how="left").fillna(0)

    # Resolve batter IDs to names via pybaseball's reverse lookup.
    # The Statcast pitch frame's 'player_name' column refers to the PITCHER, so
    # we can't use it for batters — we have to query Chadwick's player table.
    batter_ids = out["batter"].dropna().astype(int).unique().tolist()
    if batter_ids:
        lookup = playerid_reverse_lookup(batter_ids, key_type="mlbam")
        lookup["player_name"] = lookup["name_last"].str.title() + ", " + lookup["name_first"].str.title()
        lookup = lookup[["key_mlbam", "player_name"]].rename(columns={"key_mlbam": "batter"})
        out["batter"] = out["batter"].astype(int)
        out = out.merge(lookup, on="batter", how="left")
    else:
        out["player_name"] = out["batter"].astype(str)

    out["player_name"] = out["player_name"].fillna(out["batter"].astype(str))

    # Rate calculations (guarded against divide-by-zero)
    out["k_pct"]        = (out["k"] / out["pa"] * 100).where(out["pa"] > 0)
    out["bb_pct"]       = (out["bb"] / out["pa"] * 100).where(out["pa"] > 0)
    out["hard_hit_pct"] = (out["hard_hit"] / out["batted_balls"] * 100).where(out["batted_balls"] > 0)
    out["barrel_pct"]   = (out["barrels"] / out["batted_balls"] * 100).where(out["batted_balls"] > 0)

    return out

def aggregate_pitchers(df: pd.DataFrame) -> pd.DataFrame:
    """Per-pitcher rate stats from pitch-level data."""
    if df.empty:
        return pd.DataFrame()

    pa = df[df["events"].notna()].copy()
    by_pa = pa.groupby("pitcher", as_index=False).agg(
        tbf=("events", "count"),
        k=("events", lambda x: (x == "strikeout").sum()),
        bb=("events", lambda x: (x == "walk").sum()),
    )

    # All pitches grouped by pitcher
    by_pitches = df.groupby("pitcher", as_index=False).agg(
        pitches=("description", "count"),
        called_strikes=("description", lambda x: (x == "called_strike").sum()),
        swinging_strikes=("description", lambda x: (x == "swinging_strike").sum()),
        fouls=("description", lambda x: (x.isin(["foul", "foul_tip"])).sum()),
        balls_in_play=("description", lambda x: (x == "hit_into_play").sum()),
        avg_velo=("release_speed", "mean"),
    )

    out = by_pa.merge(by_pitches, on="pitcher", how="left").fillna(0)

    # Get pitcher names from a separate lookup (Statcast doesn't include them by default)
    # Use the first pitcher name we can find per pitcher id
    names = df.dropna(subset=["pitcher"]).groupby("pitcher")["player_name"].first().reset_index()
    out = out.merge(names, on="pitcher", how="left")

    # Whiff% = SwStr / total swings (swinging_strikes + fouls + balls_in_play)
    out["swings"]      = out["swinging_strikes"] + out["fouls"] + out["balls_in_play"]
    out["whiff_pct"]   = (out["swinging_strikes"] / out["swings"] * 100).where(out["swings"] > 0)
    out["csw_pct"]     = ((out["called_strikes"] + out["swinging_strikes"]) / out["pitches"] * 100).where(out["pitches"] > 0)
    out["k_pct"]       = (out["k"] / out["tbf"] * 100).where(out["tbf"] > 0)
    out["bb_pct"]      = (out["bb"] / out["tbf"] * 100).where(out["tbf"] > 0)

    return out


# ── Public window getters (cached aggregations) ───────────────────────────────

def hitters_window(start: str, end: str) -> pd.DataFrame:
    """Hitter rate stats over [start, end]. Cached."""
    key = f"trend_hit_{start}_{end}"
    cached = cache.load(key)
    if cached is not None:
        return pd.DataFrame(cached)
    df = _pull_pitches(start, end)
    agg = aggregate_hitters(df)
    cache.save(key, agg.to_dict(orient="records"))
    return agg


def pitchers_window(start: str, end: str) -> pd.DataFrame:
    """Pitcher rate stats over [start, end]. Cached."""
    key = f"trend_pit_{start}_{end}"
    cached = cache.load(key)
    if cached is not None:
        return pd.DataFrame(cached)
    df = _pull_pitches(start, end)
    agg = aggregate_pitchers(df)
    cache.save(key, agg.to_dict(orient="records"))
    return agg