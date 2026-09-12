import type {
  DashboardData,
  Transaction,
  MonthlyTrend,
  SpendingCategory,
  Goal,
} from '@/types'

// =============================================
// Saarthi Finance — Seed / Mock Data
// Primary persona: Ananya Verma, Indore
// =============================================

export const MOCK_TRANSACTIONS: Transaction[] = [
  { id: 't001', date: '2024-09-01', merchant: 'HDFC Salary Credit', category: 'Salary', amount: 58000, type: 'credit', channel: 'NEFT', recurring: true },
  { id: 't002', date: '2024-09-02', merchant: 'Reliance Fresh', category: 'Groceries', amount: 2200, type: 'debit', channel: 'UPI', recurring: false },
  { id: 't003', date: '2024-09-03', merchant: 'Indore Apartment Rent', category: 'Rent', amount: 11000, type: 'debit', channel: 'NEFT', recurring: true },
  { id: 't004', date: '2024-09-04', merchant: 'MP Electricity Board', category: 'Utilities', amount: 1100, type: 'debit', channel: 'UPI', recurring: true },
  { id: 't005', date: '2024-09-05', merchant: 'Rapido Bike', category: 'Transport', amount: 350, type: 'debit', channel: 'UPI', recurring: false },
  { id: 't006', date: '2024-09-06', merchant: 'Apollo Pharmacy', category: 'Healthcare', amount: 620, type: 'debit', channel: 'UPI', recurring: false },
  { id: 't007', date: '2024-09-07', merchant: 'Big Bazaar', category: 'Shopping', amount: 1800, type: 'debit', channel: 'UPI', recurring: false },
  { id: 't008', date: '2024-09-08', merchant: 'Byju\'s Subscription', category: 'Education', amount: 999, type: 'debit', channel: 'UPI', recurring: true },
  { id: 't009', date: '2024-09-10', merchant: 'SBI EMI', category: 'EMI', amount: 9500, type: 'debit', channel: 'Auto-debit', recurring: true },
  { id: 't010', date: '2024-09-11', merchant: 'Savings Transfer — RD', category: 'Savings', amount: 5000, type: 'debit', channel: 'NEFT', recurring: true },
  { id: 't011', date: '2024-09-12', merchant: 'D-Mart', category: 'Groceries', amount: 1750, type: 'debit', channel: 'UPI', recurring: false },
  { id: 't012', date: '2024-09-13', merchant: 'Myntra', category: 'Shopping', amount: 2400, type: 'debit', channel: 'Credit Card', recurring: false },
  { id: 't013', date: '2024-09-15', merchant: 'Netflix', category: 'Entertainment', amount: 649, type: 'debit', channel: 'Credit Card', recurring: true },
  { id: 't014', date: '2024-09-16', merchant: 'Zomato', category: 'Entertainment', amount: 480, type: 'debit', channel: 'UPI', recurring: false },
  { id: 't015', date: '2024-09-18', merchant: 'BSNL Broadband', category: 'Utilities', amount: 799, type: 'debit', channel: 'Auto-debit', recurring: true },
  { id: 't016', date: '2024-09-19', merchant: 'Ola Cabs', category: 'Transport', amount: 520, type: 'debit', channel: 'UPI', recurring: false },
  { id: 't017', date: '2024-09-20', merchant: 'Sister UPI Transfer', category: 'UPI Transfer', amount: 2000, type: 'debit', channel: 'UPI', recurring: false },
  { id: 't018', date: '2024-09-22', merchant: 'Indore Medical Clinic', category: 'Healthcare', amount: 350, type: 'debit', channel: 'UPI', recurring: false },
  { id: 't019', date: '2024-09-24', merchant: 'Amazon', category: 'Shopping', amount: 3200, type: 'debit', channel: 'Credit Card', recurring: false },
  { id: 't020', date: '2024-09-26', merchant: 'Petrol Pump UPI', category: 'Transport', amount: 600, type: 'debit', channel: 'UPI', recurring: false },
]

