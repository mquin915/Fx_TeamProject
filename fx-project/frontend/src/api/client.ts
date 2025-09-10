const BASE = '' // vite proxy 사용: /api -> http://localhost:8000

export async function apiGet(path: string) {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`${path} ${res.status}`)
  return res.json()
}
