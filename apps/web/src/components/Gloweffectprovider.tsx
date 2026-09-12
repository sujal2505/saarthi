import { useEffect, useRef } from 'react'

/**
 * GlowEffectProvider — mount this ONCE near the root of the app (e.g. in
 * `App.tsx`, above/around your <Routes>). Once mounted, every box on every
 * page — current ones and any you add later — gets the ambient ring +
 * pointer-tracked highlight + bloom defined under "42. Glowing Effect" in
 * globals.css, automatically.
 *
 * This does NOT reimplement the visual effect — that already lives in
 * globals.css (.glow-card / .glow-effect / .glow-card-content). This
 * component's only job is to:
 *
 *   1. Find every element matching BOX_SELECTOR (your existing card
 *      classNames — .card, .goal-card, .rec-card, etc. — plus an opt-in
 *      `glow-box` for anything else).
 *   2. Give it the `glow-card` class (activates the ambient ring + bloom,
 *      since that CSS is keyed off `.glow-card`).
 *   3. Insert one real `.glow-effect` child into it (the pointer-tracked
 *      bright ring layer — this is a genuine DOM node in your CSS design,
 *      not something that can be done with pure CSS custom properties).
 *   4. Track the pointer and update --glow-x / --glow-y / --glow-opacity on
 *      the box itself (which both `.glow-card`'s box-shadow and its
 *      `.glow-effect` child's gradient read, via normal custom-property
 *      inheritance) — exactly like the original per-instance
 *      <GlowingEffect /> component did, just for every box at once.
 *
 * Why this is safe next to React re-renders:
 * - It only ever APPENDS one new sibling node per box; it never moves,
 *   wraps, or removes any node React already created. Appending an extra
 *   node React doesn't know about can't break React's reconciliation,
 *   because React's own insertBefore/removeChild calls reference specific
 *   nodes, not positions — foreign siblings elsewhere don't interfere.
 * - It never overwrites `className` wholesale (it uses classList.add, which
 *   only ever adds `glow-card` if missing).
 * - It's "self-healing": if a box's className ever gets fully replaced by a
 *   React re-render (wiping the `glow-card` class we added), the
 *   MutationObserver below notices the class attribute changed and just
 *   re-applies it — no manual bookkeeping needed anywhere else in the app.
 *
 * To bring a brand-new box type into the glow, add `glow-box` to its
 * className — nothing else to configure. To keep a specific box un-glowed,
 * add `no-glow` to it (or one of its ancestors).
 */

const BOX_SELECTOR = [
    '.card',
    '.glow-box',
    '.goal-card',
    '.rec-card',
    '.stat-card',
    '.loan-disclaimer',
    '.disclaimer-strip',
    '.insight-card',
    '.alert-banner',
].join(', ')

const PROXIMITY = 90 // px outside the box's edge where the highlight starts fading in
const SPREAD = 55 // px radius of the pointer highlight's gradient

export function GlowEffectProvider() {
    const tracked = useRef<Set<HTMLElement>>(new Set())

    useEffect(() => {
        function ensureGlow(el: HTMLElement) {
            if (el.closest('.no-glow')) return

            if (!el.classList.contains('glow-card')) {
                el.classList.add('glow-card')
            }

            if (!el.querySelector(':scope > .glow-effect')) {
                const ring = document.createElement('div')
                ring.className = 'glow-effect'
                ring.setAttribute('aria-hidden', 'true')
                ring.style.setProperty('--glow-spread', `${SPREAD}px`)
                ring.style.setProperty('--glow-from', 'var(--color-saffron-light)')
                ring.style.setProperty('--glow-to', 'var(--color-teal-light)')
                el.insertBefore(ring, el.firstChild)
            }

            tracked.current.add(el)
        }

        function scan(root: ParentNode) {
            root.querySelectorAll<HTMLElement>(BOX_SELECTOR).forEach(ensureGlow)
        }

        // Initial pass over whatever's already on the page.
        scan(document.body)

        // Catch boxes added later (new goal cards, alerts, modals, whole new
        // pages) and repair boxes whose className got fully replaced by a
        // React re-render.
        const observer = new MutationObserver(mutations => {
            for (const m of mutations) {
                if (m.type === 'childList') {
                    m.addedNodes.forEach(node => {
                        if (!(node instanceof HTMLElement)) return
                        if (node.matches(BOX_SELECTOR)) ensureGlow(node)
                        scan(node)
                    })
                } else if (m.type === 'attributes' && m.target instanceof HTMLElement) {
                    const el = m.target
                    if (tracked.current.has(el) && el.matches(BOX_SELECTOR)) ensureGlow(el)
                }
            }
        })
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class'],
        })

        // Single global pointer listener drives every tracked box's glow.
        let raf = 0
        const handlePointerMove = (e: PointerEvent) => {
            cancelAnimationFrame(raf)
            raf = requestAnimationFrame(() => {
                tracked.current.forEach(el => {
                    if (!document.body.contains(el)) {
                        tracked.current.delete(el)
                        return
                    }

                    const rect = el.getBoundingClientRect()
                    const x = e.clientX - rect.left
                    const y = e.clientY - rect.top
                    const withinX = x > -PROXIMITY && x < rect.width + PROXIMITY
                    const withinY = y > -PROXIMITY && y < rect.height + PROXIMITY

                    if (withinX && withinY) {
                        const distX = x < 0 ? -x : x > rect.width ? x - rect.width : 0
                        const distY = y < 0 ? -y : y > rect.height ? y - rect.height : 0
                        const dist = Math.sqrt(distX * distX + distY * distY)
                        const opacity = 1 - Math.min(dist / PROXIMITY, 1)
                        el.style.setProperty('--glow-x', `${x}px`)
                        el.style.setProperty('--glow-y', `${y}px`)
                        el.style.setProperty('--glow-opacity', String(Math.max(opacity, 0.35)))
                    } else {
                        el.style.setProperty('--glow-opacity', '0')
                    }
                })
            })
        }

        window.addEventListener('pointermove', handlePointerMove, { passive: true })

        return () => {
            observer.disconnect()
            window.removeEventListener('pointermove', handlePointerMove)
            cancelAnimationFrame(raf)
        }
    }, [])

    return null
}