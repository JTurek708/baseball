"""
signals/composite.py
Aggregates individual signals into a composite player score and
produces the buy/sell watchlist filtered against your roster + FA pool.

Phase 1: divergence only.
Phase 2 will add trend signals; Phase 3 adds schedule.
"""
from backend.signals import divergence
from backend.config import (
    WEIGHT_DIVERGENCE, WEIGHT_TREND, WEIGHT_SCHEDULE,
    WATCHLIST_BUY_COUNT, WATCHLIST_SELL_COUNT,
)


def composite_score(signals: dict) -> float:
    """
    Build a single weighted score from per-signal results.
    Currently divergence-only; trend and schedule will plug in here.
    """
    div_score   = signals.get("divergence", {}).get("score", 0.0)
    trend_score = signals.get("trend", {}).get("score", 0.0)
    sched_score = signals.get("schedule", {}).get("score", 0.0)

    return (
        div_score   * WEIGHT_DIVERGENCE +
        trend_score * WEIGHT_TREND +
        sched_score * WEIGHT_SCHEDULE
    )


def _build_player_record(div_result: dict) -> dict:
    """Wrap a divergence result as a watchlist candidate."""
    return {
        "name":        div_result["player_name"],
        "type":        div_result["type"],
        "direction":   div_result["direction"],
        "strength":    div_result["strength"],
        "composite":   composite_score({"divergence": div_result}),
        "signals":     {"divergence": div_result},
        "reasoning":   [div_result["reasoning"]],
    }


def build_watchlist(roster_names: set[str], fa_names: set[str]) -> dict:
    """
    Run all signals across hitters and pitchers, then split into:
      - buys:  unrostered or roster-fringe candidates trending up
      - sells: your players trending down
    """
    all_results = []
    for div in divergence.scan_all_hitters() + divergence.scan_all_pitchers():
        all_results.append(_build_player_record(div))

    # Sort by composite descending — strongest signals float to top
    all_results.sort(key=lambda x: -x["composite"])

    buys  = []
    sells = []

    for player in all_results:
        is_mine = player["name"] in roster_names
        is_fa   = player["name"] in fa_names

        if player["direction"] == "buy" and (is_fa or not is_mine):
            # Unowned or in the FA pool, trending up
            player["status"] = "fa" if is_fa else "rostered_elsewhere"
            buys.append(player)
        elif player["direction"] == "sell" and is_mine:
            # On your team, trending down
            player["status"] = "yours"
            sells.append(player)

    return {
        "buys":  buys[:WATCHLIST_BUY_COUNT],
        "sells": sells[:WATCHLIST_SELL_COUNT],
    }


def export_markdown(watchlist: dict) -> str:
    """
    Render watchlist as markdown — paste straight into your fantasy column draft.
    """
    lines = ["# Fantasy Watchlist", ""]

    if watchlist.get("buys"):
        lines.append("## Buy Candidates")
        lines.append("")
        for p in watchlist["buys"]:
            badge = "🟢" if p["strength"] == "strong" else "🟡"
            tag   = " (FA)" if p.get("status") == "fa" else ""
            lines.append(f"**{badge} {p['name']}**{tag}")
            for r in p["reasoning"]:
                lines.append(f"- {r}")
            lines.append("")

    if watchlist.get("sells"):
        lines.append("## Sell Candidates")
        lines.append("")
        for p in watchlist["sells"]:
            badge = "🔴" if p["strength"] == "strong" else "🟠"
            lines.append(f"**{badge} {p['name']}**")
            for r in p["reasoning"]:
                lines.append(f"- {r}")
            lines.append("")

    return "\n".join(lines)
