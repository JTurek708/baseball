// Types matching what our FastAPI endpoints return.
// VSCode uses these for autocomplete + error checking.

export interface DivergenceSignal {
  signal: "divergence"
  type: "hitter" | "pitcher"
  direction: "buy" | "sell"
  strength: "strong" | "moderate"
  score: number
  reasoning: string
  // Hitter-specific
  xwoba?: number
  woba?: number
  pa?: number
  // Pitcher-specific
  xera?: number
  era?: number
  ip?: number
  gap?: number
}

export interface WatchlistPlayer {
  name: string
  type: "hitter" | "pitcher"
  direction: "buy" | "sell"
  strength: "strong" | "moderate"
  composite: number
  reasoning: string[]
  status: "fa" | "yours" | "rostered_elsewhere"
  signals: {
    divergence?: DivergenceSignal
  }
}

export interface Watchlist {
  buys: WatchlistPlayer[]
  sells: WatchlistPlayer[]
}

// ── Roster types ──────────────────────────────────────────────────────────────

export interface RosterPlayer {
  name: string
  espn_id: number
  positions: string[]
  pro_team: string
  injured: boolean
  injury_status: string | null
  lineup_slot: string | null
  on_bench: boolean
  is_pitcher: boolean
  fantasy_score: number
  season_stats?: Record<string, number>
  projected_points?: number

  // Savant overlay fields (may be missing if no match)
  xwoba?: number
  woba?: number
  pa?: number
  barrel_batted_rate?: number
  hard_hit_percent?: number
  k_percent?: number
  bb_percent?: number
  xera?: number
  era?: number
  whiff_percent?: number
}

export interface Matchup {
  my_score: number
  opp_score: number
  opponent: string
}

// ── Add/Drop types ────────────────────────────────────────────────────────────

export interface AddDropSuggestion {
  add: string
  add_team: string
  add_score: number
  drop: string
  drop_score: number
  gain: number
  is_pitcher: boolean
}

// ── Standings types ───────────────────────────────────────────────────────────

export interface StandingTeam {
  team_name: string
  owner: string
  wins: number
  losses: number
  ties: number
  standing: number
}