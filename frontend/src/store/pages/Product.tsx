import { type SyntheticEvent, useEffect, useMemo, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Star, ChevronRight } from 'lucide-react'
import { products, type Product as ProductType } from '@/store/data/products'
import { useCart } from '@/store/hooks/use-cart'
import { cn } from '@/lib/utils'

const sizes = ['8\u00d78', '10\u00d710', '12\u00d712'] as const

const fadeUp = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] },
}

function stagger(i: number) {
  return { ...fadeUp, transition: { ...fadeUp.transition, delay: 0.08 * i } }
}

function handleImgError(e: SyntheticEvent<HTMLImageElement>) {
  const el = e.currentTarget
  el.onerror = null
  el.src = ''
  el.style.background = '#EDE4D8'
}

function StarRating({ rating, count }: { rating: number; count: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-0.5">
        {Array.from({ length: 5 }, (_, i) => {
          const filled = i < Math.round(rating)
          return (
            <Star
              key={i}
              size={16}
              className={filled ? 'text-accent fill-accent' : 'text-muted fill-none'}
            />
          )
        })}
      </div>
      <span className="text-sm text-muted-foreground">
        {rating} ({count} reviews)
      </span>
    </div>
  )
}

const badgeStyles: Record<string, string> = {
  bestseller: 'bg-gradient-to-r from-gold to-gold-light text-databricks-navy dark:text-[#0D0B09]',
  tabbyMatch: 'bg-gradient-to-r from-gold to-gold-light text-databricks-navy dark:text-[#0D0B09]',
  new: 'bg-destructive text-white',
}

const badgeLabels: Record<string, string> = {
  bestseller: 'BESTSELLER',
  tabbyMatch: 'TABBY MATCH',
  new: 'NEW',
}

function BadgePill({ badge }: { badge: NonNullable<ProductType['badge']> }) {
  return (
    <span
      className={cn(
        'inline-block rounded-full px-3 py-1 text-[10px] font-bold tracking-wider uppercase',
        badgeStyles[badge]
      )}
    >
      {badgeLabels[badge]}
    </span>
  )
}

function SuggestionCard({ product }: { product: ProductType }) {
  return (
    <Link
      to={`/store/product/${product.id}`}
      className="group block rounded-xl overflow-hidden bg-card border border-border transition-all duration-200 hover:shadow-lg hover:shadow-gold/10 hover:-translate-y-0.5"
    >
      <div className="aspect-[4/3] overflow-hidden">
        <img
          src={product.imageUrl}
          alt={product.title}
          onError={handleImgError}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
      </div>
      <div className="p-3">
        <p className="text-sm font-medium truncate">{product.title}</p>
        <p className="text-sm font-bold text-foreground dark:text-gold mt-1">
          ${product.price.toFixed(2)}
        </p>
      </div>
    </Link>
  )
}

