import { useState, useEffect } from 'react'
import { Plus, X, CheckCircle, AlertTriangle } from 'lucide-react'
import { getGoals, createGoal, getDashboard } from '@/lib/api'
import { MOCK_DASHBOARD } from '@/data/mockData'
import { formatRupee, GOAL_EMOJI, GOAL_BG } from '@/lib/utils'
import { useAuth } from '@/lib/AuthContext'
import type { Goal, GoalType } from '@/types'

const GOAL_TYPE_OPTIONS: { value: GoalType; label: string; icon: string }[] = [
  { value: 'emergency_fund', label: 'Emergency Fund', icon: '🛡️' },
  { value: 'education', label: 'Education', icon: '🎓' },
  { value: 'home_repair', label: 'Home Repair', icon: '🏡' },
  { value: 'festival', label: 'Festival', icon: '🪔' },
  { value: 'vehicle', label: 'Vehicle', icon: '🛵' },
  { value: 'custom', label: 'Custom Goal', icon: '⭐' },
]

export default function GoalsPage() {
  const { customerId, customer } = useAuth()
  const [goals, setGoals] = useState<Goal[]>([])
  const [monthlySavings, setMonthlySavings] = useState(16700)
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', type: 'emergency_fund' as GoalType, target_amount: '', target_date: '', monthly_contribution: '' })

  useEffect(() => {
    setLoading(true)
    Promise.all([
      getGoals(customerId).catch(() => MOCK_DASHBOARD.goals),
      getDashboard(customerId).catch(() => MOCK_DASHBOARD),
    ]).then(([fetchedGoals, dash]) => {
      setGoals(fetchedGoals && fetchedGoals.length > 0 ? fetchedGoals : (dash.goals || MOCK_DASHBOARD.goals))
      setMonthlySavings(dash.cash_flow?.monthly_savings || 16700)
    }).finally(() => setLoading(false))
  }, [customerId])

  const handleCreate = async () => {
    if (!form.name || !form.target_amount || !form.target_date || !form.monthly_contribution) return
    const target = parseFloat(form.target_amount)
    const monthly = parseFloat(form.monthly_contribution)

    try {
      const created = await createGoal(customerId, {
        type: form.type,
        name: form.name,
        target_amount: target,
        current_amount: 0,
        target_date: form.target_date,
        monthly_contribution: monthly,
      })
      setGoals(prev => [created, ...prev])
    } catch {
      const localGoal: Goal = {
        id: `g${Date.now()}`,
        type: form.type,
        name: form.name,
        target_amount: target,
        current_amount: 0,
        target_date: form.target_date,
        monthly_contribution: monthly,
        progress_pct: 0,
        months_remaining: Math.ceil(target / monthly),
        on_track: true,
      }
      setGoals(prev => [localGoal, ...prev])
    }
    setShowForm(false)
    setForm({ name: '', type: 'emergency_fund', target_amount: '', target_date: '', monthly_contribution: '' })
  }

  const totalSavingsRequired = goals.reduce((s, g) => s + g.monthly_contribution, 0)

  return (
    <div className="page-container fade-in">
      <div className="page-header" style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h1>Goal Planning</h1>
          <p>Set clear financial goals and track progress for {customer?.name || 'you'}.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(true)} id="add-goal-btn">
          <Plus size={16} /> New Goal
        </button>
      </div>

      {loading ? (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '40vh' }}>
          <div className="spinner spinner--lg" />
        </div>
      ) : (
        <>
          {/* Summary bar */}
          <div className="card fade-in-delay-1" style={{ marginBottom: '1.25rem', display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Active Goals</div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.625rem', fontWeight: 700, color: 'var(--color-navy)' }}>{goals.length}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Monthly Commitment</div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.625rem', fontWeight: 700, color: 'var(--color-teal)' }}>{formatRupee(totalSavingsRequired)}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>On Track</div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.625rem', fontWeight: 700, color: 'var(--color-green)' }}>{goals.filter(g => g.on_track).length} / {goals.length}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Available for Goals</div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.625rem', fontWeight: 700, color: monthlySavings - totalSavingsRequired > 0 ? 'var(--color-green)' : 'var(--color-terracotta)' }}>
                {formatRupee(monthlySavings - totalSavingsRequired, true)}
              </div>
            </div>
          </div>

          {/* Goal cards */}
          <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
            {goals.map((goal, idx) => (
              <div key={goal.id} className="goal-card fade-in" style={{ animationDelay: `${idx * 0.06}s` }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.875rem' }}>
                  <div className="goal-card-icon" style={{ background: GOAL_BG[goal.type] ?? '#f5f5f5' }}>
                    {GOAL_EMOJI[goal.type] ?? '⭐'}
                  </div>
                  <span className={`badge ${goal.on_track ? 'badge-green' : 'badge-red'}`}>
                    {goal.on_track ? (
                      <><CheckCircle size={11} /> On track</>
                    ) : (
                      <><AlertTriangle size={11} /> Behind</>
                    )}
                  </span>
                </div>
                <div className="goal-card-title">{goal.name}</div>
                <div className="goal-card-amount">{formatRupee(goal.target_amount)}</div>
                <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginBottom: '0.875rem' }}>
                  {formatRupee(goal.current_amount)} saved · {goal.months_remaining} months remaining
                </div>
                <div className="progress-bar" style={{ marginBottom: '0.5rem' }}>
                  <div
                    className="progress-fill"
                    style={{ width: `${Math.min(100, Math.max(0, goal.progress_pct))}%`, background: goal.on_track ? 'var(--color-teal)' : 'var(--color-amber)' }}
                  />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                  <span>{goal.progress_pct.toFixed(0)}% complete</span>
                  <span>{formatRupee(goal.monthly_contribution)}/mo</span>
                </div>
                <div style={{ fontSize: '0.775rem', color: 'var(--color-text-muted)', marginTop: '0.5rem' }}>
                  Target: {new Date(goal.target_date).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' })}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Create goal modal */}
      {showForm && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(26,35,50,0.45)', zIndex: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
          <div className="card card--raised" style={{ width: '100%', maxWidth: 480, maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
              <h3>Create New Goal</h3>
              <button className="btn-icon" onClick={() => setShowForm(false)} aria-label="Close">
                <X size={20} />
              </button>
            </div>

            {/* Goal type grid */}
            <div style={{ marginBottom: '1.25rem' }}>
              <label className="form-label">Goal Type</label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '0.5rem' }}>
                {GOAL_TYPE_OPTIONS.map(opt => (
                  <button
                    key={opt.value}
                    onClick={() => setForm(f => ({ ...f, type: opt.value, name: f.name || opt.label }))}
                    style={{
                      background: form.type === opt.value ? 'var(--color-saffron-pale)' : 'var(--color-ivory-dark)',
                      border: `1.5px solid ${form.type === opt.value ? 'var(--color-saffron)' : 'var(--color-border)'}`,
                      borderRadius: 'var(--radius-md)',
                      padding: '0.625rem',
                      cursor: 'pointer',
                      textAlign: 'center',
                      transition: 'all 0.15s',
                      fontFamily: 'var(--font-body)',
                    }}
                  >
                    <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>{opt.icon}</div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 500, color: form.type === opt.value ? 'var(--color-saffron)' : 'var(--color-text-secondary)' }}>{opt.label}</div>
                  </button>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label className="form-label" htmlFor="goal-name">Goal Name</label>
              <input id="goal-name" className="input" placeholder="e.g. Emergency Fund" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
              <div>
                <label className="form-label" htmlFor="goal-target">Target Amount (₹)</label>
                <input id="goal-target" type="number" className="input" placeholder="100000" value={form.target_amount} onChange={e => setForm(f => ({ ...f, target_amount: e.target.value }))} />
              </div>
              <div>
                <label className="form-label" htmlFor="goal-date">Target Date</label>
                <input id="goal-date" type="date" className="input" value={form.target_date} onChange={e => setForm(f => ({ ...f, target_date: e.target.value }))} />
              </div>
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <label className="form-label" htmlFor="goal-monthly">Monthly Contribution (₹)</label>
              <input id="goal-monthly" type="number" className="input" placeholder="5000" value={form.monthly_contribution} onChange={e => setForm(f => ({ ...f, monthly_contribution: e.target.value }))} />
              {form.target_amount && form.monthly_contribution && (
                <div className="insight-card insight-card--teal" style={{ marginTop: '0.5rem', fontSize: '0.8rem' }}>
                  At {formatRupee(parseFloat(form.monthly_contribution))}/month, you'll reach {formatRupee(parseFloat(form.target_amount))} in approximately <strong>{Math.ceil(parseFloat(form.target_amount) / parseFloat(form.monthly_contribution))} months</strong>.
                </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button className="btn btn-secondary btn-block" onClick={() => setShowForm(false)}>Cancel</button>
              <button className="btn btn-primary btn-block" onClick={handleCreate} id="save-goal-btn">Save Goal</button>
            </div>
          </div>
        </div>
      )}

      <div style={{ marginBottom: '2rem' }} />
    </div>
  )
}
