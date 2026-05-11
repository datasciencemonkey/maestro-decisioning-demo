import { useState } from 'react'
import { SlidersHorizontal, X } from 'lucide-react'
import { products } from '@/store/data/products'
import { useProducts, type PetFilter } from '@/store/hooks/use-products'
import FilterSidebar from '@/store/components/FilterSidebar'
import ProductGrid from '@/store/components/ProductGrid'
import NbaPanel from '@/store/components/NbaPanel'
import UploadModal from '@/store/components/UploadModal'
import { cn } from '@/lib/utils'

const petChips: { value: PetFilter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'cat', label: '\uD83D\uDC31 Cats' },
  { value: 'dog', label: '\uD83D\uDC15 Dogs' },
]

export default function Category() {
  const { filter, updateFilter, applyMatch, filtered, recommendations } = useProducts(products)
  const [modalOpen, setModalOpen] = useState(false)
  const [filtersOpen, setFiltersOpen] = useState(false)

  return (
    <div className="relative max-w-7xl mx-auto px-4 md:px-12 py-6">
      {/* Decorative gradient orb */}
      <div className="absolute -top-20 -right-20 w-80 h-80 rounded-full bg-[radial-gradient(circle,rgba(196,168,122,0.05),transparent_70%)] pointer-events-none" />
      {/* Breadcrumb */}
      <nav className="text-sm text-muted-foreground mb-4">
        <span>Home</span>
        <span className="mx-1.5 text-muted-foreground">&gt;</span>
        <span>Photo Books</span>
        <span className="mx-1.5 text-muted-foreground">&gt;</span>
        <span className="text-foreground font-medium">Pet Photo Books</span>
      </nav>

      {/* Page heading */}
      <div className="mb-6">
        <h1 className="font-serif text-3xl mb-1 text-foreground">Pet Photo Books</h1>
        <p className="text-sm text-muted-foreground">
          Capture your furry friend's best moments in a custom photo book
        </p>
      </div>

      {/* Mobile: filter bar with pet chips + filters button */}
      <div className="flex items-center gap-2 mb-4 md:hidden">
        <div className="flex-1 flex gap-2 overflow-x-auto no-scrollbar">
          {petChips.map(chip => (
            <button
              key={chip.value}
              onClick={() => updateFilter({ pet: chip.value })}
              className={cn(
                'shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer',
                filter.pet === chip.value
                  ? 'bg-[#0B2026] text-white dark:bg-gold dark:text-[#0D0B09]'
                  : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
              )}
            >
              {chip.label}
            </button>
          ))}
        </div>
        <button
          onClick={() => setFiltersOpen(!filtersOpen)}
          className="shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-xs font-medium cursor-pointer"
        >
          {filtersOpen ? <X size={14} /> : <SlidersHorizontal size={14} />}
          Filters
        </button>
      </div>

      {/* Mobile: collapsible filter panel */}
      {filtersOpen && (
        <div className="mb-4 md:hidden border border-border rounded-xl p-4 bg-card">
          <FilterSidebar
            filter={filter}
            onFilterChange={updateFilter}
            onMatchClick={() => { setModalOpen(true); setFiltersOpen(false) }}
            className="w-full"
          />
        </div>
      )}

      {/* 3-column layout */}
      <div className="flex gap-8">
        {/* Left: Filters (hidden on mobile) */}
        <div className="hidden md:block">
          <FilterSidebar
            filter={filter}
            onFilterChange={updateFilter}
            onMatchClick={() => setModalOpen(true)}
          />
        </div>

        {/* Center: Product grid */}
        <ProductGrid
          products={filtered}
          sort={filter.sort}
          onSortChange={sort => updateFilter({ sort })}
        />

        {/* Right: NBA panel (hidden below desktop) */}
        <div className="hidden lg:block">
          <NbaPanel recommendations={recommendations} />
        </div>
      </div>

      {/* Upload modal */}
      <UploadModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onMatch={applyMatch}
      />
    </div>
  )
}
