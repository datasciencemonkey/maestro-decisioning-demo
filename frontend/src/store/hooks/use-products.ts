import { useState, useMemo, useCallback } from 'react'
import type { Product } from '@/store/data/products'

export type { Product } from '@/store/data/products'

export interface Recommendation {
  id: string
  title: string
  image: string
  matchPercent: number
}

export type PetFilter = 'all' | 'cat' | 'dog'
export type SortOption = 'recommended' | 'priceLow' | 'priceHigh' | 'rating'

export interface ProductFilter {
  pet: PetFilter
  sort: SortOption
}

export function useProducts(products: Product[]) {
  const [filter, setFilter] = useState<ProductFilter>({
    pet: 'all',
    sort: 'recommended',
  })
  const [matchActive, setMatchActive] = useState(false)
  const [matchScores, setMatchScores] = useState<Map<string, number>>(new Map())

  const updateFilter = useCallback((partial: Partial<ProductFilter>) => {
    setFilter(prev => ({ ...prev, ...partial }))
  }, [])

  const applyMatch = useCallback(() => {
    const scores = new Map<string, number>()
    for (const p of products) {
      if (p.category === 'cat') {
        scores.set(p.id, Math.floor(Math.random() * 20) + 80)
      }
    }
    setMatchScores(scores)
    setMatchActive(true)
    setFilter(prev => ({ ...prev, pet: 'cat' }))
  }, [products])

  const filtered = useMemo(() => {
    let list = [...products]

    // pet filter
    if (filter.pet !== 'all') {
      list = list.filter(p => p.category === filter.pet || p.category === 'all')
    }

    // apply match scores + badges
    if (matchActive) {
      list = list.map(p => {
        const score = matchScores.get(p.id)
        if (score != null) {
          return {
            ...p,
            matchPercent: score,
            badge: score >= 90 ? 'tabbyMatch' as const : p.badge,
          }
        }
        return p
      })
    }

    // sort
    switch (filter.sort) {
      case 'priceLow':
        list.sort((a, b) => a.price - b.price)
        break
      case 'priceHigh':
        list.sort((a, b) => b.price - a.price)
        break
      case 'rating':
        list.sort((a, b) => b.rating - a.rating)
        break
      case 'recommended':
      default:
        if (matchActive) {
          list.sort((a, b) => (b.matchPercent ?? 0) - (a.matchPercent ?? 0))
        }
        break
    }

    return list
  }, [products, filter, matchActive, matchScores])

  const recommendations = useMemo<Recommendation[]>(() => {
    const cats = products.filter(p => p.category === 'cat')
    return cats.slice(0, 3).map(p => ({
      id: p.id,
      title: p.title,
      image: p.imageUrl,
      matchPercent: matchScores.get(p.id) ?? Math.floor(Math.random() * 15) + 82,
    }))
  }, [products, matchScores])

  return {
    filter,
    updateFilter,
    matchActive,
    applyMatch,
    filtered,
    recommendations,
  }
}
