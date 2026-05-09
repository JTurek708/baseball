"""
data_sources/espn.py
ESPN league data: roster, matchup, free agents, standings.
"""
from espn_api.baseball import League
from backend.config import ESPN_LEAGUE_ID, ESPN_TEAM_ID, ESPN_YEAR, ESPN_SWID, ESPN_S2


def _league() -> League:
    kwargs = dict(league_id=ESPN_LEAGUE_ID, year=ESPN_YEAR)
    if ESPN_SWID and ESPN_S2:
        kwargs["swid"] = ESPN_SWID
        kwargs["espn_s2"] = ESPN_S2
    return League(**kwargs)


def get_my_team():
    return _league().teams[ESPN_TEAM_ID - 1]


def _player_dict(p) -> dict:
    positions = p.eligibleSlots if isinstance(p.eligibleSlots, list) else [p.eligibleSlots]

    # Pull season-to-date stats (key 0 = season). Use empty dict if missing.
    season_stats = {}
    season_points = 0.0
    projected_points = 0.0
    projected_stats = {}
    if hasattr(p, "stats") and p.stats:
        season_block = p.stats.get(0, {})
        season_stats = season_block.get("breakdown", {})
        season_points = season_block.get("points", 0.0)
        projected_points = season_block.get("projected_points", 0.0)
        projected_stats = season_block.get("projected_breakdown", {})

    return {
        "name":             p.name,
        "espn_id":          p.playerId,
        "positions":        positions,
        "pro_team":         p.proTeam,
        "injured":          p.injured,
        "injury_status":    p.injuryStatus,
        "lineup_slot":      getattr(p, "lineupSlot", None),
        "on_bench":         getattr(p, "lineupSlot", None) in ("BE", "IL", "IL10", "NA"),
        "season_stats":     season_stats,
        "season_points":    season_points,
        "projected_points": projected_points,
        "projected_stats":  projected_stats,
    }


def get_roster() -> list[dict]:
    return [_player_dict(p) for p in get_my_team().roster]


def get_matchup() -> dict:
    league = _league()
    team   = get_my_team()
    for box in league.box_scores():
        if box.home_team == team or box.away_team == team:
            is_home = box.home_team == team
            return {
                "my_score":  box.home_score if is_home else box.away_score,
                "opp_score": box.away_score if is_home else box.home_score,
                "opponent":  (box.away_team if is_home else box.home_team).team_name,
            }
    return {}


def get_free_agents(size: int = 100, position: str | None = None) -> list[dict]:
    league = _league()
    pos    = [position] if position else []
    return [_player_dict(p) for p in league.free_agents(size=size, position=pos)]


def get_standings() -> list[dict]:
    out = []
    for t in _league().teams:
        owner_name = ""
        if t.owners:
            o = t.owners[0]
            owner_name = f"{o.get('firstName', '')} {o.get('lastName', '')}".strip()
        out.append({
            "team_name":  t.team_name,
            "owner":      owner_name,
            "wins":       t.wins,
            "losses":     t.losses,
            "ties":       t.ties,
            "standing":   t.standing,   # ESPN's official rank
        })
    out.sort(key=lambda x: x["standing"])
    return out