import { AlertTriangle, CheckCircle, Info, ShieldCheck, ChevronDown, ChevronUp, ShieldAlert, HeartHandshake } from 'lucide-react'
import { useState, useEffect } from 'react'
import { getDashboard } from '@/lib/api'
import { formatRupee } from '@/lib/utils'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/lib/AuthContext'
import { useI18n } from '@/lib/i18n'
import type { DashboardData } from '@/types'

export default function BorrowingPage() {
  const { customerId, customer } = useAuth()
  const { t } = useI18n()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [showWhy, setShowWhy] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    setLoading(true)
    getDashboard(customerId)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [customerId])

  if (loading || !data) {
    return (
      <div className="page-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', flexDirection: 'column', gap: '1rem' }}>
        <div className="spinner spinner--lg" />
        <p className="text-muted">{t('loadingDashboard')}</p>
      </div>
    )
  }

  const { recommendation, financial_health, cash_flow } = data
  const isSuppressed = Boolean(
    recommendation.suppressed ||
    recommendation.loan_suppressed ||
    financial_health.score < 45 ||
    (recommendation as any).loan_suppressed
  )

  const safeMaxAmount = Math.max(0, Math.round(cash_flow.monthly_income * 2.5))
  const safeMinAmount = Math.min(25000, safeMaxAmount)
  const safeEmi = Math.round(safeMaxAmount * 0.015)
  const safeEmiRatio = cash_flow.monthly_income > 0
    ? Math.round(((cash_flow.monthly_emi + safeEmi) / cash_flow.monthly_income) * 100)
    : 0

  return (
    <div className="page-container fade-in">
      <div className="page-header">
        <h1>{t('responsibleBorrowing')}</h1>
        <p>{t('safeBorrowingDescription')} {customer?.name || 'your'}.</p>
      </div>

      {/* Main disclaimer */}
      <div className="loan-disclaimer fade-in" style={{ marginBottom: '1.5rem' }}>
        <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: 1 }} />
        <div>
            <strong>{t('important')}:</strong> {t('financialGuidanceDisclaimer')}
        </div>
      </div>

      {/* Suppressed Banner if Customer is in Financial Stress */}
      {isSuppressed && (
        <div
          className="fade-in glow-box"
          style={{
            background: '#fff3cd',
            border: '1px solid #ffeeba',
            borderLeft: '5px solid #d9534f',
            borderRadius: 10,
            padding: '1.25rem',
            marginBottom: '1.5rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <ShieldAlert size={24} style={{ color: '#d9534f' }} />
            <div>
              <h3 style={{ fontSize: '1.1rem', color: '#721c24', margin: 0 }}>
                Responsible Lending Safeguard: New Loan Recommendations Suppressed
              </h3>
              <span style={{ fontSize: '0.8rem', color: '#856404' }}>
                Rule: Protected customer borrowing — debt trap prevention active
              </span>
            </div>
          </div>
          <p style={{ fontSize: '0.875rem', color: '#555', lineHeight: 1.6, margin: '0.5rem 0' }}>
            {recommendation.suppression_reason ||
              (recommendation as any).not_recommended_reason ||
              `Financial health score is currently ${financial_health.score}/100. Existing EMI obligations require primary focus before taking on additional credit.`}
          </p>
          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.75rem', flexWrap: 'wrap' }}>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => navigate('/assistant')}
              style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
            >
              <HeartHandshake size={15} /> Talk to Saarthi Assistant for Debt Plan
            </button>
            <button
              className="btn btn-outline btn-sm"
              onClick={() => navigate('/spending')}
            >
              Review Monthly Spending
            </button>
          </div>
        </div>
      )}

      {/* Health + Recommendation summary */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
        {/* Financial readiness */}
        <div className="card">
          <div style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)', marginBottom: '0.875rem' }}>
            {t('financialReadiness')}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.25rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 700, color: 'var(--color-navy)', lineHeight: 1 }}>
                {financial_health.score}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{t('healthScore')}</div>
            </div>
            <div style={{ flex: 1 }}>
              <span className={`badge ${financial_health.score > 70 ? 'badge-teal' : financial_health.score > 50 ? 'badge-amber' : 'badge-red'}`} style={{ marginBottom: '0.5rem' }}>
                {financial_health.label}
              </span>
              <p style={{ fontSize: '0.8125rem', lineHeight: 1.55 }}>{financial_health.explanation}</p>
            </div>
          </div>

          {/* Key indicators */}
          {financial_health.components && [
            { label: 'Income stability', val: financial_health.components.income_stability, safe: financial_health.components.income_stability >= 70 },
            { label: 'Current debt burden', val: financial_health.components.debt_burden, safe: financial_health.components.debt_burden >= 60 },
            { label: 'Repayment behavior', val: financial_health.components.repayment_behavior, safe: financial_health.components.repayment_behavior >= 75 },
            { label: 'Liquidity (emergency fund)', val: financial_health.components.liquidity, safe: financial_health.components.liquidity >= 60 },
          ].map(({ label, val, safe }) => (
            <div key={label} className="score-component-row">
              <div className="score-component-label">{label}</div>
              <div className="score-component-bar-wrap">
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${Math.min(100, Math.max(0, val))}%`, background: safe ? 'var(--color-teal)' : 'var(--color-amber)' }} />
                </div>
              </div>
              <div className="score-component-value">{Math.round(val)}</div>
            </div>
          ))}
        </div>

        {/* Safe borrowing range */}
        <div className="card">
          <div style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)', marginBottom: '0.875rem' }}>
            {t('safeBorrowingRange')}
          </div>
          <div style={{ textAlign: 'center', padding: '1rem 0' }}>
            <div style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>
              {isSuppressed ? t('recommendedBorrowing') : t('estimatedSafeRange')}
            </div>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 700, color: isSuppressed ? '#d9534f' : 'var(--color-navy)', lineHeight: 1.1 }}>
              {isSuppressed ? '₹0 (Suppressed)' : `${formatRupee(safeMinAmount, true)} – ${formatRupee(safeMaxAmount, true)}`}
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
              {isSuppressed ? 'Priority: Debt stabilization & restructuring' : 'Based on income and existing obligations'}
            </div>
          </div>

          <div className="divider" />

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
              <span style={{ color: 'var(--color-text-secondary)' }}>{t('monthlyIncome')}</span>
              <span style={{ fontWeight: 600 }}>{formatRupee(cash_flow.monthly_income)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
              <span style={{ color: 'var(--color-text-secondary)' }}>{t('currentEmi')}</span>
              <span style={{ fontWeight: 600 }}>{formatRupee(cash_flow.monthly_emi)}</span>
            </div>
            {!isSuppressed && (
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>Est. new EMI (max range)</span>
                <span style={{ fontWeight: 600, color: 'var(--color-saffron)' }}>+ {formatRupee(safeEmi)}</span>
              </div>
            )}
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
              <span style={{ color: 'var(--color-text-secondary)' }}>Combined EMI burden</span>
              <span style={{ fontWeight: 600, color: safeEmiRatio <= 35 ? 'var(--color-green)' : 'var(--color-amber)' }}>
                {safeEmiRatio}% of income
              </span>
            </div>
          </div>

          <div className="divider" />
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8125rem', color: isSuppressed ? '#d9534f' : 'var(--color-green)' }}>
            <ShieldCheck size={15} />
            <span>{isSuppressed ? 'Protected: New loan offers suppressed to prevent distress' : 'Combined burden stays below 40% safe threshold'}</span>
          </div>

          <button className="btn btn-primary btn-block" style={{ marginTop: '1rem' }} onClick={() => navigate('/simulator')}>
            {t('testSimulator')}
          </button>
        </div>
      </div>

      {/* Recommendation card */}
      <div className="rec-card fade-in-delay-2" style={{ marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.875rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-saffron)', marginBottom: '0.375rem' }}>
              {t('saarthiRecommendation')}
            </div>
            <h3 style={{ fontSize: '1.125rem' }}>{recommendation.title}</h3>
          </div>
          <div className="rec-card-confidence">
            <CheckCircle size={14} />
            {Math.round((recommendation.confidence || 0.85) * 100)}% confidence
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '0.75rem', marginBottom: '1rem' }}>
          <div style={{ textAlign: 'center', background: 'rgba(255,255,255,0.7)', borderRadius: 10, padding: '0.75rem' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Product</div>
            <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{recommendation.product}</div>
          </div>
          <div style={{ textAlign: 'center', background: 'rgba(255,255,255,0.7)', borderRadius: 10, padding: '0.75rem' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Suggested</div>
            <div style={{ fontWeight: 700, fontSize: '1rem', color: isSuppressed ? '#d9534f' : 'var(--color-teal)' }}>
              {recommendation.recommended_amount ? `${formatRupee(recommendation.recommended_amount)}` : t('guidanceOnly')}
            </div>
          </div>
          <div style={{ textAlign: 'center', background: 'rgba(255,255,255,0.7)', borderRadius: 10, padding: '0.75rem' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Status</div>
            <div style={{ fontWeight: 600, fontSize: '0.875rem', color: isSuppressed ? '#d9534f' : 'var(--color-teal)' }}>
              {isSuppressed ? t('loanSuppressed') : t('eligible')}
            </div>
          </div>
        </div>

        {/* Why expandable */}
        <button
          style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', fontFamily: 'var(--font-body)', fontWeight: 600, fontSize: '0.875rem', color: 'var(--color-navy)', padding: '0.25rem 0' }}
          onClick={() => setShowWhy(!showWhy)}
          aria-expanded={showWhy}
        >
          <Info size={15} />
          {t('whyRecommended')}
          {showWhy ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
        </button>
        {showWhy && (
          <div style={{ marginTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {(recommendation.why || []).map((w, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', fontSize: '0.8375rem' }}>
                <div className="step-badge" style={{ width: 20, height: 20, fontSize: '0.65rem', flexShrink: 0 }}>{i + 1}</div>
                <span style={{ color: 'var(--color-text-secondary)', lineHeight: 1.55 }}>{w}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Final disclaimer */}
      <div className="disclaimer-strip">
        <Info size={15} style={{ flexShrink: 0, marginTop: 1, color: 'var(--color-text-muted)' }} />
        <span>
          Saarthi Finance is an explainable financial guidance platform. All recommendations are generated from your financial behavior patterns and are for informational purposes only. They do not constitute formal credit approval, loan offers, or professional financial advice. Please consult your bank or a certified financial advisor before making any borrowing decisions.
        </span>
      </div>

      <div style={{ marginBottom: '2rem' }} />
    </div>
  )
}