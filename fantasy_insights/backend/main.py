"""
main.py
FastAPI app — routes, frontend serving.
Run with: uvicorn backend.main:app --reload --port 8000
"""
from fastapi import FastAPI, HTTPException
# from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse
# import os

from backend.data_sources import espn, savant, fangraphs
from backend.signals import composite
from backend.value_model import enrich_roster, add_drop_suggestions
from backend.signals import composite, trend

app = FastAPI(title="Fantasy Hub")



# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok"}


# ── ESPN-backed routes ────────────────────────────────────────────────────────

@app.get("/api/roster")
def roster():
    try:
        return enrich_roster(espn.get_roster())
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/matchup")
def matchup():
    try:
        return espn.get_matchup()
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/standings")
def standings():
    try:
        return espn.get_standings()
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/add-drop")
def add_drop(size: int = 40):
    try:
        return add_drop_suggestions(espn.get_roster(), espn.get_free_agents(size=size))
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Watchlist (the Phase 1 main event) ────────────────────────────────────────

@app.get("/api/watchlist")
def watchlist():
    """Buy/sell candidates ranked by composite signal score."""
    try:
        roster_names = {p["name"] for p in espn.get_roster()}
        fa_names     = {p["name"] for p in espn.get_free_agents(size=200)}
        return composite.build_watchlist(roster_names, fa_names)
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/watchlist/markdown", response_class=PlainTextResponse)
def watchlist_markdown():
    """Same data, rendered as markdown — drop straight into your column."""
    try:
        roster_names = {p["name"] for p in espn.get_roster()}
        fa_names     = {p["name"] for p in espn.get_free_agents(size=200)}
        wl = composite.build_watchlist(roster_names, fa_names)
        return composite.export_markdown(wl)
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Leaderboards ──────────────────────────────────────────────────────────────

@app.get("/api/leaderboard/batters")
def lb_batters(source: str = "savant"):
    try:
        df = savant.batters() if source == "savant" else fangraphs.batters()
        return df.head(100).fillna("").to_dict(orient="records")
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/leaderboard/pitchers")
def lb_pitchers(source: str = "savant"):
    try:
        df = savant.pitchers() if source == "savant" else fangraphs.pitchers()
        return df.head(100).fillna("").to_dict(orient="records")
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/api/last-updated")
def last_updated():
    """When the Savant data backing the watchlist/leaderboard was last refreshed."""
    return {"last_updated": savant.data_last_updated()}

@app.get("/api/trends")
def trends():
    """Buy/sell candidates based on recent-window vs baseline shifts."""
    try:
        return trend.build_trends()
    except Exception as e:
        raise HTTPException(500, str(e))