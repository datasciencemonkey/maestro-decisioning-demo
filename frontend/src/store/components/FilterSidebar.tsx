import { Camera } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { ProductFilter, PetFilter } from '@/store/hooks/use-products'

const petChips: { value: PetFilter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'cat', label: '\uD83D\uDC31 Cats' },
  { value: 'dog', label: '\uD83D\uDC15 Dogs' },
]

const sizeOptions = [
  { value: '8x8', label: '8\u00d78 Standard', defaultChecked: true },
  { value: '10x10', label: '10\u00d710 Large', defaultChecked: false },
  { value: '12x12', label: '12\u00d712 XL', defaultChecked: false },
]

interface FilterSidebarProps {
  filter: ProductFilter
  onFilterChange: (partial: Partial<ProductFilter>) => void
  onMatchClick: () => void
}

export default function FilterSidebar({ filter, onFilterChange, onMatchClick }: FilterSidebarProps) {
  return (
    <aside className="w-56 shrink-0 space-y-6">
      <h2 className="font-serif text-lg">Filters</h2>

      {/* Pet type */}
      <div>
        <p className="text-[10px] font-bold tracking-[2px] text-muted-foreground mb-2.5">
          PET TYPE
        </p>
        <div className="flex flex-wrap gap-2">
          {petChips.map(chip => (
            <button
              key={chip.value}
              onClick={() => onFilterChange({ pet: chip.value })}
              className={cn(
                'px-3 py-1.5 rounded-lg text-xs font-medium transition-colors cursor-pointer',
                filter.pet === chip.value
                  ? 'bg-espresso text-white dark:bg-gold dark:text-espresso'
                  : 'bg-cream text-mocha dark:bg-secondary dark:text-secondary-foreground hover:bg-cream/80 dark:hover:bg-secondary/80'
              )}
            >
              {chip.label}
            </button>
          ))}
        </div>
      </div>

      {/* Book size */}
      <div>
        <p className="text-[10px] font-bold tracking-[2px] text-muted-foreground mb-2.5">
          BOOK SIZE
        </p>
        <div className="space-y-2">
          {sizeOptions.map(opt => (
            <label
              key={opt.value}
              className="flex items-center gap-2.5 cursor-pointer group"
            >
              <input
                type="checkbox"
                defaultChecked={opt.defaultChecked}
                className="w-4 h-4 rounded border-border accent-gold cursor-pointer"
              />
              <span className="text-sm text-foreground group-hover:text-mocha dark:group-hover:text-gold transition-colors">
                {opt.label}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Match My Pet card */}
      <button
        onClick={onMatchClick}
        className={cn(
          'w-full p-4 rounded-xl border-2 border-dashed border-gold/40',
          'bg-gold/[0.04] dark:bg-gold/[0.06]',
          'flex flex-col items-center gap-2 text-center',
          'hover:border-gold/70 hover:bg-gold/[0.08] transition-all cursor-pointer'
        )}
      >
        <Camera size={24} className="text-gold" />
        <span className="text-sm font-semibold text-gold">Match My Pet</span>
        <span className="text-[11px] text-muted-foreground">AI-powered photo matching</span>
      </button>
    </aside>
  )
}
