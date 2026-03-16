'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Save } from 'lucide-react'
import { workflowsApi } from '@/utils/api'
import Navbar from '@/components/Navbar'
import ProtectedRoute from '@/components/ProtectedRoute'

export default function CreateWorkflowPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    trigger_type: 'manual',
    nodes: [],
    edges: [],
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSaving(true)

    try {
      const response = await workflowsApi.create(formData)
      router.push('/workflows')
    } catch (error: any) {
      console.error('Failed to create workflow:', error)
      setError(error.response?.data?.detail || 'Failed to create workflow. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <Navbar />

        <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="mb-8">
            <Link
              href="/workflows"
              className="inline-flex items-center space-x-2 text-gray-600 hover:text-indigo-600 transition-colors mb-4"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Workflows</span>
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">Create New Workflow</h1>
            <p className="text-gray-600 mt-1">Define a new automation workflow</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Workflow Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition"
                    placeholder="e.g., Lead Qualification Pipeline"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={4}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition resize-none"
                    placeholder="Describe what this workflow does..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Trigger Type <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={formData.trigger_type}
                    onChange={(e) => setFormData({ ...formData, trigger_type: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition bg-white"
                  >
                    <option value="manual">Manual</option>
                    <option value="schedule">Schedule</option>
                    <option value="webhook">Webhook</option>
                    <option value="file_upload">File Upload</option>
                    <option value="event">Event</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={saving}
                className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white px-6 py-3 rounded-lg font-semibold flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl transition-all"
              >
                <Save className="w-5 h-5" />
                <span>{saving ? 'Creating...' : 'Create Workflow'}</span>
              </button>
              <Link
                href="/workflows"
                className="px-6 py-3 bg-white hover:bg-gray-50 text-gray-700 rounded-lg font-semibold border-2 border-gray-200 hover:border-gray-300 transition-all"
              >
                Cancel
              </Link>
            </div>
          </form>

          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-800 text-sm">
              <strong>Note:</strong> After creating the workflow, you'll be able to add nodes and configure the workflow logic in the visual builder.
            </p>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  )
}
