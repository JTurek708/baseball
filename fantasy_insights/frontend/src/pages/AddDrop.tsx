import { useEffect, useState } from "react"
import { apiGet } from "@/lib/api"
import type { AddDropSuggestion } from "@/lib/types"
import { LoadingState, ErrorState } from "@/components/States"

export function AddDrop() {
  const [suggestions, setSuggestions] = useState<AddDropSuggestion[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiGet<AddDropSuggestion[]>("/api/add-drop?size=40")
      .then(setSuggestions)
      .catch(e => setError(e.message))
  }, [])

  if (error) return <ErrorState message={error} />
  if (!suggestions) return <LoadingState message="scanning the wire..." />

  return (
    <div className="p-7">
      <div className="flex items-baseline gap-2.5 mb-3.5">
        <h2 className="font-bold tracking-[0.15em] text-lg uppercase">Add / Drop</h2>
        <span className="font-mono text-[9px] tracking-wider uppercase text-leather bg-oak px-2 py-0.5 rounded-sm">
          scored vs. your roster
        </span>
      </div>

      {suggestions.length === 0 ? (
        <div className="text-leather font-mono text-xs py-12 text-center">
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
    <div className="grid grid-cols-[auto_1fr_auto] items-center gap-4 bg-cream-deep border border-oak border-l-[3px] border-l-brass rounded-sm px-4 py-3.5 hover:border-oak-deep transition-colors">
      <div className="font-bold text-xl w-8 text-center text-brass">+</div>
      <div className="min-w-0">
        <div className="text-[15px] font-semibold mb-1 flex items-center gap-2 flex-wrap">
          {s.add}
          <span className="font-mono text-[9px] tracking-wider uppercase px-1.5 py-0.5 rounded-sm bg-oak text-leather">
            {s.is_pitcher ? "P" : "B"}
          </span>
        </div>
        <div className="font-mono text-[11px] text-leather">
          drop {s.drop} ({s.drop_score} → {s.add_score} pts)
        </div>
      </div>
      <div className="font-mono text-sm font-medium text-oxblood bg-oxblood/10 border border-oxblood/30 px-3 py-1 rounded-sm whitespace-nowrap">
        +{s.gain}
      </div>
    </div>
  )
}

