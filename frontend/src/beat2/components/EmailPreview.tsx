import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Mail, CheckCircle2, Send } from 'lucide-react'

interface EmailData {
  subject: string
  body_html: string
  hero_image_url: string
  cta_text: string
  cta_url: string
}

interface EmailPreviewProps {
  email?: EmailData
  visible: boolean
  delivered: boolean
}

const CONFETTI_COLORS = [
  'var(--color-gold)',
  'var(--color-databricks-cyan)',
  'var(--color-status-triggered)',
  'var(--color-status-suppressed)',
  'var(--color-gold-light)',
  'var(--color-databricks-cyan)',
  'var(--color-status-triggered)',
  'var(--color-gold)',
]

// Pre-computed burst vectors so they're stable across renders
const BURST_VECTORS = [
  { dx: 52, dy: -68 },
  { dx: -44, dy: -72 },
  { dx: 76, dy: -30 },
  { dx: -80, dy: -18 },
  { dx: 28, dy: -84 },
  { dx: -28, dy: -56 },
  { dx: 60, dy: -58 },
  { dx: -60, dy: -44 },
]

export default function EmailPreview({ email, visible, delivered }: EmailPreviewProps) {
  const [showDelivered, setShowDelivered] = useState(false)
  const [imgError, setImgError] = useState(false)

  useEffect(() => {
    if (delivered) {
      const t = setTimeout(() => setShowDelivered(true), 1200)
      return () => clearTimeout(t)
    }
  }, [delivered])

  if (!visible || !email) return null

  return (
    <div className="relative">
      {/* Gold divider line — draws itself left to right */}
      <motion.div
        initial={{ scaleX: 0, opacity: 0 }}
        animate={{ scaleX: 1, opacity: 1 }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        className="h-px mb-6 origin-left"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, var(--color-gold) 40%, var(--color-gold-light) 60%, transparent 100%)',
        }}
      />

      {/* Outer frame — Databricks platform chrome */}
      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ type: 'spring', damping: 22, stiffness: 180, delay: 0.25 }}
        className="bg-card border border-border rounded-xl overflow-hidden"
        style={{ boxShadow: '0 4px 32px rgba(0,0,0,0.12)' }}
      >
        {/* Platform label bar */}
        <div className="flex items-center justify-between px-5 py-2.5 border-b border-border bg-card">
          <div className="flex items-center gap-2">
            <Mail size={12} className="text-[var(--color-databricks-cyan)]" />
            <span
              className="text-[10px] font-bold tracking-[0.16em] uppercase"
              style={{ color: 'var(--color-databricks-cyan)' }}
            >
              Composed by Agent
            </span>
          </div>

          <AnimatePresence>
            {showDelivered && (
              <motion.div
                initial={{ opacity: 0, scale: 0.4, y: -6 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ type: 'spring', damping: 10, stiffness: 320 }}
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold tracking-[0.12em] uppercase border"
                style={{
                  background: 'rgba(34,197,94,0.1)',
                  borderColor: 'rgba(34,197,94,0.35)',
                  color: 'var(--color-status-triggered)',
                }}
              >
                <CheckCircle2 size={11} />
                Delivered
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Inner email card — Fluttershy brand */}
        <div className="m-4 rounded-lg overflow-hidden border"
          style={{ borderColor: 'rgba(196,168,122,0.25)' }}
        >
          {/* Brand header */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="flex items-center gap-2 px-6 py-3"
            style={{ background: 'var(--color-cream)' }}
          >
            <span className="text-base leading-none">🐾</span>
            <span
              className="font-serif text-sm font-medium"
              style={{ color: 'var(--color-espresso)' }}
            >
              Fluttershy Pet Photo Co.
            </span>
          </motion.div>

          {/* Hero image — blur-to-sharp reveal */}
          {!imgError && (
            <motion.div
              initial={{ opacity: 0, filter: 'blur(16px)' }}
              animate={{ opacity: 1, filter: 'blur(0px)' }}
              transition={{ delay: 0.7, duration: 0.8, ease: 'easeOut' }}
              className="w-full overflow-hidden"
              style={{ aspectRatio: '2/1', background: 'var(--color-cream)' }}
            >
              <img
                src={email.hero_image_url}
                alt="Whiskers the tabby kitten"
                className="w-full h-full object-cover"
                onError={() => setImgError(true)}
              />
            </motion.div>
          )}

          {/* Email body */}
          <div className="px-6 py-5" style={{ background: '#FFFFFF' }}>
            {/* Subject line */}
            <motion.h2
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9, duration: 0.4 }}
              className="font-serif text-lg leading-tight mb-3"
              style={{ color: 'var(--color-gold)' }}
            >
              {email.subject}
            </motion.h2>

            {/* Body HTML */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.1, duration: 0.45 }}
              className="text-sm leading-relaxed mb-4"
              style={{
                color: 'var(--color-espresso)',
                fontFamily: 'var(--font-sans)',
              }}
              // eslint-disable-next-line react/no-danger
              dangerouslySetInnerHTML={{ __html: email.body_html }}
            />

            {/* CTA button */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.3, type: 'spring', damping: 16, stiffness: 200 }}
              className="flex justify-center"
            >
              <a
                href={email.cta_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-7 py-3 rounded-lg font-bold text-sm no-underline"
                style={{
                  background: 'var(--color-gold)',
                  color: 'var(--color-espresso)',
                  boxShadow: '0 2px 12px rgba(196,168,122,0.35)',
                }}
              >
                <Send size={14} />
                {email.cta_text}
              </a>
            </motion.div>

            {/* Free shipping subtext */}
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.5, duration: 0.4 }}
              className="text-center text-[11px] mt-3"
              style={{ color: 'var(--color-mocha)' }}
            >
              Free shipping on orders over $35
            </motion.p>
          </div>

          {/* Email footer */}
          <div
            className="px-6 py-3 border-t"
            style={{
              background: 'rgba(237,228,216,0.5)',
              borderColor: 'rgba(196,168,122,0.15)',
            }}
          >
            <p className="text-[10px] text-center" style={{ color: 'var(--color-mocha)' }}>
              Fluttershy &middot; Unsubscribe &middot; Privacy Policy
            </p>
          </div>
        </div>
      </motion.div>

      {/* Confetti burst — 8 colored particles */}
      <AnimatePresence>
        {showDelivered && (
          <>
            {BURST_VECTORS.map((vec, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 1, scale: 0, x: 0, y: 0 }}
                animate={{
                  opacity: 0,
                  scale: 1.2,
                  x: vec.dx,
                  y: vec.dy,
                }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.75, delay: i * 0.04, ease: [0.22, 1, 0.36, 1] }}
                className="absolute w-2.5 h-2.5 rounded-full pointer-events-none"
                style={{
                  top: 12,
                  right: 96,
                  backgroundColor: CONFETTI_COLORS[i],
                }}
              />
            ))}
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
