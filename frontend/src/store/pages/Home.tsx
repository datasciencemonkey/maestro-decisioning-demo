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
  { label: 'Photo Books', icon: '\uD83D\uDCDA', href: '/store/photo-books', comingSoon: false },
  { label: 'Cards', icon: '\uD83D\uDC8C', href: null, comingSoon: true },
  { label: 'Prints', icon: '\uD83D\uDDBC\uFE0F', href: null, comingSoon: true },
  { label: 'Gifts', icon: '\uD83C\uDF81', href: null, comingSoon: true },
]

// ─── Home page ──────────────────────────────────────────────────
export default function Home() {
  const navigate = useNavigate()
  const featured = products.slice(0, 4)

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* ── Hero Banner ── */}
      <section className="relative h-[300px] md:h-[420px] flex items-center justify-center overflow-hidden bg-gradient-to-br from-cream to-linen dark:from-[#1A1612] dark:to-[#0D0B09]">
        {/* Background image overlay — slow ken-burns zoom */}
        <img
          src="https://images.unsplash.com/photo-1615497001839-b0a0eac3274c?w=1400&h=800&fit=crop"
          alt=""
          loading="lazy"
          className="absolute inset-0 w-full h-full object-cover opacity-[0.30] dark:opacity-[0.20] scale-105 transition-transform duration-[20000ms] hover:scale-100"
        />
        <div className="absolute inset-0 bg-white/50 dark:bg-[#0D0B09]/50" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-background" />

        <div className="relative z-10 text-center px-6 max-w-2xl">
          <motion.span
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="inline-block text-xs font-bold tracking-[3px] uppercase text-accent mb-4"
          >
            Welcome Home Collection
          </motion.span>

          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="font-serif text-3xl md:text-5xl leading-tight text-foreground mb-4"
          >
            Pet Photo Books
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="text-sm md:text-base text-foreground/60 mb-8"
          >
            Tell their story. Keep their moments.
          </motion.p>

          <motion.button
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.65, duration: 0.6 }}
            onClick={() => navigate('/store/photo-books')}
            className="inline-flex items-center gap-2 px-8 py-3 rounded-lg bg-[#EB1600] text-white dark:bg-gradient-to-r dark:from-gold dark:to-gold-light dark:text-[#0D0B09] font-semibold text-sm shadow-lg shadow-[#EB1600]/20 hover:shadow-xl hover:shadow-[#EB1600]/30 dark:shadow-gold/20 dark:hover:shadow-gold/30 hover:-translate-y-0.5 transition-all duration-200 cursor-pointer"
          >
            Start Creating
            <ArrowRight size={16} />
          </motion.button>
        </div>
      </section>

      {/* ── Shop by Category ── */}
      <section className="max-w-5xl mx-auto px-4 md:px-6 py-8">
        <Reveal className="text-center mb-10">
          <h2 className="font-serif text-3xl text-foreground">Shop by Category</h2>
        </Reveal>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
          {categories.map((cat, i) => (
            <Reveal key={cat.label} delay={0.05 + i * 0.08}>
              {cat.comingSoon ? (
                <div className="rounded-lg border border-border bg-card p-8 text-center opacity-60 cursor-not-allowed dark:bg-card dark:border-border">
                  <span className="text-4xl block mb-3">{cat.icon}</span>
                  <span className="text-base font-medium text-card-foreground block">
                    {cat.label}
                  </span>
                  <span className="text-[10px] font-semibold tracking-wider text-muted-foreground uppercase mt-1.5 block">
                    Coming Soon
                  </span>
                </div>
              ) : (
                <motion.div
                  whileHover={{ y: -3 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                  onClick={() => navigate(cat.href!)}
                  className="cursor-pointer rounded-lg border border-border bg-card p-8 text-center hover:border-accent/30 hover:shadow-md transition-all duration-200 dark:bg-card dark:border-border"
                >
                  <span className="text-4xl block mb-3">{cat.icon}</span>
                  <span className="text-base font-medium text-card-foreground">
                    {cat.label}
                  </span>
                </motion.div>
              )}
            </Reveal>
          ))}
        </div>
      </section>

      {/* ── Featured Products ── */}
      <section className="max-w-6xl mx-auto px-4 md:px-6 pb-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1], delay: 0.5 }}
          className="flex items-center justify-center gap-4 mb-10"
        >
          <h2 className="font-serif text-3xl text-foreground">Featured</h2>
          <span
            onClick={() => navigate('/store/photo-books')}
            className="text-sm font-medium text-[#EB1600] hover:text-[#EB1600]/80 dark:text-gold dark:hover:text-gold-light cursor-pointer transition-colors"
          >
            View All &rarr;
          </span>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {featured.map((product, i) => (
            <motion.div
              key={product.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1], delay: 0.6 + i * 0.1 }}
            >
              <ProductCard product={product} />
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  )
}
