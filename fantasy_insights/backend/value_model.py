"""
value_model.py
Roster enrichment + add/drop suggestions.
Uses ESPN's pre-computed fantasy points (already in league scoring format)
and overlays Savant predictive stats for context.
"""
from backend.data_sources import savant, clean_nan
from backend.config import SCORING_FORMAT
from backend.formats import points_h2h

ADAPTERS = {
    "points_h2h": points_h2h,
}


def adapter():
    return ADAPTERS.get(SCORING_FORMAT, points_h2h)


def enrich_roster(roster: list[dict]) -> list[dict]:
    """Add Savant predictive overlays to each rostered player.
    Fantasy score comes from ESPN's pre-computed points."""
    out = []
    for p in roster:
        is_pit = adapter().is_pitcher(p)
        sv     = savant.lookup(p["name"], is_pitcher=is_pit)
        merged = {
            **p,
            **sv,
            "fantasy_score": round(p.get("season_points", 0.0), 1),
            "is_pitcher": is_pit,
        }
        out.append(clean_nan(merged))
    return sorted(out, key=lambda x: -x["fantasy_score"])


def add_drop_suggestions(roster: list[dict], free_agents: list[dict], n: int = 8) -> list[dict]:
    """Compare each FA's ESPN season points to your weakest same-type player."""
    scored_roster = enrich_roster(roster)
    suggestions = []

    for fa in free_agents:
        is_pit = adapter().is_pitcher(fa)
        fa_sc  = round(fa.get("season_points", 0.0), 1)

        same_type = [p for p in scored_roster if p["is_pitcher"] == is_pit]
        if not same_type:
            continue

        weakest = min(same_type, key=lambda x: x["fantasy_score"])
        gain    = fa_sc - weakest["fantasy_score"]

        if gain > 0:
            suggestions.append({
                "add":        fa["name"],
                "add_team":   fa.get("pro_team", ""),
                "add_score":  fa_sc,
                "drop":       weakest["name"],
                "drop_score": weakest["fantasy_score"],
                "gain":       round(gain, 1),
                "is_pitcher": is_pit,
            })

    return sorted(suggestions, key=lambda x: -x["gain"])[:n]