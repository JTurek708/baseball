import { useEffect, useState } from "react"
import { apiGet } from "@/lib/api"
import type { TrendsResponse, TrendPlayer } from "@/lib/types"
import { LoadingState, ErrorState } from "@/components/States"
import { LastUpdated } from "@/components/LastUpdated"

export function Trends() {
  const [data,    setData]    = useState<TrendsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState<string | null>(null)
  const [limit,   setLimit]   = useState(8)

  useEffect(() => {
    apiGet<TrendsResponse>("/api/trends")
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingState message="reading the tea leaves..." />
  if (error)   return <ErrorState message={error} />
  if (!data)   return null

  return (
    <div className="p-7">
      <div className="flex justify-end mb-3">
        <LastUpdated />
      </div>

      <SectionHeader title="Trending Up" tag="recent metrics outpacing baseline" />
      <PlayerList players={data.buys.slice(0, limit)} kind="buy" />
      <ShowMore
        total={data.buys.length}
        shown={Math.min(limit, data.buys.length)}
        onMore={() => setLimit(l => l + 12)}
        onAll={() => setLimit(999)}
      />

      <div className="mt-7">
        <SectionHeader title="Trending Down" tag="recent metrics slipping vs baseline" />
        <PlayerList players={data.sells.slice(0, limit)} kind="sell" />
        <ShowMore
          total={data.sells.length}
          shown={Math.min(limit, data.sells.length)}
          onMore={() => setLimit(l => l + 12)}
          onAll={() => setLimit(999)}
        />
      </div>
    </div>
  )
}

// ── Subcomponents ────────────────────────────────────────────────────────────

function SectionHeader({ title, tag }: { title: string; tag: string }) {
  return (
    <div className="flex items-baseline gap-2.5 mb-3.5">
      <h2 className="font-bold tracking-[0.15em] text-lg uppercase">{title}</h2>
      <span className="font-mono text-[9px] tracking-wider uppercase text-leather bg-oak px-2 py-0.5 rounded-sm">
        {tag}
      </span>
    </div>
  )
}

function PlayerList({ players, kind }: { players: TrendPlayer[]; kind: "buy" | "sell" }) {
  if (players.length === 0) {
    return (
      <div className="text-leather font-mono text-xs py-12 text-center">
        {kind === "buy" ? "No trending-up movers right now." : "No trending-down movers right now."}
      </div>
    )
  }
  return (
    <div className="flex flex-col gap-2">
      {players.map((p, i) => <PlayerRow key={i} player={p} kind={kind} />)}
    </div>
  )
}

function PlayerRow({ player, kind }: { player: TrendPlayer; kind: "buy" | "sell" }) {
  const arrow = kind === "buy" ? "↑↑" : "↓↓"
  const borderColor = kind === "buy" ? "border-l-oxblood" : "border-l-rust"
  const arrowColor  = kind === "buy" ? "text-oxblood"     : "text-rust"

  return (
    <div className={`grid grid-cols-[auto_1fr_auto] items-center gap-4 bg-cream-deep border border-oak border-l-[3px] ${borderColor} rounded-sm px-4 py-3.5 hover:border-oak-deep transition-colors`}>
      <div className={`font-bold text-xl w-8 text-center ${arrowColor}`}>{arrow}</div>
      <div className="min-w-0">
        <div className="text-[15px] font-semibold mb-1 flex items-center gap-2 flex-wrap">
          {player.name}
          <span className="font-mono text-[9px] tracking-wider uppercase px-1.5 py-0.5 rounded-sm bg-oak text-leather">
            {player.signal_count} signals
          </span>
        </div>
        <div className="font-mono text-[11px] text-leather leading-relaxed">
          {player.reasoning.map((r, i) => <div key={i}>{r}</div>)}
        </div>
      </div>
      <div className="font-bold text-xl text-leather text-right min-w-[54px]">
        {player.magnitude.toFixed(1)}
      </div>
    </div>
  )
}

function ShowMore({
  total, shown, onMore, onAll,
}: {
  total: number
  shown: number
  onMore: () => void
  onAll: () => void
}) {
  if (shown >= total) return null
  return (
    <div className="mt-3 flex items-center justify-center gap-3 font-mono text-[11px] text-leather">
      <span>showing {shown} of {total}</span>
      <span className="text-leather-soft">·</span>
      <button
        onClick={onMore}
        className="text-walnut-soft hover:text-oxblood transition-colors uppercase tracking-wider"
      >
        Show 12 more
      </button>
      <span className="text-leather-soft">·</span>
      <button
        onClick={onAll}
        className="text-walnut-soft hover:text-oxblood transition-colors uppercase tracking-wider"
      >
        Show all
      </button>
    </div>
  )
}