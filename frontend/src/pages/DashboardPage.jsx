import { useState } from 'react'
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts'
import {
  TrendingUp, TrendingDown, DollarSign, Percent, AlertTriangle,
  CheckCircle, Info, ChevronLeft, ChevronRight, Download, Star,
  Calendar, Layers, Target, CreditCard, Zap
} from 'lucide-react'
import ChatPanel from './ChatPanel'

const COLORS = [
  '#2563eb', '#0891b2', '#7c3aed', '#ea580c', '#db2777',
  '#ca8a04', '#65a30d', '#0284c7', '#a855f7', '#e11d48', '#16a34a', '#f97316'
]

const CATEGORY_COLORS = {
  'Food & Dining': '#ea580c',
  'Transport': '#2563eb',
  'Shopping': '#7c3aed',
  'Entertainment': '#db2777',
  'Utilities': '#ca8a04',
  'Healthcare': '#059669',
  'Rent/Housing': '#dc2626',
  'Salary/Income': '#16a34a',
  'Freelance Income': '#65a30d',
  'Subscriptions': '#6366f1',
  'Personal Care': '#0891b2',
  'Miscellaneous': '#6b7280',
}

function SummaryCard({ icon: Icon, label, value, sub, color }) {
  return (
    <div className="card animate-slide-up" style={{ borderLeft: `3px solid ${color}` }}>
      <div className="flex items-start justify-between mb-3">
        <div className="w-9 h-9 rounded-lg flex items-center justify-center"
             style={{ background: `${color}10` }}>
          <Icon size={17} style={{ color }} />
        </div>
      </div>
      <p className="text-xs font-medium mb-1" style={{ color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{label}</p>
      <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>{value}</p>
      {sub && <p className="text-xs mt-1.5" style={{ color: 'var(--text-muted)' }}>{sub}</p>}
    </div>
  )
}

function InsightCard({ insight }) {
  const typeConfig = {
    warning: { icon: AlertTriangle, color: '#d97706', bg: 'var(--warning-bg)', border: 'rgba(217,119,6,0.15)' },
    positive: { icon: CheckCircle, color: '#059669', bg: 'var(--success-bg)', border: 'rgba(5,150,105,0.15)' },
    neutral: { icon: Info, color: '#6366f1', bg: 'rgba(99,102,241,0.06)', border: 'rgba(99,102,241,0.15)' },
  }
  
  const config = typeConfig[insight.type] || typeConfig.neutral
  const Icon = config.icon

  return (
    <div className="p-4 rounded-lg" style={{ background: config.bg, border: `1px solid ${config.border}` }}>
      <div className="flex items-start gap-3">
        <Icon size={15} style={{ color: config.color, marginTop: 2 }} className="shrink-0" />
        <div>
          <p className="font-semibold text-sm mb-1" style={{ color: 'var(--text-primary)' }}>
            {insight.title}
          </p>
          <p className="text-sm leading-relaxed" style={{ color: 'var(--text-muted)' }}>
            {insight.detail}
          </p>
        </div>
      </div>
    </div>
  )
}

const IMPACT_CONFIG = {
  High: { color: '#dc2626', bg: 'var(--danger-bg)' },
  Medium: { color: '#d97706', bg: 'var(--warning-bg)' },
  Low: { color: '#6b7280', bg: 'rgba(107,114,128,0.08)' },
}

const CustomTooltipStyle = {
  background: '#ffffff',
  border: '1px solid #e5e7eb',
  borderRadius: 8,
  color: '#111827',
  fontFamily: 'Inter, sans-serif',
  fontSize: 13,
  boxShadow: '0 4px 12px rgba(0,0,0,0.08)'
}

// Custom Legend for Pie chart with color dots + category names
function CustomPieLegend({ payload }) {
  return (
    <div className="flex flex-wrap justify-center gap-x-4 gap-y-1.5 mt-2">
      {payload.map((entry, idx) => (
        <div key={idx} className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: entry.color }} />
          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>{entry.value}</span>
        </div>
      ))}
    </div>
  )
}

// Format month label: "2024-01" → "Jan '24"
function formatMonth(m) {
  if (!m) return m
  const parts = m.split('-')
  if (parts.length !== 2) return m
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  const monthIdx = parseInt(parts[1], 10) - 1
  return `${months[monthIdx] || parts[1]} '${parts[0].slice(2)}`
}

