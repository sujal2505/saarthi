// =============================================
// Saarthi Finance — API Client
// Tries real backend, falls back to mock data
// =============================================

import { MOCK_DASHBOARD } from '@/data/mockData'
import type {
  DashboardData,
  SimulatorInput,
  SimulatorOutput,
  Alert,
  Goal,
} from '@/types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`)
  return res.json() as Promise<T>
}

// -------- Dashboard ---------
export async function getDashboard(customerId: string): Promise<DashboardData> {
  if (USE_MOCK) return MOCK_DASHBOARD
  try {
    return await apiFetch<DashboardData>(`/api/v1/customers/${customerId}/dashboard`)
  } catch {
    console.warn('[Saarthi] Backend unavailable — using mock data')
    return MOCK_DASHBOARD
  }
}

// -------- Auth ---------
export async function demoLogin(phone: string, language: string): Promise<{ token: string; customer_id: string }> {
  if (USE_MOCK) {
    return { token: 'demo-jwt-token', customer_id: 'cust_001' }
  }
  try {
    return await apiFetch('/api/v1/auth/demo-login', {
      method: 'POST',
      body: JSON.stringify({ phone, language }),
    })
  } catch {
    return { token: 'demo-jwt-token', customer_id: 'cust_001' }
  }
}

// -------- Alerts ---------
export async function getAlerts(customerId: string): Promise<Alert[]> {
  if (USE_MOCK) return MOCK_DASHBOARD.alerts
  try {
    return await apiFetch<Alert[]>(`/api/v1/customers/${customerId}/alerts`)
  } catch {
    return MOCK_DASHBOARD.alerts
  }
}

// -------- Goals ---------
export async function getGoals(customerId: string): Promise<Goal[]> {
  if (USE_MOCK) return MOCK_DASHBOARD.goals
  try {
    return await apiFetch<Goal[]>(`/api/v1/customers/${customerId}/goals`)
  } catch {
    return MOCK_DASHBOARD.goals
  }
}

export async function createGoal(
  customerId: string,
  goal: Omit<Goal, 'id' | 'progress_pct' | 'months_remaining' | 'on_track'>
): Promise<Goal> {
  if (USE_MOCK) {
    return {
      ...goal,
      id: `g${Date.now()}`,
      progress_pct: (goal.current_amount / goal.target_amount) * 100,
      months_remaining: Math.ceil(
        (goal.target_amount - goal.current_amount) / goal.monthly_contribution
      ),
      on_track: true,
    }
  }
  try {
    return await apiFetch<Goal>(`/api/v1/customers/${customerId}/goals`, {
      method: 'POST',
      body: JSON.stringify(goal),
    })
  } catch {
    return {
      ...goal,
      id: `g${Date.now()}`,
      progress_pct: (goal.current_amount / goal.target_amount) * 100,
      months_remaining: Math.ceil(
        (goal.target_amount - goal.current_amount) / goal.monthly_contribution
      ),
      on_track: true,
    }
  }
}

