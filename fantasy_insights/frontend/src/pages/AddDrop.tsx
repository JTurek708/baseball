import { useEffect, useState } from "react"
import { apiGet } from "@/lib/api"
import type { AddDropSuggestion } from "@/lib/types"

export function AddDrop() {
  const [suggestions, setSuggestions] = useState<AddDropSuggestion[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiGet<AddDropSuggestion[]>("/api/add-drop?size=40")
      .then(setSuggestions)
      .catch(e => setError(e.message))
  }, [])

  if (error) return <ErrorState message={error} />
  if (!suggestions) return <LoadingState />

  return (
    <div className="p-7">
      <div className="flex items-baseline gap-2.5 mb-3.5">
        <h2 className="font-bold tracking-[0.15em] text-lg uppercase">Add / Drop</h2>
        <span className="font-mono text-[9px] tracking-wider uppercase text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded-sm">
          scored vs. your roster
        </span>
      </div>

      {suggestions.length === 0 ? (
        <div className="text-zinc-500 font-mono text-xs py-12 text-center">
          No clear upgrades right now.
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {suggestions.map((s, i) => <SuggestionRow key={i} s={s} />)}
        </div>
      )}
    </div>
  )
}

function SuggestionRow({ s }: { s: AddDropSuggestion }) {
  return (
    <div className="grid grid-cols-[auto_1fr_auto] items-center gap-4 bg-zinc-900 border border-zinc-800 border-l-[3px] border-l-blue-500 rounded-sm px-4 py-3.5 hover:border-zinc-700 transition-colors">
      <div className="font-bold text-xl w-8 text-center text-blue-500">+</div>
      <div className="min-w-0">
        <div className="text-[15px] font-semibold mb-1 flex items-center gap-2 flex-wrap">
          {s.add}
          <span className="font-mono text-[9px] tracking-wider uppercase px-1.5 py-0.5 rounded-sm bg-zinc-800 text-zinc-500">
            {s.is_pitcher ? "P" : "B"}
          </span>
        </div>
        <div className="font-mono text-[11px] text-zinc-500">
          drop {s.drop} ({s.drop_score} → {s.add_score} pts)
        </div>
      </div>
      <div className="font-mono text-sm font-medium text-lime-400 bg-lime-400/10 border border-lime-400/30 px-3 py-1 rounded-sm whitespace-nowrap">
        +{s.gain}
      </div>
    </div>
  )
}

function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3.5 text-zinc-500 font-mono text-xs">
      <div className="w-7 h-7 border-2 border-zinc-800 border-t-lime-400 rounded-full animate-spin" />
      scanning the wire...
    </div>
  )
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="p-7">
      <div className="bg-red-500/10 border border-red-500/30 rounded p-3.5 font-mono text-xs text-red-500">
        ⚠ {message}
      </div>
    </div>
  )
}