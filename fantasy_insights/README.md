# Fantasy Hub

Personal fantasy baseball analytics tool — surfaces buy/sell candidates a week
ahead of the rest of the league using xStats divergence, with trend and schedule
signals coming in later phases.

## Setup

```bash
# Create virtualenv + activate
python3 -m venv venv
source venv/bin/activate

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# → fill in ESPN_LEAGUE_ID, ESPN_TEAM_ID, ESPN_SWID, ESPN_S2
```

### Getting your ESPN cookies (private league)
1. Log into ESPN in Chrome
2. F12 → Application → Cookies → espn.com
3. Copy `SWID` → ESPN_SWID
4. Copy `espn_s2` → ESPN_S2

## Run

```bash
uvicorn backend.main:app --reload --port 8000
```

→ http://localhost:8000

## Project Structure

```
backend/
├── data_sources/   # ESPN, Savant, Fangraphs clients + shared cache
├── signals/        # divergence (Phase 1), trend (Phase 2), schedule (Phase 3)
├── formats/        # scoring adapters — points_h2h for now
├── value_model.py  # roster scoring + add/drop
├── config.py       # ALL personal info, weights, thresholds
└── main.py         # FastAPI app
frontend/
└── index.html      # dashboard
```

## Phase status

- [x] **Phase 1** — xStats divergence engine + watchlist UI + markdown export
- [ ] **Phase 2** — Trend engine (rolling 15d / 30d / season comparisons)
- [ ] **Phase 3** — Schedule strength engine (park factors + opponent matchups)

## Tuning

All thresholds live in `backend/config.py`:
- `HITTER_XWOBA_GAP` — minimum xwOBA-wOBA gap to flag (default .030)
- `HITTER_BIG_GAP` — gap considered "strong" signal (default .050)
- `PITCHER_XERA_GAP` — minimum ERA-xERA gap (default 0.50)
- `WEIGHT_DIVERGENCE` / `WEIGHT_TREND` / `WEIGHT_SCHEDULE` — composite weights

After a few weeks of using it, you'll have intuitions about what's predictive
vs. noise. Adjust thresholds, watch how the watchlist changes.
