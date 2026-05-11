import { AnimatePresence, motion } from 'framer-motion'
import { ChevronDown } from 'lucide-react'
import ProductCard from '@/store/components/ProductCard'
import type { Product } from '@/store/data/products'
import type { SortOption } from '@/store/hooks/use-products'

const sortOptions: { value: SortOption; label: string }[] = [
  { value: 'recommended', label: 'Recommended' },
  { value: 'priceLow', label: 'Price: Low to High' },
  { value: 'priceHigh', label: 'Price: High to Low' },
  { value: 'rating', label: 'Top Rated' },
]

interface ProductGridProps {
  products: Product[]
  sort: SortOption
  onSortChange: (sort: SortOption) => void
}

export default function ProductGrid({ products, sort, onSortChange }: ProductGridProps) {
  return (
    <div className="flex-1 min-w-0">
      {/* Sort bar */}
      <div className="flex justify-between items-center mb-6">
        <p className="text-sm text-muted-foreground">
          Showing <span className="font-semibold text-foreground">{products.length}</span> products
        </p>
        <div className="relative">
          <select
            value={sort}
            onChange={e => onSortChange(e.target.value as SortOption)}
            className="appearance-none bg-card border border-border rounded-lg px-3 py-1.5 text-sm pr-8 text-foreground cursor-pointer focus:outline-none focus:ring-1 focus:ring-gold/40"
          >
            {sortOptions.map(opt => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <ChevronDown
            size={14}
            className="absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none text-muted-foreground"
          />
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-2 xl:grid-cols-3 gap-6">
        <AnimatePresence mode="popLayout">
          {products.map(product => (
            <motion.div
              key={product.id}
              layout
              layoutId={product.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
              className="h-full"
            >
              <ProductCard product={product} />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {products.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
          <p className="text-sm">No products match your filters</p>
        </div>
      )}
    </div>
  )
}
