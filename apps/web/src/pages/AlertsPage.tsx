import { AlertTriangle, TrendingDown, Shield, Eye, MessageCircle, FileText, CheckCircle } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getAlerts } from '@/lib/api'
import { useAuth } from '@/lib/AuthContext'
import { useI18n } from '@/lib/i18n'
import type { Alert } from '@/types'

const SEVERITY_CONFIG: Record<string, { label: string; badgeClass: string; borderColor: string; bgColor: string }> = {
  critical: { label: 'Critical', badgeClass: 'badge-red', borderColor: 'var(--color-terracotta)', bgColor: 'var(--color-terracotta-pale)' },
  high: { label: 'High', badgeClass: 'badge-red', borderColor: 'var(--color-terracotta)', bgColor: 'var(--color-terracotta-pale)' },
  medium: { label: 'Medium', badgeClass: 'badge-amber', borderColor: 'var(--color-amber)', bgColor: 'var(--color-amber-pale)' },
  low: { label: 'Low', badgeClass: 'badge-navy', borderColor: 'var(--color-border)', bgColor: 'var(--color-ivory-dark)' },
}

const TYPE_ICONS: Record<string, React.ElementType> = {
  cash_flow: TrendingDown,
  unusual_spending: Eye,
  missed_emi_risk: AlertTriangle,
  savings_decline: TrendingDown,
  fraud_review: Shield,
  stress: AlertTriangle,
  expense_surge: TrendingDown,
}

function AlertCard({ alert, onTalkToSupport, onReviewFinances, t }: { alert: Alert; onTalkToSupport: () => void; onReviewFinances: () => void; t: (key: string) => string }) {
  const config = SEVERITY_CONFIG[alert.severity] || SEVERITY_CONFIG.medium
  const Icon = TYPE_ICONS[alert.type] ?? AlertTriangle

  return (
    <div
      className="card fade-in"
      style={{
        borderLeft: `4px solid ${config.borderColor}`,
        background: config.bgColor,
        padding: '1.25rem',
      }}
      role="alert"
      aria-label={`${config.label} alert: ${alert.title}`}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.875rem' }}>
        <div style={{
          width: 40, height: 40, borderRadius: 10,
          background: `${config.borderColor}20`,
          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        }}>
          <Icon size={18} style={{ color: config.borderColor }} />
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.375rem', flexWrap: 'wrap' }}>
            <h4 style={{ fontSize: '0.9375rem', margin: 0 }}>{alert.title}</h4>
            <span className={`badge ${config.badgeClass}`}>{config.label}</span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', lineHeight: 1.6, marginBottom: '0.5rem' }}>
            {alert.description}
          </p>

          {alert.evidence && (
            <div style={{ fontFamily: 'monospace', fontSize: '0.775rem', background: 'rgba(26,35,50,0.06)', padding: '0.375rem 0.625rem', borderRadius: 6, color: 'var(--color-navy)', marginBottom: '0.75rem', display: 'inline-block' }}>
              📊 {alert.evidence}
            </div>
          )}

          <div style={{ background: 'rgba(255,255,255,0.7)', borderRadius: 8, padding: '0.625rem 0.75rem', marginBottom: '1rem', fontSize: '0.8rem', display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
            <CheckCircle size={14} style={{ color: 'var(--color-teal)', flexShrink: 0, marginTop: 1 }} />
            <span style={{ color: 'var(--color-navy)' }}><strong>{t('recommendedAction')} </strong>{alert.action}</span>
          </div>

          <div style={{ display: 'flex', gap: '0.625rem', flexWrap: 'wrap' }}>
            <button
              className="btn btn-sm"
              style={{ background: 'var(--color-navy)', color: '#fff', borderRadius: 8 }}
              onClick={onTalkToSupport}
            >
              <MessageCircle size={14} /> {t('talkSupport')}
            </button>
            <button
              className="btn btn-secondary btn-sm"
              onClick={onReviewFinances}
            >
              <FileText size={14} /> {alert.action_label || t('reviewFinances')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function AlertsPage() {
  const { customerId, customer } = useAuth()
  const { t } = useI18n()
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    setLoading(true)
    getAlerts(customerId)
      .then(setAlerts)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [customerId])

  const highCount = alerts.filter(a => a.severity === 'high' || a.severity === 'critical').length
  const mediumCount = alerts.filter(a => a.severity === 'medium').length

  return (
    <div className="page-container fade-in">
      <div className="page-header">
        <h1>{t('alertsNotifications')}</h1>
        <p>{t('earlySignals')} {customer?.name || 'you'}.</p>
      </div>

      {loading ? (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '40vh' }}>
          <div className="spinner spinner--lg" />
        </div>
      ) : (
        <>
          {/* Summary */}
          <div style={{ display: 'flex', gap: '0.875rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
            {[
              { label: t('totalAlerts'), val: alerts.length, color: 'var(--color-navy)' },
              { label: t('highPriority'), val: highCount, color: 'var(--color-terracotta)' },
              { label: t('medium'), val: mediumCount, color: 'var(--color-amber)' },
              { label: t('low'), val: alerts.filter(a => a.severity === 'low').length, color: 'var(--color-text-muted)' },
            ].map(({ label, val, color }) => (
              <div key={label} className="stat-card" style={{ minWidth: 120, flex: '1 1 120px' }}>
                <div className="stat-card-label">{label}</div>
                <div className="stat-card-value" style={{ color, fontSize: '1.75rem' }}>{val}</div>
              </div>
            ))}
          </div>

          {/* Alert list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {alerts.length === 0 ? (
              <div className="card" style={{ textAlign: 'center', padding: '2rem' }}>
                <CheckCircle size={32} style={{ color: 'var(--color-green)', marginBottom: '0.5rem' }} />
                <h3>{t('noActiveAlerts')}</h3>
                <p style={{ color: 'var(--color-text-muted)' }}>{t('healthyFinances')}</p>
              </div>
            ) : (
              alerts
                .sort((a, b) => {
                  const order: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 }
                  return (order[a.severity] ?? 2) - (order[b.severity] ?? 2)
                })
                .map(alert => (
                  <AlertCard
                    key={alert.id}
                    alert={alert}
                    onTalkToSupport={() => navigate('/assistant')}
                    t={t}
                    onReviewFinances={() => {
                      if (alert.type === 'cash_flow' || alert.type === 'unusual_spending' || alert.type === 'savings_decline' || alert.type === 'expense_surge') navigate('/spending')
                      else if (alert.type === 'missed_emi_risk') navigate('/borrowing')
                      else navigate('/dashboard')
                    }}
                  />
                ))
            )}
          </div>
        </>
      )}

      <div className="disclaimer-strip" style={{ marginTop: '1.5rem' }}>
        <Shield size={14} style={{ flexShrink: 0, color: 'var(--color-text-muted)' }} />
        <span>Alerts are generated from behavioral analysis of your financial data and are designed to help you take preventive action. They are not accusations or official notifications. Any fraud-related alerts are flagged for your awareness and do not imply confirmed fraud activity.</span>
      </div>

      <div style={{ marginBottom: '2rem' }} />
    </div>
  )
}
