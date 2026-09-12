import { useEffect, useRef } from 'react'

/**
 * GlowingEffect — a lightweight, dependency-free reimplementation of the
 * Aceternity "glowing border" effect, restyled to Saarthi's palette
 * (saffron → teal) instead of the default rainbow/gray glow.
 *
 * Usage: place as the FIRST child inside a `position: relative` container
 * that has its own border-radius (e.g. `.card`, `.glow-card`). It tracks
 * the pointer anywhere on the page and lights up the container's border
 * when the pointer comes within `proximity` px of it.
 *
 * Renders nothing visually itself — it just measures and sets CSS custom
 * properties (--glow-x, --glow-y, --glow-opacity) that `.glow-effect` in
 * globals.css reads to paint the ring.
 */
interface GlowingEffectProps {
    /** Radius (px) of the glow's radial gradient. */
    spread?: number
    /** Distance (px) from the element's edge at which the glow starts fading in. */
    proximity?: number
    /** Disable the effect entirely (e.g. on touch devices, or a "muted" card). */
    disabled?: boolean
    /** Ring color at the pointer position. Defaults to brand saffron. */
    colorFrom?: string
    /** Ring color away from the pointer. Defaults to brand teal. */
    colorTo?: string
}

export function GlowingEffect({
    spread = 60,
    proximity = 110,
    disabled = false,
    colorFrom = 'var(--color-saffron-light)',
    colorTo = 'var(--color-teal-light)',
}: GlowingEffectProps) {
    const ref = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (disabled) return
        const el = ref.current
        const card = el?.parentElement
        if (!el || !card) return

        let raf = 0

        const handlePointerMove = (e: PointerEvent) => {
            cancelAnimationFrame(raf)
            raf = requestAnimationFrame(() => {
                const rect = card.getBoundingClientRect()
                const x = e.clientX - rect.left
                const y = e.clientY - rect.top
                const withinX = x > -proximity && x < rect.width + proximity
                const withinY = y > -proximity && y < rect.height + proximity

                if (withinX && withinY) {
                    // distance to nearest edge, used to fade the glow in as it approaches
                    const distX = x < 0 ? -x : x > rect.width ? x - rect.width : 0
                    const distY = y < 0 ? -y : y > rect.height ? y - rect.height : 0
                    const dist = Math.sqrt(distX * distX + distY * distY)
                    const opacity = 1 - Math.min(dist / proximity, 1)

                    // Set on the CARD (parent), not just this element — custom
                    // properties inherit downward, so both the ring (.glow-effect)
                    // and the outer bloom (box-shadow on .glow-card itself) react.
                    card.style.setProperty('--glow-x', `${x}px`)
                    card.style.setProperty('--glow-y', `${y}px`)
                    card.style.setProperty('--glow-opacity', String(Math.max(opacity, 0.35)))
                } else {
                    card.style.setProperty('--glow-opacity', '0')
                }
            })
        }

        window.addEventListener('pointermove', handlePointerMove, { passive: true })
        return () => {
            window.removeEventListener('pointermove', handlePointerMove)
            cancelAnimationFrame(raf)
        }
    }, [disabled, proximity])

    if (disabled) return null

    return (
        <div
            ref={ref}
            className="glow-effect"
            aria-hidden
            style={
                {
                    '--glow-spread': `${spread}px`,
                    '--glow-from': colorFrom,
                    '--glow-to': colorTo,
                } as React.CSSProperties
            }
        />
    )
}

/**
 * GlowCard — drop-in replacement for a plain `.card` div when you want the
 * proximity glow. Wrap existing card content with it, e.g.:
 *
 *   <GlowCard>
 *     <div className="section-title">Quick Actions</div>
 *     ...
 *   </GlowCard>
 *
 * Pass `as="div"` styles or extra classes via `className` — GlowCard already
 * includes your `.card` base styling.
 */
export function GlowCard({
    children,
    className = '',
    baseClass = 'card',
    style,
    proximity = 72,
    spread = 40,
    disabled = false,
}: {
    children: React.ReactNode
    className?: string
    /** Base styling class this box already uses — 'card' (default), 'stat-card', 'goal-card', etc. */
    baseClass?: string
    style?: React.CSSProperties
    proximity?: number
    spread?: number
    disabled?: boolean
}) {
    return (
        <div className={`glow-card ${baseClass} ${className}`} style={style}>
            <GlowingEffect proximity={proximity} spread={spread} disabled={disabled} />
            <div className="glow-card-content">{children}</div>
        </div>
    )
}