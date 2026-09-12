import { useState, useRef, useEffect, useCallback } from 'react'
import { sendMessage } from '@/lib/api'
import { useAuth } from '@/lib/AuthContext'

/**
 * Terminal styles (.term-*) live in src/styles/globals.css, appended at the
 * end of that file — no separate stylesheet needed since globals.css is
 * already imported once, app-wide.
 *
 * NOTE: `language` is read from `customer?.preferred_language` with a
 * fallback to 'en'. If your AuthContext's Customer type names this field
 * differently (e.g. `language`), adjust the one line below where it's read.
 */

type LineKind = 'input' | 'output' | 'error' | 'system'

interface TerminalLine {
  id: string
  kind: LineKind
  text: string
  /** only 'output' lines get the typewriter effect */
  animate?: boolean
}

const PROMPT_USER = 'you@saarthi:~$'
const PROMPT_BOT = 'saarthi>'

const SUGGESTIONS = [
  'Why is my financial health score low?',
  'Can I afford to take a new loan right now?',
  'How much am I overspending this month?',
  'Help me build an emergency fund',
]

const WELCOME_LINES: TerminalLine[] = [
  { id: 'w1', kind: 'system', text: 'Saarthi Assistant — v1.0 (synthetic data, demo mode)' },
  { id: 'w2', kind: 'system', text: 'Type a question about your money, or try one of the suggestions below.' },
]

function useTypewriter(fullText: string, speed = 18, onDone?: () => void) {
  const [shown, setShown] = useState('')
  useEffect(() => {
    setShown('')
    if (!fullText) return
    let i = 0
    const id = setInterval(() => {
      i += 1
      setShown(fullText.slice(0, i))
      if (i >= fullText.length) {
        clearInterval(id)
        onDone?.()
      }
    }, speed)
    return () => clearInterval(id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fullText])
  return shown
}

function TerminalOutputLine({ text, prompt }: { text: string; prompt: string }) {
  const shown = useTypewriter(text)
  const done = shown.length >= text.length
  return (
    <div className="term-line term-line--output">
      <span className="term-prompt term-prompt--bot">{prompt}</span>
      <span className="term-text">
        {shown}
        {!done && <span className="term-cursor" />}
      </span>
    </div>
  )
}

export default function AssistantPage() {
  const { customerId, customer } = useAuth() as {
    customerId: string
    customer?: { name?: string; preferred_language?: string; language?: string }
  }
  const language = customer?.preferred_language ?? customer?.language ?? 'en'
  const [lines, setLines] = useState<TerminalLine[]>(WELCOME_LINES)
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [lines, busy])

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const pushLine = useCallback((line: Omit<TerminalLine, 'id'>) => {
    setLines(prev => [...prev, { ...line, id: `${Date.now()}-${Math.random()}` }])
  }, [])

  const runCommand = useCallback(async (raw: string) => {
    const command = raw.trim()
    if (!command) return

    pushLine({ kind: 'input', text: command })

    if (command.toLowerCase() === 'clear') {
      setLines(WELCOME_LINES)
      return
    }
    if (command.toLowerCase() === 'help') {
      pushLine({ kind: 'system', text: 'Try: ' + SUGGESTIONS.join('  •  ') })
      return
    }

    setBusy(true)
    try {
      const res = await sendMessage({
        customer_id: customerId,
        message: command,
        language,
        customer_name: customer?.name,
      })
      pushLine({ kind: 'output', text: res.reply, animate: true })
    } catch {
      pushLine({ kind: 'error', text: 'Could not reach Saarthi Assistant. Please try again.' })
    } finally {
      setBusy(false)
    }
  }, [customerId, customer, language, pushLine])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (busy) return
    const value = input
    setInput('')
    runCommand(value)
  }

  return (
    <div className="page-container fade-in">
      <div className="page-header">
        <h1 style={{ fontFamily: 'var(--font-display)' }}>Ask Saarthi</h1>
        <p>Your financial questions, answered in plain language.</p>
      </div>

      <div className="term-window">
        <div className="term-titlebar">
          <div className="term-dots">
            <span className="term-dot term-dot--red" />
            <span className="term-dot term-dot--amber" />
            <span className="term-dot term-dot--green" />
          </div>
          <div className="term-title">saarthi@finance — ask</div>
          <div style={{ width: 54 }} />
        </div>

        <div className="term-body" ref={scrollRef}>
          {lines.map(line => {
            if (line.kind === 'input') {
              return (
                <div key={line.id} className="term-line term-line--input">
                  <span className="term-prompt term-prompt--user">{PROMPT_USER}</span>
                  <span className="term-text">{line.text}</span>
                </div>
              )
            }
            if (line.kind === 'error') {
              return (
                <div key={line.id} className="term-line term-line--error">
                  <span className="term-prompt term-prompt--bot">{PROMPT_BOT}</span>
                  <span className="term-text">{line.text}</span>
                </div>
              )
            }
            if (line.kind === 'system') {
              return (
                <div key={line.id} className="term-line term-line--system">
                  <span className="term-text">{line.text}</span>
                </div>
              )
            }
            return line.animate
              ? <TerminalOutputLine key={line.id} text={line.text} prompt={PROMPT_BOT} />
              : (
                <div key={line.id} className="term-line term-line--output">
                  <span className="term-prompt term-prompt--bot">{PROMPT_BOT}</span>
                  <span className="term-text">{line.text}</span>
                </div>
              )
          })}

          {busy && (
            <div className="term-line term-line--output">
              <span className="term-prompt term-prompt--bot">{PROMPT_BOT}</span>
              <span className="term-typing">
                <span className="term-typing-dot" />
                <span className="term-typing-dot" />
                <span className="term-typing-dot" />
              </span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="term-line term-line--prompt">
            <span className="term-prompt term-prompt--user">{PROMPT_USER}</span>
            <input
              ref={inputRef}
              className="term-input"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder={busy ? 'Waiting for Saarthi…' : 'Ask a question and press Enter'}
              disabled={busy}
              autoComplete="off"
              spellCheck={false}
            />
          </form>
        </div>
      </div>

      <div className="term-suggestions">
        {SUGGESTIONS.map(s => (
          <button
            key={s}
            className="chip"
            onClick={() => !busy && runCommand(s)}
            disabled={busy}
            type="button"
          >
            {s}
          </button>
        ))}
      </div>

      <p className="term-disclaimer">
        Saarthi Assistant offers general financial guidance based on synthetic demo data — not personalised investment or loan advice.
      </p>
    </div>
  )
}