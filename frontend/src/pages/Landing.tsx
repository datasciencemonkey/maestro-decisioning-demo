import { useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useInView } from 'framer-motion'
import { useTheme } from '@/hooks/use-theme'
import { Sun, Moon } from 'lucide-react'

// ─── Particle canvas ────────────────────────────────────────────
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

// ─── Cursor glow ────────────────────────────────────────────────
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

// ─── Animated section wrapper ───────────────────────────────────
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

// ─── Beat card ──────────────────────────────────────────────────
const beats = [
  { num: '1', title: 'Browse & Discover', desc: 'Cindy uploads Whiskers\u2019 photo. Vector Search matches the kitten against the catalog in real time \u2014 tabby templates surface to the top.', tag: 'Real-time Multimodal', dotClass: 'bg-gradient-to-br from-gold to-gold-light text-espresso' },
  { num: '2', title: 'Reason & Decide', desc: 'Cart abandoned. The agent reasons across 9 domains \u2014 frequency cap breach detected, Spring Seasonal suppressed, abandoned cart recovery prioritized.', tag: 'Cross-Campaign Reasoning', dotClass: 'bg-espresso text-gold border border-gold/20' },
  { num: '3', title: 'Activate & Send', desc: 'Segment-of-one email composed with Whiskers-matched imagery, personalized copy, and governed activation via partner ESP.', tag: 'Segment of One', dotClass: 'bg-gradient-to-br from-mocha to-[#A08468] text-white' },
]

const techItems = ['Pydantic AI', 'MLflow Tracing', 'DBOS on Lakebase', 'Unity Catalog', 'Agent Bricks', 'Vector Search', 'AI Gateway', 'Databricks Apps']