export default function Product() {
  const { id } = useParams<{ id: string }>()
  const cart = useCart()
  const [selectedSize, setSelectedSize] = useState<string>(sizes[1])
  const [added, setAdded] = useState(false)

  useEffect(() => {
    if (!added) return
    const t = setTimeout(() => setAdded(false), 1500)
    return () => clearTimeout(t)
  }, [added])

  const suggestions = useMemo(() => {
    const product = products.find(p => p.id === id)
    if (!product) return []
    const others = products.filter(p => p.id !== product.id)
    // Deterministic shuffle based on product id
    const seed = product.id.split('').reduce((a, c) => a + c.charCodeAt(0), 0)
    const shuffled = [...others].sort((a, b) => {
      const ha = (a.id.charCodeAt(0) * seed) % 100
      const hb = (b.id.charCodeAt(0) * seed) % 100
      return ha - hb
    })
    return shuffled.slice(0, 3)
  }, [id])

  const product = products.find(p => p.id === id)

  if (!product) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <p className="text-2xl font-serif mb-2">Product not found</p>
          <Link to="/store" className="text-sm text-foreground dark:text-gold underline">
            Back to store
          </Link>
        </div>
      </div>
    )
  }

  function handleAddToCart() {
    if (!product) return
    cart.addItem({
      id: product.id,
      name: product.title,
      price: product.price,
      quantity: 1,
      image: product.imageUrl,
    })
    setAdded(true)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-12 py-6 md:py-10">
      {/* Breadcrumb */}
      <motion.nav {...stagger(0)} className="flex items-center gap-2 text-xs md:text-sm text-muted-foreground mb-8">
        <Link to="/store" className="hover:text-foreground transition-colors">
          Home
        </Link>
        <ChevronRight size={14} className="text-muted-foreground" />
        <Link to="/store/photo-books" className="hover:text-foreground transition-colors">
          Photo Books
        </Link>
        <ChevronRight size={14} className="text-muted-foreground" />
        <span className="text-foreground font-medium">{product.title}</span>
      </motion.nav>

      {/* Two-column layout */}
      <div className="flex flex-col lg:flex-row gap-6 lg:gap-12">
        {/* Left — Image */}
        <motion.div
          className="w-full lg:flex-[5] min-w-0"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="relative rounded-2xl overflow-hidden shadow-lg bg-cream dark:bg-muted">
            <img
              src={product.imageUrl}
              alt={product.title}
              onError={handleImgError}
              className="w-full h-full object-cover aspect-[4/3]"
            />
            {/* Soft vignette inset */}
            <div className="absolute inset-0 rounded-2xl shadow-[inset_0_0_60px_rgba(0,0,0,0.08)] pointer-events-none" />
          </div>
        </motion.div>

        {/* Right — Info */}
        <div className="w-full lg:flex-[4] min-w-0 flex flex-col gap-5">
          {/* Badge */}
          {product.badge && (
            <motion.div {...stagger(1)}>
              <BadgePill badge={product.badge} />
            </motion.div>
          )}

          {/* Title */}
          <motion.h1 {...stagger(2)} className="font-sans font-bold text-2xl md:text-4xl text-foreground">
            {product.title}
          </motion.h1>

          {/* Subtitle */}
          <motion.p {...stagger(3)} className="text-muted-foreground text-sm -mt-2">
            {product.subtitle}
          </motion.p>

          {/* Rating */}
          <motion.div {...stagger(4)}>
            <StarRating rating={product.rating} count={product.reviewCount} />
          </motion.div>

          {/* Price */}
          <motion.p {...stagger(5)} className="flex items-center gap-2 text-3xl font-bold mt-2 text-foreground">
            <span className="w-2 h-2 rounded-full bg-accent shrink-0" />
            ${product.price.toFixed(2)}
          </motion.p>

          {/* Size selector */}
          <motion.div {...stagger(6)}>
            <p className="text-xs font-bold tracking-[2px] text-muted-foreground uppercase mb-2">
              Size
            </p>
            <div className="flex gap-2">
              {sizes.map(size => (
                <button
                  key={size}
                  onClick={() => setSelectedSize(size)}
                  className={cn(
                    'px-4 md:px-6 py-2 md:py-2.5 rounded-full border-2 text-sm font-medium transition-all cursor-pointer',
                    selectedSize === size
                      ? 'border-[#0B2026] bg-[#0B2026] text-white dark:border-gold dark:bg-gold dark:text-[#0D0B09]'
                      : 'border-border hover:border-accent/50'
                  )}
                >
                  {size}
                </button>
              ))}
            </div>
          </motion.div>

          {/* Add to cart button */}
          <motion.div {...stagger(7)}>
            <button
              onClick={handleAddToCart}
              className={cn(
                'w-full py-4 rounded-lg text-lg font-semibold cursor-pointer transition-all',
                added
                  ? 'bg-green-600 text-white'
                  : 'bg-[#EB1600] text-white dark:bg-gold dark:text-[#0D0B09] hover:shadow-lg hover:shadow-[#EB1600]/25 dark:hover:shadow-gold/25',
                'active:translate-y-0'
              )}
            >
              {added ? 'Added to Cart!' : <>Add to Cart &mdash; ${product.price.toFixed(2)}</>}
            </button>
          </motion.div>

          {/* Description */}
          {product.description && (
            <motion.div {...stagger(8)}>
              <p className="text-sm leading-relaxed text-muted-foreground border-t border-border pt-5">
                {product.description}
              </p>
            </motion.div>
          )}

        </div>
      </div>

      {/* You might also like — full width */}
      {suggestions.length > 0 && (
        <section className="mt-16 pb-12">
          <motion.div {...stagger(9)}>
            <h2 className="font-sans font-bold text-xl mb-6">You Might Also Like</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {suggestions.map(s => (
                <SuggestionCard key={s.id} product={s} />
              ))}
            </div>
          </motion.div>
        </section>
      )}
    </div>
  )
}
