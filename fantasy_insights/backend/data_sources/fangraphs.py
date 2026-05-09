"""
data_sources/fangraphs.py
Fangraphs leaderboards via pybaseball, which handles the auth dance.
"""
import pandas as pd
from datetime import datetime
from pybaseball import batting_stats, pitching_stats
from backend.data_sources import cache

YEAR = datetime.now().year


def batters(year: int = YEAR) -> pd.DataFrame:
    cached = cache.load(f"fg_bat_{year}")
    if cached is not None:
        return pd.DataFrame(cached)
    try:
        df = batting_stats(year, qual=1)
        cache.save(f"fg_bat_{year}", df.to_dict(orient="records"))
        return df
    except Exception as e:
        print(f"[Fangraphs batters] {e}")
        return pd.DataFrame()


def pitchers(year: int = YEAR) -> pd.DataFrame:
    cached = cache.load(f"fg_pit_{year}")
    if cached is not None:
        return pd.DataFrame(cached)
    try:
        df = pitching_stats(year, qual=1)
        cache.save(f"fg_pit_{year}", df.to_dict(orient="records"))
        return df
    except Exception as e:
        print(f"[Fangraphs pitchers] {e}")
        return pd.DataFrame()


def lookup(player_name: str, is_pitcher: bool = False) -> dict:
    """Find a single player's row by 'First Last' name."""
    df = pitchers() if is_pitcher else batters()
    if df.empty or "Name" not in df.columns:
        return {}
    parts = player_name.strip().split()
    if len(parts) < 2:
        return {}
    last, first = parts[-1].lower(), parts[0].lower()
    mask = df["Name"].str.lower().str.contains(last, na=False) & \
           df["Name"].str.lower().str.contains(first, na=False)
    hits = df[mask]
    return hits.iloc[0].to_dict() if not hits.empty else {}