// ─── Landing page ───────────────────────────────────────────────
export default function Landing() {
  const navigate = useNavigate()
  const { theme, toggle } = useTheme()

  const launchDemo = useCallback(() => {
    navigate('/store')
  }, [navigate])

  return (
    <div className="bg-[#0D0B09] text-white min-h-screen relative">
      <ParticleCanvas />
      <CursorGlow />

      {/* ── Hero ── */}
      <section className="relative z-2 min-h-screen flex flex-col items-center justify-center text-center px-8 overflow-hidden">
        {/* Concentric rings */}
        {[600, 900, 1200].map((size, i) => (
          <div
            key={size}
            className="absolute rounded-full border border-gold/[0.06] animate-pulse"
            style={{ width: size, height: size, animationDelay: `${i}s`, animationDuration: '6s' }}
          />
        ))}

        {/* Theme toggle */}
        <button
          onClick={toggle}
          className="absolute top-6 right-8 p-2 rounded-lg border border-white/10 hover:border-gold/30 transition-colors"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <Sun size={16} className="text-gold" /> : <Moon size={16} className="text-gold" />}
        </button>

        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.8 }}
          className="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-gold/[0.08] border border-gold/[0.15] text-[11px] font-semibold tracking-[2.5px] text-gold mb-8"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-gold animate-pulse" />
          DATABRICKS AI PRACTICE
        </motion.div>

        {/* Title */}
        <h1 className="font-serif text-[clamp(40px,6vw,72px)] font-normal leading-[1.1] max-w-[900px] mb-7">
          {['The ', null, 'Lives on Your ', 'Data Platform'].map((text, i) => (
            <span key={i} className="block overflow-hidden">
              <motion.span
                className="inline-block"
                initial={{ y: '110%' }}
                animate={{ y: 0 }}
                transition={{ delay: 0.5 + i * 0.15, duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
              >
                {i === 1 ? (
                  <span className="bg-gradient-to-r from-gold via-gold-light to-gold bg-[length:200%_auto] bg-clip-text text-transparent animate-[goldShift_4s_linear_infinite]">
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
          transition={{ delay: 1.1, duration: 0.8 }}
          className="text-[17px] leading-[1.8] text-white/50 max-w-[560px] mb-12"
        >
          One AI agent reasons across campaigns, production calendars, support tickets, and ML models &mdash; makes a governed decision in&nbsp;under&nbsp;2&nbsp;seconds.
          <br /><br />
          Follow <strong className="text-gold font-medium">Cindy</strong> and her kitten <strong className="text-gold font-medium">Whiskers</strong> through the journey.
        </motion.p>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3, duration: 0.8 }}
          className="relative"
        >
          <div className="absolute -bottom-20 left-1/2 -translate-x-1/2 w-[200px] h-[200px] rounded-full bg-[radial-gradient(circle,rgba(196,168,122,0.25),transparent_70%)] animate-[glowPulse_3s_ease-in-out_infinite]" />
          <button
            onClick={launchDemo}
            className="relative group inline-flex items-center gap-3 px-11 py-[18px] rounded-[14px] bg-gradient-to-br from-gold to-gold-light text-espresso font-semibold text-[16px] tracking-[0.5px] overflow-hidden transition-all duration-250 hover:-translate-y-[3px] hover:shadow-[0_12px_40px_rgba(196,168,122,0.35)] active:translate-y-0 cursor-pointer"
          >
            <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full animate-[ctaShimmer_3s_ease-in-out_infinite]" />
            <span className="relative z-10">Launch Demo</span>
            <span className="relative z-10 text-xl transition-transform group-hover:translate-x-1">&rarr;</span>
          </button>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.8 }}
          className="absolute bottom-8 flex flex-col items-center gap-2"
        >
          <span className="text-[10px] tracking-[2px] text-white/25">SCROLL</span>
          <div className="w-px h-8 bg-gradient-to-b from-gold/40 to-transparent animate-[scrollBounce_2s_ease_infinite]" />
        </motion.div>
      </section>

      {/* ── Flow section ── */}
      <section className="relative z-2 px-8 py-28 bg-gradient-to-b from-[#0D0B09] to-[#1A1612]">
        <Reveal className="text-center mb-16">
          <h2 className="font-serif text-4xl mb-3">Three Beats. One Agent.</h2>
          <p className="text-white/40 text-sm">A 15-minute live demo proving Databricks is the agentic CDP</p>
        </Reveal>

        <div className="relative max-w-[1100px] mx-auto flex items-stretch gap-0">
          {/* Connector line */}
          <div className="absolute top-6 left-0 right-0 h-px bg-gradient-to-r from-transparent via-gold/20 to-transparent" />

          {beats.map((beat, i) => (
            <Reveal key={beat.num} delay={0.1 + i * 0.2} className="flex-1 px-4 relative">
              <div className={`w-12 h-12 rounded-[14px] flex items-center justify-center font-bold text-base mb-6 mx-auto relative z-10 transition-all duration-300 hover:scale-110 hover:shadow-lg hover:shadow-gold/20 ${beat.dotClass}`}>
                {beat.num}
              </div>
              {i < 2 && (
                <div className="absolute top-6 -right-4 w-8 h-px bg-gold/30">
                  <div className="absolute right-0 -top-[3px] w-0 h-0 border-[3px] border-transparent border-l-gold/30" />
                </div>
              )}
              <div className="bg-white/[0.03] border border-white/[0.06] rounded-2xl p-8 text-center transition-all duration-300 hover:bg-gold/[0.04] hover:border-gold/[0.12]">
                <h3 className="font-serif text-xl mb-3">{beat.title}</h3>
                <p className="text-[13px] leading-[1.7] text-white/45 mb-4">{beat.desc}</p>
                <span className="inline-block text-[9px] font-bold tracking-[1.5px] uppercase text-gold px-3 py-1.5 rounded-md bg-gold/[0.08] border border-gold/[0.12]">
                  {beat.tag}
                </span>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ── Tech marquee ── */}
      <div className="relative z-2 py-10 bg-gold/[0.03] border-y border-gold/[0.06] overflow-hidden">
        <div className="flex gap-12 animate-[techMarquee_20s_linear_infinite] w-max hover:[animation-play-state:paused]">
          {[...techItems, ...techItems].map((item, i) => (
            <span key={i} className="flex items-center gap-2 text-xs font-medium tracking-wider text-white/30 whitespace-nowrap hover:text-gold transition-colors">
              <span className="w-[5px] h-[5px] rounded-full bg-gold/50" />
              {item}
            </span>
          ))}
        </div>
      </div>

      {/* ── Bottom CTA ── */}
      <section className="relative z-2 py-24 text-center bg-gradient-to-b from-[#1A1612] to-[#0D0B09] overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-[radial-gradient(circle,rgba(196,168,122,0.06),transparent_70%)]" />
        <Reveal>
          <h2 className="font-serif text-[32px] mb-3 relative">Ready to see the agent think?</h2>
        </Reveal>
        <Reveal delay={0.1}>
          <p className="text-white/40 text-sm mb-10 relative">Watch Cindy's journey from browse to abandoned cart to personalized recovery.</p>
        </Reveal>
        <Reveal delay={0.2} className="relative">
          <button
            onClick={launchDemo}
            className="relative group inline-flex items-center gap-3 px-11 py-[18px] rounded-[14px] bg-gradient-to-br from-gold to-gold-light text-espresso font-semibold text-[16px] overflow-hidden transition-all duration-250 hover:-translate-y-[3px] hover:shadow-[0_12px_40px_rgba(196,168,122,0.35)] cursor-pointer"
          >
            <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full animate-[ctaShimmer_3s_ease-in-out_infinite]" />
            <span className="relative z-10">Enter the Demo</span>
            <span className="relative z-10 text-xl transition-transform group-hover:translate-x-1">&rarr;</span>
          </button>
        </Reveal>
      </section>

      {/* ── Footer ── */}
      <footer className="relative z-2 py-5 text-center text-[11px] text-white/20 border-t border-white/[0.04]">
        Built on Databricks &mdash; one platform, one governance plane, one agent.
      </footer>

      <style>{`
        @keyframes goldShift { 0% { background-position: 0% } 100% { background-position: 200% } }
        @keyframes ctaShimmer { 0% { transform: translateX(-100%) } 50%,100% { transform: translateX(100%) } }
        @keyframes glowPulse { 0%,100% { opacity:.6; transform: translateX(-50%) scale(1) } 50% { opacity:1; transform: translateX(-50%) scale(1.2) } }
        @keyframes scrollBounce { 0%,100% { transform: scaleY(1); opacity:.6 } 50% { transform: scaleY(.5); opacity:.2 } }
        @keyframes techMarquee { 0% { transform: translateX(0) } 100% { transform: translateX(-50%) } }
      `}</style>
    </div>
  )
}
