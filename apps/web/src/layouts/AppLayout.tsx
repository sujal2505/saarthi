import { useState } from 'react'
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
} from 'lucide-react'
import { useAuth } from '@/lib/AuthContext'
import NebulaBackground from '@/components/NebulaBackground'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/spending', label: 'Spending', icon: PieChart },
  { to: '/borrowing', label: 'Borrowing', icon: HandCoins },
  { to: '/goals', label: 'Goals', icon: Target },
  { to: '/simulator', label: 'Simulator', icon: Calculator },
  { to: '/assistant', label: 'Ask Saarthi', icon: MessageCircle },
  { to: '/alerts', label: 'Alerts', icon: Bell },
]

export default function AppLayout() {
  const { customer, logout, customerId, switchCustomer } = useAuth()

  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const initials = customer?.name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase() ?? 'A'

  const handleLogout = () => {
    logout()
    navigate('/')
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
      <nav className={`sidebar ${sidebarOpen ? 'open' : ''}`} aria-label="Main navigation">
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
            <div className="sidebar-tagline">Banking that understands your next step.</div>
          </div>

          <div className="sidebar-nav" style={{ position: 'relative', zIndex: 1 }}>
            <div className="sidebar-section-label">Navigation</div>
            {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
                onClick={() => setSidebarOpen(false)}
              >
                <Icon className="sidebar-link-icon" aria-hidden />
                {label}
              </NavLink>
            ))}
          </div>

          <div className="sidebar-footer" style={{ position: 'relative', zIndex: 1 }}>
            <div className="sidebar-user">
              <div className="sidebar-avatar" aria-hidden>{initials}</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="sidebar-user-name">{customer?.name}</div>
                <div className="sidebar-user-city">{customer?.city}, {customer?.state}</div>
              </div>
            </div>

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
              🔄 Sync CSV to Database
            </button>

            <button
              className="sidebar-link"
              onClick={handleLogout}
              style={{ marginTop: '0.25rem', color: 'rgba(255,255,255,0.5)' }}
              aria-label="Log out"
            >
              <LogOut className="sidebar-link-icon" aria-hidden />
              Log out
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
            <div className="sidebar-avatar" style={{ width: 32, height: 32, fontSize: '0.75rem' }} aria-hidden>
              {initials}
            </div>
          </header>

          <div style={{ position: 'relative', zIndex: 1 }}>
            <Outlet />
          </div>
        </div>
      </div>

      {/* Mobile bottom nav */}
      <nav className="bottom-nav" aria-label="Mobile navigation">
        <div className="bottom-nav-inner">
          {NAV_ITEMS.slice(0, 5).map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `bottom-nav-item ${isActive ? 'active' : ''}`}
              aria-label={label}
            >
              <Icon aria-hidden />
              <span>{label === 'Ask Saarthi' ? 'Saarthi' : label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}
