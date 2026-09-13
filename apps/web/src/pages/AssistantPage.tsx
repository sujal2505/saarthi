/**
 * apps/web/src/pages/AssistantPage.tsx
 * - Matches dark nebula theme
 * - Calls Gemini via backend with correct request shape
 * - Falls back to mock only when backend is truly unavailable
 */

import { useState, useRef, useEffect, useCallback } from 'react'
import { useAuth } from '@/lib/AuthContext'
import { useI18n } from '@/lib/i18n'
import NebulaBackground from '@/components/NebulaBackground'

// ─── Types ───────────────────────────────────────────────────────────────────

interface Message {
  id: string
  role: 'user' | 'assistant'
  text: string
  timestamp: Date
}

// ─── Suggested prompts ────────────────────────────────────────────────────────

const SUGGESTED_PROMPTS = [
  'What is my biggest financial risk?',
  'What is my highest spending category?',
  'What is my emergency fund status?',
  'Why did my health score change?',
  'Am I saving enough each month?',
  'Can I afford a ₹10,000 loan right now?',
]

const API_BASE = import.meta.env.VITE_API_URL || ''

// ─── Component ────────────────────────────────────────────────────────────────

export default function AssistantPage() {
  // Safely destructure — works regardless of exact AuthContext field names
  const auth = useAuth() as unknown as Record<string, unknown>
  const customerId =
    (auth.customerId as string) ||
    (auth.customer_id as string) ||
    (auth.id as string) ||
    'cust_001'
  const customerName =
    (auth.customerName as string) ||
    (auth.customer_name as string) ||
    (auth.name as string) ||
    undefined
  const language =
    (auth.language as string) || (auth.lang as string) || 'en'
  const { t } = useI18n()

  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 140) + 'px'
  }

  const sendMsg = useCallback(
    async (text: string) => {
      const trimmed = text.trim()
      if (!trimmed || isLoading) return

      setError(null)

      const userMsg: Message = {
        id: crypto.randomUUID(),
        role: 'user',
        text: trimmed,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, userMsg])
      setInput('')
      if (inputRef.current) inputRef.current.style.height = 'auto'
      setIsLoading(true)

      try {
        // Build conversation history for context
        const history = messages.map((m) => ({
          role: m.role === 'assistant' ? 'model' : 'user',
          text: m.text,
        }))

        const token = localStorage.getItem('token') || sessionStorage.getItem('token') || ''

        const res = await fetch(`${API_BASE}/api/v1/assistant/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({
            customer_id: customerId,
            message: trimmed,
            language,
            customer_name: customerName,
            history,               // sent so Gemini has conversation context
          }),
        })

        if (!res.ok) throw new Error(`Server error ${res.status}`)
        const data = await res.json() as { reply: string }

        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            text: data.reply,
            timestamp: new Date(),
          },
        ])
      } catch (err: unknown) {
        const msg =
          err instanceof Error
            ? `Could not reach the assistant (${err.message}). Is the backend running?`
            : 'Something went wrong. Please try again.'
        setError(msg)
      } finally {
        setIsLoading(false)
        setTimeout(() => inputRef.current?.focus(), 50)
      }
    },
    [customerId, customerName, language, messages, isLoading]
  )

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMsg(input)
    }
  }

  const isEmpty = messages.length === 0

  return (
    <div className="sa-page">
      <NebulaBackground className="sa-nebula" brightness={0.82} />
      {/* ── Header ── */}
      <div className="sa-header">
        <div className="sa-avatar-lg">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"
              fill="currentColor"
            />
          </svg>
        </div>
        <div className="sa-header-text">
          <h1 className="sa-title">{t('askSaarthi')}</h1>
          <p className="sa-subtitle">
            {t('askPlain')}
          </p>
        </div>
        {messages.length > 0 && (
          <button className="sa-new-btn" onClick={() => setMessages([])}>
            + {t('newChat')}
          </button>
        )}
      </div>

      {/* ── Chat area ── */}
      <div className="sa-chat">
        {isEmpty ? (
          <div className="sa-empty">
            <div className="sa-empty-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                <path
                  d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"
                  fill="currentColor"
                  opacity="0.3"
                />
                <path
                  d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  fill="none"
                />
              </svg>
            </div>
            <p className="sa-empty-heading">{t('whatKnow')}</p>
            <p className="sa-empty-sub">
              {t('seeData')}
            </p>
            <div className="sa-grid">
              {SUGGESTED_PROMPTS.map((p) => (
                <button
                  key={p}
                  className="sa-chip"
                  onClick={() => sendMsg(p)}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="sa-messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`sa-msg sa-msg--${msg.role}`}>
                {msg.role === 'assistant' && (
                  <div className="sa-msg-avatar">S</div>
                )}
                <div className="sa-bubble">
                  <p className="sa-bubble-text">{msg.text}</p>
                  <time className="sa-bubble-time">
                    {msg.timestamp.toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </time>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="sa-msg sa-msg--assistant">
                <div className="sa-msg-avatar">S</div>
                <div className="sa-bubble sa-bubble--typing">
                  <span className="sa-dot" />
                  <span className="sa-dot" />
                  <span className="sa-dot" />
                </div>
              </div>
            )}

            {error && (
              <div className="sa-error">
                <span>⚠ {error}</span>
                <button onClick={() => setError(null)}>✕</button>
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* ── Input ── */}
      <div className="sa-input-bar">
        <textarea
          ref={inputRef}
          className="sa-input"
          placeholder={t('askPlaceholder')}
          value={input}
          rows={1}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button
          className="sa-send"
          onClick={() => sendMsg(input)}
          disabled={!input.trim() || isLoading}
          aria-label={t('send')}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path
              d="M22 2L11 13M22 2L15 22l-4-9-9-4 20-7z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>

      <style>{`
        /* ── Layout ── */
        .sa-page {
          display: flex;
          flex-direction: column;
          position: relative;
          height: calc(100vh - 2.5rem);
          width: min(860px, calc(100% - 2rem));
          min-height: 620px;
          margin: 1.25rem auto;
          background: rgba(8, 7, 28, 0.32);
          border: 1px solid rgba(167, 139, 250, 0.28);
          border-radius: 18px;
          box-shadow: 0 18px 48px rgba(5, 20, 25, 0.22);
          overflow: hidden;
          font-family: inherit;
        }
        .sa-nebula {
          z-index: 0;
          opacity: 0.96;
        }
        .sa-header,
        .sa-chat,
        .sa-input-bar {
          position: relative;
          z-index: 1;
        }

        /* ── Header ── */
        .sa-header {
          display: flex;
          align-items: center;
          gap: 14px;
          padding: 24px 28px 18px;
          background: rgba(10, 8, 34, 0.58);
          border-bottom: 1px solid rgba(167, 139, 250, 0.2);
          flex-shrink: 0;
        }
        .sa-avatar-lg {
          width: 44px;
          height: 44px;
          border-radius: 14px;
          background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          color: #ede9fe;
          flex-shrink: 0;
          box-shadow: 0 0 20px rgba(124, 58, 237, 0.4);
        }
        .sa-header-text { flex: 1; }
        .sa-title {
          font-size: 1.15rem;
          font-weight: 700;
          margin: 0;
          color: #f5f3ff;
          letter-spacing: -0.01em;
        }
        .sa-subtitle {
          font-size: 0.8rem;
          margin: 3px 0 0;
          color: #c4b5fd;
        }
        .sa-new-btn {
          background: rgba(124, 58, 237, 0.16);
          border: 1px solid rgba(167, 139, 250, 0.34);
          border-radius: 8px;
          color: #ddd6fe;
          font-size: 0.78rem;
          padding: 7px 13px;
          cursor: pointer;
          transition: all 0.15s;
          white-space: nowrap;
        }
        .sa-new-btn:hover {
          background: rgba(124, 58, 237, 0.3);
          color: #ffffff;
        }

        /* ── Chat area ── */
        .sa-chat {
          flex: 1;
          overflow-y: auto;
          padding: 24px 28px;
          background: rgba(8, 7, 28, 0.2);
          scroll-behavior: smooth;
        }
        .sa-chat::-webkit-scrollbar { width: 4px; }
        .sa-chat::-webkit-scrollbar-thumb {
          background: rgba(124, 58, 237, 0.25);
          border-radius: 2px;
        }

        /* ── Empty state ── */
        .sa-empty {
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          padding: 20px 0 10px;
        }
        .sa-empty-icon {
          width: 60px;
          height: 60px;
          border-radius: 18px;
          background: rgba(124, 58, 237, 0.14);
          border: 1px solid rgba(167, 139, 250, 0.26);
          display: flex;
          align-items: center;
          justify-content: center;
          color: #c4b5fd;
          margin-bottom: 16px;
        }
        .sa-empty-heading {
          font-size: 1.2rem;
          font-weight: 600;
          color: #f5f3ff;
          margin: 0 0 8px;
        }
        .sa-empty-sub {
          font-size: 0.875rem;
          color: #b8add4;
          margin: 0 0 28px;
          max-width: 380px;
          line-height: 1.55;
        }
        .sa-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 10px;
          width: 100%;
          max-width: 600px;
        }
        .sa-chip {
          background: rgba(24, 15, 58, 0.82);
          border: 1px solid rgba(167, 139, 250, 0.24);
          border-radius: 12px;
          padding: 13px 15px;
          font-size: 0.82rem;
          color: #ddd6fe;
          text-align: left;
          cursor: pointer;
          transition: all 0.15s;
          line-height: 1.4;
          backdrop-filter: blur(4px);
        }
        .sa-chip:hover {
          background: rgba(124, 58, 237, 0.28);
          border-color: rgba(196, 181, 253, 0.56);
          color: #ffffff;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(4, 30, 35, 0.24);
        }

        /* ── Messages ── */
        .sa-messages {
          display: flex;
          flex-direction: column;
          gap: 18px;
        }
        .sa-msg {
          display: flex;
          gap: 10px;
          align-items: flex-start;
        }
        .sa-msg--user { flex-direction: row-reverse; }
        .sa-msg-avatar {
          width: 32px;
          height: 32px;
          border-radius: 9px;
          background: linear-gradient(135deg, #4f46e5, #7c3aed);
          color: #f5f3ff;
          font-size: 0.78rem;
          font-weight: 700;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          margin-top: 2px;
          box-shadow: 0 0 10px rgba(124, 58, 237, 0.38);
        }
        .sa-bubble {
          max-width: 70%;
          border-radius: 16px;
          padding: 12px 16px;
          background: rgba(17, 59, 67, 0.94);
          border: 1px solid rgba(167, 139, 250, 0.24);
          backdrop-filter: blur(8px);
        }
        .sa-msg--user .sa-bubble {
          background: rgba(232, 119, 10, 0.2);
          border-color: rgba(245, 147, 50, 0.42);
        }
        .sa-bubble-text {
          margin: 0 0 5px;
          font-size: 0.9rem;
          line-height: 1.65;
          color: #f3fffd;
          white-space: pre-wrap;
          word-break: break-word;
        }
        .sa-bubble-time {
          font-size: 0.7rem;
          color: #a99bc7;
          display: block;
        }

        /* ── Typing dots ── */
        .sa-bubble--typing {
          display: flex;
          align-items: center;
          gap: 5px;
          padding: 16px 18px;
        }
        .sa-dot {
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: #7c3aed;
          animation: sa-blink 1.4s ease-in-out infinite;
        }
        .sa-dot:nth-child(2) { animation-delay: 0.2s; }
        .sa-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes sa-blink {
          0%, 60%, 100% { opacity: 0.25; transform: scale(0.75); }
          30% { opacity: 1; transform: scale(1); }
        }

        /* ── Error ── */
        .sa-error {
          display: flex;
          align-items: center;
          justify-content: space-between;
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.25);
          border-radius: 10px;
          padding: 10px 14px;
          font-size: 0.82rem;
          color: #fca5a5;
          gap: 12px;
        }
        .sa-error button {
          background: none;
          border: none;
          color: #fca5a5;
          cursor: pointer;
          font-size: 0.85rem;
          opacity: 0.6;
          flex-shrink: 0;
        }
        .sa-error button:hover { opacity: 1; }

        /* ── Input bar ── */
        .sa-input-bar {
          display: flex;
          align-items: flex-end;
          gap: 10px;
          padding: 14px 24px 24px;
          background: rgba(10, 8, 34, 0.58);
          border-top: 1px solid rgba(167, 139, 250, 0.2);
          flex-shrink: 0;
        }
        .sa-input {
          flex: 1;
          background: rgba(16, 11, 42, 0.88);
          border: 1px solid rgba(167, 139, 250, 0.32);
          border-radius: 14px;
          padding: 12px 16px;
          font-size: 0.9rem;
          color: #f5f3ff;
          font-family: inherit;
          resize: none;
          outline: none;
          transition: border-color 0.15s, background 0.15s;
          line-height: 1.5;
          max-height: 140px;
          overflow-y: auto;
          backdrop-filter: blur(8px);
        }
        .sa-input::placeholder { color: #8f82ad; }
        .sa-input:focus {
          border-color: rgba(196, 181, 253, 0.72);
          background: rgba(22, 14, 54, 0.96);
          box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.16);
        }
        .sa-input:disabled { opacity: 0.45; cursor: not-allowed; }
        .sa-send {
          width: 44px;
          height: 44px;
          border-radius: 12px;
          background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%);
          border: none;
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          flex-shrink: 0;
          transition: opacity 0.15s, box-shadow 0.15s;
          box-shadow: 0 0 16px rgba(124, 58, 237, 0.45);
        }
        .sa-send:hover:not(:disabled) {
          box-shadow: 0 0 22px rgba(124, 58, 237, 0.62);
        }
        .sa-send:disabled {
          opacity: 0.35;
          cursor: not-allowed;
          box-shadow: none;
        }

        @media (max-width: 520px) {
          .sa-page {
            width: calc(100% - 1rem);
            height: calc(100vh - 5.5rem);
            min-height: 520px;
            margin: 0.625rem auto;
          }
          .sa-grid { grid-template-columns: 1fr; }
          .sa-bubble { max-width: 86%; }
          .sa-header { padding: 16px 18px 14px; }
          .sa-chat { padding: 16px 18px; }
          .sa-input-bar { padding: 12px 16px 18px; }
        }
      `}</style>
    </div>
  )
}