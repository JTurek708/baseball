"""
data_sources/cache.py
Tiny disk-cache helper. All data sources funnel through this.
"""
import os, json
from datetime import datetime
from backend.config import CACHE_DIR, CACHE_HOURS

os.makedirs(CACHE_DIR, exist_ok=True)


def _path(key: str) -> str:
    return os.path.join(CACHE_DIR, f"{key}.json")


def load(key: str, max_age_hours: float = CACHE_HOURS):
    """Return cached data if fresh, else None."""
    p = _path(key)
    if not os.path.exists(p):
        return None
    age_hours = (datetime.now().timestamp() - os.path.getmtime(p)) / 3600
    if age_hours > max_age_hours:
        return None
    with open(p) as f:
        return json.load(f)


def save(key: str, data):
    """Write data to cache."""
    with open(_path(key), "w") as f:
        json.dump(data, f, default=str)
