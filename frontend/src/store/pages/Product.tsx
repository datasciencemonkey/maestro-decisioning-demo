import { type SyntheticEvent, useMemo, useState } from 'react'
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
              className={filled ? 'text-[#C4A87A] fill-[#C4A87A]' : 'text-muted fill-none'}
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
  bestseller: 'bg-gradient-to-r from-gold to-gold-light text-espresso',
  tabbyMatch: 'bg-gradient-to-r from-gold to-gold-light text-espresso',
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
        <p className="text-sm font-bold text-mocha dark:text-gold mt-1">
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

  const product = products.find(p => p.id === id)

  const suggestions = useMemo(() => {
    if (!product) return []
    const others = products.filter(p => p.id !== product.id)
    const shuffled = [...others].sort(() => Math.random() - 0.5)
    return shuffled.slice(0, 3)
  }, [product])

  if (!product) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <p className="text-2xl font-serif mb-2">Product not found</p>
          <Link to="/store" className="text-sm text-mocha dark:text-gold underline">
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
  }

  return (
    <div className="max-w-7xl mx-auto px-12 py-8">
      {/* Breadcrumb */}
      <motion.nav {...stagger(0)} className="flex items-center gap-2 text-sm text-muted-foreground mb-8">
        <Link to="/store" className="hover:text-foreground transition-colors">
          Home
        </Link>
        <ChevronRight size={14} className="text-[#C4A87A]" />
        <Link to="/store/photo-books" className="hover:text-foreground transition-colors">
          Photo Books
        </Link>
        <ChevronRight size={14} className="text-[#C4A87A]" />
        <span className="text-foreground font-medium">{product.title}</span>
      </motion.nav>

      {/* Two-column layout */}
      <div className="flex gap-12">
        {/* Left — Image */}
        <motion.div
          className="flex-[5] min-w-0"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="rounded-2xl overflow-hidden shadow-lg bg-cream dark:bg-muted">
            <img
              src={product.imageUrl}
              alt={product.title}
              onError={handleImgError}
              className="w-full h-full object-cover aspect-[4/3]"
            />
          </div>
        </motion.div>

        {/* Right — Info */}
        <div className="flex-[4] min-w-0 flex flex-col gap-5">
          {/* Badge */}
          {product.badge && (
            <motion.div {...stagger(1)}>
              <BadgePill badge={product.badge} />
            </motion.div>
          )}

          {/* Title */}
          <motion.h1 {...stagger(2)} className="font-serif text-4xl text-foreground">
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
          <motion.p {...stagger(5)} className="text-3xl font-bold mt-2 text-foreground">
            ${product.price.toFixed(2)}
          </motion.p>

          {/* Size selector */}
          <motion.div {...stagger(6)}>
            <p className="text-[10px] font-bold tracking-[2px] text-muted-foreground uppercase mb-2">
              Size
            </p>
            <div className="flex gap-2">
              {sizes.map(size => (
                <button
                  key={size}
                  onClick={() => setSelectedSize(size)}
                  className={cn(
                    'px-6 py-2.5 rounded-full border-2 text-sm font-medium transition-all cursor-pointer',
                    selectedSize === size
                      ? 'border-[#2C1810] bg-[#2C1810] text-white dark:border-[#C4A87A] dark:bg-[#C4A87A] dark:text-[#0D0B09]'
                      : 'border-border hover:border-[#C4A87A]/50'
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
                'w-full py-4 rounded-xl text-lg font-semibold cursor-pointer',
                'bg-gradient-to-r from-[#7C6353] to-[#A08468] text-white',
                'hover:shadow-lg hover:shadow-[#7C6353]/25 transition-all',
                'active:translate-y-0'
              )}
            >
              Add to Cart &mdash; ${product.price.toFixed(2)}
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

          {/* You might also like */}
          <motion.div {...stagger(9)} className="mt-12 mb-6">
            <h2 className="font-serif text-xl mb-6">You Might Also Like</h2>
            <div className="grid grid-cols-3 gap-4">
              {suggestions.map(s => (
                <SuggestionCard key={s.id} product={s} />
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
