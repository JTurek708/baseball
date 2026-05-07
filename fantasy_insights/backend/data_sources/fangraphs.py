"""
data_sources/fangraphs.py
Fangraphs leaderboards via their public JSON API.
"""
import requests, pandas as pd
from datetime import datetime
from backend.data_sources import cache

YEAR = datetime.now().year
BASE = "https://www.fangraphs.com/api/leaders/major-league/data"
HDR  = {"User-Agent": "Mozilla/5.0"}


def _fetch(params: dict, key: str) -> pd.DataFrame:
    cached = cache.load(key)
    if cached is not None:
        return pd.DataFrame(cached)
    try:
        r = requests.get(BASE, params=params, headers=HDR, timeout=20)
        r.raise_for_status()
        data = r.json().get("data", [])
        cache.save(key, data)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"[Fangraphs] {e}")
        return pd.DataFrame()


def batters(year: int = YEAR) -> pd.DataFrame:
    return _fetch({
        "pos": "all", "stats": "bat", "lg": "all", "qual": "0",
        "pageitems": 500, "pagenum": 1, "ind": "0",
        "season": year, "season1": year, "type": "8",
    }, f"fg_bat_{year}")


def pitchers(year: int = YEAR) -> pd.DataFrame:
    return _fetch({
        "pos": "all", "stats": "pit", "lg": "all", "qual": "0",
        "pageitems": 500, "pagenum": 1, "ind": "0",
        "season": year, "season1": year, "type": "8",
    }, f"fg_pit_{year}")
