import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  ArrowRight,
  ChevronRight,
  PieChart,
  HandCoins,
  MessageCircle,
  Target,
  CheckCircle,
} from 'lucide-react'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts'
import { getDashboard } from '@/lib/api'
import { formatRupee, formatRelativeDate, CATEGORY_EMOJI, CATEGORY_BG, getHealthColor } from '@/lib/utils'
import { useAuth } from '@/lib/AuthContext'
import { GlowCard } from '@/components/ui/glowing-effect'
import type { DashboardData } from '@/types'

function HealthScoreRing({ score }: { score: number }) {
  const radius = 54
  const circumference = 2 * Math.PI * radius
  const progress = (score / 100) * circumference
  const color = getHealthColor(score)

  return (
    <div className="health-ring-wrapper">
      <svg width="140" height="140" viewBox="0 0 140 140" aria-label={`Financial health score: ${score} out of 100`}>
        <circle cx="70" cy="70" r={radius} fill="none" stroke="var(--color-border-light)" strokeWidth="10" />
        <circle
          cx="70" cy="70" r={radius}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={circumference - progress}
          strokeLinecap="round"
          transform="rotate(-90 70 70)"
          style={{ transition: 'stroke-dashoffset 1s ease' }}
        />
        <text x="70" y="65" textAnchor="middle" className="score-ring-label" style={{ fill: 'var(--color-navy)' }}>
          {score}
        </text>
        <text x="70" y="82" textAnchor="middle" className="score-ring-sub" style={{ fill: 'var(--color-text-muted)', fontSize: '11px', fontFamily: 'Inter, sans-serif' }}>
          /100
        </text>
      </svg>
    </div>
  )
}

interface QuickAction {
  label: string
  icon: React.ElementType
  to: string
  color: string
  bg: string
}

const QUICK_ACTIONS: QuickAction[] = [
  { label: 'View Spending', icon: PieChart, to: '/spending', color: 'var(--color-teal)', bg: 'var(--color-teal-pale)' },
  { label: 'Plan a Goal', icon: Target, to: '/goals', color: 'var(--color-green)', bg: 'var(--color-green-pale)' },
  { label: 'Explore Borrowing', icon: HandCoins, to: '/borrowing', color: 'var(--color-saffron)', bg: 'var(--color-saffron-pale)' },
  { label: 'Ask Saarthi', icon: MessageCircle, to: '/assistant', color: 'var(--color-navy)', bg: '#e8ecf2' },
]

