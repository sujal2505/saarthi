import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Shield, ChevronRight, Globe, RefreshCw, ShieldCheck } from 'lucide-react'
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

const LOGIN_COPY: Record<Language, Record<string, string>> = {
  en: { finance: 'Finance', welcome: 'Welcome back', enterMobile: 'Enter your mobile number to continue', preferred: 'Preferred Language', mobile: 'Mobile Number', placeholder: 'Enter your 10-digit mobile number', continue: 'Continue', demo: 'Demo Mode', tryIt: 'Try it instantly', secure: 'Secure & Private', customer: 'Customer', phone: 'Phone', language: 'Language', hindiDemo: 'Select Hindi for full demo', failed: 'Login failed. Please try again.', invalidMobile: 'Enter a valid 10-digit mobile number.', humanCheck: 'Human verification', solve: 'Solve this simple question to continue', answer: 'Answer', answerPlaceholder: 'Enter answer', refreshQuestion: 'Get a new question', wrongAnswer: 'That answer is not correct. Try again.', verified: 'Human verified' },
  hi: { finance: 'वित्त', welcome: 'वापसी पर स्वागत है', enterMobile: 'जारी रखने के लिए मोबाइल नंबर दर्ज करें', preferred: 'पसंदीदा भाषा', mobile: 'मोबाइल नंबर', placeholder: 'अपना 10 अंकों का मोबाइल नंबर दर्ज करें', continue: 'जारी रखें', demo: 'डेमो मोड', tryIt: 'तुरंत आज़माएं', secure: 'सुरक्षित और निजी', customer: 'ग्राहक', phone: 'फोन', language: 'भाषा', hindiDemo: 'पूरे डेमो के लिए हिंदी चुनें', failed: 'लॉगिन विफल हुआ। फिर प्रयास करें।', invalidMobile: 'कृपया सही 10 अंकों का मोबाइल नंबर दर्ज करें।', humanCheck: 'मानव सत्यापन', solve: 'जारी रखने के लिए यह आसान सवाल हल करें', answer: 'उत्तर', answerPlaceholder: 'उत्तर दर्ज करें', refreshQuestion: 'नया सवाल', wrongAnswer: 'उत्तर सही नहीं है। फिर प्रयास करें।', verified: 'मानव सत्यापन पूरा हुआ' },
  mr: { finance: 'वित्त', welcome: 'पुन्हा स्वागत आहे', enterMobile: 'पुढे जाण्यासाठी मोबाईल नंबर टाका', preferred: 'प्राधान्याची भाषा', mobile: 'मोबाईल नंबर', placeholder: 'तुमचा १० अंकी मोबाईल नंबर टाका', continue: 'पुढे जा', demo: 'डेमो मोड', tryIt: 'त्वरित वापरून पहा', secure: 'सुरक्षित आणि खासगी', customer: 'ग्राहक', phone: 'फोन', language: 'भाषा', hindiDemo: 'पूर्ण डेमोसाठी हिंदी निवडा', failed: 'लॉगिन अयशस्वी. पुन्हा प्रयत्न करा.', invalidMobile: 'कृपया योग्य १० अंकी मोबाईल नंबर टाका.', humanCheck: 'मानवी पडताळणी', solve: 'पुढे जाण्यासाठी हा सोपा प्रश्न सोडवा', answer: 'उत्तर', answerPlaceholder: 'उत्तर टाका', refreshQuestion: 'नवीन प्रश्न', wrongAnswer: 'उत्तर चुकीचे आहे. पुन्हा प्रयत्न करा.', verified: 'मानवी पडताळणी पूर्ण' },
  ta: { finance: 'நிதி', welcome: 'மீண்டும் வரவேற்கிறோம்', enterMobile: 'தொடர உங்கள் மொபைல் எண்ணை உள்ளிடவும்', preferred: 'விருப்ப மொழி', mobile: 'மொபைல் எண்', placeholder: '10 இலக்க மொபைல் எண்ணை உள்ளிடவும்', continue: 'தொடரவும்', demo: 'டெமோ முறை', tryIt: 'உடனே முயற்சிக்கவும்', secure: 'பாதுகாப்பானது மற்றும் தனிப்பட்டது', customer: 'வாடிக்கையாளர்', phone: 'தொலைபேசி', language: 'மொழி', hindiDemo: 'முழு டெமோவிற்கு இந்தி தேர்வு செய்யவும்', failed: 'உள்நுழைவு தோல்வியடைந்தது. மீண்டும் முயற்சிக்கவும்.', invalidMobile: 'சரியான 10 இலக்க மொபைல் எண்ணை உள்ளிடவும்.', humanCheck: 'மனித சரிபார்ப்பு', solve: 'தொடர இந்த எளிய கேள்வியைத் தீர்க்கவும்', answer: 'பதில்', answerPlaceholder: 'பதிலை உள்ளிடவும்', refreshQuestion: 'புதிய கேள்வி', wrongAnswer: 'பதில் தவறானது. மீண்டும் முயற்சிக்கவும்.', verified: 'மனித சரிபார்ப்பு முடிந்தது' },
  bn: { finance: 'অর্থ', welcome: 'আবার স্বাগতম', enterMobile: 'চালিয়ে যেতে মোবাইল নম্বর লিখুন', preferred: 'পছন্দের ভাষা', mobile: 'মোবাইল নম্বর', placeholder: '১০ সংখ্যার মোবাইল নম্বর লিখুন', continue: 'চালিয়ে যান', demo: 'ডেমো মোড', tryIt: 'এখনই চেষ্টা করুন', secure: 'নিরাপদ ও ব্যক্তিগত', customer: 'গ্রাহক', phone: 'ফোন', language: 'ভাষা', hindiDemo: 'সম্পূর্ণ ডেমোর জন্য হিন্দি নির্বাচন করুন', failed: 'লগইন ব্যর্থ হয়েছে। আবার চেষ্টা করুন.', invalidMobile: 'সঠিক ১০ সংখ্যার মোবাইল নম্বর লিখুন।', humanCheck: 'মানব যাচাই', solve: 'চালিয়ে যেতে এই সহজ প্রশ্নটি সমাধান করুন', answer: 'উত্তর', answerPlaceholder: 'উত্তর লিখুন', refreshQuestion: 'নতুন প্রশ্ন', wrongAnswer: 'উত্তর সঠিক নয়। আবার চেষ্টা করুন।', verified: 'মানব যাচাই সম্পন্ন' },
}

