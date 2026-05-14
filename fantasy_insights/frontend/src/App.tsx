import { BrowserRouter, Route, Routes } from "react-router-dom"
import { Header }    from "./components/Header"
import { Nav }       from "./components/Nav"
import { Watchlist } from "./pages/Watchlist"
import { Roster }    from "./pages/Roster"
import { AddDrop }   from "./pages/AddDrop"
import { Standings } from "./pages/Standings"
import { Leaderboard } from "./pages/Leaderboard"

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-cream text-walnut">
        <Header />
        <Nav />
        <main className="max-w-7xl mx-auto">
          <Routes>
            <Route path="/"            element={<Watchlist />} />
            <Route path="/roster"      element={<Roster />} />
            <Route path="/add-drop"    element={<AddDrop />} />
            <Route path="/standings"   element={<Standings />} />
            <Route path="/leaderboard" element={<Leaderboard />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}