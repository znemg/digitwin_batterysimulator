import React, { useState } from 'react'
import { fetchAiSummary, postChat } from '../api'
import { useApi } from '../hooks/useApi'

/**
 * AISummary - AI-generated insights and chat interface
 * 
 * Fetches:
 *   1. GET /api/ai/summary
 *   2. POST /api/ai/chat (when user sends message)
 * 
 * Expected responses:
 *   
 *   GET /api/ai/summary:
 *   {
 *     title: string
 *     content: string (AI-generated summary of the run)
 *   }
 *   
 *   POST /api/ai/chat (request):
 *   {
 *     q: string (user question)
 *   }
 *   
 *   POST /api/ai/chat (response):
 *   {
 *     answer: string
 *   }
 */
export default function AISummary(){
  const { data, loading } = useApi(()=>fetchAiSummary(), [])
  const [q, setQ] = useState('')
  const [resp, setResp] = useState(null)

  async function send(){
    const r = await postChat(q)
    setResp(r.answer)
  }

  if(loading) return <div style={{padding:24}}>Loading AI summary…</div>

  return (
    <div style={{padding:24}}>
      <div className="summary-card">
        <div className="summary-card-title">AI Summary</div>
        <div className="summary-text">{data?.content || "No summary available"}</div>
      </div>
      <div className="chat-container">
        <div className="chat-messages">
          {resp && <div className="chat-msg assistant"><div className="chat-bubble">{resp}</div></div>}
        </div>
        <div className="chat-input-row">
          <input className="chat-input" value={q} onChange={e=>setQ(e.target.value)} onKeyDown={e=>{if(e.key=="Enter")send();}} placeholder="Ask AI (battery, gunshot)" />
          <button className="chat-send" onClick={send}>↩</button>
        </div>
      </div>
    </div>
  )
}
