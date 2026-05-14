// Wraps fetch() so all our API calls share consistent error handling.
// Vite proxies /api/* to FastAPI on :8000 (see vite.config.ts).

export async function apiGet<T = unknown>(path: string): Promise<T> {
  const res = await fetch(path)
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API ${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

export async function apiGetText(path: string): Promise<string> {
  const res = await fetch(path)
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`)
  return res.text()
}