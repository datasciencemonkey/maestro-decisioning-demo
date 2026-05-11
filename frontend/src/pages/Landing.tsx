import { useEffect, useRef, useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useInView } from 'framer-motion'
import { Sun, Moon } from 'lucide-react'
import { useTheme } from '../hooks/use-theme'

// ─── Brand tokens (light mode = Databricks official) ───────────
const L = {
  bg: '#F9F7F4',
  text: '#0B2026',
  secondary: '#4A4A4A',
  accent: '#40D1F5',
  cta: '#EB1600',
  hover: '#F1F5FA',
  border: '#0B2026',
  borderLight: '#0B2026',
} as const

// ─── Particle canvas (dark mode only) ──────────────────────────
function ParticleCanvas() {
  const ref = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const c = ref.current!
    const ctx = c.getContext('2d')!
    let raf: number
    let w = (c.width = window.innerWidth)
    let h = (c.height = window.innerHeight)

    const pts = Array.from({ length: 55 }, () => ({
      x: Math.random() * w,
      y: Math.random() * h,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      r: Math.random() * 1.5 + 0.5,
      o: Math.random() * 0.3 + 0.1,
    }))

    const onResize = () => { w = c.width = innerWidth; h = c.height = innerHeight }
    window.addEventListener('resize', onResize)

    function draw() {
      ctx.clearRect(0, 0, w, h)
      for (let i = 0; i < pts.length; i++) {
        const p = pts[i]
        p.x += p.vx; p.y += p.vy
        if (p.x < 0) p.x = w; if (p.x > w) p.x = 0
        if (p.y < 0) p.y = h; if (p.y > h) p.y = 0
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(196,168,122,${p.o})`; ctx.fill()
        for (let j = i + 1; j < pts.length; j++) {
          const q = pts[j]
          const dx = p.x - q.x, dy = p.y - q.y, d = Math.sqrt(dx * dx + dy * dy)
          if (d < 140) {
            ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y)
            ctx.strokeStyle = `rgba(196,168,122,${0.06 * (1 - d / 140)})`
            ctx.stroke()
          }
        }
      }
      raf = requestAnimationFrame(draw)
    }
    draw()
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', onResize) }
  }, [])

  return <canvas ref={ref} className="fixed inset-0 pointer-events-none z-0" />
}

// ─── Cursor glow (dark mode only) ──────────────────────────────
function CursorGlow() {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current) {
        ref.current.style.left = e.clientX + 'px'
        ref.current.style.top = e.clientY + 'px'
      }
    }
    window.addEventListener('mousemove', handler)
    return () => window.removeEventListener('mousemove', handler)
  }, [])
  return (
    <div
      ref={ref}
      className="fixed w-[400px] h-[400px] rounded-full pointer-events-none z-[1] -translate-x-1/2 -translate-y-1/2 transition-[left,top] duration-300"
      style={{ background: 'radial-gradient(circle, rgba(196,168,122,0.08) 0%, transparent 70%)' }}
    />
  )
}

// ─── Animated section wrapper ──────────────────────────────────
function Reveal({ children, className = '', delay = 0 }: { children: React.ReactNode; className?: string; delay?: number }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-80px' })
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 28 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1], delay }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// ─── Data ──────────────────────────────────────────────────────
const beats = [
  { num: '1', title: 'Browse & Discover', desc: 'Cindy uploads Whiskers\u2019 photo. Vector Search matches the kitten against the catalog in real time \u2014 tabby templates surface to the top.', tag: 'Real-time Multimodal' },
  { num: '2', title: 'Reason & Decide', desc: 'Cart abandoned. The agent reasons across 9 domains \u2014 frequency cap breach detected, Spring Seasonal suppressed, abandoned cart recovery prioritized.', tag: 'Cross-Campaign Reasoning' },
  { num: '3', title: 'Activate & Send', desc: 'Segment-of-one email composed with Whiskers-matched imagery, personalized copy, and governed activation via partner ESP.', tag: 'Segment of One' },
]

const cindyJourney = [
  { id: 'browse', emoji: '\uD83D\uDECD\uFE0F', title: 'Cindy Browses', desc: 'Looking for a photo book for her new kitten Whiskers' },
  { id: 'upload', emoji: '\uD83D\uDCF8', title: 'Uploads a Photo', desc: 'Whiskers\u2019 cutest tabby portrait goes in' },
  { id: 'match', emoji: '\u2728', title: 'AI Matches', desc: 'Vector Search finds tabby-themed templates in real time' },
  { id: 'cart', emoji: '\uD83D\uDED2', title: 'Adds to Cart', desc: 'Welcome Home 24pg photo book \u2014 $42' },
  { id: 'abandon', emoji: '\uD83D\uDCA8', title: 'Abandons Cart', desc: 'Cindy closes the tab. The agent activates.' },
  { id: 'reason', emoji: '\uD83E\uDDE0', title: 'Agent Reasons', desc: '9 domains in 2 seconds. Spring promo suppressed.' },
  { id: 'send', emoji: '\uD83D\uDC8C', title: 'Email Sent', desc: 'Personalized recovery with Whiskers imagery' },
  { id: 'convert', emoji: '\uD83C\uDF89', title: 'Cindy Converts', desc: 'Whiskers\u2019 album ships on time' },
]

const techItems = ['Pydantic AI', 'MLflow Tracing', 'DBOS on Lakebase', 'Unity Catalog', 'Agent Bricks', 'Vector Search', 'AI Gateway', 'Databricks Apps']

// ─── Journey sidebar ───────────────────────────────────────────
function JourneySidebar({ dark }: { dark: boolean }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [activeIndex, setActiveIndex] = useState(-1)

  useEffect(() => {
    const onScroll = () => {
      const scrollY = window.scrollY
      const docHeight = document.documentElement.scrollHeight - window.innerHeight
      const progress = docHeight > 0 ? scrollY / docHeight : 0
      const idx = Math.min(
        cindyJourney.length - 1,
        Math.floor(progress * (cindyJourney.length + 1))
      )
      setActiveIndex(idx)
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // Compute the progress line height
  const lineProgress = activeIndex >= 0
    ? ((activeIndex + 1) / cindyJourney.length) * 100
    : 0

  return (
    <div ref={containerRef} className="w-full">
      {/* Header */}
      <div className="mb-6">
        <p
          className="text-[10px] font-bold tracking-[2.5px] uppercase mb-2"
          style={{ color: dark ? 'rgba(196,168,122,0.5)' : L.secondary }}
        >
          Cindy&apos;s Journey
        </p>
        <div
          className="h-px w-12"
          style={{ background: dark ? 'rgba(196,168,122,0.2)' : L.border + '20' }}
        />
      </div>

      {/* Steps */}
      <div className="relative">
        {/* Background vertical line */}
        <div
          className="absolute left-[15px] top-2 bottom-2 w-px"
          style={{ background: dark ? 'rgba(255,255,255,0.06)' : L.border + '15' }}
        />
        {/* Animated progress line */}
        <div
          className="absolute left-[15px] top-2 w-px transition-all duration-700 ease-out"
          style={{
            height: `${lineProgress}%`,
            background: dark
              ? 'linear-gradient(to bottom, rgba(196,168,122,0.6), rgba(196,168,122,0.2))'
              : `linear-gradient(to bottom, ${L.cta}99, ${L.cta}33)`,
          }}
        />

        {cindyJourney.map((step, i) => {
          const isPast = i < activeIndex
          const isCurrent = i === activeIndex
          const isFuture = i > activeIndex

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: 12 }}
              animate={{
                opacity: isFuture ? 0.2 : 1,
                x: 0,
              }}
              transition={{
                duration: 0.5,
                delay: isFuture ? 0 : 0.05 * i,
                ease: [0.16, 1, 0.3, 1],
              }}
              className="relative flex items-start gap-3.5 mb-5 last:mb-0"
            >
              {/* Dot */}
              <div className="relative z-10 shrink-0 flex items-center justify-center w-[30px] h-[30px]">
                <div
                  className="rounded-full transition-all duration-500"
                  style={{
                    width: isCurrent ? 14 : 10,
                    height: isCurrent ? 14 : 10,
                    background: isCurrent
                      ? dark ? '#C4A87A' : L.cta
                      : isPast
                        ? dark ? 'rgba(196,168,122,0.6)' : L.cta + '80'
                        : dark ? 'rgba(255,255,255,0.08)' : L.border + '18',
                    border: isFuture
                      ? `1px solid ${dark ? 'rgba(255,255,255,0.08)' : L.border + '18'}`
                      : 'none',
                    animation: isCurrent
                      ? dark
                        ? 'journeyPulse 2s ease infinite'
                        : 'journeyPulseLight 2s ease infinite'
                      : undefined,
                  }}
                />
              </div>

              {/* Content */}
              <div className="pt-0.5 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-base leading-none">{step.emoji}</span>
                  <span
                    className="text-[14px] font-semibold leading-tight transition-colors duration-300"
                    style={{
                      color: isCurrent
                        ? dark ? '#C4A87A' : L.text
                        : isPast
                          ? dark ? 'rgba(255,255,255,0.65)' : L.text + 'B0'
                          : dark ? 'rgba(255,255,255,0.2)' : L.secondary + '60',
                    }}
                  >
                    {step.title}
                  </span>
                </div>
                <p
                  className="text-[13px] leading-[1.5] transition-colors duration-300"
                  style={{
                    color: isCurrent
                      ? dark ? 'rgba(255,255,255,0.45)' : L.secondary
                      : isPast
                        ? dark ? 'rgba(255,255,255,0.25)' : L.secondary + '90'
                        : dark ? 'rgba(255,255,255,0.1)' : L.secondary + '40',
                  }}
                >
                  {step.desc}
                </p>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}

// ─── Mobile journey track ──────────────────────────────────────
function JourneyMobileTrack({ dark, activeIndex }: { dark: boolean; activeIndex: number }) {
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to active step
  useEffect(() => {
    if (scrollRef.current && activeIndex >= 0) {
      const child = scrollRef.current.children[0]?.children[activeIndex] as HTMLElement | undefined
      if (child) {
        child.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
      }
    }
  }, [activeIndex])

  return (
    <div ref={scrollRef} className="overflow-x-auto -mx-4 px-4 pb-1" style={{ scrollbarWidth: 'none' }}>
      <div className="flex gap-2.5 w-max">
        {cindyJourney.map((step, i) => {
          const isPast = i < activeIndex
          const isCurrent = i === activeIndex
          return (
            <div
              key={step.id}
              className="flex items-center gap-1.5 px-3 py-2 text-[11px] whitespace-nowrap transition-all duration-500"
              style={{
                borderRadius: 4,
                border: `1px solid ${
                  isCurrent
                    ? dark ? 'rgba(196,168,122,0.4)' : L.border
                    : isPast
                      ? dark ? 'rgba(255,255,255,0.08)' : L.border + '30'
                      : dark ? 'rgba(255,255,255,0.04)' : L.border + '12'
                }`,
                background: isCurrent
                  ? dark ? 'rgba(196,168,122,0.08)' : L.hover
                  : 'transparent',
                color: isCurrent
                  ? dark ? '#C4A87A' : L.text
                  : isPast
                    ? dark ? 'rgba(255,255,255,0.45)' : L.secondary
                    : dark ? 'rgba(255,255,255,0.18)' : L.secondary + '50',
              }}
            >
              <span>{step.emoji}</span>
              <span className="font-medium">{step.title}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ─── Landing page ──────────────────────────────────────────────
export default function Landing() {
  const navigate = useNavigate()
  const { theme, toggle } = useTheme()
  const dark = theme === 'dark'
  const [mobileActiveIndex, setMobileActiveIndex] = useState(-1)

  const launchDemo = useCallback(() => {
    navigate('/store')
  }, [navigate])

  // Mobile scroll tracker
  useEffect(() => {
    const onScroll = () => {
      const scrollY = window.scrollY
      const docHeight = document.documentElement.scrollHeight - window.innerHeight
      const progress = docHeight > 0 ? scrollY / docHeight : 0
      setMobileActiveIndex(Math.min(
        cindyJourney.length - 1,
        Math.floor(progress * (cindyJourney.length + 1))
      ))
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div
      className="min-h-screen relative transition-colors duration-300"
      style={{
        background: dark ? '#0D0B09' : L.bg,
        color: dark ? '#ffffff' : L.text,
      }}
    >
      {/* Dark-mode-only ambient effects */}
      {dark && <ParticleCanvas />}
      {dark && <CursorGlow />}

      {/* ── Theme toggle ── */}
      <button
        onClick={toggle}
        className={`fixed top-5 right-5 z-50 w-9 h-9 flex items-center justify-center rounded-[4px] transition-all duration-[250ms] ease-in-out ${
          dark
            ? 'border border-white/[0.08] bg-white/[0.04] text-white/60 hover:bg-white/10'
            : 'border border-[#0B2026] bg-transparent text-[#4A4A4A] hover:bg-[#0B2026] hover:text-white'
        }`}
        aria-label="Toggle theme"
      >
        {dark ? <Sun size={15} /> : <Moon size={15} />}
      </button>

      {/* ── Two-column layout wrapper ── */}
      <div className="relative z-10 flex">
        {/* ── Main content column ── */}
        <div className="w-full lg:w-[65%] xl:w-[68%]">

          {/* ── Hero ── */}
          <section className="relative min-h-screen flex flex-col items-center justify-center text-center px-8 overflow-hidden">
            {/* Concentric rings (dark only) */}
            {dark && [600, 900, 1200].map((size, i) => (
              <div
                key={size}
                className="absolute rounded-full border border-gold/[0.06] animate-pulse"
                style={{ width: size, height: size, animationDelay: `${i}s`, animationDuration: '6s' }}
              />
            ))}

            {/* Light mode: subtle warm radial */}
            {!dark && (
              <div
                className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full pointer-events-none"
                style={{ background: 'radial-gradient(circle, rgba(64,209,245,0.04) 0%, transparent 70%)' }}
              />
            )}

            {/* Title */}
            <h1 className="font-serif text-[clamp(36px,5.5vw,68px)] font-normal leading-[1.1] max-w-[850px] mb-7">
              {['The ', null, 'Lives on Your ', 'Data Platform'].map((text, i) => (
                <span key={i} className="block overflow-hidden">
                  <motion.span
                    className="inline-block"
                    initial={{ y: '110%' }}
                    animate={{ y: 0 }}
                    transition={{ delay: 0.3 + i * 0.15, duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
                  >
                    {i === 1 ? (
                      <span
                        className={dark
                          ? 'bg-gradient-to-r from-gold via-gold-light to-gold bg-[length:200%_auto] bg-clip-text text-transparent animate-[goldShift_4s_linear_infinite]'
                          : ''
                        }
                        style={!dark ? { color: L.cta } : undefined}
                      >
                        Agentic CDP
                      </span>
                    ) : text}
                  </motion.span>
                </span>
              ))}
            </h1>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9, duration: 0.8 }}
              className="text-[17px] leading-[1.8] max-w-[540px] mb-12"
              style={{ color: dark ? 'rgba(255,255,255,0.5)' : L.secondary }}
            >
              Our governed agentic AI reasons across campaigns, production calendars, support tickets, and ML models &mdash; decides what to do, sets its own plan, and pulls through at exactly the right moment.
            </motion.p>

            {/* CTA */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.1, duration: 0.8 }}
              className="relative"
            >
              {dark && (
                <div className="absolute -bottom-20 left-1/2 -translate-x-1/2 w-[200px] h-[200px] rounded-full bg-[radial-gradient(circle,rgba(196,168,122,0.25),transparent_70%)] animate-[glowPulse_3s_ease-in-out_infinite]" />
              )}
              <button
                onClick={launchDemo}
                className={`relative group inline-flex items-center gap-3 px-11 py-[18px] font-semibold text-[15px] overflow-hidden cursor-pointer transition-all duration-[250ms] ease-in-out ${
                  dark
                    ? 'rounded-[14px] bg-gradient-to-br from-gold to-gold-light text-espresso hover:-translate-y-[3px] hover:shadow-[0_12px_40px_rgba(196,168,122,0.35)] active:translate-y-0'
                    : 'rounded-[4px] bg-[#EB1600] text-white border-none hover:bg-[#0B2026] hover:-translate-y-[2px] hover:shadow-[0_8px_24px_rgba(11,32,38,0.15)]'
                }`}
                style={{ letterSpacing: dark ? '0.5px' : '1.5px' }}
              >
                {dark && <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full animate-[ctaShimmer_3s_ease-in-out_infinite]" />}
                <span className="relative z-10">Launch Demo</span>
                <span className="relative z-10 text-xl transition-transform group-hover:translate-x-1">&rarr;</span>
              </button>
            </motion.div>

            {/* Scroll indicator */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.6 }}
              className="absolute bottom-8 flex flex-col items-center gap-2"
            >
              <span
                className="text-[10px] tracking-[2px]"
                style={{ color: dark ? 'rgba(255,255,255,0.25)' : L.secondary + '40' }}
              >
                SCROLL
              </span>
              <div
                className="w-px h-8 animate-[scrollBounce_2s_ease_infinite]"
                style={{
                  background: dark
                    ? 'linear-gradient(to bottom, rgba(196,168,122,0.4), transparent)'
                    : `linear-gradient(to bottom, ${L.border}40, transparent)`,
                }}
              />
            </motion.div>
          </section>

          {/* ── Mobile journey track (visible below lg) ── */}
          <div
            className="lg:hidden sticky top-0 z-40 py-3 px-4"
            style={{
              background: dark ? 'rgba(13,11,9,0.95)' : `${L.bg}F2`,
              backdropFilter: 'blur(8px)',
              borderBottom: `1px solid ${dark ? 'rgba(255,255,255,0.04)' : L.border + '15'}`,
            }}
          >
            <JourneyMobileTrack dark={dark} activeIndex={mobileActiveIndex} />
          </div>

          {/* ── Three Beats ── */}
          <section
            className="relative px-4 md:px-8 py-28"
            style={{
              background: dark
                ? 'linear-gradient(to bottom, #12100D, #1A1612)'
                : L.hover,
            }}
          >
            <Reveal className="text-center mb-16">
              <h2 className="font-serif text-4xl mb-3">Three Beats. One Goal.</h2>
              <p style={{ color: dark ? 'rgba(255,255,255,0.4)' : L.secondary }} className="text-sm">
                A 15-minute live demo proving Databricks is the agentic CDP
              </p>
            </Reveal>

            <div className="relative max-w-[1000px] mx-auto flex flex-col md:flex-row items-stretch gap-6 md:gap-0">
              {/* Connector line (desktop only) */}
              <div
                className="hidden md:block absolute top-6 left-0 right-0 h-px"
                style={{
                  background: dark
                    ? 'linear-gradient(to right, transparent, rgba(196,168,122,0.2), transparent)'
                    : `linear-gradient(to right, transparent, ${L.border}20, transparent)`,
                }}
              />

              {beats.map((beat, i) => (
                <Reveal key={beat.num} delay={0.1 + i * 0.2} className="flex-1 px-4 relative">
                  <div
                    className="w-12 h-12 flex items-center justify-center font-bold text-base mb-6 mx-auto relative z-10 transition-all duration-300 hover:scale-110"
                    style={{
                      borderRadius: dark ? 14 : 4,
                      ...(dark
                        ? i === 0
                          ? { background: 'linear-gradient(135deg, #C4A87A, #DBC09E)', color: '#2C1810' }
                          : i === 1
                            ? { background: '#2C1810', color: '#C4A87A', border: '1px solid rgba(196,168,122,0.2)' }
                            : { background: 'linear-gradient(135deg, #7C6353, #A08468)', color: '#ffffff' }
                        : { background: L.text, color: '#ffffff' }
                      ),
                    }}
                  >
                    {beat.num}
                  </div>
                  {i < 2 && (
                    <div
                      className="hidden md:block absolute top-6 -right-4 w-8 h-px"
                      style={{ background: dark ? 'rgba(196,168,122,0.3)' : L.border + '25' }}
                    >
                      <div
                        className="absolute right-0 -top-[3px] w-0 h-0"
                        style={{
                          border: '3px solid transparent',
                          borderLeftColor: dark ? 'rgba(196,168,122,0.3)' : L.border + '25',
                        }}
                      />
                    </div>
                  )}
                  <div
                    className={`p-8 text-center transition-all duration-[250ms] ease-in-out ${
                      dark
                        ? 'rounded-[16px] bg-white/[0.03] border border-white/[0.06] hover:bg-[rgba(196,168,122,0.04)] hover:border-[rgba(196,168,122,0.12)]'
                        : 'rounded-[4px] bg-white border border-[#0B202615] hover:border-[#0B202640] hover:shadow-[0_4px_20px_rgba(0,0,0,0.04)]'
                    }`}
                  >
                    <h3 className="font-serif text-xl mb-3">{beat.title}</h3>
                    <p
                      className="text-[15px] leading-[1.7] mb-4"
                      style={{ color: dark ? 'rgba(255,255,255,0.45)' : L.secondary }}
                    >
                      {beat.desc}
                    </p>
                    <span
                      className="inline-block text-[11px] font-bold uppercase px-3 py-1.5"
                      style={{
                        letterSpacing: '1.5px',
                        borderRadius: 2,
                        color: dark ? '#C4A87A' : L.text,
                        background: dark ? 'rgba(196,168,122,0.08)' : L.text + '08',
                        border: `1px solid ${dark ? 'rgba(196,168,122,0.12)' : L.border + '15'}`,
                      }}
                    >
                      {beat.tag}
                    </span>
                  </div>
                </Reveal>
              ))}
            </div>
          </section>

          {/* ── Tech marquee ── */}
          <div
            className="py-10 overflow-hidden"
            style={{
              background: dark ? 'rgba(196,168,122,0.03)' : L.bg,
              borderTop: `1px solid ${dark ? 'rgba(196,168,122,0.06)' : L.border + '15'}`,
              borderBottom: `1px solid ${dark ? 'rgba(196,168,122,0.06)' : L.border + '15'}`,
            }}
          >
            <p
              className="text-[10px] tracking-[3px] text-center mb-4 uppercase font-bold"
              style={{ color: dark ? 'rgba(196,168,122,0.4)' : L.secondary + '80' }}
            >
              Powered by the Databricks Stack
            </p>
            <div className="flex gap-12 animate-[techMarquee_20s_linear_infinite] w-max hover:[animation-play-state:paused]">
              {[...techItems, ...techItems].map((item, i) => (
                <span
                  key={i}
                  className={`flex items-center gap-2 text-sm font-medium tracking-wider whitespace-nowrap transition-colors duration-200 ${
                    dark
                      ? 'text-white/30 hover:text-[#C4A87A]'
                      : 'text-[#5A6F77]/40 hover:text-[#EB1600]'
                  }`}
                >
                  <span
                    className="w-[5px] h-[5px] rounded-full"
                    style={{ background: dark ? 'rgba(196,168,122,0.5)' : 'rgba(90,111,119,0.4)' }}
                  />
                  {item}
                </span>
              ))}
            </div>
          </div>

          {/* ── Bottom CTA ── */}
          <section
            className="py-24 text-center px-4 md:px-8 overflow-hidden relative"
            style={{
              background: dark
                ? 'linear-gradient(to bottom, #1A1612, #0D0B09)'
                : L.bg,
            }}
          >
            {dark && (
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-[radial-gradient(circle,rgba(196,168,122,0.06),transparent_70%)]" />
            )}
            <Reveal>
              <h2 className="font-serif text-[32px] mb-3 relative">Ready to see the agent think?</h2>
            </Reveal>
            <Reveal delay={0.1}>
              <p
                className="text-sm mb-10 relative"
                style={{ color: dark ? 'rgba(255,255,255,0.4)' : L.secondary }}
              >
                Watch Cindy&apos;s journey from browse to abandoned cart to personalized recovery.
              </p>
            </Reveal>
            <Reveal delay={0.2} className="relative">
              <button
                onClick={launchDemo}
                className={`relative group inline-flex items-center gap-3 px-11 py-[18px] font-semibold text-[15px] overflow-hidden cursor-pointer transition-all duration-[250ms] ease-in-out ${
                  dark
                    ? 'rounded-[14px] bg-gradient-to-br from-gold to-gold-light text-espresso hover:-translate-y-[3px] hover:shadow-[0_12px_40px_rgba(196,168,122,0.35)]'
                    : 'rounded-[4px] bg-[#EB1600] text-white border-none hover:bg-[#0B2026] hover:-translate-y-[2px] hover:shadow-[0_8px_24px_rgba(11,32,38,0.15)]'
                }`}
                style={{ letterSpacing: dark ? '0.5px' : '1.5px' }}
              >
                {dark && <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full animate-[ctaShimmer_3s_ease-in-out_infinite]" />}
                <span className="relative z-10">Launch Demo</span>
                <span className="relative z-10 text-xl transition-transform group-hover:translate-x-1">&rarr;</span>
              </button>
            </Reveal>
          </section>

          {/* ── Footer ── */}
          <footer
            className="py-5 text-center text-[11px]"
            style={{
              color: dark ? 'rgba(255,255,255,0.2)' : L.secondary + '60',
              borderTop: `1px solid ${dark ? 'rgba(255,255,255,0.04)' : L.border + '12'}`,
            }}
          >
            Built on Databricks &mdash; one platform, one governance plane, one agent.
          </footer>
        </div>

        {/* ── Cindy's Journey sidebar (desktop only) ── */}
        <aside className="hidden lg:block w-[35%] xl:w-[32%] relative">
          <div
            className="sticky top-20 p-6 pr-8 ml-2 mr-6 mt-[30vh] transition-colors duration-300"
            style={{
              borderRadius: dark ? 12 : 4,
              background: dark ? 'rgba(18,16,13,0.8)' : '#ffffff',
              border: `1px solid ${dark ? 'rgba(255,255,255,0.06)' : L.border + '15'}`,
              backdropFilter: dark ? 'blur(8px)' : undefined,
            }}
          >
            <JourneySidebar dark={dark} />
          </div>
        </aside>
      </div>
    </div>
  )
}
