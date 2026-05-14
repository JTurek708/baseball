import { useEffect, useState } from "react"
import { apiGet } from "@/lib/api"
import type { StandingTeam } from "@/lib/types"

export function Standings() {
  const [teams, setTeams] = useState<StandingTeam[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiGet<StandingTeam[]>("/api/standings")
      .then(setTeams)
      .catch(e => setError(e.message))
  }, [])

  if (error) return <ErrorState message={error} />
  if (!teams) return <LoadingState />

  return (
    <div className="p-7">
      <div className="flex items-baseline gap-2.5 mb-3.5">
        <h2 className="font-bold tracking-[0.15em] text-lg uppercase">League Standings</h2>
      </div>

      <div className="flex flex-col gap-1.5">
        {teams.map((t, i) => {
          const isMine = t.team_name.includes("L Train")
          return (
            <div
              key={i}
              className={`grid grid-cols-[28px_1fr_auto_auto] items-center gap-4 bg-zinc-900 border rounded-sm px-4 py-3 ${
                isMine ? "border-lime-400/30" : "border-zinc-800"
              }`}
            >
              <div className="font-bold text-lg text-zinc-700">{i + 1}</div>
              <div>
                <div className="font-semibold">{t.team_name}</div>
                <div className="font-mono text-[10px] text-zinc-500 font-normal">{t.owner}</div>
              </div>
              <div className="font-mono text-xs text-zinc-500">
                {t.wins}–{t.losses}{t.ties ? "–" + t.ties : ""}
              </div>
              <div className="font-bold text-lg text-zinc-500">#{t.standing}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3.5 text-zinc-500 font-mono text-xs">
      <div className="w-7 h-7 border-2 border-zinc-800 border-t-lime-400 rounded-full animate-spin" />
      fetching standings...
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