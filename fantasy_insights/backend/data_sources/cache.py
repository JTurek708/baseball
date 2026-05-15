"""
data_sources/cache.py
Disk cache with daily refresh — data is considered stale once the
clock passes midnight, so the first page load each day pulls fresh data.
"""
import os, json
from datetime import datetime, time
from backend.config import CACHE_DIR

os.makedirs(CACHE_DIR, exist_ok=True)


def _path(key: str) -> str:
    return os.path.join(CACHE_DIR, f"{key}.json")


def _todays_midnight() -> float:
    """Epoch timestamp of the most recent midnight (start of today, local time)."""
    now = datetime.now()
    midnight = datetime.combine(now.date(), time.min)
    return midnight.timestamp()


def load(key: str):
    """Return cached data if it was written today, else None."""
    p = _path(key)
    if not os.path.exists(p):
        return None
    # Stale if the file was last modified before today's midnight
    if os.path.getmtime(p) < _todays_midnight():
        return None
    with open(p) as f:
        return json.load(f)


def save(key: str, data):
    """Write data to cache."""
    with open(_path(key), "w") as f:
        json.dump(data, f, default=str)

def last_updated(key: str) -> str | None:
    """ISO timestamp of when this cache key was last written, or None if absent."""
    p = _path(key)
    if not os.path.exists(p):
        return None
    return datetime.fromtimestamp(os.path.getmtime(p)).isoformat()