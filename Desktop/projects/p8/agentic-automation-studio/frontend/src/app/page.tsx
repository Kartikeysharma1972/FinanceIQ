'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Activity, Workflow, Zap, Database, Brain, ArrowRight, Sparkles } from 'lucide-react'
import Navbar from '@/components/Navbar'
import ProtectedRoute from '@/components/ProtectedRoute'
import { isAuthenticated } from '@/utils/auth'

export default function Home() {
  const router = useRouter()
  const [stats, setStats] = useState({
    workflows: 0,
    executions: 0,
    agents: 0,
    tools: 0
  })

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login')
      return
    }
    fetchStats()
  }, [router])

  const fetchStats = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL
      
      const [agentsRes, toolsRes] = await Promise.all([
        fetch(`${apiUrl}/api/agents`),
        fetch(`${apiUrl}/api/tools`)
      ])

      const agents = await agentsRes.json()
      const tools = await toolsRes.json()

      setStats({
        workflows: 0,
        executions: 0,
        agents: agents.count || 0,
        tools: tools.count || 0
      })
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  if (!isAuthenticated()) {
    return null
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
          {/* Hero Section */}
          <div className="text-center mb-12 sm:mb-16">
            <div className="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 bg-indigo-100 rounded-2xl mb-6">
              <Sparkles className="w-8 h-8 sm:w-10 sm:h-10 text-indigo-600" />
            </div>
            <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
              Build Autonomous AI Workflows
            </h1>
            <p className="text-lg sm:text-xl text-gray-600 mb-8 max-w-2xl mx-auto px-4">
              Production-grade AI automation platform running entirely on local models. 
              Create intelligent workflows that think, plan, and execute autonomously.
            </p>
            <div className="flex flex-col sm:flex-row justify-center items-center space-y-3 sm:space-y-0 sm:space-x-4 px-4">
              <Link
                href="/workflows/create"
                className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-lg font-semibold flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl transition-all"
              >
                <Workflow className="w-5 h-5" />
                <span>Create Workflow</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/workflows"
                className="w-full sm:w-auto bg-white hover:bg-gray-50 text-gray-700 px-8 py-4 rounded-lg font-semibold border-2 border-gray-200 hover:border-gray-300 transition-all shadow-sm"
              >
                View All Workflows
              </Link>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-12 sm:mb-16">
            <div className="bg-white rounded-xl p-4 sm:p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Workflow className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
                </div>
                <span className="text-2xl sm:text-3xl font-bold text-gray-900">{stats.workflows}</span>
              </div>
              <h3 className="text-sm sm:text-base text-gray-600 font-medium">Active Workflows</h3>
            </div>

            <div className="bg-white rounded-xl p-4 sm:p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <Activity className="w-5 h-5 sm:w-6 sm:h-6 text-green-600" />
                </div>
                <span className="text-2xl sm:text-3xl font-bold text-gray-900">{stats.executions}</span>
              </div>
              <h3 className="text-sm sm:text-base text-gray-600 font-medium">Total Executions</h3>
            </div>

            <div className="bg-white rounded-xl p-4 sm:p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <Brain className="w-5 h-5 sm:w-6 sm:h-6 text-purple-600" />
                </div>
                <span className="text-2xl sm:text-3xl font-bold text-gray-900">{stats.agents}</span>
              </div>
              <h3 className="text-sm sm:text-base text-gray-600 font-medium">AI Agents</h3>
            </div>

            <div className="bg-white rounded-xl p-4 sm:p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <Zap className="w-5 h-5 sm:w-6 sm:h-6 text-yellow-600" />
                </div>
                <span className="text-2xl sm:text-3xl font-bold text-gray-900">{stats.tools}</span>
              </div>
              <h3 className="text-sm sm:text-base text-gray-600 font-medium">Available Tools</h3>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
            <div className="bg-white rounded-xl p-6 sm:p-8 shadow-sm border border-gray-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 sm:w-14 sm:h-14 bg-indigo-100 rounded-xl flex items-center justify-center mb-6">
                <Brain className="w-6 h-6 sm:w-7 sm:h-7 text-indigo-600" />
              </div>
              <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3">Autonomous Agents</h3>
              <p className="text-gray-600 leading-relaxed text-sm sm:text-base">
                AI agents with Observe-Plan-Execute-Evaluate reasoning loops that make intelligent decisions and adapt to complex scenarios.
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 sm:p-8 shadow-sm border border-gray-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 sm:w-14 sm:h-14 bg-blue-100 rounded-xl flex items-center justify-center mb-6">
                <Workflow className="w-6 h-6 sm:w-7 sm:h-7 text-blue-600" />
              </div>
              <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3">Visual Workflow Builder</h3>
              <p className="text-gray-600 leading-relaxed text-sm sm:text-base">
                Drag-and-drop interface to design complex automation pipelines with conditional logic and multi-agent collaboration.
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 sm:p-8 shadow-sm border border-gray-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 sm:w-14 sm:h-14 bg-green-100 rounded-xl flex items-center justify-center mb-6">
                <Database className="w-6 h-6 sm:w-7 sm:h-7 text-green-600" />
              </div>
              <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-3">100% Local & Open Source</h3>
              <p className="text-gray-600 leading-relaxed text-sm sm:text-base">
                Runs entirely on local LLMs via Ollama - no paid APIs, no external dependencies, complete privacy and control.
              </p>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
