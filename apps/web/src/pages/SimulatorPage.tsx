import { useState, useCallback } from 'react'
import { AlertTriangle, Info, TrendingDown, RotateCcw } from 'lucide-react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'
import { calculateEmi } from '@/lib/api'
import { formatRupee } from '@/lib/utils'
import { MOCK_DASHBOARD } from '@/data/mockData'
import { useI18n } from '@/lib/i18n'
import type { SimulatorOutput } from '@/types'

const DEFAULT_INPUT = { loan_amount: 100000, interest_rate: 12, tenure_months: 24, monthly_savings_delta: 0 }

export default function SimulatorPage() {
  const { t } = useI18n()
  const [input, setInput] = useState(DEFAULT_INPUT)
  const [result, setResult] = useState<SimulatorOutput | null>(null)
  const [loading, setLoading] = useState(false)

  const currentCashFlow = MOCK_DASHBOARD.cash_flow

  const recalculate = useCallback(async (newInput = input) => {
    setLoading(true)
    try {
      const res = await calculateEmi(newInput)
      setResult(res)
    } finally {
      setLoading(false)
    }
  }, [input])

  const handleChange = (key: string, val: number) => {
    const updated = { ...input, [key]: val }
    setInput(updated)
    recalculate(updated)
  }

  const reset = () => {
    setInput(DEFAULT_INPUT)
    setResult(null)
  }

  const newHealthScore = result ? Math.max(0, MOCK_DASHBOARD.financial_health.score + result.health_impact) : MOCK_DASHBOARD.financial_health.score

  const comparisonData = result
    ? [
        { name: 'Current', savings: currentCashFlow.monthly_savings, emi: currentCashFlow.monthly_emi },
        { name: 'After Loan', savings: Math.max(0, result.new_savings_rate / 100 * currentCashFlow.monthly_income), emi: currentCashFlow.monthly_emi + result.monthly_emi },
      ]
    : []

  return (
    <div className="page-container fade-in">
      <div className="page-header">
        <h1>{t('whatIf')}</h1>
        <p>{t('simulatorDescription')}</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        {/* Sliders panel */}
        <div className="card fade-in-delay-1">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
            <div className="section-title" style={{ margin: 0 }}>{t('adjustAssumptions')}</div>
            <button className="btn btn-ghost btn-sm" onClick={reset} aria-label="Reset to defaults">
              <RotateCcw size={14} /> {t('reset')}
            </button>
          </div>

          {[
            { key: 'loan_amount', label: 'Loan Amount', min: 10000, max: 500000, step: 5000, unit: '₹', display: formatRupee(input.loan_amount, true) },
            { key: 'interest_rate', label: 'Interest Rate (p.a.)', min: 7, max: 24, step: 0.5, unit: '%', display: `${input.interest_rate}%` },
            { key: 'tenure_months', label: 'Tenure (months)', min: 6, max: 60, step: 6, unit: 'mo', display: `${input.tenure_months} months` },
          ].map(({ key, label, min, max, step, display }) => (
            <div key={key} style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <label className="form-label" style={{ margin: 0 }}>{label}</label>
                <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1rem', color: 'var(--color-navy)' }}>{display}</span>
              </div>
              <input
                type="range"
                className="slider"
                min={min}
                max={max}
                step={step}
                value={input[key as keyof typeof input]}
                onChange={e => handleChange(key, parseFloat(e.target.value))}
                aria-label={label}
                style={{ background: `linear-gradient(to right, var(--color-saffron) ${((input[key as keyof typeof input] as number - min) / (max - min)) * 100}%, var(--color-border) 0%)` }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
                <span>{key === 'loan_amount' ? formatRupee(min, true) : key === 'interest_rate' ? `${min}%` : `${min}mo`}</span>
                <span>{key === 'loan_amount' ? formatRupee(max, true) : key === 'interest_rate' ? `${max}%` : `${max}mo`}</span>
              </div>
            </div>
          ))}

          <button
            className="btn btn-primary btn-block"
            onClick={() => recalculate(input)}
            disabled={loading}
            id="simulate-btn"
          >
            {loading ? <span className="spinner spinner--sm" /> : t('calculateImpact')}
          </button>
        </div>

        {/* Results panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {!result && (
            <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 200, textAlign: 'center' }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>🧮</div>
              <p style={{ fontSize: '0.9rem' }}>{t('adjustSliders')}</p>
            </div>
          )}

          {result && (
            <>
              {/* Warning */}
              {result.warning && (
                <div className="alert-banner alert-banner--warning fade-in">
                  <AlertTriangle size={17} style={{ flexShrink: 0 }} />
                  <div>
                    <strong>{t('caution')}</strong>
                    <p style={{ fontSize: '0.8125rem', marginTop: '0.2rem' }}>{result.warning}</p>
                  </div>
                </div>
              )}

              {!result.warning && result.is_affordable && (
                <div className="alert-banner alert-banner--success fade-in">
                  <Info size={17} style={{ flexShrink: 0 }} />
                  <span>{t('affordable')}</span>
                </div>
              )}

              {/* Key numbers */}
              <div className="card fade-in" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.875rem' }}>
                {[
                  { label: t('emiPayments'), val: formatRupee(result.monthly_emi), color: 'var(--color-saffron)' },
                  { label: t('totalRepayment'), val: formatRupee(result.total_repayment, true), color: 'var(--color-navy)' },
                  { label: t('totalInterest'), val: formatRupee(result.total_interest, true), color: 'var(--color-terracotta)' },
                  { label: t('newSavingsRate'), val: `${result.new_savings_rate}%`, color: result.new_savings_rate > 20 ? 'var(--color-green)' : result.new_savings_rate > 10 ? 'var(--color-amber)' : 'var(--color-terracotta)' },
                  { label: t('emiIncomeRatio'), val: `${(result.emi_to_income_ratio * 100).toFixed(0)}%`, color: result.emi_to_income_ratio < 0.4 ? 'var(--color-green)' : 'var(--color-terracotta)' },
                  { label: t('healthScoreImpact'), val: `${result.health_impact > 0 ? '+' : ''}${result.health_impact} pts`, color: result.health_impact >= 0 ? 'var(--color-green)' : 'var(--color-terracotta)' },
                ].map(({ label, val, color }) => (
                  <div key={label} style={{ background: 'var(--color-ivory-dark)', borderRadius: 10, padding: '0.75rem', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.25rem' }}>{label}</div>
                    <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.125rem', fontWeight: 700, color }}>{val}</div>
                  </div>
                ))}
              </div>

              {/* Before/After bar chart */}
              {comparisonData.length > 0 && (
                <div className="card fade-in">
                  <div className="section-title">{t('beforeAfter')}</div>
                  <ResponsiveContainer width="100%" height={160}>
                    <BarChart data={comparisonData} barGap={8}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" />
                      <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 11 }} tickFormatter={v => `${v / 1000}K`} />
                      <Tooltip formatter={(v: any) => formatRupee(Number(v) || 0)} contentStyle={{ borderRadius: 8, fontSize: 13 }} />
                      <Bar dataKey="savings" name="Monthly Savings" fill="var(--color-teal)" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="emi" name="Total EMI" fill="var(--color-saffron)" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* Health score impact */}
              <div className="card fade-in">
                <div className="section-title">{t('projectedHealth')}</div>
                <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>{t('current')}</div>
                    <div style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 700, color: 'var(--color-teal)' }}>{MOCK_DASHBOARD.financial_health.score}</div>
                  </div>
                  <TrendingDown size={22} style={{ color: 'var(--color-terracotta)' }} />
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>{t('afterLoan')}</div>
                    <div style={{ fontFamily: 'var(--font-display)', fontSize: '2rem', fontWeight: 700, color: newHealthScore >= 65 ? 'var(--color-teal)' : newHealthScore >= 50 ? 'var(--color-amber)' : 'var(--color-terracotta)' }}>{newHealthScore}</div>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div className="insight-card" style={{ fontSize: '0.8125rem' }}>
                      This loan would reduce your health score by <strong>{Math.abs(result.health_impact)} points</strong>.
                      {result.health_impact < -10 && ' Consider a smaller amount or longer tenure.'}
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="disclaimer-strip" style={{ marginTop: '1.5rem' }}>
        <Info size={15} style={{ flexShrink: 0, marginTop: 1, color: 'var(--color-text-muted)' }} />
        <span>Simulator calculations are for educational purposes only and are based on your current mock profile data. Actual EMI, eligibility, and interest rates will differ based on your bank's terms and credit assessment.</span>
      </div>

      <div style={{ marginBottom: '2rem' }} />
    </div>
  )
}
