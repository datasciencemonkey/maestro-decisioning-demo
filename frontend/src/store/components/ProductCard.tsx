import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Star, ShoppingCart } from 'lucide-react'
import type { Product } from '@/store/data/products'

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

export default function ProductCard({ product }: { product: Product }) {
  const navigate = useNavigate()

  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      onClick={() => navigate(`/store/product/${product.id}`)}
      className="group cursor-pointer rounded-lg overflow-hidden bg-card border border-border shadow-sm hover:shadow-lg transition-shadow duration-300 dark:border-border"
    >
      {/* Image */}
      <div className="relative aspect-[4/3] overflow-hidden">
        <img
          src={product.imageUrl}
          alt={product.title}
          loading="lazy"
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        {product.badge && (
          <span
            className={`absolute top-3 left-3 px-2.5 py-1 text-[10px] font-bold tracking-widest rounded-md ${badgeStyles[product.badge]}`}
          >
            {badgeLabels[product.badge]}
          </span>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        <h3 className="font-serif text-lg text-card-foreground leading-tight mb-0.5">
          {product.title}
        </h3>
        <p className="text-xs text-muted-foreground mb-2">{product.subtitle}</p>

        {/* Rating */}
        <div className="flex items-center gap-1 mb-3">
          {Array.from({ length: 5 }, (_, i) => (
            <Star
              key={i}
              size={13}
              className={
                i < Math.round(product.rating)
                  ? 'fill-gold text-gold'
                  : 'fill-none text-muted-foreground/40'
              }
            />
          ))}
          <span className="text-[11px] text-muted-foreground ml-1">
            ({product.reviewCount})
          </span>
        </div>

        {/* Price + Add to Cart */}
        <div className="flex items-center justify-between">
          <span className="text-lg font-semibold text-card-foreground">
            ${product.price}
          </span>
          <button
            onClick={(e) => {
              e.stopPropagation()
              // Cart integration handled by parent/context
            }}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-md bg-gradient-to-r from-gold to-gold-light text-espresso hover:from-gold-light hover:to-gold transition-all duration-200 hover:shadow-md"
          >
            <ShoppingCart size={13} />
            Add to Cart
          </button>
        </div>
      </div>
    </motion.div>
  )
}
