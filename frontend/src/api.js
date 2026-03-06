const API_BASE = 'http://localhost:8000/api'

async function getJson(path){
  const res = await fetch(`${API_BASE}${path}`)
  if(!res.ok) throw new Error('Network error')
  return res.json()
}

export function fetchRuns(){ return getJson('/runs') }
export function fetchRun(id){ return getJson(`/runs/${id}`) }
export function fetchNetmap(){ return getJson('/netmap') }
export function fetchAiSummary(){ return getJson('/ai/summary') }
export async function postChat(q){
  const res = await fetch(`${API_BASE}/ai/chat`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({q}) })
  return res.json()
}
