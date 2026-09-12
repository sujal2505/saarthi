import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import NebulaBackground from './NebulaBackground'
import './NebulaHero.css'

gsap.registerPlugin(ScrollTrigger)

type NebulaHeroProps = {
    navLinks?: string[]
    ctaLabel?: string
    onCtaClick?: () => void
    taglineLines?: string[][]
    subheadingWords?: string[]
    wordmarkTop?: string
    wordmarkBottom?: string
    socialLinks?: string[]
    footerTag?: string
}

/** Splits a phrase into individually-animatable word spans. */
function Words({ text, className }: { text: string; className: string }) {
    return (
        <>
            {text.split(' ').map((word, i) => (
                <span className="nebula-hero__mask" key={`${word}-${i}`}>
                    <span className={className}>{word}</span>
                </span>
            ))}
        </>
    )
}

export default function NebulaHero({
    navLinks = ['Dashboard', 'Goals', 'Assistant'],
    ctaLabel = 'Sign In',
    onCtaClick,
    taglineLines = [
        ['Money', 'clarity,'],
        ['built', 'around', 'your', 'goals.'],
    ],
    subheadingWords = 'Track spending, plan borrowing, and simulate your future — in one place.'.split(' '),
    wordmarkTop = 'Saarthi',
    wordmarkBottom = 'Finance.',
    socialLinks = ['Twitter', 'LinkedIn'],
    footerTag = 'v1.0',
}: NebulaHeroProps) {
    const rootRef = useRef<HTMLDivElement | null>(null)

    useEffect(() => {
        const root = rootRef.current
        if (!root) return

        const ctx = gsap.context(() => {
            gsap.set(['.nebula-hero__name-top', '.nebula-hero__name-bottom'], { yPercent: 110 })
            gsap.set('.nebula-hero__word, .nebula-hero__tagline-word, .nebula-hero__sub-word, .nebula-hero__footer-word', {
                yPercent: 110,
            })

            const tl = gsap.timeline({ defaults: { ease: 'power4.out' } })
            tl.to('.nebula-hero__word', { yPercent: 0, duration: 1.0, stagger: 0.04 }, 0.1)
                .to('.nebula-hero__name-top', { yPercent: 0, duration: 1.4 }, 0.2)
                .to('.nebula-hero__name-bottom', { yPercent: 0, duration: 1.4 }, 0.38)

            gsap.to('.nebula-hero__tagline-word', {
                scrollTrigger: { trigger: '.nebula-hero__tagline', start: 'top 95%' },
                yPercent: 0,
                duration: 1.0,
                stagger: 0.04,
            })

            gsap.to('.nebula-hero__sub-word', {
                scrollTrigger: { trigger: '.nebula-hero__subheading', start: 'top 95%' },
                yPercent: 0,
                duration: 1.0,
                stagger: 0.03,
            })

            gsap.to('.nebula-hero__footer-word', {
                scrollTrigger: { trigger: '.nebula-hero__footer', start: 'top 95%' },
                yPercent: 0,
                duration: 0.9,
                stagger: 0.03,
            })
        }, root)

        return () => ctx.revert()
    }, [])

    return (
        <div className="nebula-hero" ref={rootRef}>
            <NebulaBackground />
            <div className="nebula-hero__grain" />
            <div className="nebula-hero__vignette" />

            <main className="nebula-hero__main">
                <header className="nebula-hero__header">
                    <div className="nebula-hero__topbar">
                        <nav className="nebula-hero__nav" aria-label="Primary">
                            {navLinks.map((link) => (
                                <span className="nebula-hero__mask" key={link}>
                                    <a href="#" className="nebula-hero__word nebula-hero__link">
                                        {link}
                                    </a>
                                </span>
                            ))}
                        </nav>
                        <span className="nebula-hero__mask">
                            <button type="button" className="nebula-hero__word nebula-hero__cta" onClick={onCtaClick}>
                                {ctaLabel}
                            </button>
                        </span>
                    </div>

                    <div className="nebula-hero__copy">
                        <p className="nebula-hero__tagline">
                            {taglineLines.map((line, i) => (
                                <span key={i}>
                                    {line.map((word, j) => (
                                        <span className="nebula-hero__mask" key={`${word}-${j}`}>
                                            <span className="nebula-hero__tagline-word">{word}</span>
                                        </span>
                                    ))}
                                    {i < taglineLines.length - 1 && <br />}
                                </span>
                            ))}
                        </p>
                        <p className="nebula-hero__subheading">
                            {subheadingWords.map((word, i) => (
                                <span className="nebula-hero__mask" key={`${word}-${i}`}>
                                    <span className="nebula-hero__sub-word">{word}</span>
                                </span>
                            ))}
                        </p>
                    </div>
                </header>

                <section className="nebula-hero__wordmark-section" aria-label="Introduction">
                    <h1 className="nebula-hero__wordmark">
                        <span className="nebula-hero__mask nebula-hero__mask--top">
                            <span className="nebula-hero__name-top">{wordmarkTop}</span>
                        </span>
                        <span className="nebula-hero__mask nebula-hero__mask--bottom">
                            <span className="nebula-hero__name-bottom">{wordmarkBottom}</span>
                        </span>
                    </h1>
                </section>

                <footer className="nebula-hero__footer">
                    <div className="nebula-hero__footer-row">
                        <span className="nebula-hero__mask">
                            <span className="nebula-hero__footer-word">{footerTag}</span>
                        </span>
                        <nav className="nebula-hero__social" aria-label="Social links">
                            {socialLinks.map((link, i) => (
                                <span key={link} style={{ display: 'inline-flex', alignItems: 'center', gap: '1rem' }}>
                                    <span className="nebula-hero__mask">
                                        <a href="#" className="nebula-hero__footer-word nebula-hero__link">
                                            {link}
                                        </a>
                                    </span>
                                    {i < socialLinks.length - 1 && <span className="nebula-hero__divider">/</span>}
                                </span>
                            ))}
                        </nav>
                    </div>
                </footer>
            </main>
        </div>
    )
}
