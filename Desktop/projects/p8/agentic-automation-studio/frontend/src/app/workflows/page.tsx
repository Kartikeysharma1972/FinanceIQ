'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Workflow, Plus, Play, Pause, Trash2, Edit } from 'lucide-react'
import { workflowsApi } from '@/utils/api'
import Navbar from '@/components/Navbar'
import ProtectedRoute from '@/components/ProtectedRoute'

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchWorkflows()
  }, [])

  const fetchWorkflows = async () => {
    try {
      const response = await workflowsApi.list()
      setWorkflows(response.data)
    } catch (error) {
      console.error('Failed to fetch workflows:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this workflow?')) return
    
    try {
      await workflowsApi.delete(id)
      fetchWorkflows()
    } catch (error) {
      console.error('Failed to delete workflow:', error)
      alert('Failed to delete workflow')
    }
  }

  const handleToggleStatus = async (id: string, currentStatus: string) => {
    try {
      if (currentStatus === 'active') {
        await workflowsApi.pause(id)
      } else {
        await workflowsApi.activate(id)
      }
      fetchWorkflows()
    } catch (error) {
      console.error('Failed to toggle workflow status:', error)
      alert('Failed to update workflow status')
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Workflows</h1>
              <p className="text-gray-600 mt-1">Manage and monitor your automation workflows</p>
            </div>
            <Link
              href="/workflows/create"
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center space-x-2 shadow-lg hover:shadow-xl transition-all"
            >
              <Plus className="w-5 h-5" />
              <span>Create Workflow</span>
            </Link>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              <p className="mt-4 text-gray-600">Loading workflows...</p>
            </div>
          ) : workflows.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gray-100 rounded-full mb-6">
                <Workflow className="w-10 h-10 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No workflows yet</h3>
              <p className="text-gray-600 mb-8">Create your first workflow to get started with automation</p>
              <Link
                href="/workflows/create"
                className="inline-flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all"
              >
                <Plus className="w-5 h-5" />
                <span>Create Workflow</span>
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {workflows.map((workflow: any) => (
                <div
                  key={workflow.id}
                  className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-all"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">{workflow.name}</h3>
                      <p className="text-sm text-gray-600 line-clamp-2">{workflow.description || 'No description'}</p>
                    </div>
                    <span
                      className={`ml-3 px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap ${
                        workflow.status === 'active'
                          ? 'bg-green-100 text-green-700'
                          : workflow.status === 'paused'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {workflow.status}
                    </span>
                  </div>

                  <div className="text-sm text-gray-600 mb-4 space-y-1">
                    <div className="flex items-center">
                      <span className="font-medium">Trigger:</span>
                      <span className="ml-2 capitalize">{workflow.trigger_type}</span>
                    </div>
                    <div className="flex items-center">
                      <span className="font-medium">Nodes:</span>
                      <span className="ml-2">{workflow.nodes?.length || 0}</span>
                    </div>
                  </div>

                  <div className="flex space-x-2 pt-4 border-t border-gray-100">
                    <Link
                      href={`/workflows/${workflow.id}`}
                      className="flex-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 px-3 py-2 rounded-lg text-sm font-medium flex items-center justify-center space-x-1 transition-colors"
                    >
                      <Edit className="w-4 h-4" />
                      <span>Edit</span>
                    </Link>
                    <button
                      onClick={() => handleToggleStatus(workflow.id, workflow.status)}
                      className="bg-yellow-50 hover:bg-yellow-100 text-yellow-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                      title={workflow.status === 'active' ? 'Pause' : 'Activate'}
                    >
                      {workflow.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    </button>
                    <button
                      onClick={() => handleDelete(workflow.id)}
                      className="bg-red-50 hover:bg-red-100 text-red-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </ProtectedRoute>
  )
}
