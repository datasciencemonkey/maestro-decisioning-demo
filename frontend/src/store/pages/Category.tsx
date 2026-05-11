import { useState } from 'react'
import { products } from '@/store/data/products'
import { useProducts } from '@/store/hooks/use-products'
import FilterSidebar from '@/store/components/FilterSidebar'
import ProductGrid from '@/store/components/ProductGrid'
import NbaPanel from '@/store/components/NbaPanel'
import UploadModal from '@/store/components/UploadModal'

export default function Category() {
  const { filter, updateFilter, applyMatch, filtered, recommendations } = useProducts(products)
  const [modalOpen, setModalOpen] = useState(false)

  return (
    <div className="max-w-7xl mx-auto px-8 py-6">
      {/* Breadcrumb */}
      <nav className="text-sm text-muted-foreground mb-4">
        <span>Home</span>
        <span className="mx-1.5 text-[#C4A87A]">&gt;</span>
        <span>Photo Books</span>
        <span className="mx-1.5 text-[#C4A87A]">&gt;</span>
        <span className="text-foreground font-medium">Pet Photo Books</span>
      </nav>

      {/* Page heading */}
      <div className="mb-6">
        <h1 className="font-serif text-2xl mb-1">Pet Photo Books</h1>
        <p className="text-sm text-muted-foreground">
          Capture your furry friend's best moments in a custom photo book
        </p>
      </div>

      {/* 3-column layout */}
      <div className="flex gap-8">
        {/* Left: Filters */}
        <FilterSidebar
          filter={filter}
          onFilterChange={updateFilter}
          onMatchClick={() => setModalOpen(true)}
        />

        {/* Center: Product grid */}
        <ProductGrid
          products={filtered}
          sort={filter.sort}
          onSortChange={sort => updateFilter({ sort })}
        />

        {/* Right: NBA panel */}
        <NbaPanel recommendations={recommendations} />
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
