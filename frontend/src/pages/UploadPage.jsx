import { useState, useCallback, useRef } from 'react'
import { Upload, FileText, FileSpreadsheet, Shield, BarChart3, Lightbulb, Target, AlertCircle } from 'lucide-react'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

const FEATURES = [
  { icon: BarChart3, title: 'Detailed Analysis', desc: 'Get a comprehensive breakdown of your income, expenses, and savings patterns.' },
  { icon: Lightbulb, title: 'Smart Insights', desc: 'Receive personalized observations about your spending habits and trends.' },
  { icon: Target, title: 'Action Plan', desc: 'Get prioritized recommendations to optimize your finances.' },
  { icon: Shield, title: 'Fully Private', desc: 'Your data is processed in-memory and never stored permanently.' },
]

export default function UploadPage({ onUploadComplete }) {
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const fileInputRef = useRef(null)

  const processFile = useCallback(async (file) => {
    if (!file) return
    
    const ext = file.name.split('.').pop().toLowerCase()
    if (!['pdf', 'csv'].includes(ext)) {
      setError('Please upload a PDF or CSV file')
      return
    }
    
    setSelectedFile(file)
    setError('')
    setUploading(true)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      onUploadComplete(response.data.session_id)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Is the backend running?')
      setUploading(false)
      setSelectedFile(null)
    }
  }, [onUploadComplete])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    processFile(file)
  }, [processFile])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => setIsDragging(false), [])

  const handleFileInput = useCallback((e) => {
    processFile(e.target.files[0])
  }, [processFile])

  return (
    <div className="animate-fade-in">
      {/* Hero */}
      <div className="text-center mb-12 pt-4">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight" 
            style={{ color: 'var(--text-primary)', letterSpacing: '-0.03em' }}>
          Analyze your finances{' '}
          <span style={{ color: 'var(--accent)' }}>intelligently</span>
        </h1>
        
        <p className="text-lg max-w-xl mx-auto" style={{ color: 'var(--text-muted)', lineHeight: 1.7 }}>
          Upload your bank statement and get a complete financial analysis 
          with spending insights, budget suggestions, and a personalized action plan.
        </p>
      </div>

      {/* Upload Zone */}
      <div className="max-w-xl mx-auto mb-14">
        <div
          className={`upload-zone rounded-xl p-10 text-center cursor-pointer relative ${isDragging ? 'dragging' : ''}`}
          style={{ background: isDragging ? 'var(--accent-dim)' : 'var(--bg-card)', boxShadow: 'var(--shadow-sm)' }}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => !uploading && fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.csv"
            onChange={handleFileInput}
            className="hidden"
          />
          
          {uploading ? (
            <div className="flex flex-col items-center gap-4">
              <div className="relative">
                <div className="w-14 h-14 rounded-full" 
                     style={{ border: '3px solid var(--border)' }} />
                <div className="w-14 h-14 rounded-full absolute top-0 left-0 animate-spin"
                     style={{ border: '3px solid transparent', borderTopColor: 'var(--accent)' }} />
              </div>
              <div>
                <p className="font-semibold text-base" style={{ color: 'var(--accent)' }}>
                  Uploading {selectedFile?.name}...
                </p>
                <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
                  Starting analysis pipeline
                </p>
              </div>
            </div>
          ) : (
            <>
              <div className="flex justify-center gap-3 mb-5">
                <div className="w-11 h-11 rounded-lg flex items-center justify-center"
                     style={{ background: 'rgba(220,38,38,0.06)', border: '1px solid rgba(220,38,38,0.12)' }}>
                  <FileText size={20} style={{ color: '#dc2626' }} />
                </div>
                <div className="w-11 h-11 rounded-lg flex items-center justify-center"
                     style={{ background: 'var(--accent-dim)', border: '1px solid var(--accent-border)' }}>
                  <FileSpreadsheet size={20} style={{ color: 'var(--accent)' }} />
                </div>
              </div>
              
              <div className="w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-3"
                   style={{ background: 'var(--accent-dim)' }}>
                <Upload size={18} style={{ color: 'var(--accent)' }} />
              </div>
              
              <p className="font-semibold text-lg mb-1" style={{ color: 'var(--text-primary)' }}>
                Drop your bank statement here
              </p>
              <p className="text-sm mb-4" style={{ color: 'var(--text-muted)' }}>
                or click to browse files
              </p>
              <span className="text-xs px-3 py-1.5 rounded-md font-mono"
                    style={{ background: 'var(--bg-secondary)', color: 'var(--text-muted)' }}>
                Supports PDF and CSV · Max 50MB
              </span>
            </>
          )}
        </div>

        {error && (
          <div className="mt-3 p-3.5 rounded-lg flex items-center gap-2.5"
               style={{ background: 'var(--danger-bg)', border: '1px solid rgba(220,38,38,0.12)' }}>
            <AlertCircle size={16} style={{ color: 'var(--danger)' }} className="shrink-0" />
            <p className="text-sm" style={{ color: 'var(--danger)' }}>{error}</p>
          </div>
        )}

        <div className="mt-3 text-center">
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            No real data?{' '}
            <a 
              href="/sample_statement.csv" 
              download
              onClick={(e) => e.stopPropagation()}
              className="underline font-medium"
              style={{ color: 'var(--accent)' }}
            >
              Download sample statement
            </a>
            {' '}to try it out
          </p>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 stagger">
        {FEATURES.map(({ icon: Icon, title, desc }) => (
          <div key={title} className="card">
            <div className="w-9 h-9 rounded-lg flex items-center justify-center mb-3"
                 style={{ background: 'var(--accent-dim)' }}>
              <Icon size={17} style={{ color: 'var(--accent)' }} />
            </div>
            <h3 className="font-semibold text-sm mb-1" style={{ color: 'var(--text-primary)' }}>
              {title}
            </h3>
            <p className="text-sm leading-relaxed" style={{ color: 'var(--text-muted)' }}>{desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
