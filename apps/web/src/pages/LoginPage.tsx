import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, ChevronRight, Globe } from 'lucide-react'
import { useAuth } from '@/lib/AuthContext'
import type { Language } from '@/types'
import NebulaBackground from '@/components/NebulaBackground'

const LANGUAGES: { code: Language; label: string; native: string }[] = [
  { code: 'en', label: 'English', native: 'English' },
  { code: 'hi', label: 'Hindi', native: 'हिन्दी' },
  { code: 'mr', label: 'Marathi', native: 'मराठी' },
  { code: 'ta', label: 'Tamil', native: 'தமிழ்' },
  { code: 'bn', label: 'Bengali', native: 'বাংলা' },
]

const HERO_CONTENT: Record<Language, { heading: string; sub: string }> = {
  en: { heading: 'Financial guidance that knows where you stand — and where you\'re headed.', sub: 'Built for how India actually earns, spends, and borrows.' },
  hi: { heading: 'बैंकिंग जो आपका अगला कदम समझे।', sub: 'भारत के लिए बनाया गया पारदर्शी वित्तीय मार्गदर्शन।' },
  mr: { heading: 'बँकिंग जे तुमची पुढची पायरी समजते.', sub: 'भारतासाठी तयार केलेले पारदर्शक आर्थिक मार्गदर्शन.' },
  ta: { heading: 'உங்கள் அடுத்த படியை புரிந்துகொள்ளும் வங்கி.', sub: 'பாரதிற்காக வடிவமைக்கப்பட்ட வெளிப்படையான நிதி வழிகாட்டுதல்.' },
  bn: { heading: 'ব্যাংকিং যা আপনার পরবর্তী পদক্ষেপ বোঝে।', sub: 'ভারতের জন্য তৈরি স্বচ্ছ আর্থিক নির্দেশনা।' },
}

export default function LoginPage() {
  const [phone, setPhone] = useState('')
  const [language, setLanguage] = useState<Language>('en')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  const hero = HERO_CONTENT[language]

  const handleDemoLogin = async () => {
    setLoading(true)
    setError('')
    try {
      await login(phone || '9800000001', language)
      navigate('/dashboard')
    } catch {
      setError('Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      {/* Left panel */}
      <div className="login-left" style={{ position: 'relative', overflow: 'hidden' }}>
        <NebulaBackground />
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ marginBottom: '2.5rem' }}>
            <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.75rem', fontWeight: 700, color: '#fff', marginBottom: '0.25rem' }}>
              Saarthi<span style={{ color: 'var(--color-saffron)' }}>.</span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.4)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
              Finance
            </div>
          </div>

          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(1.5rem, 4vw, 2.25rem)', fontWeight: 600, color: '#fff', lineHeight: 1.3, marginBottom: '1rem' }}>
            {hero.heading}
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: '1rem', lineHeight: 1.65, marginBottom: '2.5rem' }}>
            {hero.sub}
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {[
              { icon: '🏦', text: 'See your financial health, explained simply' },
              { icon: '🛡️', text: 'Borrow only what you can safely repay' },
              { icon: '🔔', text: 'Get warned before a shortfall happens' },
              { icon: '💬', text: 'Ask Saarthi anything, in your own language' },
            ].map(({ icon, text }) => (
              <div key={text} style={{ display: 'flex', alignItems: 'center', gap: '0.875rem' }}>
                <div style={{ width: 36, height: 36, borderRadius: 8, background: 'rgba(255,255,255,0.08)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.1rem', flexShrink: 0 }}>
                  {icon}
                </div>
                <span style={{ color: 'rgba(255,255,255,0.75)', fontSize: '0.9rem' }}>{text}</span>
              </div>
            ))}
          </div>

          <div style={{ marginTop: '3rem', padding: '0.875rem 1rem', background: 'rgba(255,255,255,0.06)', borderRadius: 10, border: '1px solid rgba(255,255,255,0.1)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
              <Shield size={14} style={{ color: 'var(--color-teal-light)' }} />
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-teal-light)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Secure & Private</span>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'rgba(255,255,255,0.45)', lineHeight: 1.5 }}>
              Built with synthetic data for demonstration. No real financial information is collected, stored, or shared.
            </p>
          </div>
        </div>
      </div>

      {/* Right panel */}
      <div className="login-right">
        <div style={{ maxWidth: 360, margin: '0 auto', width: '100%' }}>
          <h2 style={{ marginBottom: '0.375rem' }}>Welcome back</h2>
          <p style={{ fontSize: '0.9rem', marginBottom: '2rem' }}>Enter your mobile number to continue</p>

          {/* Language selector */}
          <div style={{ marginBottom: '1.25rem' }}>
            <label className="form-label" htmlFor="language-select">
              <Globe size={13} style={{ display: 'inline', marginRight: 4, verticalAlign: 'middle' }} />
              Preferred Language
            </label>
            <select
              id="language-select"
              className="input"
              value={language}
              onChange={e => setLanguage(e.target.value as Language)}
            >
              {LANGUAGES.map(l => (
                <option key={l.code} value={l.code}>
                  {l.native} — {l.label}
                </option>
              ))}
            </select>
          </div>

          {/* Phone */}
          <div style={{ marginBottom: '1.5rem' }}>
            <label className="form-label" htmlFor="phone-input">Mobile Number</label>
            <input
              id="phone-input"
              type="tel"
              className="input"
              placeholder="Enter your 10-digit mobile number"
              value={phone}
              onChange={e => setPhone(e.target.value)}
              maxLength={10}
              onKeyDown={e => e.key === 'Enter' && handleDemoLogin()}
            />
          </div>

          {error && (
            <div className="alert-banner alert-banner--danger" style={{ marginBottom: '1rem' }}>
              <span>{error}</span>
            </div>
          )}

          <button
            id="demo-login-btn"
            className="btn btn-primary btn-lg btn-block"
            onClick={handleDemoLogin}
            disabled={loading}
          >
            {loading ? (
              <span className="spinner spinner--sm" />
            ) : (
              <>
                Continue
                <span
                  style={{
                    fontSize: '0.65rem',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: '0.03em',
                    background: 'rgba(255,255,255,0.22)',
                    borderRadius: 999,
                    padding: '0.15rem 0.5rem',
                    marginLeft: '0.5rem',
                  }}
                >
                  Demo Mode
                </span>
                <ChevronRight size={18} />
              </>
            )}
          </button>

          <div style={{ textAlign: 'center', margin: '1.25rem 0', color: 'var(--color-text-muted)', fontSize: '0.8125rem' }}>
            — or —
          </div>

          <div style={{ background: 'var(--color-saffron-pale)', border: '1px solid #f3d7b0', borderRadius: 10, padding: '0.875rem 1rem' }}>
            <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-saffron)', marginBottom: '0.375rem' }}>
              Try it instantly
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', lineHeight: 1.55 }}>
              <div><strong>Customer:</strong> Ananya Verma, Indore</div>
              <div><strong>Phone:</strong> Any 10-digit number</div>
              <div><strong>Language:</strong> Select Hindi for full demo</div>
            </div>
          </div>

          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textAlign: 'center', marginTop: '1.5rem', lineHeight: 1.55 }}>
            Saarthi Finance offers financial guidance, not loan approvals or investment advice. All data shown is synthetic.
          </p>
        </div>
      </div>
    </div>
  )
}