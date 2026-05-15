import { useEffect, useState } from "react"
import { apiGet } from "@/lib/api"

// Small metadata line showing when the underlying Savant data was last pulled.
export function LastUpdated() {
  const [ts, setTs] = useState<string | null>(null)

  useEffect(() => {
    apiGet<{ last_updated: string | null }>("/api/last-updated")
      .then(d => setTs(d.last_updated))
      .catch(() => setTs(null))
  }, [])

  if (!ts) return null

  const formatted = new Date(ts).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  })

  return (
    <span className="font-mono text-[10px] text-leather-soft tracking-wider uppercase">
      Data updated {formatted}
    </span>
  )
}