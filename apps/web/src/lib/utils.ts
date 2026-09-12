// =============================================
// Saarthi Finance — Utility Functions
// =============================================

/**
 * Format a number as Indian Rupee (₹)
 */
export function formatRupee(amount: number, compact = false): string {
  if (compact) {
    if (amount >= 10_00_000) return `₹${(amount / 10_00_000).toFixed(1)}L`
    if (amount >= 1_00_000) return `₹${(amount / 1_00_000).toFixed(1)}L`
    if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`
    return `₹${amount}`
  }
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

/**
 * Format a date string to readable Indian format
 */
export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

/**
 * Format a date to relative (e.g. "2 days ago")
 */
export function formatRelativeDate(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))
  if (diff === 0) return 'Today'
  if (diff === 1) return 'Yesterday'
  if (diff < 7) return `${diff} days ago`
  return formatDate(dateStr)
}

/**
 * Get health score label color
 */
export function getHealthColor(score: number): string {
  if (score >= 80) return 'var(--color-green)'
  if (score >= 65) return 'var(--color-teal)'
  if (score >= 50) return 'var(--color-amber)'
  return 'var(--color-terracotta)'
}

/**
 * Get severity badge class
 */
export function getSeverityClass(severity: string): string {
  switch (severity) {
    case 'critical':
    case 'high': return 'badge-red'
    case 'medium': return 'badge-amber'
    case 'low': return 'badge-navy'
    default: return 'badge-navy'
  }
}

/**
 * Category emoji map
 */
export const CATEGORY_EMOJI: Record<string, string> = {
  Salary: '💰',
  Groceries: '🛒',
  Rent: '🏠',
  Utilities: '💡',
  Transport: '🚗',
  Healthcare: '🏥',
  Education: '📚',
  Shopping: '🛍️',
  Entertainment: '🎬',
  EMI: '🏦',
  Savings: '🐷',
  'UPI Transfer': '📱',
  Other: '📄',
}

/**
 * Category background color map
 */
export const CATEGORY_BG: Record<string, string> = {
  Salary: '#e8f5ee',
  Groceries: '#e6f7f5',
  Rent: '#e8ecf2',
  Utilities: '#fef3e2',
  Transport: '#f0f4f8',
  Healthcare: '#fdecea',
  Education: '#f0e8ff',
  Shopping: '#fff3e0',
  Entertainment: '#fce4ec',
  EMI: '#e8ecf2',
  Savings: '#e8f5ee',
  'UPI Transfer': '#e6f7f5',
  Other: '#f5f5f5',
}

/**
 * Clamp a number between min and max
 */
export function clamp(val: number, min: number, max: number): number {
  return Math.min(Math.max(val, min), max)
}

/**
 * Get goal type emoji
 */
export const GOAL_EMOJI: Record<string, string> = {
  emergency_fund: '🛡️',
  education: '🎓',
  home_repair: '🏡',
  festival: '🪔',
  vehicle: '🛵',
  custom: '⭐',
}

/**
 * Get goal type background
 */
export const GOAL_BG: Record<string, string> = {
  emergency_fund: '#e6f7f5',
  education: '#f0e8ff',
  home_repair: '#fef3e2',
  festival: '#fff3e0',
  vehicle: '#fdecea',
  custom: '#e8f5ee',
}