type MathChallenge = { left: number; right: number; operator: '+' | '-'; answer: number }

function createMathChallenge(): MathChallenge {
  const left = Math.floor(Math.random() * 9) + 2
  const right = Math.floor(Math.random() * 9) + 1
  const operator = Math.random() > 0.5 ? '+' : '-'
  return operator === '+'
    ? { left, right, operator, answer: left + right }
    : { left: Math.max(left, right), right: Math.min(left, right), operator, answer: Math.abs(left - right) }
}

export default function LoginPage() {
  const [phone, setPhone] = useState('')
  const [language, setLanguage] = useState<Language>('en')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [challenge, setChallenge] = useState<MathChallenge>(() => createMathChallenge())
  const [challengeAnswer, setChallengeAnswer] = useState('')
  const [verificationError, setVerificationError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  const hero = HERO_CONTENT[language]
  const copy = LOGIN_COPY[language]
  const isPhoneValid = /^\d{10}$/.test(phone)

  const handleDemoLogin = async () => {
    if (!/^\d{10}$/.test(phone)) {
      setError(copy.invalidMobile)
      return
    }
    if (Number(challengeAnswer) !== challenge.answer) {
      setVerificationError(copy.wrongAnswer)
      return
    }
    setLoading(true)
    setError('')
    try {
      await login(phone, language)
      navigate('/dashboard')
    } catch {
      setError(copy.failed)
    } finally {
      setLoading(false)
    }
  }

  const refreshChallenge = () => {
    setChallenge(createMathChallenge())
    setChallengeAnswer('')
    setVerificationError('')
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
              {copy.finance}
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
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-teal-light)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{copy.secure}</span>
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
          <h2 style={{ marginBottom: '0.375rem' }}>{copy.welcome}</h2>
          <p style={{ fontSize: '0.9rem', marginBottom: '2rem' }}>{copy.enterMobile}</p>

          {/* Language selector */}
          <div style={{ marginBottom: '1.25rem' }}>
            <label className="form-label" htmlFor="language-select">
              <Globe size={13} style={{ display: 'inline', marginRight: 4, verticalAlign: 'middle' }} />
              {copy.preferred}
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
            <label className="form-label" htmlFor="phone-input">{copy.mobile}</label>
            <input
              id="phone-input"
              type="tel"
              className="input"
              placeholder={copy.placeholder}
              value={phone}
              onChange={e => setPhone(e.target.value)}
              maxLength={10}
              onKeyDown={e => e.key === 'Enter' && handleDemoLogin()}
            />
          </div>

          {isPhoneValid && <div className="human-check" style={{ marginBottom: '1.25rem' }}>
            <div className="human-check-heading">
              <span><ShieldCheck size={15} /> {copy.humanCheck}</span>
              <button type="button" className="human-check-refresh" onClick={refreshChallenge} aria-label={copy.refreshQuestion} title={copy.refreshQuestion}>
                <RefreshCw size={15} />
              </button>
            </div>
            <p>{copy.solve}</p>
            <div className="human-check-controls">
              <strong>{challenge.left} {challenge.operator} {challenge.right} =</strong>
              <input
                type="number"
                inputMode="numeric"
                className="input"
                aria-label={copy.answer}
                placeholder={copy.answerPlaceholder}
                value={challengeAnswer}
                onChange={e => { setChallengeAnswer(e.target.value); setVerificationError('') }}
                onKeyDown={e => e.key === 'Enter' && handleDemoLogin()}
              />
            </div>
            {verificationError ? <div className="human-check-error">{verificationError}</div> : challengeAnswer && Number(challengeAnswer) === challenge.answer ? <div className="human-check-success"><ShieldCheck size={14} /> {copy.verified}</div> : null}
          </div>}

          {error && (
            <div className="alert-banner alert-banner--danger" style={{ marginBottom: '1rem' }}>
              <span>{error}</span>
            </div>
          )}

          <button
            id="demo-login-btn"
            className="btn btn-primary btn-lg btn-block"
            onClick={handleDemoLogin}
            disabled={loading || !isPhoneValid || Number(challengeAnswer) !== challenge.answer}
          >
            {loading ? (
              <span className="spinner spinner--sm" />
            ) : (
              <>
                {copy.continue}
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
                  {copy.demo}
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
              {copy.tryIt}
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', lineHeight: 1.55 }}>
              <div><strong>{copy.customer}:</strong> Ananya Verma, Indore</div>
              <div><strong>{copy.phone}:</strong> Any 10-digit number</div>
              <div><strong>{copy.language}:</strong> {copy.hindiDemo}</div>
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