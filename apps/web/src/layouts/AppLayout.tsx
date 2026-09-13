import { useRef, useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  PieChart,
  HandCoins,
  Target,
  Calculator,
  MessageCircle,
  Bell,
  LogOut,
  Menu,
  Camera,
  X,
  Save,
} from 'lucide-react'
import { useAuth } from '@/lib/AuthContext'
import { useI18n } from '@/lib/i18n'
import type { Customer, Language } from '@/types'
import NebulaBackground from '@/components/NebulaBackground'

const NAV_ITEMS = [
  { to: '/dashboard', key: 'dashboard', icon: LayoutDashboard },
  { to: '/spending', key: 'spending', icon: PieChart },
  { to: '/borrowing', key: 'borrowing', icon: HandCoins },
  { to: '/goals', key: 'goals', icon: Target },
  { to: '/simulator', key: 'simulator', icon: Calculator },
  { to: '/assistant', key: 'askSaarthi', icon: MessageCircle },
  { to: '/alerts', key: 'alerts', icon: Bell },
]

export default function AppLayout() {
  const { customer, logout, customerId, switchCustomer, language, setLanguage, profilePhoto, setProfilePhoto, updateProfile } = useAuth()
  const { t } = useI18n()

  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const [profileSaving, setProfileSaving] = useState(false)
  const [profileError, setProfileError] = useState('')
  const photoInputRef = useRef<HTMLInputElement>(null)
  const [profileForm, setProfileForm] = useState<Omit<Customer, 'id'>>({
    name: customer?.name || '', city: customer?.city || '', state: customer?.state || '', address: customer?.address || '',
    preferred_language: customer?.preferred_language || language, phone: customer?.phone || '',
    age: customer?.age, occupation: customer?.occupation || '', dependents: customer?.dependents,
  })

  const initials = customer?.name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase() ?? 'A'

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const openProfile = () => {
    setProfileError('')
    setProfileForm({
      name: customer?.name || '', city: customer?.city || '', state: customer?.state || '', address: customer?.address || '',
      preferred_language: language, phone: customer?.phone || '', age: customer?.age,
      occupation: customer?.occupation || '', dependents: customer?.dependents,
    })
    setProfileOpen(true)
  }

  const handlePhoto = (file?: File) => {
    if (!file) return
    if (!file.type.startsWith('image/')) {
      setProfileError('Please select an image file.')
      return
    }
    const reader = new FileReader()
    reader.onload = () => setProfilePhoto(String(reader.result))
    reader.readAsDataURL(file)
  }

  const saveProfile = async () => {
    setProfileSaving(true)
    setProfileError('')
    try {
      await updateProfile(profileForm)
      setLanguage(profileForm.preferred_language)
      setProfileOpen(false)
    } catch {
      setProfileError('Could not save your profile. Please check that the backend is running.')
    } finally {
      setProfileSaving(false)
    }
  }

  return (
    <div className="app-layout">
      {/* Sidebar overlay for mobile */}
      <div
        className={`sidebar-overlay ${sidebarOpen ? 'visible' : ''}`}
        onClick={() => setSidebarOpen(false)}
        aria-hidden
      />

      {/* Sidebar */}
      <nav className={`sidebar ${sidebarOpen ? 'open' : ''}`} aria-label={t('navigation')}>
        {/* Inner wrapper only — keeps the nav's own CSS position (fixed/sticky/etc) untouched */}
        <div style={{ position: 'relative', width: '100%', height: '100%' }}>
          {/* Ambient nebula layer — confined to the sidebar, behind logo/nav/footer */}
          <div
            aria-hidden
            style={{
              position: 'absolute',
              inset: 0,
              zIndex: 0,
              opacity: 0.35,
              pointerEvents: 'none',
              overflow: 'hidden',
            }}
          >
            <NebulaBackground />
          </div>

          <div className="sidebar-logo" style={{ position: 'relative', zIndex: 1 }}>
            <div className="sidebar-logo-mark">
              Saarthi<span>.</span>
            </div>
            <div className="sidebar-tagline">{t('tagline')}</div>
          </div>

          <div className="sidebar-nav" style={{ position: 'relative', zIndex: 1 }}>
            <div className="sidebar-section-label">{t('navigation')}</div>
            {NAV_ITEMS.map(({ to, key, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                onClick={() => setSidebarOpen(false)}
              >
                <Icon className="sidebar-link-icon" aria-hidden />
                {t(key)}
              </NavLink>
            ))}
          </div>

          <div className="sidebar-footer" style={{ position: 'relative', zIndex: 1 }}>
            <button className="sidebar-user" onClick={openProfile} style={{ width: '100%', border: 0, background: 'transparent', font: 'inherit', textAlign: 'left', cursor: 'pointer', color: 'inherit', appearance: 'none' }} aria-label="Edit profile">
              <div className="sidebar-avatar" aria-hidden style={profilePhoto ? { backgroundImage: `url(${profilePhoto})`, backgroundSize: 'cover', backgroundPosition: 'center', color: 'transparent' } : undefined}>
                {profilePhoto ? '' : initials}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="sidebar-user-name">{customer?.name}</div>
                <div className="sidebar-user-city">{customer?.city}, {customer?.state}</div>
              </div>
              <Camera size={15} style={{ color: 'rgba(255,255,255,0.55)', flexShrink: 0 }} />
            </button>

            <div style={{ marginTop: '0.75rem', marginBottom: '0.5rem' }}>
              <label htmlFor="persona-select" style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'block' }}>
                Switch Persona (Demo)
              </label>
              <select
                id="persona-select"
                value={customerId}
                onChange={(e) => switchCustomer(e.target.value)}
                style={{
                  width: '100%',
                  marginTop: '0.25rem',
                  background: 'rgba(255,255,255,0.08)',
                  color: '#fff',
                  border: '1px solid rgba(255,255,255,0.15)',
                  borderRadius: '6px',
                  padding: '5px 8px',
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                }}
              >
                <option value="cust_001" style={{ background: '#1a2332', color: '#fff' }}>🟢 Ananya Verma (Teacher · 81)</option>
                <option value="cust_002" style={{ background: '#1a2332', color: '#fff' }}>🔴 Ramesh Patil (Stressed · Suppressed · 28)</option>
                <option value="cust_003" style={{ background: '#1a2332', color: '#fff' }}>🟢 Meena Devi (Tailor · 93)</option>
                <option value="cust_004" style={{ background: '#1a2332', color: '#fff' }}>🟡 Arjun Kumar (Delivery · Suppressed · 62)</option>
                <option value="cust_005" style={{ background: '#1a2332', color: '#fff' }}>🔴 Sunita Rao (Vendor · Suppressed · 44)</option>
                <option value="cust_006" style={{ background: '#1a2332', color: '#fff' }}>🟢 Priya Sharma (Nurse · 95)</option>
                <option value="cust_007" style={{ background: '#1a2332', color: '#fff' }}>🟡 Mohan Das (Farmer · Suppressed · 58)</option>
                <option value="cust_008" style={{ background: '#1a2332', color: '#fff' }}>🟢 Kavitha Nair (Beautician · 78)</option>
                <option value="cust_009" style={{ background: '#1a2332', color: '#fff' }}>🟢 Rahul Gupta (Shopkeeper · 94)</option>
                <option value="cust_010" style={{ background: '#1a2332', color: '#fff' }}>🟢 Deepa Pillai (Govt Employee · 91)</option>
              </select>
            </div>

            <button
              onClick={async () => {
                try {
                  await fetch('http://localhost:8000/api/v1/seed/reload');
                  await switchCustomer(customerId);
                  alert('Database successfully reloaded from transactions.csv!');
                } catch (e) {
                  console.error(e);
                  alert('Error reloading from CSV. Check backend server.');
                }
              }}
              style={{
                width: '100%',
                background: 'rgba(232, 119, 10, 0.1)',
                border: '1px dashed var(--color-saffron)',
                color: 'var(--color-saffron)',
                borderRadius: '6px',
                padding: '5px 8px',
                fontSize: '0.72rem',
                cursor: 'pointer',
                marginBottom: '0.5rem',
                fontWeight: 500,
              }}
            >
              🔄 {t('syncCsv')}
            </button>

            <button
              className="sidebar-link"
              onClick={handleLogout}
              style={{ marginTop: '0.25rem', color: 'rgba(255,255,255,0.5)' }}
              aria-label="Log out"
            >
              <LogOut className="sidebar-link-icon" aria-hidden />
              {t('logout')}
            </button>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <div className="main-content">
        {/* Inner wrapper only — keeps main-content's own CSS position (fixed/sticky/etc) untouched */}
        <div style={{ position: 'relative', width: '100%', minHeight: '100%' }}>
          {/* Ambient nebula layer — sits behind the topbar/Outlet, confined to main-content only */}
          <div
            aria-hidden
            style={{
              position: 'absolute',
              inset: 0,
              zIndex: 0,
              opacity: 0.16,
              pointerEvents: 'none',
              overflow: 'hidden',
            }}
          >
            <NebulaBackground />
          </div>

          {/* Mobile top bar */}
          <header className="mobile-topbar" style={{ position: 'relative', zIndex: 1 }}>
            <button
              className="btn-icon"
              style={{ color: '#fff' }}
              onClick={() => setSidebarOpen(true)}
              aria-label="Open navigation menu"
            >
              <Menu size={22} />
            </button>
            <div className="mobile-logo">Saarthi<span>.</span></div>
            <div className="sidebar-avatar" style={{ width: 32, height: 32, fontSize: '0.75rem', ...(profilePhoto ? { backgroundImage: `url(${profilePhoto})`, backgroundSize: 'cover', backgroundPosition: 'center', color: 'transparent' } : {}) }} aria-hidden>
              {profilePhoto ? '' : initials}
            </div>
          </header>

          <div style={{ position: 'relative', zIndex: 1 }}>
            <Outlet />
          </div>
        </div>
      </div>

      {/* Mobile bottom nav */}
      <nav className="bottom-nav" aria-label={t('navigation')}>
        <div className="bottom-nav-inner">
          {NAV_ITEMS.slice(0, 5).map(({ to, key, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `bottom-nav-item ${isActive ? 'active' : ''}`}
              aria-label={t(key)}
            >
              <Icon aria-hidden />
              <span>{key === 'askSaarthi' ? 'Saarthi' : t(key)}</span>
            </NavLink>
          ))}
        </div>
      </nav>

      {profileOpen && (
        <div className="profile-modal-backdrop" onClick={() => setProfileOpen(false)}>
          <section className="profile-modal" onClick={event => event.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="profile-title">
            <div className="profile-modal-header">
              <div>
                <div className="profile-eyebrow">Saarthi Finance</div>
                <h2 id="profile-title">Edit your profile</h2>
              </div>
              <button className="btn-icon" onClick={() => setProfileOpen(false)} aria-label="Close profile editor"><X size={20} /></button>
            </div>

            <div className="profile-photo-row">
              <button className="profile-photo-button" onClick={() => photoInputRef.current?.click()} aria-label="Change profile photo">
                <div className="profile-photo" style={profilePhoto ? { backgroundImage: `url(${profilePhoto})`, backgroundSize: 'cover', backgroundPosition: 'center' } : undefined}>
                  {!profilePhoto && initials}
                </div>
                <span><Camera size={14} /> Change photo</span>
              </button>
              <input ref={photoInputRef} type="file" accept="image/*" hidden onChange={event => handlePhoto(event.target.files?.[0])} />
              <p>Keep your profile details current so your financial guidance stays personal.</p>
            </div>

            <div className="profile-form-grid">
              {[
                ['name', 'Full name', 'text'], ['phone', 'Phone number', 'tel'], ['address', 'Address', 'text'], ['city', 'City', 'text'],
                ['state', 'State', 'text'], ['occupation', 'Occupation', 'text'], ['age', 'Age', 'number'],
                ['dependents', 'Dependents', 'number'],
              ].map(([field, label, type]) => (
                <label key={field} className="profile-field">
                  <span>{label}</span>
                  <input type={type} value={profileForm[field as keyof typeof profileForm] ?? ''} onChange={event => setProfileForm(prev => ({ ...prev, [field]: type === 'number' ? (event.target.value ? Number(event.target.value) : undefined) : event.target.value }))} />
                </label>
              ))}
              <label className="profile-field">
                <span>Preferred language</span>
                <select value={profileForm.preferred_language} onChange={event => setProfileForm(prev => ({ ...prev, preferred_language: event.target.value as Language }))}>
                  <option value="en">English</option><option value="hi">हिन्दी</option><option value="mr">मराठी</option><option value="ta">தமிழ்</option><option value="bn">বাংলা</option>
                </select>
              </label>
            </div>

            {profileError && <div className="profile-error">{profileError}</div>}
            <div className="profile-modal-actions">
              <button className="btn btn-secondary" onClick={() => setProfileOpen(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={saveProfile} disabled={profileSaving}><Save size={15} /> {profileSaving ? 'Saving…' : 'Save changes'}</button>
            </div>
          </section>
        </div>
      )}
    </div>
  )
}
