import { useEffect, useState } from "react"
import { apiGet } from "@/lib/api"
import type { StandingTeam } from "@/lib/types"
import { LoadingState, ErrorState } from "@/components/States"

export function Standings() {
  const [teams, setTeams] = useState<StandingTeam[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiGet<StandingTeam[]>("/api/standings")
      .then(setTeams)
      .catch(e => setError(e.message))
  }, [])

  if (error) return <ErrorState message={error} />
  if (!teams) return <LoadingState message="fetching standings..." />

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
              className={`grid grid-cols-[28px_1fr_auto_auto] items-center gap-4 bg-cream-deep border rounded-sm px-4 py-3 ${
                isMine ? "border-oxblood/30" : "border-oak"
              }`}
            >
              <div className="font-bold text-lg text-leather-soft">{i + 1}</div>
              <div>
                <div className="font-semibold">{t.team_name}</div>
                <div className="font-mono text-[10px] text-leather font-normal">{t.owner}</div>
              </div>
              <div className="font-mono text-xs text-leather">
                {t.wins}–{t.losses}{t.ties ? "–" + t.ties : ""}
              </div>
              <div className="font-bold text-lg text-leather">#{t.standing}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

