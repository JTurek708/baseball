"""
data_sources/savant.py
Baseball Savant Statcast leaderboards.
Returns DataFrames; signal modules consume these.
"""
import requests, pandas as pd, io
from datetime import datetime
from backend.data_sources import cache

YEAR = datetime.now().year
BASE = "https://baseballsavant.mlb.com/leaderboard/custom"


def _fetch_csv(params: dict, key: str) -> pd.DataFrame:
    cached = cache.load(key)
    if cached is not None:
        return pd.DataFrame(cached)
    r = requests.get(BASE, params={**params, "csv": "true"}, timeout=20)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    cache.save(key, df.to_dict(orient="records"))
    return df


def batters(year: int = YEAR, min_pa: str | int = "q") -> pd.DataFrame:
    """Season-to-date batter Statcast data."""
    return _fetch_csv({
        "year": year, "type": "batter", "min": min_pa,
        "selections": "pa,xba,xslg,xwoba,xobp,woba,ba,slg,obp,iso,"
                      "barrel_batted_rate,hard_hit_percent,k_percent,bb_percent,"
                      "exit_velocity_avg,sweet_spot_percent,sprint_speed",
        "sort": "xwoba", "sortDir": "desc",
    }, f"sv_bat_{year}_{min_pa}")


def pitchers(year: int = YEAR, min_ip: str | int = "q") -> pd.DataFrame:
    """Season-to-date pitcher Statcast data."""
    return _fetch_csv({
        "year": year, "type": "pitcher", "min": min_ip,
        "selections": "p_formatted_ip,p_era,xera,k_percent,bb_percent,"
                      "whiff_percent,csw_rate,hard_hit_percent,barrel_batted_rate,"
                      "xwoba,woba",
        "sort": "xera", "sortDir": "asc",
    }, f"sv_pit_{year}_{min_ip}")


def name_col(df: pd.DataFrame) -> str:
    """Savant CSVs use this column name; old endpoints use 'player_name'."""
    if "last_name, first_name" in df.columns:
        return "last_name, first_name"
    if "player_name" in df.columns:
        return "player_name"
    return df.columns[0]


def lookup(player_name: str, is_pitcher: bool = False) -> dict:
    """Find a single player's row by 'First Last' name."""
    df = pitchers(min_ip=0) if is_pitcher else batters(min_pa=0)
    col = name_col(df)
    parts = player_name.strip().split()
    if len(parts) < 2:
        return {}
    last, first = parts[-1].lower(), parts[0].lower()
    mask = df[col].str.lower().str.contains(last, na=False) & \
           df[col].str.lower().str.contains(first, na=False)
    hits = df[mask]
    return hits.iloc[0].to_dict() if not hits.empty else {}
