import { useEffect, useState } from "react"
import { apiGet } from "@/lib/api"
import type { RosterPlayer, Matchup } from "@/lib/types"

// ESPN's standard slot ordering. Anything not in this list goes to the bottom.
const SLOT_ORDER = ['C','1B','2B','3B','SS','MI','CI','LF','CF','RF','OF','DH','UTIL','SP','RP','P','BE','IL','IL10','NA']

function slotRank(slot: string | null) {
  if (!slot) return 999
  const i = SLOT_ORDER.indexOf(slot)
  return i === -1 ? 999 : i
}

export function Roster() {
  const [players, setPlayers] = useState<RosterPlayer[] | null>(null)
  const [matchup, setMatchup] = useState<Matchup | null>(null)
  const [error,   setError]   = useState<string | null>(null)

  useEffect(() => {
    // Promise.all fires both requests in parallel
    Promise.all([
      apiGet<RosterPlayer[]>("/api/roster"),
      apiGet<Matchup>("/api/matchup"),
    ])
      .then(([roster, match]) => {
        setPlayers(roster)
        setMatchup(match)
      })
      .catch(e => setError(e.message))
  }, [])

  if (error) return <ErrorState message={error} />
  if (!players) return <LoadingState />

  // Sort by slot order, then split into three groups
  const sorted   = [...players].sort((a, b) => slotRank(a.lineup_slot) - slotRank(b.lineup_slot))
  const hitters  = sorted.filter(p => !p.on_bench && !p.is_pitcher)
  const pitchers = sorted.filter(p => !p.on_bench &&  p.is_pitcher)
  const bench    = sorted.filter(p =>  p.on_bench)

  return (
    <div className="p-7">
      {matchup && <MatchupBanner matchup={matchup} />}

      <SectionHeader
        title="Active"
        tag={`${hitters.length} hitters · ${pitchers.length} pitchers · ${bench.length} bench`}
      />
      {hitters.length  > 0 && <HitterTable rows={hitters} />}
      {pitchers.length > 0 && <PitcherTable rows={pitchers} />}

      {bench.length > 0 && (
        <>
          <div className="mt-7"><SectionHeader title="Bench / IL" /></div>
          <BenchTable rows={bench} />
        </>
      )}
    </div>
  )
}

// ── Matchup banner ────────────────────────────────────────────────────────────

function MatchupBanner({ matchup }: { matchup: Matchup }) {
  return (
    <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-5 bg-cream-deep border border-oak rounded-sm px-7 py-5 mb-6">
      <div className="font-bold tracking-[0.1em] text-lg uppercase text-oxblood">
        L Train Legends
      </div>
      <div className="text-center">
        <div className="font-bold tracking-[0.4em] text-4xl">
          {matchup.my_score}
          <span className="text-leather-soft px-2">–</span>
          {matchup.opp_score}
        </div>
        <div className="font-mono text-[9px] tracking-[0.2em] uppercase text-leather mt-1">
          Current Week
        </div>
      </div>
      <div className="text-right font-bold tracking-[0.1em] text-lg uppercase">
        {matchup.opponent}
      </div>
    </div>
  )
}

// ── Tables ────────────────────────────────────────────────────────────────────

function HitterTable({ rows }: { rows: RosterPlayer[] }) {
  return (
    <RosterTable
      rows={rows}
      headers={["Slot", "Player", "Pos", "Team", "xwOBA", "Barrel%", "HH%", "K%", "Pts"]}
      renderStats={p => [
        formatNum(p.xwoba),
        formatPct(p.barrel_batted_rate),
        formatPct(p.hard_hit_percent),
        formatPct(p.k_percent),
      ]}
    />
  )
}

function PitcherTable({ rows }: { rows: RosterPlayer[] }) {
  return (
    <RosterTable
      rows={rows}
      headers={["Slot", "Player", "Pos", "Team", "xERA", "K%", "BB%", "Whiff%", "Pts"]}
      renderStats={p => [
        formatNum(p.xera),
        formatPct(p.k_percent),
        formatPct(p.bb_percent),
        formatPct(p.whiff_percent),
      ]}
    />
  )
}

