// =============================================
// Saarthi Finance — Shared TypeScript Types
// =============================================

export type Language = 'en' | 'hi' | 'mr' | 'ta' | 'bn'

// -------- Customer ---------
export interface Customer {
  id: string
  name: string
  city: string
  state: string
  preferred_language: Language
  phone?: string
  age?: number
  occupation?: string
  dependents?: number
}

// -------- Financial Health ---------
export interface HealthComponents {
  income_stability: number
  savings: number
  expense_management: number
  debt_burden: number
  repayment_behavior: number
  liquidity: number
}

export interface FinancialHealth {
  score: number
  label: 'Excellent' | 'Good' | 'Stable' | 'Fair' | 'Poor'
  change: number // +/- from last month
  components: HealthComponents
  positive_factors: string[]
  risk_factors: string[]
  explanation: string
}

// -------- Cash Flow ---------
export interface CashFlow {
  monthly_income: number
  monthly_expenses: number
  monthly_emi: number
  monthly_savings: number
  savings_rate: number
}

// -------- Recommendation ---------
export interface Recommendation {
  type: 'savings' | 'loan' | 'insurance' | 'investment' | 'credit_card' | 'restructure' | string
  title: string
  product: string
  recommended_amount: number
  estimated_emi?: number
  confidence: number
  why: string[]
  warning: string
  human_review_required: boolean
  suppressed?: boolean
  loan_suppressed?: boolean
  suppression_reason?: string
  category?: string
  not_recommended?: string[]
  not_recommended_reason?: string
}

// -------- Alert ---------
export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical'
export type AlertType =
  | 'cash_flow'
  | 'unusual_spending'
  | 'missed_emi_risk'
  | 'savings_decline'
  | 'fraud_review'
  | 'stress'
  | 'expense_surge'
  | string

export interface Alert {
  id: string
  type: AlertType
  severity: AlertSeverity
  title: string
  description: string
  evidence?: string
  action: string
  action_label?: string
}

// -------- Transaction ---------
export type TransactionCategory =
  | 'Salary'
  | 'Groceries'
  | 'Rent'
  | 'Utilities'
  | 'Transport'
  | 'Healthcare'
  | 'Education'
  | 'Shopping'
  | 'Entertainment'
  | 'EMI'
  | 'Savings'
  | 'UPI Transfer'
  | 'Other'

export interface Transaction {
  id: string
  date: string
  merchant: string
  category: TransactionCategory
  amount: number
  type: 'credit' | 'debit'
  channel?: string
  recurring?: boolean
  description?: string
}

// -------- Monthly Trend ---------
export interface MonthlyTrend {
  month: string // e.g. "Apr"
  income: number
  expenses: number
  savings: number
}

// -------- Spending Category ---------
export interface SpendingCategory {
  category: TransactionCategory
  amount: number
  percentage: number
  color: string
  trend?: 'up' | 'down' | 'stable'
  change_pct?: number
}

// -------- Goal ---------
export type GoalType = 'emergency_fund' | 'education' | 'home_repair' | 'festival' | 'vehicle' | 'custom'

export interface Goal {
  id: string
  type: GoalType
  name: string
  target_amount: number
  current_amount: number
  target_date: string
  monthly_contribution: number
  progress_pct: number
  months_remaining: number
  on_track: boolean
}

// -------- Simulator ---------
export interface SimulatorInput {
  loan_amount: number
  interest_rate: number
  tenure_months: number
  monthly_savings_delta?: number
}

export interface SimulatorOutput {
  monthly_emi: number
  total_repayment: number
  total_interest: number
  emi_to_income_ratio: number
  new_savings_rate: number
  health_impact: number // delta to health score
  is_affordable: boolean
  warning?: string
}

// -------- Assistant ---------
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  language: Language
}

export interface AssistantContext {
  summary: string
}

// -------- Dashboard (full) ---------
export interface DashboardData {
  customer: Customer
  financial_health: FinancialHealth
  cash_flow: CashFlow
  recommendation: Recommendation
  alerts: Alert[]
  recent_transactions: Transaction[]
  goals: Goal[]
  assistant_context: AssistantContext
  monthly_trend: MonthlyTrend[]
  spending_categories: SpendingCategory[]
}

// -------- API generic ---------
export interface ApiResponse<T> {
  data: T | null
  error: string | null
  loading: boolean
}
