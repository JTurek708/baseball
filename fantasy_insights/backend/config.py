"""
config.py
All personal info and tunable thresholds live here.
This is the only place to look when tuning behavior.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── ESPN ──────────────────────────────────────────────────────────────────────
ESPN_LEAGUE_ID = int(os.getenv("ESPN_LEAGUE_ID", 0))
ESPN_TEAM_ID   = int(os.getenv("ESPN_TEAM_ID", 1))
ESPN_YEAR      = int(os.getenv("ESPN_YEAR", 2026))
ESPN_SWID      = os.getenv("ESPN_SWID", "")
ESPN_S2        = os.getenv("ESPN_S2", "")

LEAGUE_SIZE    = int(os.getenv("LEAGUE_SIZE", 8))
SCORING_FORMAT = os.getenv("SCORING_FORMAT", "points_h2h")  # which adapter to use

CACHE_DIR      = "./data/cache"
CACHE_HOURS    = 6  # default cache lifespan for stat data

# ── Signal weights (how the composite score is built) ─────────────────────────
# These should sum to 1.0. Tune as you learn what's predictive.
WEIGHT_DIVERGENCE = 0.40   # xStats vs actual
WEIGHT_TREND      = 0.35   # rolling-window momentum  (Phase 2)
WEIGHT_SCHEDULE   = 0.25   # upcoming opponent strength (Phase 3)

# ── Divergence thresholds ─────────────────────────────────────────────────────
# Hitters
HITTER_MIN_PA              = 75      # minimum PA before we trust the divergence
HITTER_XWOBA_GAP           = 0.030   # |xwOBA - wOBA| must exceed this to flag
HITTER_BIG_GAP             = 0.050   # ≥ this is a "strong" signal

# Pitchers
PITCHER_MIN_IP             = 25      # minimum IP before we trust ERA divergence
PITCHER_XERA_GAP           = 0.50    # |xERA - ERA| in earned runs
PITCHER_BIG_GAP            = 1.00    # ≥ this is a "strong" signal

# ── Watchlist sizing ──────────────────────────────────────────────────────────
WATCHLIST_BUY_COUNT  = 100
WATCHLIST_SELL_COUNT = 100

# ── Trend engine thresholds ──────────────────────────────────────────────────
# Window sizes (days)
TREND_RECENT_DAYS         = 15
TREND_BASELINE_RECENT_DAYS = 30   # the "30 days" baseline for the 15d-vs-30d comparison

# Hitter thresholds — minimum absolute change in percentage points (or wOBA units)
TREND_HITTER_BARREL    = 3.0
TREND_HITTER_HH        = 4.0
TREND_HITTER_K         = 4.0
TREND_HITTER_BB        = 2.0
TREND_HITTER_XWOBA_CON = 0.030

# Pitcher thresholds
TREND_PITCHER_K     = 4.0
TREND_PITCHER_BB    = 2.0
TREND_PITCHER_WHIFF = 4.0
TREND_PITCHER_CSW   = 3.0
TREND_PITCHER_VELO  = 1.0   # mph

# How many candidates to surface
TRENDS_LIST_SIZE = 100