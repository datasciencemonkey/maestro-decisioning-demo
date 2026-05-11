import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Star, ShoppingCart, Check } from 'lucide-react'
import type { Product } from '@/store/data/products'
import { useCart } from '@/store/hooks/use-cart'

const badgeStyles: Record<string, string> = {
  bestseller:
    'bg-gradient-to-r from-[#C4A87A] to-[#DBC09E] text-[#2C1810] text-[10px] font-bold tracking-wider px-3 py-1 rounded-full',
  tabbyMatch:
    'bg-gradient-to-r from-[#C4A87A] to-[#DBC09E] text-[#2C1810] text-[10px] font-bold tracking-wider px-3 py-1 rounded-full',
  new: 'bg-red-500 text-white text-[10px] font-bold tracking-wider px-3 py-1 rounded-full',
}

function badgeLabel(product: Product): string {
  if (product.badge === 'bestseller') return 'BESTSELLER'
  if (product.badge === 'tabbyMatch')
    return product.matchPercent
      ? `TABBY MATCH ${product.matchPercent}%`
      : 'TABBY MATCH'
  if (product.badge === 'new') return 'NEW'
  return ''
}

export default function ProductCard({ product }: { product: Product }) {
  const navigate = useNavigate()
  const cart = useCart()
  const [imgError, setImgError] = useState(false)
  const [added, setAdded] = useState(false)

  useEffect(() => {
    if (!added) return
    const t = setTimeout(() => setAdded(false), 1500)
    return () => clearTimeout(t)
  }, [added])

  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      onClick={() => navigate(`/store/product/${product.id}`)}
      className="group flex flex-col cursor-pointer rounded-xl bg-card border border-border shadow-sm hover:shadow-xl transition-all duration-300"
    >
      {/* Image */}
      <div className="relative aspect-[4/3] overflow-hidden rounded-t-xl">
        {imgError ? (
          <div className="w-full h-full bg-[#FFF8F0] dark:bg-muted" />
        ) : (
          <img
            src={product.imageUrl}
            alt={product.title}
            loading="lazy"
            onError={() => setImgError(true)}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
        )}
        {/* Hover gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
        {product.badge && (
          <span
            className={`absolute top-3 left-3 ${badgeStyles[product.badge]}`}
          >
            {badgeLabel(product)}
          </span>
        )}
      </div>

      {/* Content */}
      <div className="flex flex-col flex-1 p-4">
        <h3 className="font-serif text-lg text-card-foreground leading-tight mb-0.5">
          {product.title}
        </h3>
        <p className="text-xs text-muted-foreground mb-2">{product.subtitle}</p>

        {/* Rating */}
        <div className="flex items-center gap-1 mb-3">
          {Array.from({ length: 5 }, (_, i) => (
            <Star
              key={i}
              size={14}
              className={
                i < Math.round(product.rating)
                  ? 'fill-[#C4A87A] text-[#C4A87A]'
                  : 'fill-none text-muted-foreground/40'
              }
            />
          ))}
          <span className="text-xs text-muted-foreground ml-1">
            ({product.reviewCount})
          </span>
        </div>

        {/* Price + Add to Cart */}
        <div className="mt-auto flex items-center justify-between gap-2">
          <span className="text-lg font-semibold text-card-foreground">
            ${product.price.toFixed(2)}
          </span>
          <button
            onClick={(e) => {
              e.stopPropagation()
              cart.addItem({
                id: product.id,
                name: product.title,
                price: product.price,
                quantity: 1,
                image: product.imageUrl,
              })
              setAdded(true)
            }}
            className="relative overflow-hidden flex-1 inline-flex items-center justify-center gap-1.5 bg-[#EB1600] text-white dark:bg-gold dark:text-[#0D0B09] rounded-lg py-2.5 text-sm font-semibold hover:opacity-90 transition-opacity after:absolute after:inset-0 after:bg-gradient-to-r after:from-transparent after:via-white/20 after:to-transparent after:-translate-x-full hover:after:translate-x-full after:transition-transform after:duration-500"
          >
            {added ? <Check size={14} /> : <ShoppingCart size={14} />}
            {added ? 'Added!' : 'Add to Cart'}
          </button>
        </div>
      </div>
    </motion.div>
  )
}
