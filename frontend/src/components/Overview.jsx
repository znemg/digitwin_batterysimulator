import React from 'react'

/**
 * Overview Dashboard - displays run metrics and performance charts
 * 
 * Props:
 *   run: {
 *     id: number
 *     name: string
 *     model: string
 *     hw: string
 *     duration: string
 *     status: "pass" | "warning" | "fail"
 *     metrics: {
 *       accuracy: number (0-100)
 *       fpr: number (0-100)
 *       latency: number (milliseconds)
 *       detections: number
 *       battery: number (0-100)
 *       congestion: number (0-100)
 *       throughput: number
 *     }
 *   }
 * 
 * Data source: GET /api/runs/{run_id}
 */
export default function Overview({run}){
  return (
    <div id="pageOverview" style={{overflowY:'auto', padding:24}}>
      <div className="run-meta-card" id="overviewMeta">
        <span className="run-meta-label">Loaded Run: {run?.name}</span>
        <span className="run-chip chip-model" id="ovChipModel">{run?.model || '—'}</span>
        <span className="run-chip chip-hw" id="ovChipHw">{run?.hw || '—'}</span>
        <span className="run-chip chip-dur" id="ovChipDur">{run?.duration || '—'}</span>
        <span className={`run-chip ${run?.status==='warning'?'chip-warn':'chip-pass'}`} id="ovChipStatus">{run?.status? run.status.toUpperCase(): 'PASS'}</span>
      </div>

      <div className="metrics-row">
        <div className="metric-card pass-state">
          <div className="m-label">AI Accuracy <span className="help-icon">?<span className="help-tip">Percentage of correct detections out of total events in the scenario pack. Higher is better.</span></span></div>
          <div className="m-value">{run?.metrics?.accuracy ?? '—%'}{typeof run?.metrics?.accuracy==='number'?'%':''}</div>
          <div className="m-trend up">↑ 2.1% vs baseline</div>
        </div>

        <div className="metric-card warn-state">
          <div className="m-label">False Positive Rate <span className="help-icon">?<span className="help-tip">Percentage of false detections out of all positive detections. Lower is better.</span></span></div>
          <div className="m-value">{run?.metrics?.fpr ?? '—%'}{typeof run?.metrics?.fpr==='number'?'%':''}</div>
          <div className="m-trend down">↑ 1.2% vs baseline</div>
        </div>

        <div className="metric-card pass-state">
          <div className="m-label">Avg Inference Latency <span className="help-icon">?<span className="help-tip">Mean time from audio input to model output on the node's hardware.</span></span></div>
          <div className="m-value">{run?.metrics?.latency ?? '—ms'}</div>
          <div className="m-trend up">↓ 12ms vs baseline</div>
        </div>

        <div className="metric-card pass-state">
          <div className="m-label">Detection Count <span className="help-icon">?<span className="help-tip">Total number of AI detections during this run (expected: 130).</span></span></div>
          <div className="m-value">{run?.metrics?.detections ?? '—'}</div>
          <div className="m-trend" style={{color:'var(--text-muted)'}}>expected: 130</div>
        </div>

        <div className="metric-card" style={{borderLeft:'3px solid var(--purple)'}}>
          <div className="m-label">Battery Health <span className="help-icon">?<span className="help-tip">Average remaining battery across all sensor nodes at end of run.</span></span></div>
          <div className="m-value">{run?.metrics?.battery ?? '—'}%</div>
          <div className="m-trend down">R1 critical (23%)</div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-box">
          <div className="chart-hdr"><div className="chart-title">Detections by Type <span className="help-icon">?<span className="help-tip">Breakdown of what the AI system is detecting most often during this run.</span></span></div></div>
          <svg className="svg-chart" viewBox="0 0 500 200" preserveAspectRatio="none">
            <line x1="80" y1="20" x2="80" y2="175" stroke="#1e2d48" strokeWidth="1"></line>
            <line x1="80" y1="175" x2="490" y2="175" stroke="#1e2d48" strokeWidth="1"></line>
            <rect x="90" y="38" width="340" height="22" rx="3" fill="rgba(0,230,138,0.6)"></rect><text x="440" y="53" fill="#7e93b0" fontSize="10" fontFamily="JetBrains Mono">42</text>
            <text x="75" y="53" fill="#7e93b0" fontSize="10" textAnchor="end" fontFamily="DM Sans">Bird</text>
            <rect x="90" y="68" width="226" height="22" rx="3" fill="rgba(255,77,106,0.6)"></rect><text x="326" y="83" fill="#7e93b0" fontSize="10" fontFamily="JetBrains Mono">28</text>
            <text x="75" y="83" fill="#7e93b0" fontSize="10" textAnchor="end" fontFamily="DM Sans">Gunshot</text>
            <rect x="90" y="98" width="178" height="22" rx="3" fill="rgba(255,190,46,0.6)"></rect><text x="278" y="113" fill="#7e93b0" fontSize="10" fontFamily="JetBrains Mono">22</text>
            <text x="75" y="113" fill="#7e93b0" fontSize="10" textAnchor="end" fontFamily="DM Sans">Chainsaw</text>
            <rect x="90" y="128" width="162" height="22" rx="3" fill="rgba(59,130,246,0.6)"></rect><text x="262" y="143" fill="#7e93b0" fontSize="10" fontFamily="JetBrains Mono">20</text>
            <text x="75" y="143" fill="#7e93b0" fontSize="10" textAnchor="end" fontFamily="DM Sans">Voice</text>
            <rect x="90" y="158" width="121" height="22" rx="3" fill="rgba(167,139,250,0.6)"></rect><text x="221" y="173" fill="#7e93b0" fontSize="10" fontFamily="JetBrains Mono">15</text>
            <text x="75" y="173" fill="#7e93b0" fontSize="10" textAnchor="end" fontFamily="DM Sans">Vehicle</text>
          </svg>
        </div>

        <div className="chart-box">
          <div className="chart-hdr"><div className="chart-title">Latency by Network Rank <span className="help-icon">?<span className="help-tip">Average end-to-end latency grouped by hop distance from the Command Center. Rank 1 = direct connection, Rank 3 = 3 hops away.</span></span></div></div>
          <svg className="svg-chart" viewBox="0 0 500 200" preserveAspectRatio="none">
            <line x1="60" y1="20" x2="60" y2="175" stroke="#1e2d48" strokeWidth="1"></line><line x1="60" y1="175" x2="490" y2="175" stroke="#1e2d48" strokeWidth="1"></line>
            <line x1="60" y1="135" x2="490" y2="135" stroke="#1e2d48" strokeWidth="0.5" strokeDasharray="4"></line><line x1="60" y1="95" x2="490" y2="95" stroke="#1e2d48" strokeWidth="0.5" strokeDasharray="4"></line><line x1="60" y1="55" x2="490" y2="55" stroke="#1e2d48" strokeWidth="0.5" strokeDasharray="4"></line>
            <text x="55" y="178" fill="#4a5f7a" fontSize="9" textAnchor="end" fontFamily="JetBrains Mono">0ms</text><text x="55" y="138" fill="#4a5f7a" fontSize="9" textAnchor="end" fontFamily="JetBrains Mono">50ms</text><text x="55" y="98" fill="#4a5f7a" fontSize="9" textAnchor="end" fontFamily="JetBrains Mono">100ms</text><text x="55" y="58" fill="#4a5f7a" fontSize="9" textAnchor="end" fontFamily="JetBrains Mono">150ms</text>
            <rect x="100" y="135" width="80" height="40" rx="4" fill="rgba(0,230,138,0.5)"></rect><text x="140" y="190" fill="#7e93b0" fontSize="10" textAnchor="middle" fontFamily="JetBrains Mono">Rank 1</text><text x="140" y="130" fill="#00e68a" fontSize="10" textAnchor="middle" fontFamily="JetBrains Mono" fontWeight="600">38ms</text>
            <rect x="220" y="95" width="80" height="80" rx="4" fill="rgba(255,190,46,0.5)"></rect><text x="260" y="190" fill="#7e93b0" fontSize="10" textAnchor="middle" fontFamily="JetBrains Mono">Rank 2</text><text x="260" y="90" fill="#ffbe2e" fontSize="10" textAnchor="middle" fontFamily="JetBrains Mono" fontWeight="600">95ms</text>
            <rect x="340" y="55" width="80" height="120" rx="4" fill="rgba(255,77,106,0.5)"></rect><text x="380" y="190" fill="#7e93b0" fontSize="10" textAnchor="middle" fontFamily="JetBrains Mono">Rank 3</text><text x="380" y="50" fill="#ff4d6a" fontSize="10" textAnchor="middle" fontFamily="JetBrains Mono" fontWeight="600">142ms</text>
          </svg>
        </div>
      </div>

      <div className="chart-box" style={{marginBottom:20}}>
        <div className="chart-hdr"><div className="chart-title">Accuracy vs Confidence Threshold <span className="help-icon">?<span className="help-tip">Shows tradeoff: higher threshold reduces false positives but may miss real events. The dotted line shows false positive rate at each threshold.</span></span></div></div>
        <svg className="svg-chart" viewBox="0 0 500 200" preserveAspectRatio="none">
          <line x1="50" y1="20" x2="50" y2="175" stroke="#1e2d48" strokeWidth="1"></line><line x1="50" y1="175" x2="490" y2="175" stroke="#1e2d48" strokeWidth="1"></line>
          <text x="270" y="198" fill="#4a5f7a" fontSize="9" textAnchor="middle" fontFamily="DM Sans">Confidence Threshold →</text>
          <text x="45" y="178" fill="#4a5f7a" fontSize="8" textAnchor="end" fontFamily="JetBrains Mono">0%</text><text x="45" y="100" fill="#4a5f7a" fontSize="8" textAnchor="end" fontFamily="JetBrains Mono">50%</text><text x="45" y="25" fill="#4a5f7a" fontSize="8" textAnchor="end" fontFamily="JetBrains Mono">100%</text>
          <text x="70" y="193" fill="#4a5f7a" fontSize="8" fontFamily="JetBrains Mono">0.3</text><text x="270" y="193" fill="#4a5f7a" fontSize="8" textAnchor="middle" fontFamily="JetBrains Mono">0.65</text><text x="470" y="193" fill="#4a5f7a" fontSize="8" textAnchor="end" fontFamily="JetBrains Mono">0.95</text>
          <polyline fill="none" stroke="#00e68a" strokeWidth="2" points="70,28 140,32 210,38 280,42 320,55 380,75 440,110 470,140"></polyline>
          <polyline fill="none" stroke="#ff4d6a" strokeWidth="2" strokeDasharray="6,3" points="70,60 140,80 210,105 280,130 320,145 380,158 440,166 470,170"></polyline>
          <line x1="280" y1="20" x2="280" y2="175" stroke="var(--cyan)" strokeWidth="1.5" strokeDasharray="4,3"></line>
          <text x="280" y="15" fill="var(--cyan)" fontSize="9" textAnchor="middle" fontFamily="JetBrains Mono">current: 0.65</text>
          <line x1="350" y1="28" x2="370" y2="28" stroke="#00e68a" strokeWidth="2"></line><text x="375" y="32" fill="#7e93b0" fontSize="9" fontFamily="DM Sans">Accuracy</text>
          <line x1="350" y1="42" x2="370" y2="42" stroke="#ff4d6a" strokeWidth="2" strokeDasharray="4,2"></line><text x="375" y="46" fill="#7e93b0" fontSize="9" fontFamily="DM Sans">False Positive Rate</text>
        </svg>
      </div>
    </div>
  )
}