// -------- Simulator ---------
export async function calculateEmi(input: SimulatorInput): Promise<SimulatorOutput> {
  // Always compute locally for instant feedback (also call API if available)
  const localResult = computeEmiLocally(input)
  if (USE_MOCK) return localResult
  try {
    return await apiFetch<SimulatorOutput>('/api/v1/simulator/emi', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  } catch {
    return localResult
  }
}

function computeEmiLocally(input: SimulatorInput): SimulatorOutput {
  const { loan_amount, interest_rate, tenure_months } = input
  const r = interest_rate / 100 / 12
  let monthly_emi = 0
  if (r === 0) {
    monthly_emi = loan_amount / tenure_months
  } else {
    monthly_emi = (loan_amount * r * Math.pow(1 + r, tenure_months)) / (Math.pow(1 + r, tenure_months) - 1)
  }
  const total_repayment = monthly_emi * tenure_months
  const total_interest = total_repayment - loan_amount
  const monthly_income = MOCK_DASHBOARD.cash_flow.monthly_income
  const existing_emi = MOCK_DASHBOARD.cash_flow.monthly_emi
  const total_emi = existing_emi + monthly_emi
  const emi_to_income_ratio = total_emi / monthly_income
  const new_savings = monthly_income - MOCK_DASHBOARD.cash_flow.monthly_expenses - total_emi
  const new_savings_rate = (new_savings / monthly_income) * 100
  const health_impact = emi_to_income_ratio > 0.5 ? -18 : emi_to_income_ratio > 0.4 ? -10 : emi_to_income_ratio > 0.3 ? -5 : -2
  const is_affordable = emi_to_income_ratio < 0.45 && new_savings_rate > 10

  let warning: string | undefined
  if (emi_to_income_ratio > 0.5) {
    warning = 'Combined EMI would exceed 50% of income — this significantly strains your finances.'
  } else if (emi_to_income_ratio > 0.4) {
    warning = 'Combined EMI burden is high. Consider a smaller loan amount or longer tenure.'
  } else if (new_savings_rate < 10) {
    warning = 'This loan would reduce your savings rate below 10%. Try increasing the tenure.'
  }

  return {
    monthly_emi: Math.round(monthly_emi),
    total_repayment: Math.round(total_repayment),
    total_interest: Math.round(total_interest),
    emi_to_income_ratio: Math.round(emi_to_income_ratio * 100) / 100,
    new_savings_rate: Math.round(new_savings_rate * 10) / 10,
    health_impact,
    is_affordable,
    warning,
  }
}

// -------- Assistant ---------
export interface ChatRequest {
  customer_id: string
  message: string
  language: string
  customer_name?: string
}

export async function sendMessage(req: ChatRequest): Promise<{ reply: string }> {
  if (USE_MOCK) return { reply: getMockAssistantReply(req.message, req.language, req.customer_id, req.customer_name) }
  try {
    return await apiFetch<{ reply: string }>('/api/v1/assistant/chat', {
      method: 'POST',
      body: JSON.stringify(req),
    })
  } catch {
    return { reply: getMockAssistantReply(req.message, req.language, req.customer_id, req.customer_name) }
  }
}

function getMockAssistantReply(message: string, language: string, customerId?: string, customerName?: string): string {
  const m = message.toLowerCase()
  const isHindi = language === 'hi' || /kya|kaise|mera|meri|bachat|kharcha|paisa/i.test(message)
  const name = customerName?.split(' ')[0] || (customerId === 'cust_002' ? 'Ramesh' : 'Ananya')
  const isStressed = customerId === 'cust_002' || customerId === 'cust_004' || customerId === 'cust_005' || customerId === 'cust_007'

  if (m.includes('loan') || m.includes('lena') || m.includes('borrow') || m.includes('karj')) {
    if (isStressed) {
      return isHindi
        ? `${name} ji, aapka financial health score abhi kam hai aur EMI burden zyada hai. Hamare responsible lending niyam ke tahat naye loan ke offers suppress kiye gaye hain taaki aap par aur karz na badhe. Pehle debt restructuring par dhyan dein.\n\n*Disclaimer: Yeh sirf financial guidance hai. Loan approval ke liye bank se sampark karein.*`
        : `${name}, your financial health score indicates financial stress and high EMI burden. Under our responsible lending safeguards, new loan recommendations are suppressed to protect you from debt distress. We suggest debt restructuring counselling.`
    }
    return isHindi
      ? `${name} ji, aapka financial health score accha hai. Lekin naya loan lene se pehle emergency fund aur budget zaroor check karein. Yeh guidance hai, formal loan approval nahi.\n\n*Disclaimer: Yeh sirf financial guidance hai. Loan approval ke liye bank se sampark karein.*`
      : `${name}, your financial health score is stable. You can explore safe borrowing, but please use the Borrowing Simulator to verify that your monthly savings remain protected.`
  }
  if (m.includes('savings') || m.includes('bachat') || m.includes('save')) {
    return isHindi
      ? `${name} ji, apni aamdani ka kam se kam 20% bachana ek surakshit aadat hai. Aap hamare Goal Planning section mein naya savings goal set kar sakte hain.`
      : `${name}, saving at least 20% of your income builds strong financial resilience. You can track automated milestones in the Goal Planning tab.`
  }
  if (m.includes('emi') || m.includes('repay')) {
    return isHindi
      ? `${name} ji, EMI ko hamesha monthly income ke 40% se kam rakhna surakshit maana jata hai.`
      : `${name}, keeping your total EMI below 40% of monthly income is recommended for financial safety.`
  }
  if (m.includes('kharcha') || m.includes('expense') || m.includes('spend')) {
    return isHindi
      ? `${name} ji, Spending Analysis page par jakar aap apne sabhi categories ka kharch dekh sakte hain.`
      : `${name}, you can review your complete category-wise spending patterns in the Spending Analysis tab.`
  }
  return isHindi
    ? `Namaste ${name} ji! Main Saarthi hoon — aapka financial guide. Aap apne kharche, savings, loan ya goals ke baare mein sawaal pooch sakte hain.`
    : `Hello ${name}! I am Saarthi, your financial guide. Feel free to ask about your spending, savings, EMI burden, or safe borrowing.`
}
