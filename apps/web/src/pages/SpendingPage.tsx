import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, RefreshCw } from 'lucide-react'
import {
  PieChart as RPieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from 'recharts'
import { getDashboard } from '@/lib/api'
import { MOCK_DASHBOARD } from '@/data/mockData'
import { formatRupee, CATEGORY_BG } from '@/lib/utils'
import { useAuth } from '@/lib/AuthContext'
import { useI18n } from '@/lib/i18n'
import { GlowCard } from '@/components/ui/glowing-effect'
import type { DashboardData } from '@/types'

const INSIGHTS_EN = [
  { text: 'Your grocery spend is higher than previous months. Consider a weekly budget to control this.', type: 'saffron' },
  { text: 'Discretionary and shopping spend rose recently. Review recurring purchases.', type: 'saffron' },
  { text: 'Utilities and rent remain stable — great consistency!', type: 'teal' },
  { text: 'Always keep an emergency buffer before taking on any new recurring commitments.', type: 'teal' },
]
const INSIGHTS_HI = [
  { text: 'किराने का खर्च पिछले महीनों से ज़्यादा है। साप्ताहिक बजट बनाएं।', type: 'saffron' },
  { text: 'गैर-जरूरी खर्च बढ़ा है — अपनी ऑनलाइन खरीदारी पर नज़र रखें।', type: 'saffron' },
  { text: 'किराया और बिजली बिल स्थिर हैं — बहुत अच्छा!', type: 'teal' },
  { text: 'नया कर्ज या खर्च करने से पहले हमेशा इमरजेंसी फंड को प्राथमिकता दें।', type: 'teal' },
]

export default function SpendingPage() {
  const { customerId, customer, language } = useAuth()
  const { t } = useI18n()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getDashboard(customerId)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [customerId])

  const spending_categories = data?.spending_categories || MOCK_DASHBOARD.spending_categories
  const monthly_trend = data?.monthly_trend || MOCK_DASHBOARD.monthly_trend
  const recent_txns = data?.recent_transactions || MOCK_DASHBOARD.recent_transactions
  const recurring_txns = recent_txns.filter(t => t.recurring)
  const insights = language === 'hi' ? INSIGHTS_HI : INSIGHTS_EN

  return (
    <div className="page-container fade-in">
      <div className="page-header" style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h1>{t('spendingAnalysis')}</h1>
          <p>{t('monthlySpendingFor')} {customer?.name || 'you'}</p>
        </div>
      </div>

      {loading ? (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '40vh' }}>
          <div className="spinner spinner--lg" />
        </div>
      ) : (
        <>
          {/* Top row: donut + bar */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.6fr', gap: '1rem', marginBottom: '1rem' }}>
            {/* Donut */}
            <GlowCard proximity={90}>
              <div className="section-title">{t('categorySpending')}</div>
              <ResponsiveContainer width="100%" height={220}>
                <RPieChart>
                  <Pie
                    data={spending_categories}
                    dataKey="amount"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={2}
                  >
                    {spending_categories.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color || '#4a5568'} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: any) => [formatRupee(Number(value)), 'Amount']} />
                </RPieChart>
              </ResponsiveContainer>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.375rem', marginTop: '0.5rem' }}>
                {spending_categories.slice(0, 6).map(c => (
                  <div key={c.category} style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', fontSize: '0.75rem' }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: c.color || '#4a5568', flexShrink: 0 }} />
                    <span style={{ color: 'var(--color-text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {c.category}
                    </span>
                  </div>
                ))}
              </div>
            </GlowCard>

            {/* Monthly trend bar chart */}
            <GlowCard proximity={110}>
              <div className="section-title">{t('monthlyIncomeOutflow')}</div>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={monthly_trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border-light)" />
                  <XAxis dataKey="month" stroke="var(--color-text-muted)" fontSize={12} />
                  <YAxis stroke="var(--color-text-muted)" fontSize={11} tickFormatter={(v) => `₹${v / 1000}k`} />
                  <Tooltip formatter={(value: any) => [formatRupee(Number(value)), '']} />
                  <Legend wrapperStyle={{ fontSize: '0.8rem', paddingTop: '0.5rem' }} />
                  <Bar dataKey="income" name="Income" fill="#0d7c6e" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="expenses" name="Expenses" fill="#e8770a" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="savings" name="Savings" fill="#2d7a4f" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </GlowCard>
          </div>

          {/* Category breakdown table */}
          <GlowCard style={{ marginBottom: '1rem' }} proximity={120}>
            <div className="section-title">{t('categoryDetails')}</div>
            <div className="table-wrapper">
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--color-border-light)', textAlign: 'left' }}>
                    <th style={{ padding: '0.625rem 0.75rem', color: 'var(--color-text-muted)', fontWeight: 600 }}>{t('category')}</th>
                    <th style={{ padding: '0.625rem 0.75rem', color: 'var(--color-text-muted)', fontWeight: 600 }}>{t('amount')}</th>
                    <th style={{ padding: '0.625rem 0.75rem', color: 'var(--color-text-muted)', fontWeight: 600 }}>{t('share')}</th>
                    <th style={{ padding: '0.625rem 0.75rem', color: 'var(--color-text-muted)', fontWeight: 600 }}>{t('trend')}</th>
                    <th style={{ padding: '0.625rem 0.75rem', color: 'var(--color-text-muted)', fontWeight: 600 }}>{t('change')}</th>
                  </tr>
                </thead>
                <tbody>
                  {spending_categories.map(cat => (
                    <tr key={cat.category} style={{ borderBottom: '1px solid var(--color-border-light)' }}>
                      <td style={{ padding: '0.625rem 0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span
                          aria-hidden
                          style={{
                            width: 10,
                            height: 10,
                            borderRadius: 3,
                            background: cat.color || '#4a5568',
                            boxShadow: `0 0 0 3px ${cat.color || '#4a5568'}22`,
                            flexShrink: 0,
                          }}
                        />
                        <span style={{ fontWeight: 500 }}>{cat.category}</span>
                      </td>
                      <td style={{ padding: '0.625rem 0.75rem', fontWeight: 600 }}>{formatRupee(cat.amount)}</td>
                      <td style={{ padding: '0.625rem 0.75rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <div className="progress-bar" style={{ width: 60 }}>
                            <div className="progress-fill progress-fill--saffron" style={{ width: `${Math.min(100, cat.percentage)}%` }} />
                          </div>
                          <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>{cat.percentage}%</span>
                        </div>
                      </td>
                      <td style={{ padding: '0.625rem 0.75rem' }}>
                        {cat.trend === 'up' ? <TrendingUp size={15} style={{ color: 'var(--color-terracotta)' }} /> :
                          cat.trend === 'down' ? <TrendingDown size={15} style={{ color: 'var(--color-green)' }} /> :
                            <span style={{ color: 'var(--color-text-muted)', fontSize: '0.8rem' }}>{t('stable')}</span>}
                      </td>
                      <td style={{ padding: '0.625rem 0.75rem' }}>
                        {cat.change_pct !== undefined ? (
                          <span style={{ color: cat.trend === 'up' ? 'var(--color-terracotta)' : 'var(--color-green)', fontWeight: 600, fontSize: '0.8rem' }}>
                            {cat.trend === 'up' ? '+' : '−'}{cat.change_pct}%
                          </span>
                        ) : <span style={{ color: 'var(--color-text-muted)', fontSize: '0.8rem' }}>—</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlowCard>

          {/* Recurring expenses */}
          {recurring_txns.length > 0 && (
            <GlowCard style={{ marginBottom: '1rem' }} proximity={100}>
              <div className="section-title">
                <RefreshCw size={16} style={{ display: 'inline', marginRight: 6, verticalAlign: 'middle' }} />
                {t('recurringExpenses')}
              </div>
              {recurring_txns.slice(0, 6).map(txn => (
                <div key={txn.id} className="txn-row">
                  <div
                    className="txn-icon"
                    style={{
                      background: CATEGORY_BG[txn.category] ?? '#f5f5f5',
                      position: 'relative',
                    }}
                    aria-label={`${txn.category} category`}
                  >
                    <span
                      aria-hidden
                      style={{
                        width: 12,
                        height: 12,
                        borderRadius: 4,
                        background: spending_categories.find(category => category.category === txn.category)?.color || 'var(--color-navy-muted)',
                      }}
                    />
                  </div>
                  <div className="txn-details">
                    <div className="txn-merchant">{txn.merchant}</div>
                    <div className="txn-category">{txn.category} · {t('monthly')}</div>
                  </div>
                  <div className={`txn-amount ${txn.type === 'debit' ? 'txn-amount--debit' : 'txn-amount--credit'}`}>
                    {txn.type === 'debit' ? '−' : '+'}{formatRupee(txn.amount)}
                  </div>
                </div>
              ))}
            </GlowCard>
          )}

          {/* Insight cards */}
          <GlowCard proximity={100}>
            <div className="section-title">{t('insightsForYou')}</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {insights.map((ins, i) => (
                <div key={i} className={`insight-card ${ins.type === 'teal' ? 'insight-card--teal' : ''}`}>
                  {ins.text}
                </div>
              ))}
            </div>
          </GlowCard>
        </>
      )}

      <div style={{ marginBottom: '2rem' }} />
    </div>
  )
}