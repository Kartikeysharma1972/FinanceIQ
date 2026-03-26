import { useState } from 'react'
import { TrendingUp, Eye, EyeOff, AlertCircle, ArrowRight, User, Mail, Lock } from 'lucide-react'
import axios from 'axios'

const API_URL = 'https://financeiq-bny8.onrender.com'

export default function LoginPage({ onLogin }) {
  const [isSignup, setIsSignup] = useState(false)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isSignup) {
        if (!name.trim()) {
          setError('Please enter your name')
          setLoading(false)
          return
        }
        const res = await axios.post(`${API_URL}/auth/signup`, { name, email, password })
        onLogin(res.data.user)
      } else {
        const res = await axios.post(`${API_URL}/auth/login`, { email, password })
        onLogin(res.data.user)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.')
      setLoading(false)
    }
  }

  const switchMode = () => {
    setIsSignup(!isSignup)
    setError('')
    setName('')
    setEmail('')
    setPassword('')
  }

  return (
    <div className="min-h-screen flex" style={{ background: 'var(--bg-primary)' }}>
      {/* Left panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between p-12" 
           style={{ 
             background: 'linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%)',
             position: 'relative',
             overflow: 'hidden'
           }}>
        {/* Subtle pattern overlay */}
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: 'radial-gradient(circle at 25% 25%, rgba(255,255,255,0.05) 0%, transparent 50%), radial-gradient(circle at 75% 75%, rgba(255,255,255,0.03) 0%, transparent 50%)',
        }} />
        
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                 style={{ background: 'rgba(255,255,255,0.15)', backdropFilter: 'blur(10px)' }}>
              <TrendingUp size={20} style={{ color: '#ffffff' }} />
            </div>
            <span className="font-bold text-2xl text-white tracking-tight">
              Finance<span style={{ color: '#93c5fd' }}>IQ</span>
            </span>
          </div>
        </div>

        <div style={{ position: 'relative', zIndex: 1 }}>
          <h1 className="text-4xl font-bold text-white mb-4 leading-tight" style={{ letterSpacing: '-0.03em' }}>
            Smart financial insights,<br />
            powered by AI.
          </h1>
          <p className="text-lg" style={{ color: 'rgba(255,255,255,0.7)', lineHeight: 1.7 }}>
            Upload your bank statement and get a comprehensive financial analysis 
            with personalized recommendations in minutes.
          </p>

          <div className="mt-10 space-y-4">
            {[
              'AI-powered transaction categorization',
              'Personalized spending insights',
              'Actionable savings recommendations'
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="w-5 h-5 rounded-full flex items-center justify-center" 
                     style={{ background: 'rgba(255,255,255,0.2)' }}>
                  <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                    <path d="M2 5L4.5 7.5L8 3" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <span className="text-sm" style={{ color: 'rgba(255,255,255,0.85)' }}>{item}</span>
              </div>
            ))}
          </div>
        </div>

        <p className="text-xs" style={{ color: 'rgba(255,255,255,0.4)', position: 'relative', zIndex: 1 }}>
          © {new Date().getFullYear()} FinanceIQ. Your data stays private.
        </p>
      </div>

      {/* Right panel - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md animate-fade-in">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className="w-9 h-9 rounded-lg flex items-center justify-center"
                 style={{ background: 'var(--accent-dim)', border: '1px solid var(--accent-border)' }}>
              <TrendingUp size={18} style={{ color: 'var(--accent)' }} />
            </div>
            <span className="font-bold text-xl" style={{ color: 'var(--text-primary)' }}>
              Finance<span style={{ color: 'var(--accent)' }}>IQ</span>
            </span>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)', letterSpacing: '-0.025em' }}>
              {isSignup ? 'Create your account' : 'Welcome back'}
            </h2>
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
              {isSignup 
                ? 'Start analyzing your finances with AI' 
                : 'Sign in to continue to FinanceIQ'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {isSignup && (
              <div>
                <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
                  Full Name
                </label>
                <div className="relative">
                  <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" 
                        style={{ color: '#9ca3af' }} />
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="John Doe"
                    className="input-field"
                    style={{ paddingLeft: '40px' }}
                    autoComplete="name"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
                Email Address
              </label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" 
                      style={{ color: '#9ca3af' }} />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="input-field"
                  style={{ paddingLeft: '40px' }}
                  required
                  autoComplete="email"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5" style={{ color: 'var(--text-secondary)' }}>
                Password
              </label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2" 
                      style={{ color: '#9ca3af' }} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={isSignup ? 'Min 6 characters' : 'Enter your password'}
                  className="input-field"
                  style={{ paddingLeft: '40px', paddingRight: '44px' }}
                  required
                  minLength={isSignup ? 6 : undefined}
                  autoComplete={isSignup ? 'new-password' : 'current-password'}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded"
                  style={{ color: '#9ca3af' }}
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {error && (
              <div className="flex items-center gap-2.5 p-3 rounded-lg text-sm"
                   style={{ background: 'var(--danger-bg)', color: 'var(--danger)', border: '1px solid rgba(220,38,38,0.15)' }}>
                <AlertCircle size={16} className="shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2"
              style={{ padding: '12px 20px', fontSize: '15px', marginTop: '8px' }}
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  {isSignup ? 'Create Account' : 'Sign In'}
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
              {isSignup ? 'Already have an account?' : "Don't have an account?"}{' '}
              <button 
                onClick={switchMode}
                className="font-medium"
                style={{ color: 'var(--accent)', background: 'none', border: 'none', cursor: 'pointer' }}
              >
                {isSignup ? 'Sign in' : 'Create one'}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
