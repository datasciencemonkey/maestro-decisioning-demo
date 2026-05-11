import { useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, useInView } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { products } from '@/store/data/products'
import ProductCard from '@/store/components/ProductCard'

// ─── Fade-up on scroll ──────────────────────────────────────────
function Reveal({
  children,
  className = '',
  delay = 0,
}: {
  children: React.ReactNode
  className?: string
  delay?: number
}) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-60px' })
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 24 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1], delay }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// ─── Category tiles ─────────────────────────────────────────────
const categories = [
  { label: 'Photo Books', icon: '\uD83D\uDCDA', href: '/store/photo-books' },
  { label: 'Cards', icon: '\uD83D\uDC8C', href: '/store/cards' },
  { label: 'Prints', icon: '\uD83D\uDDBC\uFE0F', href: '/store/prints' },
  { label: 'Gifts', icon: '\uD83C\uDF81', href: '/store/gifts' },
]

// ─── Home page ──────────────────────────────────────────────────
export default function Home() {
  const navigate = useNavigate()
  const featured = products.slice(0, 4)

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* ── Hero Banner ── */}
      <section className="relative h-[420px] flex items-center justify-center overflow-hidden bg-gradient-to-br from-cream to-linen dark:from-[#1A1612] dark:to-[#0D0B09]">
        {/* Background image overlay */}
        <img
          src="https://images.unsplash.com/photo-1615497001839-b0a0eac3274c?w=1400&h=800&fit=crop"
          alt=""
          loading="lazy"
          className="absolute inset-0 w-full h-full object-cover opacity-[0.15] dark:opacity-[0.1]"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-background" />

        <div className="relative z-10 text-center px-6 max-w-2xl">
          <motion.span
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="inline-block text-[11px] font-bold tracking-[3px] uppercase text-gold mb-4"
          >
            Welcome Home Collection
          </motion.span>

          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="font-serif text-5xl leading-tight text-foreground mb-4"
          >
            Pet Photo Books
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="text-base text-muted-foreground mb-8"
          >
            Tell their story. Keep their moments.
          </motion.p>

          <motion.button
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.65, duration: 0.6 }}
            onClick={() => navigate('/store/photo-books')}
            className="inline-flex items-center gap-2 px-8 py-3 rounded-lg bg-gradient-to-r from-gold to-gold-light text-espresso font-semibold text-sm hover:shadow-lg hover:shadow-gold/25 hover:-translate-y-0.5 transition-all duration-200 cursor-pointer"
          >
            Start Creating
            <ArrowRight size={16} />
          </motion.button>
        </div>
      </section>

      {/* ── Shop by Category ── */}
      <section className="max-w-5xl mx-auto px-6 py-16">
        <Reveal className="text-center mb-10">
          <h2 className="font-serif text-3xl text-foreground">Shop by Category</h2>
        </Reveal>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {categories.map((cat, i) => (
            <Reveal key={cat.label} delay={0.05 + i * 0.08}>
              <motion.div
                whileHover={{ y: -3 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                onClick={() => navigate(cat.href)}
                className="cursor-pointer rounded-lg border border-border bg-card p-6 text-center hover:border-gold/40 hover:shadow-md transition-all duration-200 dark:bg-card dark:border-border"
              >
                <span className="text-3xl block mb-2">{cat.icon}</span>
                <span className="text-sm font-medium text-card-foreground">
                  {cat.label}
                </span>
              </motion.div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ── Featured Products ── */}
      <section className="max-w-6xl mx-auto px-6 pb-20">
        <Reveal className="text-center mb-10">
          <h2 className="font-serif text-3xl text-foreground">Featured</h2>
        </Reveal>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {featured.map((product, i) => (
            <Reveal key={product.id} delay={0.05 + i * 0.08}>
              <ProductCard product={product} />
            </Reveal>
          ))}
        </div>
      </section>
    </div>
  )
}
