import { useState, useEffect, useRef } from 'react'
import { CheckCircle, Circle, Loader, XCircle, AlertCircle, FileSearch, Tag, BarChart2, Lightbulb, BookOpen, RefreshCw, Package } from 'lucide-react'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

const NODES = [
  { id: 'extraction', label: 'Extraction', icon: FileSearch, desc: 'Parsing file & extracting transactions' },
  { id: 'categorization', label: 'Categorization', icon: Tag, desc: 'Classifying each transaction' },
  { id: 'analysis', label: 'Analysis', icon: BarChart2, desc: 'Computing financial metrics' },
  { id: 'insights', label: 'Insights', icon: Lightbulb, desc: 'Identifying spending patterns' },
  { id: 'advice', label: 'Advice', icon: BookOpen, desc: 'Generating personalized recommendations' },
  { id: 'reflection', label: 'Quality Check', icon: RefreshCw, desc: 'Validating advice quality' },
  { id: 'finalize', label: 'Report', icon: Package, desc: 'Assembling final report' },
]

export default function PipelinePage({ sessionId, onComplete, onError }) {
  const [nodeStatuses, setNodeStatuses] = useState({})
  const [messages, setMessages] = useState([])
  const [activeNode, setActiveNode] = useState(null)
  const [error, setError] = useState(null)
  const logRef = useRef(null)
  const eventSourceRef = useRef(null)

  useEffect(() => {
    if (!sessionId) return

    const es = new EventSource(`${API_URL}/stream/${sessionId}`)
    eventSourceRef.current = es

    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        const { node, status, message, timestamp } = data

        setMessages(prev => [...prev, { node, status, message, timestamp }])

        if (node === 'done') {
          es.close()
          fetchReport()
          return
        }

        if (status === 'running') {
          setActiveNode(node)
          setNodeStatuses(prev => ({ ...prev, [node]: 'running' }))
        } else if (status === 'done') {
          setNodeStatuses(prev => ({ ...prev, [node]: 'done' }))
          if (node === activeNode) setActiveNode(null)
        } else if (status === 'error') {
          setNodeStatuses(prev => ({ ...prev, [node]: 'error' }))
        }

        if (logRef.current) {
          logRef.current.scrollTop = logRef.current.scrollHeight
        }
      } catch (err) {
        console.warn('SSE parse error:', err)
      }
    }

    es.onerror = () => {
      setTimeout(fetchReport, 500)
    }

    return () => es.close()
  }, [sessionId])

  const fetchReport = async () => {
    try {
      let attempts = 0
      while (attempts < 30) {
        const res = await axios.get(`${API_URL}/report/${sessionId}`)
        if (res.data.status === 'complete' && res.data.report) {
          onComplete(res.data.report)
          return
        }
        await new Promise(r => setTimeout(r, 2000))
        attempts++
      }
      setError('Analysis timed out. Please try again.')
    } catch (err) {
      console.error('Report fetch error:', err)
      setError('Failed to fetch report. Is the backend running?')
    }
  }

  const getNodeStatus = (nodeId) => nodeStatuses[nodeId] || 'waiting'
  const completedCount = Object.values(nodeStatuses).filter(s => s === 'done').length
  const progress = Math.round((completedCount / NODES.length) * 100)

  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
          Analyzing Your Finances
        </h2>
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
          Processing your statement through our analysis pipeline...
        </p>
      </div>

      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex justify-between text-sm mb-2">
          <span style={{ color: 'var(--text-muted)' }}>Progress</span>
          <span className="font-mono font-medium" style={{ color: 'var(--accent)' }}>{progress}%</span>
        </div>
        <div className="h-1.5 rounded-full" style={{ background: 'var(--bg-secondary)' }}>
          <div
            className="h-1.5 rounded-full transition-all duration-700"
            style={{ 
              width: `${progress}%`,
              background: 'var(--accent)',
            }}
          />
        </div>
      </div>

      {/* Node Pipeline */}
      <div className="space-y-2 mb-8">
        {NODES.map((node, idx) => {
          const status = getNodeStatus(node.id)
          const Icon = node.icon
          
          return (
            <div
              key={node.id}
              className={`node-pill flex items-center gap-3.5 px-4 py-3.5 rounded-lg transition-all ${status === 'running' ? 'running' : ''}`}
              style={{
                background: status === 'running' 
                  ? 'var(--accent-dim)' 
                  : status === 'done' 
                    ? 'var(--bg-card)'
                    : 'var(--bg-card)',
                border: status === 'running'
                  ? '1px solid var(--accent-border)'
                  : '1px solid var(--border)',
                opacity: status === 'waiting' ? 0.6 : 1,
              }}
            >
              {/* Status icon */}
              <div className="shrink-0">
                {status === 'done' && <CheckCircle size={18} style={{ color: 'var(--success)' }} />}
                {status === 'running' && (
                  <Loader size={18} style={{ color: 'var(--accent)' }} className="animate-spin" />
                )}
                {status === 'error' && <XCircle size={18} style={{ color: 'var(--danger)' }} />}
                {status === 'waiting' && (
                  <Circle size={18} style={{ color: 'var(--text-muted)' }} />
                )}
              </div>

              {/* Node icon */}
              <div className="w-8 h-8 rounded-lg shrink-0 flex items-center justify-center"
                   style={{ 
                     background: status === 'waiting' ? 'var(--bg-secondary)' : 'var(--accent-dim)',
                   }}>
                <Icon size={14} style={{ 
                  color: status === 'waiting' ? 'var(--text-muted)' : 'var(--accent)' 
                }} />
              </div>

              {/* Label */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm" style={{ 
                    color: status === 'waiting' ? 'var(--text-muted)' : 'var(--text-primary)' 
                  }}>
                    {node.label}
                  </span>
                  {status === 'running' && (
                    <span className="badge"
                          style={{ background: 'var(--accent-dim)', color: 'var(--accent)', fontSize: '10px', padding: '2px 8px' }}>
                      PROCESSING
                    </span>
                  )}
                </div>
                <p className="text-xs mt-0.5 truncate" style={{ color: 'var(--text-muted)' }}>
                  {status === 'running' 
                    ? (messages.filter(m => m.node === node.id).slice(-1)[0]?.message || node.desc)
                    : status === 'done'
                      ? (messages.filter(m => m.node === node.id && m.status === 'done').slice(-1)[0]?.message || 'Complete')
                      : node.desc
                  }
                </p>
              </div>

              {/* Step number */}
              <div className="shrink-0 text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
                {idx + 1}/{NODES.length}
              </div>
            </div>
          )
        })}
      </div>

      {/* Live Log */}
      <div className="card" style={{ padding: '16px 20px' }}>
        <h3 className="font-medium mb-2.5 text-xs flex items-center gap-2" 
            style={{ color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: 'var(--accent)' }} />
          Activity Log
        </h3>
        <div
          ref={logRef}
          className="h-36 overflow-y-auto font-mono text-xs space-y-1"
          style={{ color: 'var(--text-muted)' }}
        >
          {messages.length === 0 && (
            <div className="shimmer-line h-3.5 rounded w-3/4" />
          )}
          {messages.map((msg, i) => (
            <div key={i} className="flex gap-3">
              <span style={{ color: 'var(--accent)', opacity: 0.7 }}>
                {new Date(msg.timestamp).toLocaleTimeString()}
              </span>
              <span style={{ 
                color: msg.status === 'error' ? 'var(--danger)' 
                       : msg.status === 'done' ? 'var(--success)' 
                       : 'var(--text-muted)' 
              }}>
                [{msg.node}] {msg.message}
              </span>
            </div>
          ))}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 rounded-lg flex items-center gap-3"
             style={{ background: 'var(--danger-bg)', border: '1px solid rgba(220,38,38,0.12)' }}>
          <AlertCircle size={16} style={{ color: 'var(--danger)' }} className="shrink-0" />
          <div>
            <p className="text-sm font-medium" style={{ color: 'var(--danger)' }}>{error}</p>
            <button onClick={onError} className="text-sm underline mt-1" 
                    style={{ color: 'var(--danger)', background: 'none', border: 'none', cursor: 'pointer' }}>
              Start over
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
