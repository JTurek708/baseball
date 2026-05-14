export function Header() {
  return (
    <header className="flex items-center justify-between px-7 h-14 bg-zinc-900 border-b border-zinc-800 sticky top-0 z-50">
      <div className="font-bold tracking-[0.2em] text-2xl">
        <span className="text-lime-400">FANTASY</span>
        <span className="text-zinc-300">HUB</span>
      </div>
      <div className="text-right text-[10px] font-mono text-zinc-500 leading-relaxed">
        <div className="text-lime-400 font-semibold">L Train Legends</div>
        <div>Los Amistades · 8-team H2H Points</div>
      </div>
    </header>
  )
}