export default function DashboardPage({ report }) {
  const [txPage, setTxPage] = useState(0)
  const [chatOpen, setChatOpen] = useState(false)
  const TX_PER_PAGE = 10

  const { summary, categories, monthly, top_expenses, insights, action_items, suggested_budget, transactions } = report
  // The session_id is needed for chat — derive from report or pass it
  const sessionId = report._sessionId

  // Prepare pie chart data — backend sends "category" key
  const pieData = (categories || []).map(c => ({
    category: c.category,
    amount: parseFloat(c.amount) || 0,
    percentage: c.percentage,
  })).filter(c => c.amount > 0)

  // Prepare monthly chart data
  const allMonths = [...new Set([
    ...Object.keys(monthly?.expenses || {}),
    ...Object.keys(monthly?.income || {})
  ])].sort()

  const monthlyData = allMonths.map(month => ({
    month: formatMonth(month),
    Expenses: parseFloat(monthly?.expenses?.[month]) || 0,
    Income: parseFloat(monthly?.income?.[month]) || 0,
  }))

  const txSlice = (transactions || []).slice(txPage * TX_PER_PAGE, (txPage + 1) * TX_PER_PAGE)
  const totalPages = Math.ceil((transactions || []).length / TX_PER_PAGE)

  const budgetPercentages = suggested_budget?.percentages || {}
  const emergencyFund = suggested_budget?.emergency_fund || {}
  const motivational = suggested_budget?.motivational_insight || ''

  // Report quality warnings
  const warnings = []
  if (!categories || categories.length === 0) warnings.push('Category breakdown is not available')
  if (monthlyData.length === 0) warnings.push('Monthly trend data could not be computed')
  if (!insights || insights.length === 0) warnings.push('AI insights were not generated')
  if (!action_items || action_items.length === 0) warnings.push('Action items were not generated')
  if (report.errors && report.errors.length > 0) {
    report.errors.forEach(e => warnings.push(e))
  }

  return (
    <div className="animate-fade-in space-y-6">
      {/* Title + Download */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-2xl font-bold" style={{ color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            Financial Report
          </h2>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            {summary.transaction_count} transactions analyzed · {new Date(report.generated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
          </p>
        </div>
        <button
          onClick={() => window.print()}
          className="no-print btn-secondary flex items-center gap-2"
        >
          <Download size={15} />
          Export PDF
        </button>
      </div>

      {/* Report Warnings */}
      {warnings.length > 0 && (
        <div className="p-4 rounded-lg" style={{ background: 'var(--warning-bg)', border: '1px solid rgba(217,119,6,0.15)' }}>
          <div className="flex items-start gap-2.5">
            <AlertTriangle size={16} style={{ color: '#d97706', marginTop: 2 }} className="shrink-0" />
            <div>
              <p className="font-semibold text-sm mb-1" style={{ color: '#92400e' }}>Report Notes</p>
              <ul className="text-sm space-y-0.5" style={{ color: '#92400e' }}>
                {warnings.map((w, i) => <li key={i}>• {w}</li>)}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 stagger">
        <SummaryCard
          icon={TrendingUp}
          label="Total Income"
          value={`$${(summary.total_income || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          color="#059669"
        />
        <SummaryCard
          icon={TrendingDown}
          label="Total Expenses"
          value={`$${(summary.total_expenses || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          sub={`$${summary.daily_avg_spending || 0}/day avg`}
          color="#dc2626"
        />
        <SummaryCard
          icon={DollarSign}
          label="Net Savings"
          value={`$${(summary.net_savings || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          color={summary.net_savings >= 0 ? '#059669' : '#dc2626'}
        />
        <SummaryCard
          icon={Percent}
          label="Savings Rate"
          value={summary.savings_rate || '0%'}
          sub={`$${summary.subscription_total || 0}/mo subscriptions`}
          color="#6366f1"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Pie Chart */}
        <div className="card">
          <h3 className="font-semibold text-sm mb-4" style={{ color: 'var(--text-primary)' }}>
            Spending by Category
          </h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  dataKey="amount"
                  nameKey="category"
                  cx="50%"
                  cy="45%"
                  outerRadius={90}
                  innerRadius={48}
                  paddingAngle={2}
                  strokeWidth={0}
                  label={({ category, percentage }) => `${percentage}%`}
                  labelLine={false}
                >
                  {pieData.map((entry, idx) => (
                    <Cell 
                      key={entry.category} 
                      fill={CATEGORY_COLORS[entry.category] || COLORS[idx % COLORS.length]} 
                    />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value, name) => [`$${Number(value).toFixed(2)}`, name]}
                  contentStyle={CustomTooltipStyle}
                />
                <Legend content={<CustomPieLegend />} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center" style={{ color: 'var(--text-muted)' }}>
              <p className="text-sm">No category data available</p>
            </div>
          )}
        </div>

        {/* Bar Chart */}
        <div className="card">
          <h3 className="font-semibold text-sm mb-4" style={{ color: 'var(--text-primary)' }}>
            Monthly Income vs Expenses
          </h3>
          {monthlyData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={monthlyData} barGap={4}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis dataKey="month" tick={{ fill: '#6b7280', fontSize: 11 }} tickLine={false} axisLine={{ stroke: '#e5e7eb' }} />
                <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} tickFormatter={v => `$${v.toLocaleString()}`} tickLine={false} axisLine={{ stroke: '#e5e7eb' }} />
                <Tooltip
                  formatter={(v, name) => [`$${Number(v).toFixed(2)}`, name]}
                  contentStyle={CustomTooltipStyle}
                />
                <Legend formatter={(v) => <span style={{ color: '#6b7280', fontSize: 11 }}>{v}</span>} />
                <Bar dataKey="Income" fill="#059669" radius={[4,4,0,0]} />
                <Bar dataKey="Expenses" fill="#dc2626" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center gap-2" style={{ color: 'var(--text-muted)' }}>
              <Calendar size={24} style={{ opacity: 0.4 }} />
              <p className="text-sm">Monthly data not available</p>
              <p className="text-xs">Statement may not contain enough date range</p>
            </div>
          )}
        </div>
      </div>

      {/* Insights Panel */}
      {insights && insights.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-sm mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <Zap size={16} style={{ color: 'var(--accent)' }} />
            Key Insights
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 stagger">
            {insights.map((insight, i) => (
              <InsightCard key={i} insight={insight} />
            ))}
          </div>
        </div>
      )}

      {/* Action Items */}
      {action_items && action_items.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-sm mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <Target size={16} style={{ color: 'var(--accent)' }} />
            Recommended Actions
          </h3>
          <div className="space-y-2.5 stagger">
            {action_items.map((item, i) => {
              const impact = item.impact || 'Medium'
              const cfg = IMPACT_CONFIG[impact] || IMPACT_CONFIG.Medium
              return (
                <div key={i} className="flex items-start gap-3.5 p-3.5 rounded-lg"
                     style={{ background: 'var(--bg-primary)', border: '1px solid var(--border)' }}>
                  <div className="w-7 h-7 rounded-full shrink-0 flex items-center justify-center font-bold text-xs"
                       style={{ background: 'var(--accent-dim)', color: 'var(--accent)' }}>
                    {item.rank || i + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm leading-relaxed" style={{ color: 'var(--text-primary)' }}>
                      {item.action}
                    </p>
                    {item.monthly_savings > 0 && (
                      <p className="text-xs mt-1.5 font-mono font-medium" style={{ color: 'var(--success)' }}>
                        Potential saving: ${item.monthly_savings}/month
                      </p>
                    )}
                  </div>
                  <span className="badge shrink-0"
                        style={{ background: cfg.bg, color: cfg.color }}>
                    {impact}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Budget + Emergency Fund Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Suggested Budget */}
        {Object.keys(budgetPercentages).length > 0 && (
          <div className="card">
            <h3 className="font-semibold text-sm mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
              <Layers size={16} style={{ color: 'var(--accent)' }} />
              Suggested Budget Allocation
            </h3>
            <div className="space-y-3">
              {Object.entries(budgetPercentages).map(([cat, pct]) => (
                <div key={cat}>
                  <div className="flex justify-between text-sm mb-1">
                    <span style={{ color: 'var(--text-secondary)' }}>{cat}</span>
                    <span className="font-mono text-xs font-medium" style={{ color: 'var(--accent)' }}>{pct}%</span>
                  </div>
                  <div className="h-1.5 rounded-full" style={{ background: 'var(--bg-secondary)' }}>
                    <div className="h-1.5 rounded-full transition-all"
                         style={{ 
                           width: `${Math.min(pct, 100)}%`,
                           background: 'var(--accent)',
                           opacity: 0.8
                         }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Emergency Fund */}
        <div className="card">
          <h3 className="font-semibold text-sm mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <Calendar size={16} style={{ color: 'var(--accent)' }} />
            Emergency Fund Plan
          </h3>
          {emergencyFund.recommended_amount ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg" style={{ background: 'var(--bg-primary)', border: '1px solid var(--border)' }}>
                  <p className="text-xs font-medium" style={{ color: 'var(--text-muted)' }}>Target</p>
                  <p className="text-lg font-bold mt-0.5" style={{ color: 'var(--accent)' }}>
                    ${emergencyFund.recommended_amount?.toLocaleString()}
                  </p>
                </div>
                <div className="p-3 rounded-lg" style={{ background: 'var(--bg-primary)', border: '1px solid var(--border)' }}>
                  <p className="text-xs font-medium" style={{ color: 'var(--text-muted)' }}>Timeline</p>
                  <p className="text-lg font-bold mt-0.5" style={{ color: 'var(--text-primary)' }}>
                    {emergencyFund.months_to_goal} mo
                  </p>
                </div>
              </div>
              {emergencyFund.advice && (
                <p className="text-sm leading-relaxed" style={{ color: 'var(--text-muted)' }}>
                  {emergencyFund.advice}
                </p>
              )}
            </div>
          ) : (
            <p className="text-sm leading-relaxed" style={{ color: 'var(--text-muted)' }}>
              Aim to save 3–6 months of expenses (${((summary.total_expenses || 0) * 4).toLocaleString()}) in a high-yield savings account.
            </p>
          )}
          
          {motivational && (
            <div className="mt-4 p-3.5 rounded-lg flex gap-3" 
                 style={{ background: 'var(--accent-dim)', border: '1px solid var(--accent-border)' }}>
              <Star size={14} style={{ color: 'var(--accent)', marginTop: 2 }} className="shrink-0" />
              <p className="text-sm italic leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                "{motivational}"
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Top Expenses */}
      {top_expenses && top_expenses.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-sm mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <CreditCard size={16} style={{ color: 'var(--accent)' }} />
            Largest Expenses
          </h3>
          <div className="space-y-2">
            {top_expenses.map((tx, i) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-lg"
                   style={{ background: 'var(--bg-primary)', border: '1px solid var(--border)' }}>
                <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-mono font-medium shrink-0"
                     style={{ background: 'var(--danger-bg)', color: 'var(--danger)' }}>
                  {i + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm truncate font-medium" style={{ color: 'var(--text-primary)' }}>
                    {tx.description}
                  </p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                    {tx.category} · {tx.date}
                  </p>
                </div>
                <p className="font-mono font-semibold text-sm shrink-0" style={{ color: 'var(--danger)' }}>
                  -${Number(tx.amount).toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Transactions Table */}
      {transactions && transactions.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-sm flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
              <Layers size={16} style={{ color: 'var(--accent)' }} />
              All Transactions
              <span className="text-xs font-normal" style={{ color: 'var(--text-muted)' }}>
                ({transactions.length})
              </span>
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border)' }}>
                  {['Date', 'Description', 'Category', 'Amount', 'Type'].map(h => (
                    <th key={h} className="pb-3 text-left font-medium text-xs" 
                        style={{ color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {txSlice.map((tx, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid var(--border-light)' }}>
                    <td className="py-2.5 pr-4 font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
                      {tx.date}
                    </td>
                    <td className="py-2.5 pr-4 max-w-xs truncate" style={{ color: 'var(--text-primary)' }}>
                      {tx.description}
                    </td>
                    <td className="py-2.5 pr-4">
                      <span className="badge"
                            style={{ 
                              background: `${CATEGORY_COLORS[tx.category] || '#6b7280'}10`,
                              color: CATEGORY_COLORS[tx.category] || '#6b7280'
                            }}>
                        {tx.category || 'Misc'}
                      </span>
                    </td>
                    <td className="py-2.5 pr-4 font-mono text-sm font-medium"
                        style={{ color: tx.type === 'credit' ? '#059669' : '#dc2626' }}>
                      {tx.type === 'credit' ? '+' : '-'}${Number(tx.amount).toFixed(2)}
                    </td>
                    <td className="py-2.5">
                      <span className="badge"
                            style={{ 
                              background: tx.type === 'credit' ? 'var(--success-bg)' : 'var(--danger-bg)',
                              color: tx.type === 'credit' ? '#059669' : '#dc2626'
                            }}>
                        {tx.type}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4 pt-4" 
                 style={{ borderTop: '1px solid var(--border)' }}>
              <button
                onClick={() => setTxPage(p => Math.max(0, p - 1))}
                disabled={txPage === 0}
                className="btn-secondary flex items-center gap-1 disabled:opacity-40"
                style={{ padding: '6px 12px', fontSize: '13px' }}
              >
                <ChevronLeft size={14} /> Prev
              </button>
              <span className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
                {txPage + 1} / {totalPages}
              </span>
              <button
                onClick={() => setTxPage(p => Math.min(totalPages - 1, p + 1))}
                disabled={txPage === totalPages - 1}
                className="btn-secondary flex items-center gap-1 disabled:opacity-40"
                style={{ padding: '6px 12px', fontSize: '13px' }}
              >
                Next <ChevronRight size={14} />
              </button>
            </div>
          )}
        </div>
      )}

      {/* Reflection note */}
      {report.reflection && (
        <div className="p-3.5 rounded-lg flex gap-2.5" 
             style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
          <Info size={14} style={{ color: 'var(--text-muted)', marginTop: 2 }} className="shrink-0" />
          <p className="text-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>
            <span className="font-medium" style={{ color: 'var(--text-secondary)' }}>Quality Note: </span>
            {report.reflection}
          </p>
        </div>
      )}

      {/* Chat Panel */}
      <ChatPanel 
        sessionId={sessionId}
        isOpen={chatOpen}
        onToggle={() => setChatOpen(!chatOpen)}
      />
    </div>
  )
}
