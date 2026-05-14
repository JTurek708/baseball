import { NavLink } from "react-router-dom"

const tabs = [
  { to: "/",           label: "Watchlist"   },
  { to: "/roster",     label: "Roster"      },
  { to: "/add-drop",   label: "Add / Drop"  },
  { to: "/standings",  label: "Standings"   },
  { to: "/leaderboard", label: "Leaderboard" },
]

export function Nav() {
  return (
    <nav className="flex px-7 bg-zinc-900 border-b border-zinc-800">
      {tabs.map(t => (
        <NavLink
          key={t.to}
          to={t.to}
          end={t.to === "/"}
          className={({ isActive }) =>
            `font-mono text-[10px] tracking-[0.15em] uppercase px-5 py-3.5 border-b-2 transition-colors ${
              isActive
                ? "text-lime-400 border-lime-400"
                : "text-zinc-500 border-transparent hover:text-zinc-200"
            }`
          }
        >
          {t.label}
        </NavLink>
      ))}
    </nav>
  )
}
