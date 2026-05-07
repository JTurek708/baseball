"""
signals/divergence.py
xStats vs actual stats — finds players whose surface stats lie about them.

Positive divergence = unlucky, expected to improve → BUY signal
Negative divergence = lucky, expected to regress    → SELL signal
"""
from backend.data_sources import savant, clean_nan
from backend.config import (
    HITTER_MIN_PA, HITTER_XWOBA_GAP, HITTER_BIG_GAP,
    PITCHER_MIN_IP, PITCHER_XERA_GAP, PITCHER_BIG_GAP,
)


def _to_float(v) -> float | None:
    """Robust float coercion. Returns None on failure rather than raising."""
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None

# ── Hitters ───────────────────────────────────────────────────────────────────

def hitter_divergence(row: dict) -> dict | None:
    """
    Compute xwOBA - wOBA for a single hitter row from Savant.
    Returns a dict with score, direction, and reasoning, or None if not enough sample.
    """
    pa    = _to_float(row.get("pa"))
    xwoba = _to_float(row.get("xwoba"))
    woba  = _to_float(row.get("woba"))

    if pa is None or pa < HITTER_MIN_PA:
        return None
    if xwoba is None or woba is None:
        return None

    gap = xwoba - woba   # positive = unlucky
    if abs(gap) < HITTER_XWOBA_GAP:
        return None

    direction = "buy" if gap > 0 else "sell"
    strength  = "strong" if abs(gap) >= HITTER_BIG_GAP else "moderate"

    # Score is 0-1 magnitude of divergence, normalized so HITTER_BIG_GAP = 1.0
    score = min(abs(gap) / HITTER_BIG_GAP, 1.5)

    return {
        "signal":       "divergence",
        "type":         "hitter",
        "direction":    direction,
        "strength":     strength,
        "score":        score,
        "xwoba":        xwoba,
        "woba":         woba,
        "gap":          round(gap, 3),
        "pa":           int(pa),
        "reasoning":    _hitter_reasoning(row, gap, xwoba, woba, int(pa)),
    }


def _hitter_reasoning(row: dict, gap: float, xwoba: float, woba: float, pa: int) -> str:
    name  = row.get("last_name, first_name") or row.get("player_name", "?")
    if "," in str(name):
        last, first = [s.strip() for s in name.split(",", 1)]
        name = f"{first} {last}"

    luck = "unlucky" if gap > 0 else "running hot"
    direction_phrase = (
        f"xwOBA {xwoba:.3f} vs actual wOBA {woba:.3f} ({gap:+.3f}) over {pa} PA — {luck}"
    )

    # Add a quality-of-contact note if available
    extras = []
    barrel = _to_float(row.get("barrel_batted_rate"))
    hh     = _to_float(row.get("hard_hit_percent"))
    if barrel is not None:
        extras.append(f"Barrel% {barrel:.1f}")
    if hh is not None:
        extras.append(f"HH% {hh:.1f}")

    extras_str = f" · {', '.join(extras)}" if extras else ""
    return f"{direction_phrase}{extras_str}"


# ── Pitchers ──────────────────────────────────────────────────────────────────

def pitcher_divergence(row: dict) -> dict | None:
    """
    Compute ERA - xERA for a single pitcher row.
    Note: lower ERA = good, so positive (ERA - xERA) = lucky → SELL.
    """
    ip   = _to_float(row.get("p_formatted_ip"))
    era  = _to_float(row.get("p_era"))
    xera = _to_float(row.get("xera"))

    if ip is None or ip < PITCHER_MIN_IP:
        return None
    if era is None or xera is None:
        return None

    gap = era - xera   # positive = unlucky (true skill better than results)
    if abs(gap) < PITCHER_XERA_GAP:
        return None

    direction = "buy" if gap > 0 else "sell"
    strength  = "strong" if abs(gap) >= PITCHER_BIG_GAP else "moderate"

    score = min(abs(gap) / PITCHER_BIG_GAP, 1.5)

    return {
        "signal":     "divergence",
        "type":       "pitcher",
        "direction":  direction,
        "strength":   strength,
        "score":      score,
        "era":        era,
        "xera":       xera,
        "gap":        round(gap, 2),
        "ip":         ip,
        "reasoning":  _pitcher_reasoning(row, gap, era, xera, ip),
    }


def _pitcher_reasoning(row: dict, gap: float, era: float, xera: float, ip: float) -> str:
    luck = "unlucky" if gap > 0 else "running hot"
    base = f"ERA {era:.2f} vs xERA {xera:.2f} ({gap:+.2f}) over {ip:.1f} IP — {luck}"

    extras = []
    k    = _to_float(row.get("k_percent"))
    bb   = _to_float(row.get("bb_percent"))
    csw  = _to_float(row.get("csw_rate"))
    if k is not None:
        extras.append(f"K% {k:.1f}")
    if bb is not None:
        extras.append(f"BB% {bb:.1f}")
    if csw is not None:
        extras.append(f"CSW% {csw:.1f}")

    extras_str = f" · {', '.join(extras)}" if extras else ""
    return f"{base}{extras_str}"


# ── Bulk scan ─────────────────────────────────────────────────────────────────

def scan_all_hitters() -> list[dict]:
    """Run divergence on every qualified hitter."""
    df = savant.batters()
    out = []
    name_col = savant.name_col(df)
    for _, row in df.iterrows():
        d = row.to_dict()
        d["_name"] = d.get(name_col)
        result = hitter_divergence(d)
        if result:
            result["player_name"] = _normalize_name(d["_name"])
            result["raw"] = clean_nan(d)
            out.append(result)
    return out


def scan_all_pitchers() -> list[dict]:
    """Run divergence on every qualified pitcher."""
    df = savant.pitchers()
    out = []
    name_col = savant.name_col(df)
    for _, row in df.iterrows():
        d = row.to_dict()
        d["_name"] = d.get(name_col)
        result = pitcher_divergence(d)
        if result:
            result["player_name"] = _normalize_name(d["_name"])
            result["raw"] = clean_nan(d)
            out.append(result)
    return out


def _normalize_name(savant_name: str) -> str:
    """'Soto, Juan' → 'Juan Soto'."""
    if not savant_name or "," not in str(savant_name):
        return str(savant_name)
    last, first = [s.strip() for s in str(savant_name).split(",", 1)]
    return f"{first} {last}"