export default function DashboardPage() {
  const { customerId, customer } = useAuth()
  const navigate = useNavigate()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDashboard(customerId)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [customerId])

  if (loading) return (
    <div className="page-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', flexDirection: 'column', gap: '1rem' }}>
      <div className="spinner spinner--lg" />
      <p className="text-muted">Loading your dashboard…</p>
    </div>
  )

  if (!data) return (
    <div className="page-container">
      <div className="alert-banner alert-banner--danger">
        <AlertTriangle size={18} />
        <span>Failed to load dashboard. Please refresh the page.</span>
      </div>
    </div>
  )

  const { financial_health, cash_flow, recommendation, alerts, recent_transactions, monthly_trend } = data
  const highAlert = alerts.find(a => a.severity === 'high' || a.severity === 'critical')
  const mediumAlert = alerts.find(a => a.severity === 'medium')
  const topAlert = highAlert ?? mediumAlert

  const greetingTime = new Date().getHours()
  const greeting = greetingTime < 12 ? 'Good morning' : greetingTime < 17 ? 'Good afternoon' : 'Good evening'

  // Health score trend: pick the right icon/copy instead of always showing "up"
  const healthChange = financial_health.change
  const HealthTrendIcon = healthChange > 0 ? TrendingUp : healthChange < 0 ? TrendingDown : Minus
  const healthTrendColor = healthChange > 0 ? 'var(--color-green)' : healthChange < 0 ? 'var(--color-terracotta)' : 'var(--color-text-muted)'
  const healthTrendText = healthChange === 0
    ? 'No change from last month'
    : `${Math.abs(healthChange)} pts ${healthChange > 0 ? 'up' : 'down'} from last month`

  return (
    <div className="page-container fade-in">
      {/* Greeting */}
      <div className="page-header">
        <h1 style={{ fontFamily: 'var(--font-display)' }}>
          {greeting}, {customer?.name?.split(' ')[0]} 👋
        </h1>
        <p>{customer?.city}, {customer?.state} · {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}</p>
      </div>

      {/* Alert banner if present */}
      {topAlert && (
        <div
          className={`alert-banner ${topAlert.severity === 'high' || topAlert.severity === 'critical' ? 'alert-banner--danger' : 'alert-banner--warning'} fade-in`}
          style={{ marginBottom: '1.5rem', cursor: 'pointer' }}
          onClick={() => navigate('/alerts')}
          role="button"
          tabIndex={0}
          onKeyDown={e => e.key === 'Enter' && navigate('/alerts')}
          aria-label={`Alert: ${topAlert.title}. Click to view all alerts.`}
        >
          <AlertTriangle size={18} style={{ flexShrink: 0, marginTop: 2 }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.2rem' }}>{topAlert.title}</div>
            <div style={{ fontSize: '0.8125rem', opacity: 0.85 }}>{topAlert.description}</div>
          </div>
          <ChevronRight size={16} style={{ flexShrink: 0 }} />
        </div>
      )}

      {/* Health Score + Cash Flow row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 2fr)', gap: '1rem', marginBottom: '1rem' }}>
        {/* Health score card */}
        <GlowCard
          className="fade-in-delay-1"
          proximity={90}
          style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '1.5rem 1rem', textAlign: 'center' }}
        >
          <div style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)', marginBottom: '0.75rem' }}>
            Financial Health
          </div>
          <HealthScoreRing score={financial_health.score} />
          <div style={{ marginTop: '0.5rem' }}>
            <span className="badge badge-teal">{financial_health.label}</span>
            <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.25rem', justifyContent: 'center' }}>
              <HealthTrendIcon size={13} style={{ color: healthTrendColor }} />
              {healthTrendText}
            </div>
          </div>
          <button
            className="btn btn-ghost btn-sm"
            style={{ marginTop: '1rem', width: '100%' }}
            onClick={() => navigate('/borrowing')}
          >
            View Details
          </button>
        </GlowCard>

        {/* Cash flow cards */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.875rem' }}>
          <GlowCard baseClass="stat-card" className="fade-in-delay-1" proximity={80}>
            <div className="stat-card-label">Monthly Income</div>
            <div className="stat-card-value" style={{ color: 'var(--color-green)' }}>{formatRupee(cash_flow.monthly_income, true)}</div>
            <div className="stat-card-sub">Stable for 6 months</div>
          </GlowCard>
          <GlowCard baseClass="stat-card" className="fade-in-delay-2" proximity={80}>
            <div className="stat-card-label">Monthly Expenses</div>
            <div className="stat-card-value">{formatRupee(cash_flow.monthly_expenses, true)}</div>
            <div className="stat-card-change stat-card-change--down">
              <TrendingUp size={12} /> +12% vs last month
            </div>
          </GlowCard>
          <GlowCard baseClass="stat-card" className="fade-in-delay-3" proximity={80}>
            <div className="stat-card-label">EMI Payments</div>
            <div className="stat-card-value">{formatRupee(cash_flow.monthly_emi, true)}</div>
            <div className="stat-card-sub">16.4% of income</div>
          </GlowCard>
          <GlowCard baseClass="stat-card" className="fade-in-delay-4" proximity={80}>
            <div className="stat-card-label">Monthly Savings</div>
            <div className="stat-card-value" style={{ color: 'var(--color-teal)' }}>{formatRupee(cash_flow.monthly_savings, true)}</div>
            <div className="stat-card-change stat-card-change--up">
              <CheckCircle size={12} />
              {cash_flow.savings_rate > 0 ? `${cash_flow.savings_rate}% savings rate` : 'No savings set aside this month'}
            </div>
          </GlowCard>
        </div>
      </div>

      {/* Trend chart */}
      <GlowCard className="fade-in-delay-2" proximity={100} style={{ marginBottom: '1rem' }}>
        <div className="section-title">Income vs Expenses — Last 6 Months</div>
        <div style={{ width: '100%', height: 240, minHeight: 240 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={monthly_trend} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" />
              <XAxis dataKey="month" tick={{ fontSize: 12, fill: 'var(--color-text-muted)' }} />
              <YAxis tick={{ fontSize: 11, fill: 'var(--color-text-muted)' }} tickFormatter={v => `₹${Math.round(v / 1000)}K`} />
              <Tooltip formatter={(v: any) => [formatRupee(Number(v) || 0), '']} labelStyle={{ fontWeight: 600 }} contentStyle={{ borderRadius: 8, border: '1px solid var(--color-border-light)', fontSize: 13 }} />
              <Area type="monotone" dataKey="income" stroke="#0d7c6e" fill="rgba(13,124,110,0.12)" strokeWidth={2} name="Income" />
              <Area type="monotone" dataKey="expenses" stroke="#e8770a" fill="rgba(232,119,10,0.12)" strokeWidth={2} name="Expenses" />
              <Area type="monotone" dataKey="savings" stroke="#2d7a4f" fill="rgba(45,122,79,0.12)" strokeWidth={2} name="Savings" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </GlowCard>

      {/* Next best step + quick actions row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        {/* Recommendation */}
        <GlowCard className="rec-card fade-in-delay-2" proximity={90}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <div className="step-badge">✦</div>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-saffron)' }}>Your Next Best Step</span>
          </div>
          <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>{recommendation.title}</h3>
          <p style={{ fontSize: '0.8375rem', color: 'var(--color-text-secondary)', marginBottom: '0.875rem', lineHeight: 1.55 }}>
            {recommendation.why[0]} — {recommendation.why[2]}
          </p>
          <div className="rec-card-confidence">
            <CheckCircle size={14} />
            {Math.round(recommendation.confidence * 100)}% confidence
          </div>
          <div style={{ marginTop: '1rem' }}>
            <button className="btn btn-primary btn-sm" onClick={() => navigate('/borrowing')}>
              See full guidance <ArrowRight size={14} />
            </button>
          </div>
        </GlowCard>

        {/* Quick actions */}
        <GlowCard className="fade-in-delay-3" proximity={90} style={{ background: 'var(--color-surface)' }}>
          <div className="section-title" style={{ marginBottom: '0.875rem' }}>Quick Actions</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.625rem' }}>
            {QUICK_ACTIONS.map(({ label, icon: Icon, to, color, bg }) => (
              <button
                key={label}
                onClick={() => navigate(to)}
                style={{
                  background: bg,
                  border: 'none',
                  borderRadius: 'var(--radius-md)',
                  padding: '0.75rem',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.5rem',
                }}
                className="btn-icon"
                aria-label={label}
              >
                <Icon size={20} style={{ color }} />
                <span style={{ fontSize: '0.8rem', fontWeight: 500, color: 'var(--color-navy)' }}>{label}</span>
              </button>
            ))}
          </div>
        </GlowCard>
      </div>

      {/* Recent transactions */}
      <GlowCard className="fade-in-delay-3" proximity={100}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <div className="section-title" style={{ margin: 0 }}>Recent Transactions</div>
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/spending')}>
            View all <ChevronRight size={14} />
          </button>
        </div>
        {recent_transactions.map(txn => (
          <div key={txn.id} className="txn-row">
            <div
              className="txn-icon"
              style={{ background: CATEGORY_BG[txn.category] ?? '#f5f5f5' }}
              aria-hidden
            >
              {CATEGORY_EMOJI[txn.category] ?? '📄'}
            </div>
            <div className="txn-details">
              <div className="txn-merchant">{txn.merchant}</div>
              <div className="txn-category">
                {txn.category} · {formatRelativeDate(txn.date)}
                {txn.recurring && <span className="badge badge-navy" style={{ marginLeft: '0.375rem', padding: '0.1rem 0.5rem', fontSize: '0.7rem' }}>Recurring</span>}
              </div>
            </div>
            <div className={`txn-amount ${txn.type === 'debit' ? 'txn-amount--debit' : 'txn-amount--credit'}`}>
              {txn.type === 'debit' ? '−' : '+'}{formatRupee(txn.amount)}
            </div>
          </div>
        ))}
      </GlowCard>

      {/* Health explanation card */}
      <GlowCard style={{ marginTop: '1rem' }} proximity={100}>
        <div className="section-title">Financial Health Breakdown</div>
        {Object.entries(financial_health.components).map(([key, val]) => {
          const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
          const color = val >= 75 ? 'var(--color-green)' : val >= 55 ? 'var(--color-teal)' : 'var(--color-amber)'
          return (
            <div key={key} className="score-component-row">
              <div className="score-component-label">{label}</div>
              <div className="score-component-bar-wrap">
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${val}%`, background: color }}
                  />
                </div>
              </div>
              <div className="score-component-value" style={{ color }}>{val}</div>
            </div>
          )
        })}
        <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {financial_health.positive_factors.map(f => (
            <div key={f} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', fontSize: '0.8125rem' }}>
              <CheckCircle size={14} style={{ color: 'var(--color-green)', flexShrink: 0, marginTop: 2 }} />
              <span style={{ color: 'var(--color-text-secondary)' }}>{f}</span>
            </div>
          ))}
          {financial_health.risk_factors.map(f => (
            <div key={f} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', fontSize: '0.8125rem' }}>
              <AlertTriangle size={14} style={{ color: 'var(--color-amber)', flexShrink: 0, marginTop: 2 }} />
              <span style={{ color: 'var(--color-text-secondary)' }}>{f}</span>
            </div>
          ))}
        </div>
      </GlowCard>

      <div style={{ marginBottom: '2rem' }} />
    </div>
  )
}