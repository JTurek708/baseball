import { useEffect, useState } from "react"
import { apiGet } from "@/lib/api"

type LbType = "batters" | "pitchers"
type LbSource = "savant" | "fangraphs"

interface LbRow {
  player_name?: string
  "last_name, first_name"?: string
  PlayerName?: string
  [key: string]: unknown
}

export function Leaderboard() {
  const [type, setType] = useState<LbType>("batters")
  const [source, setSource] = useState<LbSource>("savant")
  const [data, setData] = useState<LbRow[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Re-fetch whenever type or source changes
  useEffect(() => {
    setLoading(true)
    setError(null)
    setData(null)
    apiGet<LbRow[]>(`/api/leaderboard/${type}?source=${source}`)
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [type, source])

  return (
    <div className="p-7">
      <div className="flex gap-1.5 mb-3.5 flex-wrap">
        <ToggleButton active={type === "batters" && source === "savant"}    onClick={() => { setType("batters");  setSource("savant"); }}>Batters · Savant</ToggleButton>
        <ToggleButton active={type === "pitchers" && source === "savant"}   onClick={() => { setType("pitchers"); setSource("savant"); }}>Pitchers · Savant</ToggleButton>
        <ToggleButton active={type === "batters" && source === "fangraphs"} onClick={() => { setType("batters");  setSource("fangraphs"); }}>Batters · FG</ToggleButton>
        <ToggleButton active={type === "pitchers" && source === "fangraphs"} onClick={() => { setType("pitchers"); setSource("fangraphs"); }}>Pitchers · FG</ToggleButton>
      </div>

      {error ? (
        <div className="bg-red-500/10 border border-red-500/30 rounded p-3.5 font-mono text-xs text-red-500">⚠ {error}</div>
      ) : loading ? (
        <div className="flex flex-col items-center justify-center py-20 gap-3.5 text-zinc-500 font-mono text-xs">
          <div className="w-7 h-7 border-2 border-zinc-800 border-t-lime-400 rounded-full animate-spin" />
          loading...
        </div>
      ) : !data || data.length === 0 ? (
        <div className="text-zinc-500 font-mono text-xs py-12 text-center">No data.</div>
      ) : (
        <LbTable rows={data} type={type} />
      )}
    </div>
  )
}

function ToggleButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`font-mono text-[9px] tracking-wider uppercase px-3 py-1.5 rounded-sm transition-colors ${
        active
          ? "bg-lime-400/10 border border-lime-400 text-lime-400"
          : "bg-zinc-900 border border-zinc-800 text-zinc-500 hover:text-zinc-200"
      }`}
    >
      {children}
    </button>
  )
}

function LbTable({ rows, type }: { rows: LbRow[]; type: LbType }) {
  const isBat = type === "batters"
  const nameKey = "last_name, first_name" in rows[0] ? "last_name, first_name"
                : "PlayerName" in rows[0] ? "PlayerName" : "player_name"

  const cols = isBat
    ? ["xwoba", "barrel_batted_rate", "hard_hit_percent", "k_percent", "bb_percent", "exit_velocity_avg"]
    : ["xera",  "k_percent", "bb_percent", "whiff_percent", "hard_hit_percent"]

  const heads = isBat
    ? ["xwOBA", "Barrel%", "HH%", "K%", "BB%", "EV"]
    : ["xERA",  "K%", "BB%", "Whiff%", "HH%"]

  return (
    <div className="overflow-x-auto bg-zinc-900 border border-zinc-800 rounded-sm">
      <table className="w-full border-collapse font-mono text-xs">
        <thead>
          <tr className="bg-zinc-800">
            <th className="text-left text-[9px] tracking-wider uppercase text-zinc-500 px-3 py-2 whitespace-nowrap">#</th>
            <th className="text-left text-[9px] tracking-wider uppercase text-zinc-500 px-3 py-2 whitespace-nowrap">Name</th>
            {heads.map(h => (
              <th key={h} className="text-left text-[9px] tracking-wider uppercase text-zinc-500 px-3 py-2 whitespace-nowrap">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 50).map((r, i) => (
            <tr key={i} className="border-b border-zinc-800 last:border-b-0 hover:bg-zinc-900/50">
              <td className="text-zinc-500 text-[10px] px-3 py-2.5">{i + 1}</td>
              <td className="text-lime-400 font-medium px-3 py-2.5">{String(r[nameKey] ?? r.player_name ?? "—")}</td>
              {cols.map(c => {
                const v = r[c] as number | undefined | string
                const fmt = (c.includes("percent") || c.includes("rate")) ? fpct(v) : f3(v)
                return <td key={c} className="text-zinc-200 px-3 py-2.5">{fmt}</td>
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function f3(v: unknown) {
  const n = typeof v === "number" ? v : parseFloat(String(v))
  if (isNaN(n)) return "—"
  return n.toFixed(3)
}

function fpct(v: unknown) {
  const n = typeof v === "number" ? v : parseFloat(String(v))
  if (isNaN(n)) return "—"
  return (n < 1 ? n * 100 : n).toFixed(1) + "%"
}