import { useState, useCallback } from 'react'
import LoginPage from './pages/LoginPage'
import UploadPage from './pages/UploadPage'
import DashboardPage from './pages/DashboardPage'
import PipelinePage from './pages/PipelinePage'
import { TrendingUp, LogOut, User } from 'lucide-react'

export default function App() {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('financeiq_user')
      return saved ? JSON.parse(saved) : null
    } catch { return null }
  })
  const [page, setPage] = useState('upload')
  const [sessionId, setSessionId] = useState(null)
  const [report, setReport] = useState(null)

  const handleLogin = useCallback((userData) => {
    setUser(userData)
    localStorage.setItem('financeiq_user', JSON.stringify(userData))
  }, [])

  const handleLogout = useCallback(() => {
    setUser(null)
    localStorage.removeItem('financeiq_user')
    setSessionId(null)
    setReport(null)
    setPage('upload')
  }, [])

  const handleUploadComplete = useCallback((sid) => {
    setSessionId(sid)
    setPage('pipeline')
  }, [])

  const handleAnalysisComplete = useCallback((reportData) => {
    setReport({ ...reportData, _sessionId: sessionId })
    setPage('dashboard')
  }, [sessionId])

  const handleReset = useCallback(() => {
    setSessionId(null)
    setReport(null)
    setPage('upload')
  }, [])

  // Show login if not authenticated
  if (!user) {
    return <LoginPage onLogin={handleLogin} />
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      {/* Header */}
      <header className="no-print sticky top-0 z-50" style={{ 
        background: 'rgba(255, 255, 255, 0.85)', 
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid var(--border)'
      }}>
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <button onClick={handleReset} className="flex items-center gap-2.5 group" 
                  style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" 
                 style={{ background: 'var(--accent)', color: '#ffffff' }}>
              <TrendingUp size={16} />
            </div>
            <span className="font-bold text-lg" style={{ color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
              Finance<span style={{ color: 'var(--accent)' }}>IQ</span>
            </span>
          </button>

          <div className="flex items-center gap-3">
            {page === 'dashboard' && (
              <button
                onClick={handleReset}
                className="btn-primary no-print"
                style={{ padding: '7px 16px', fontSize: '13px' }}
              >
                New Analysis
              </button>
            )}

            <div className="flex items-center gap-2 pl-3" style={{ borderLeft: '1px solid var(--border)' }}>
              <div className="w-7 h-7 rounded-full flex items-center justify-center"
                   style={{ background: 'var(--accent-dim)', color: 'var(--accent)' }}>
                <User size={14} />
              </div>
              <span className="text-sm font-medium hidden sm:inline" style={{ color: 'var(--text-secondary)' }}>
                {user.name?.split(' ')[0]}
              </span>
              <button
                onClick={handleLogout}
                className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors"
                style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
                title="Sign out"
              >
                <LogOut size={15} />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Page Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {page === 'upload' && (
          <UploadPage onUploadComplete={handleUploadComplete} />
        )}
        {page === 'pipeline' && sessionId && (
          <PipelinePage 
            sessionId={sessionId} 
            onComplete={handleAnalysisComplete}
            onError={() => setPage('upload')}
          />
        )}
        {page === 'dashboard' && report && (
          <DashboardPage report={report} />
        )}
      </main>
    </div>
  )
}
