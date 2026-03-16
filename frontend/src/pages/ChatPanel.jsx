import { useState, useRef, useEffect } from 'react'
import { Send, MessageCircle, X, Bot, User, Loader, Sparkles } from 'lucide-react'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

const SUGGESTIONS = [
  'Sabse zyada kharcha kahan hua?',
  'How can I save more money?',
  'Meri top 3 expenses kaun si hain?',
  'Show my monthly spending trend',
  'Koi subscriptions hain jo cancel kar sakta hu?',
  'What is my savings rate?',
]

export default function ChatPanel({ sessionId, isOpen, onToggle }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hi! 👋 Main aapka FinanceIQ Assistant hu. Aap apne financial data ke baare mein kuch bhi pooch sakte hain — Hindi, English, ya Hinglish mein!\n\nFor example:\n• "Sabse zyada kharcha kahan hua?"\n• "How can I save more?"\n• "February mein kitna spend hua?"'
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 300)
    }
  }, [isOpen])

  const sendMessage = async (text) => {
    const msg = (text || input).trim()
    if (!msg || loading) return

    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: msg }])
    setLoading(true)

    try {
      const res = await axios.post(`${API_URL}/chat`, {
        session_id: sessionId,
        message: msg
      })
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.reply }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, kuch error aa gaya. Please try again! 🙏',
        isError: true
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // Floating button when closed
  if (!isOpen) {
    return (
      <div className="no-print fixed bottom-6 right-6 z-50 flex items-center gap-3">
        <div className="animate-fade-in px-4 py-2.5 rounded-xl"
             style={{
               background: 'var(--bg-card)',
               border: '1px solid var(--border)',
               boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
             }}>
          <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
            💬 Got questions about your report?
          </p>
          <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
            Ask in Hindi, English, or Hinglish
          </p>
        </div>
        <button
          onClick={onToggle}
          className="w-14 h-14 rounded-full flex items-center justify-center transition-all hover:scale-105 shrink-0"
          style={{
            background: 'var(--accent)',
            color: '#ffffff',
            boxShadow: '0 4px 20px rgba(37, 99, 235, 0.35)',
            border: 'none',
            cursor: 'pointer',
          }}
        >
          <MessageCircle size={22} />
        </button>
      </div>
    )
  }

  return (
    <div className="no-print fixed bottom-6 right-6 z-50 animate-fade-in"
         style={{
           width: '400px',
           maxWidth: 'calc(100vw - 32px)',
           height: '580px',
           maxHeight: 'calc(100vh - 100px)',
           background: 'var(--bg-card)',
           border: '1px solid var(--border)',
           borderRadius: '16px',
           boxShadow: '0 12px 40px rgba(0,0,0,0.12)',
           display: 'flex',
           flexDirection: 'column',
           overflow: 'hidden',
         }}>

      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3" 
           style={{ borderBottom: '1px solid var(--border)', background: 'var(--bg-primary)' }}>
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
               style={{ background: 'var(--accent-dim)' }}>
            <Sparkles size={16} style={{ color: 'var(--accent)' }} />
          </div>
          <div>
            <p className="font-semibold text-sm" style={{ color: 'var(--text-primary)' }}>FinanceIQ Chat</p>
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Ask anything about your report</p>
          </div>
        </div>
        <button onClick={onToggle}
                className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors"
                style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
          <X size={18} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3"
           style={{ background: 'var(--bg-primary)' }}>

        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            {/* Avatar */}
            <div className="shrink-0 w-7 h-7 rounded-full flex items-center justify-center mt-0.5"
                 style={{
                   background: msg.role === 'user' ? 'var(--accent)' : 'var(--bg-secondary)',
                   color: msg.role === 'user' ? '#ffffff' : 'var(--accent)'
                 }}>
              {msg.role === 'user' ? <User size={13} /> : <Bot size={13} />}
            </div>

            {/* Bubble */}
            <div className="max-w-[80%] rounded-xl px-3.5 py-2.5 text-sm leading-relaxed"
                 style={{
                   background: msg.role === 'user' ? 'var(--accent)' : 'var(--bg-card)',
                   color: msg.role === 'user' ? '#ffffff' : 'var(--text-primary)',
                   border: msg.role === 'user' ? 'none' : '1px solid var(--border)',
                   whiteSpace: 'pre-wrap',
                   wordBreak: 'break-word',
                 }}>
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-2.5">
            <div className="shrink-0 w-7 h-7 rounded-full flex items-center justify-center"
                 style={{ background: 'var(--bg-secondary)', color: 'var(--accent)' }}>
              <Bot size={13} />
            </div>
            <div className="rounded-xl px-4 py-3 flex items-center gap-2"
                 style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
              <Loader size={14} className="animate-spin" style={{ color: 'var(--accent)' }} />
              <span className="text-xs" style={{ color: 'var(--text-muted)' }}>Thinking...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions (show only if no user messages yet) */}
      {messages.length <= 1 && !loading && (
        <div className="px-4 py-2 flex flex-wrap gap-1.5" style={{ borderTop: '1px solid var(--border)' }}>
          {SUGGESTIONS.slice(0, 4).map((s, i) => (
            <button key={i}
                    onClick={() => sendMessage(s)}
                    className="text-xs px-2.5 py-1.5 rounded-md transition-colors"
                    style={{
                      background: 'var(--accent-dim)',
                      color: 'var(--accent)',
                      border: '1px solid var(--accent-border)',
                      cursor: 'pointer',
                      fontFamily: 'Inter, sans-serif',
                    }}>
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="px-3 py-3" style={{ borderTop: '1px solid var(--border)', background: 'var(--bg-card)' }}>
        <div className="flex items-center gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Kuch bhi poochiye..."
            className="input-field flex-1"
            style={{ padding: '9px 14px', fontSize: '13px' }}
            disabled={loading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim() || loading}
            className="w-9 h-9 rounded-lg flex items-center justify-center transition-all shrink-0"
            style={{
              background: input.trim() ? 'var(--accent)' : 'var(--bg-secondary)',
              color: input.trim() ? '#ffffff' : 'var(--text-muted)',
              border: 'none',
              cursor: input.trim() ? 'pointer' : 'default',
              opacity: loading ? 0.5 : 1,
            }}
          >
            <Send size={15} />
          </button>
        </div>
      </div>
    </div>
  )
}