export const MOCK_MONTHLY_TREND: MonthlyTrend[] = [
  { month: 'Apr', income: 58000, expenses: 28500, savings: 20000 },
  { month: 'May', income: 58000, expenses: 29200, savings: 19300 },
  { month: 'Jun', income: 58000, expenses: 30100, savings: 18400 },
  { month: 'Jul', income: 58000, expenses: 31000, savings: 17500 },
  { month: 'Aug', income: 58000, expenses: 31500, savings: 17000 },
  { month: 'Sep', income: 58000, expenses: 31800, savings: 16700 },
]

export const MOCK_SPENDING_CATEGORIES: SpendingCategory[] = [
  { category: 'Rent', amount: 11000, percentage: 34.6, color: '#1a2332', trend: 'stable' },
  { category: 'EMI', amount: 9500, percentage: 29.9, color: '#e8770a', trend: 'stable' },
  { category: 'Groceries', amount: 3950, percentage: 12.4, color: '#0d7c6e', trend: 'up', change_pct: 8 },
  { category: 'Shopping', amount: 3200, percentage: 10.1, color: '#d97706', trend: 'up', change_pct: 24 },
  { category: 'Transport', amount: 1470, percentage: 4.6, color: '#4a5568', trend: 'stable' },
  { category: 'Utilities', amount: 1899, percentage: 6.0, color: '#2d7a4f', trend: 'stable' },
  { category: 'Healthcare', amount: 970, percentage: 3.1, color: '#c0392b', trend: 'stable' },
  { category: 'Entertainment', amount: 1129, percentage: 3.5, color: '#9b59b6', trend: 'up', change_pct: 15 },
]

export const MOCK_GOALS: Goal[] = [
  {
    id: 'g001',
    type: 'emergency_fund',
    name: 'Emergency Fund',
    target_amount: 150000,
    current_amount: 60000,
    target_date: '2025-06-30',
    monthly_contribution: 5000,
    progress_pct: 40,
    months_remaining: 18,
    on_track: true,
  },
  {
    id: 'g002',
    type: 'education',
    name: 'Online Certification',
    target_amount: 35000,
    current_amount: 12000,
    target_date: '2025-03-31',
    monthly_contribution: 3500,
    progress_pct: 34.3,
    months_remaining: 6,
    on_track: true,
  },
  {
    id: 'g003',
    type: 'festival',
    name: 'Diwali Celebrations',
    target_amount: 20000,
    current_amount: 8000,
    target_date: '2024-10-31',
    monthly_contribution: 4000,
    progress_pct: 40,
    months_remaining: 2,
    on_track: false,
  },
  {
    id: 'g004',
    type: 'home_repair',
    name: 'Home Renovation',
    target_amount: 80000,
    current_amount: 5000,
    target_date: '2025-12-31',
    monthly_contribution: 4750,
    progress_pct: 6.3,
    months_remaining: 15,
    on_track: true,
  },
]