function BenchTable({ rows }: { rows: RosterPlayer[] }) {
  // Bench can mix hitters and pitchers — show type-appropriate stats per row
  return (
    <div className="bg-cream-deep border border-oak rounded-sm overflow-hidden">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-oak">
            {["Slot","Player","Pos","Team","Quality","·","·","Pts"].map((h, i) => (
              <th
                key={i}
                className={`font-mono text-[9px] tracking-wider uppercase text-leather px-3 py-2 ${i >= 4 ? "text-right" : "text-left"}`}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((p, i) => {
            const stat1 = p.is_pitcher ? formatNum(p.xera)            : formatNum(p.xwoba)
            const stat2 = p.is_pitcher ? formatPct(p.k_percent)       : formatPct(p.barrel_batted_rate)
            const stat3 = p.is_pitcher ? formatPct(p.whiff_percent)   : formatPct(p.hard_hit_percent)
            return (
              <tr
                key={i}
                className="border-b border-oak last:border-b-0 opacity-55 hover:bg-white/[.02] transition-colors"
              >
                <td className="font-mono text-[10px] tracking-wider uppercase text-leather px-3 py-3 w-16">
                  {p.lineup_slot || "—"}
                </td>
                <td className="font-semibold text-[14px] px-3 py-3">
                  {p.name}
                  {p.injured && (
                    <span className="ml-1.5 font-mono text-[10px] text-rust">
                      {p.injury_status || "INJ"}
                    </span>
                  )}
                </td>
                <td className="font-mono text-[11px] text-leather px-3 py-3">
                  {(p.positions || []).join(", ")}
                </td>
                <td className="font-mono text-[11px] text-leather px-3 py-3">
                  {p.pro_team || "—"}
                </td>
                <td className="font-mono text-[12px] text-right px-3 py-3">{stat1}</td>
                <td className="font-mono text-[12px] text-right px-3 py-3">{stat2}</td>
                <td className="font-mono text-[12px] text-right px-3 py-3">{stat3}</td>
                <td className="font-bold tracking-wider text-[16px] text-right px-3 py-3 text-leather">
                  {p.fantasy_score ?? "—"}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

// Shared table component for Hitters and Pitchers
function RosterTable({
  rows, headers, renderStats,
}: {
  rows: RosterPlayer[]
  headers: string[]
  renderStats: (p: RosterPlayer) => string[]
}) {
  return (
    <div className="bg-cream-deep border border-oak rounded-sm overflow-hidden mb-3">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-oak">
            {headers.map((h, i) => (
              <th
                key={i}
                className={`font-mono text-[9px] tracking-wider uppercase text-leather px-3 py-2 ${i >= 4 ? "text-right" : "text-left"}`}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((p, i) => (
            <tr
              key={i}
              className="border-b border-oak last:border-b-0 hover:bg-white/[.02] transition-colors"
            >
              <td className="font-mono text-[10px] tracking-wider uppercase text-oxblood px-3 py-3 w-16">
                {p.lineup_slot || "—"}
              </td>
              <td className="font-semibold text-[14px] px-3 py-3">
                {p.name}
                {p.injured && (
                  <span className="ml-1.5 font-mono text-[10px] text-rust">
                    {p.injury_status || "INJ"}
                  </span>
                )}
              </td>
              <td className="font-mono text-[11px] text-leather px-3 py-3">
                {(p.positions || []).join(", ")}
              </td>
              <td className="font-mono text-[11px] text-leather px-3 py-3">
                {p.pro_team || "—"}
              </td>
              {renderStats(p).map((s, si) => (
                <td key={si} className="font-mono text-[12px] text-right px-3 py-3">{s}</td>
              ))}
              <td className="font-bold tracking-wider text-[16px] text-right px-3 py-3">
                {p.fantasy_score ?? "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function formatNum(v?: number) {
  if (v == null || isNaN(v)) return "—"
  return v.toFixed(3)
}

function formatPct(v?: number) {
  if (v == null || isNaN(v)) return "—"
  // Savant returns 0.0-100.0 for percentages, not 0-1
  return (v < 1 ? v * 100 : v).toFixed(1) + "%"
}

function SectionHeader({ title, tag }: { title: string; tag?: string }) {
  return (
    <div className="flex items-baseline gap-2.5 mb-3.5">
      <h2 className="font-bold tracking-[0.15em] text-lg uppercase">{title}</h2>
      {tag && (
        <span className="font-mono text-[9px] tracking-wider uppercase text-leather bg-oak px-2 py-0.5 rounded-sm">
          {tag}
        </span>
      )}
    </div>
  )
}

function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3.5 text-leather font-mono text-xs">
      <div className="w-7 h-7 border-2 border-oak border-t-oxblood rounded-full animate-spin" />
      pulling roster...
    </div>
  )
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="p-7">
      <div className="bg-rust/10 border border-rust/30 rounded p-3.5 font-mono text-xs text-rust">
        ⚠ {message}
      </div>
    </div>
  )
}