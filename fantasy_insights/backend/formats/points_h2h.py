"""
formats/points_h2h.py
Scoring adapter for ESPN H2H points leagues like Los Amistades.
Other formats (roto, auction, dynasty) get their own files later.
"""

# Hitting weights
WEIGHTS_HIT = {
    "H":   1.0,  "HR":  4.0,  "RBI": 1.0,  "R":   1.0,
    "BB":  1.0,  "SB":  2.0,  "SO": -1.0,
}

# Pitching weights
WEIGHTS_PIT = {
    "IP":  3.0,  "SO":  1.0,  "BB": -1.0,  "ER": -1.0,
    "SV":  5.0,  "HLD": 2.0,  "QS":  3.0,
}


def _f(d: dict, *keys) -> float:
    for k in keys:
        v = d.get(k)
        if v is not None and v != "":
            try:
                return float(v)
            except (ValueError, TypeError):
                pass
    return 0.0


def hitter_points(stats: dict) -> float:
    return sum(_f(stats, k) * w for k, w in WEIGHTS_HIT.items())


def pitcher_points(stats: dict) -> float:
    return sum(_f(stats, k) * w for k, w in WEIGHTS_PIT.items())


def is_pitcher(player: dict) -> bool:
    return any(p in player.get("positions", []) for p in ("SP", "RP", "P"))


def score(stats: dict, pitcher: bool) -> float:
    return pitcher_points(stats) if pitcher else hitter_points(stats)
