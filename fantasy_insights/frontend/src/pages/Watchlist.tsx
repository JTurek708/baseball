import { useEffect, useState } from "react"
import { apiGet, apiGetText } from "@/lib/api"
import type { Watchlist as WatchlistData, WatchlistPlayer } from "@/lib/types"

export function Watchlist() {
  // ── React hooks: useState gives a component "memory" between renders ──
  const [data,    setData]    = useState<WatchlistData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState<string | null>(null)
  const [showExport, setShowExport] = useState(false)
  const [markdown,   setMarkdown]   = useState("")
  const [limit, setLimit] = useState(8)

  // ── useEffect runs side effects (like fetching data) on render ──
  // Empty dep array `[]` = runs once when component mounts.
  useEffect(() => {
    apiGet<WatchlistData>("/api/watchlist")
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  // ── Loading and error states ──
  if (loading) return <LoadingState />
  if (error)   return <ErrorState message={error} />
  if (!data)   return null

  // ── Open the markdown export modal ──
  async function handleExport() {
    try {
      const md = await apiGetText("/api/watchlist/markdown")
      setMarkdown(md)
      setShowExport(true)
    } catch (e) {
      alert("Export failed: " + (e as Error).message)
    }
  }

  return (
    <div className="p-7">
      {/* Buy section header */}
      <SectionHeader
        title="Buy Candidates"
        tag="unlucky · expected to improve"
        action={
          <button
            onClick={handleExport}
            className="font-mono text-[10px] tracking-[0.1em] uppercase px-3.5 py-1.5 bg-oxblood/10 border border-oxblood/30 text-oxblood rounded hover:bg-oxblood/20 transition-colors"
          >
            Export Markdown
          </button>
        }
      />
      <PlayerList players={data.buys.slice(0, limit)} kind="buy" />
      <ShowMore
        total={data.buys.length}
        shown={Math.min(limit, data.buys.length)}
        onMore={() => setLimit(l => l + 12)}
        onAll={() => setLimit(999)}
      />

      <div className="mt-7">
        <SectionHeader
          title="Sell Candidates"
          tag="running hot · expected to regress"
        />
        <PlayerList players={data.sells.slice(0, limit)} kind="sell" />
        <ShowMore
          total={data.sells.length}
          shown={Math.min(limit, data.sells.length)}
          onMore={() => setLimit(l => l + 12)}
          onAll={() => setLimit(999)}
        />
      </div>

      {/* Markdown export modal */}
      {showExport && (
        <ExportModal
          markdown={markdown}
          onClose={() => setShowExport(false)}
        />
      )}
    </div>
  )
}

// ── Subcomponents ────────────────────────────────────────────────────────────

function SectionHeader({
  title, tag, action,
}: {
  title: string
  tag: string
  action?: React.ReactNode
}) {
  return (
    <div className="flex items-baseline justify-between mb-3.5">
      <div className="flex items-baseline gap-2.5">
        <h2 className="font-bold tracking-[0.15em] text-lg uppercase">{title}</h2>
        <span className="font-mono text-[9px] tracking-wider uppercase text-leather bg-oak px-2 py-0.5 rounded-sm">
          {tag}
        </span>
      </div>
      {action}
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
  const remaining = total - shown
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

function PlayerList({
  players, kind,
}: {
  players: WatchlistPlayer[]
  kind: "buy" | "sell"
}) {
  if (players.length === 0) {
    return (
      <div className="text-leather font-mono text-xs py-12 text-center">
        {kind === "buy"
          ? "No strong buy signals right now."
          : "Your roster looks clean — no sell signals."}
      </div>
    )
  }
  return (
    <div className="flex flex-col gap-2">
      {players.map((p, i) => <PlayerRow key={i} player={p} kind={kind} />)}
    </div>
  )
}

function PlayerRow({
  player, kind,
}: {
  player: WatchlistPlayer
  kind: "buy" | "sell"
}) {
  const arrow = kind === "buy"
    ? (player.strength === "strong" ? "↑↑" : "↑")
    : (player.strength === "strong" ? "↓↓" : "↓")

  // Color logic — strong gets the bright accent, moderate gets blue/orange
  const borderColor =
    kind === "buy"
      ? (player.strength === "strong" ? "border-l-oxblood" : "border-l-brass")
      : (player.strength === "strong" ? "border-l-rust"  : "border-l-brass-deep")
  const arrowColor =
    kind === "buy"
      ? (player.strength === "strong" ? "text-oxblood" : "text-brass")
      : (player.strength === "strong" ? "text-rust"  : "text-brass-deep")

  const statusBadge =
    player.status === "fa"    ? <Badge color="lime">FA</Badge>
  : player.status === "yours" ? <Badge color="red">YOURS</Badge>
  :                              <Badge color="zinc">ROST</Badge>

  return (
    <div className={`grid grid-cols-[auto_1fr_auto] items-center gap-4 bg-cream-deep border border-oak border-l-[3px] ${borderColor} rounded-sm px-4 py-3.5 hover:border-oak-deep transition-colors`}>
      <div className={`font-bold text-xl w-8 text-center ${arrowColor}`}>
        {arrow}
      </div>
      <div className="min-w-0">
        <div className="text-[15px] font-semibold mb-1 flex items-center gap-2 flex-wrap">
          {player.name}
          {statusBadge}
        </div>
        <div className="font-mono text-[11px] text-leather leading-relaxed">
          {player.reasoning.map((r, i) => <div key={i}>{r}</div>)}
        </div>
      </div>
      <div className="font-bold text-xl text-leather text-right min-w-[54px]">
        {(player.composite * 100).toFixed(0)}
      </div>
    </div>
  )
}

function Badge({ color, children }: { color: "lime" | "red" | "zinc"; children: React.ReactNode }) {
  const classes = {
    lime: "bg-oxblood/10 text-oxblood",
    red:  "bg-rust/10 text-rust",
    zinc: "bg-oak text-leather",
  }[color]
  return (
    <span className={`font-mono text-[9px] tracking-wider uppercase px-1.5 py-0.5 rounded-sm ${classes}`}>
      {children}
    </span>
  )
}

function ExportModal({
  markdown, onClose,
}: {
  markdown: string
  onClose: () => void
}) {
  async function copy() {
    await navigator.clipboard.writeText(markdown)
    alert("Copied to clipboard.")
  }
  return (
    <div
      className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-7"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-cream-deep border border-oak rounded p-5 max-w-3xl w-full max-h-[80vh] flex flex-col">
        <div className="flex justify-between items-center mb-3.5">
          <h3 className="font-bold tracking-[0.15em] text-lg uppercase">Markdown Export</h3>
          <button onClick={onClose} className="text-leather hover:text-walnut text-lg">✕</button>
        </div>
        <textarea
          readOnly
          value={markdown}
          className="flex-1 bg-cream border border-oak rounded p-3.5 text-walnut font-mono text-xs min-h-[400px] leading-relaxed resize-y"
        />
        <div className="flex gap-2 mt-3 justify-end">
          <button
            onClick={copy}
            className="font-mono text-[10px] tracking-[0.1em] uppercase px-4 py-2 bg-oxblood text-zinc-950 rounded font-bold"
          >
            Copy to Clipboard
          </button>
        </div>
      </div>
    </div>
  )
}

function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3.5 text-leather font-mono text-xs">
      <div className="w-7 h-7 border-2 border-oak border-t-oxblood rounded-full animate-spin" />
      scanning the league...
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