export const MOCK_DASHBOARD: DashboardData = {
  customer: {
    id: 'cust_001',
    name: 'Ananya Verma',
    city: 'Indore',
    state: 'Madhya Pradesh',
    preferred_language: 'hi',
    phone: '98XXXXX321',
    age: 31,
    occupation: 'Marketing Executive',
    dependents: 2,
  },
  financial_health: {
    score: 76,
    label: 'Stable',
    change: 3,
    components: {
      income_stability: 84,
      savings: 72,
      expense_management: 70,
      debt_burden: 75,
      repayment_behavior: 89,
      liquidity: 68,
    },
    positive_factors: [
      'Income has remained stable for the last six months',
      'Savings rate is above the recommended minimum',
      'EMI repayments are consistent with no missed payments',
    ],
    risk_factors: [
      'Household expenses have increased over the last two months',
      'Shopping category spending rose by 24% last month',
      'Emergency fund is below 3-month safety threshold',
    ],
    explanation:
      'Your financial health is stable. You have consistent income and a healthy savings habit. Some recent expense increases in shopping and groceries are worth watching — if they continue, your savings rate could drop below the recommended 25% threshold.',
  },
  cash_flow: {
    monthly_income: 58000,
    monthly_expenses: 31800,
    monthly_emi: 9500,
    monthly_savings: 16700,
    savings_rate: 28.8,
  },
  recommendation: {
    type: 'savings',
    title: 'Build a stronger emergency buffer',
    product: 'Emergency Savings Plan',
    recommended_amount: 5000,
    confidence: 0.91,
    why: [
      'Your income is stable and predictable',
      'Your savings rate is currently healthy at 28.8%',
      'Household expenses have been rising — a buffer protects you',
      'Your current emergency fund covers only 1.2 months of expenses',
    ],
    warning: 'This is financial guidance, not a loan approval or financial product guarantee. Please consult a certified financial advisor before making major decisions.',
    human_review_required: false,
    suppressed: false,
  },
  alerts: [
    {
      id: 'alert_001',
      type: 'cash_flow',
      severity: 'medium',
      title: 'Monthly expenses rising steadily',
      description: 'Your household spending increased by ₹3,300 (12%) over the last two months. If this trend continues, your savings rate may fall below 25%.',
      evidence: 'Aug expenses: ₹31,500 → Sep expenses: ₹31,800',
      action: 'Review your recurring expenses and identify where you can cut back.',
      action_label: 'Review Expenses',
    },
    {
      id: 'alert_002',
      type: 'unusual_spending',
      severity: 'low',
      title: 'Shopping spend 24% higher than usual',
      description: 'You spent ₹3,200 on shopping this month, compared to your usual ₹2,600. This includes Amazon and Myntra purchases.',
      evidence: 'Shopping: ₹3,200 vs usual ₹2,580',
      action: 'If these are one-time purchases, no action needed. Otherwise, consider reviewing your subscriptions.',
      action_label: 'View Transactions',
    },
  ],
  recent_transactions: MOCK_TRANSACTIONS.slice(0, 8),
  goals: MOCK_GOALS,
  assistant_context: {
    summary:
      'Ananya has stable income of ₹58,000/month, healthy savings rate of 28.8%, and moderate expense pressure. Her EMI burden (16.4%) is within safe limits. Main concern: household expenses rising over last 2 months. Emergency fund is below safety threshold.',
  },
  monthly_trend: MOCK_MONTHLY_TREND,
  spending_categories: MOCK_SPENDING_CATEGORIES,
}

// -------- Other customers (for suppression demo) --------
export const STRESSED_CUSTOMER_DASHBOARD: Partial<DashboardData> = {
  customer: {
    id: 'cust_002',
    name: 'Ramesh Patil',
    city: 'Nashik',
    state: 'Maharashtra',
    preferred_language: 'mr',
    age: 38,
    occupation: 'Auto Driver',
    dependents: 4,
  },
  financial_health: {
    score: 41,
    label: 'Poor',
    change: -8,
    components: {
      income_stability: 35,
      savings: 22,
      expense_management: 45,
      debt_burden: 28,
      repayment_behavior: 62,
      liquidity: 18,
    },
    positive_factors: ['EMI payments are still on time'],
    risk_factors: [
      'Income dropped by 22% in last 2 months',
      'Savings rate fell to 4%',
      'EMI-to-income ratio exceeds safe threshold',
      'Negative cash flow detected',
    ],
    explanation:
      'Your finances are under significant stress. Income has declined while obligations remain high. We strongly recommend against taking on new debt until your financial situation stabilizes.',
  },
  cash_flow: {
    monthly_income: 22000,
    monthly_expenses: 18500,
    monthly_emi: 4200,
    monthly_savings: -700,
    savings_rate: -3.2,
  },
  recommendation: {
    type: 'restructure',
    title: 'Focus on stabilizing before borrowing',
    product: 'Financial Counselling Support',
    recommended_amount: 0,
    confidence: 0.95,
    why: [
      'New debt would increase stress significantly',
      'Income instability makes repayments unpredictable',
      'Current EMI burden is already at risk level',
    ],
    warning: 'A loan recommendation is not suitable at this time. Saarthi recommends speaking with a financial counsellor.',
    human_review_required: true,
    suppressed: true,
    suppression_reason: 'High financial stress detected. Loan offers suppressed to protect customer.',
  },
  alerts: [
    {
      id: 'stress_001',
      type: 'stress',
      severity: 'high',
      title: 'Financial stress detected',
      description: 'Income dropped significantly in the last two months while expenses remained high. Your cash flow is now negative.',
      evidence: 'Monthly shortfall: ₹700 | EMI burden: 19.1%',
      action: 'Consider speaking with a financial counsellor to explore options.',
      action_label: 'Talk to Support',
    },
  ],
}
