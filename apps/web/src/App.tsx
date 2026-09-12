import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './lib/AuthContext'
import AppLayout from './layouts/AppLayout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import SpendingPage from './pages/SpendingPage'
import BorrowingPage from './pages/BorrowingPage'
import GoalsPage from './pages/GoalsPage'
import SimulatorPage from './pages/SimulatorPage'
import AssistantPage from './pages/AssistantPage'
import AlertsPage from './pages/AlertsPage'
import { GlowEffectProvider } from './components/Gloweffectprovider'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <>{children}</> : <Navigate to="/" replace />
}

export default function App() {
  const { isAuthenticated } = useAuth()

  return (
    <>
      <GlowEffectProvider />
      <Routes>
        <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
        <Route
          element={
            <PrivateRoute>
              <AppLayout />
            </PrivateRoute>
          }
        >
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/spending" element={<SpendingPage />} />
          <Route path="/borrowing" element={<BorrowingPage />} />
          <Route path="/goals" element={<GoalsPage />} />
          <Route path="/simulator" element={<SimulatorPage />} />
          <Route path="/assistant" element={<AssistantPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  )
}