// Shared loading + error states, used across all pages.

export function LoadingState({ message = "loading..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3.5 text-leather font-mono text-xs">
      <div className="w-7 h-7 border-2 border-oak border-t-oxblood rounded-full animate-spin" />
      {message}
    </div>
  )
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="p-7">
      <div className="bg-rust/10 border border-rust/30 rounded p-3.5 font-mono text-xs text-rust">
        ⚠ {message}
      </div>
    </div>
  )
}