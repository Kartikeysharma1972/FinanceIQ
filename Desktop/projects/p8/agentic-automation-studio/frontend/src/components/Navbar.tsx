'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Brain, Workflow, Activity, Zap, LogOut, User } from 'lucide-react'
import { getStoredAuth, logout } from '@/utils/auth'
import { useState, useEffect } from 'react'

export default function Navbar() {
  const router = useRouter()
  const [user, setUser] = useState<{ name: string; email: string } | null>(null)

  useEffect(() => {
    const auth = getStoredAuth()
    setUser(auth.user)
  }, [])

  const handleLogout = () => {
    logout()
  }

  if (!user) {
    return null
  }

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link href="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">Agentic Studio</span>
          </Link>

          <div className="flex items-center space-x-1">
            <Link
              href="/workflows"
              className="px-3 sm:px-4 py-2 text-gray-700 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
            >
              <Workflow className="w-4 h-4" />
              <span className="hidden sm:inline">Workflows</span>
            </Link>
            <Link
              href="/executions"
              className="px-3 sm:px-4 py-2 text-gray-700 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
            >
              <Activity className="w-4 h-4" />
              <span className="hidden sm:inline">Executions</span>
            </Link>
            <Link
              href="/agents"
              className="px-3 sm:px-4 py-2 text-gray-700 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
            >
              <Zap className="w-4 h-4" />
              <span className="hidden sm:inline">Agents</span>
            </Link>
            
            <div className="ml-2 sm:ml-4 pl-2 sm:pl-4 border-l border-gray-200 flex items-center space-x-2 sm:space-x-4">
              <div className="hidden sm:flex items-center space-x-2 text-sm text-gray-600">
                <User className="w-4 h-4" />
                <span className="font-medium">{user.name}</span>
              </div>
              <button
                onClick={handleLogout}
                className="px-3 sm:px-4 py-2 text-gray-700 hover:text-red-600 hover:bg-red-50 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
