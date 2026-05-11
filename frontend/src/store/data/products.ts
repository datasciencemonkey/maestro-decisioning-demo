export type Product = {
  id: string
  title: string
  subtitle: string
  price: number
  rating: number
  reviewCount: number
  imageUrl: string
  category: 'cat' | 'dog' | 'all'
  badge?: 'bestseller' | 'tabbyMatch' | 'new'
  matchPercent?: number
  description?: string
}

export const products: Product[] = [
  { id: 'pb_welcome_home_24pp', title: 'Welcome Home 24pg', subtitle: 'Tabby collection \u00b7 Hardcover', price: 42, rating: 4.9, reviewCount: 124, imageUrl: 'https://images.unsplash.com/photo-1615497001839-b0a0eac3274c?w=600&h=400&fit=crop', category: 'cat', badge: 'bestseller', description: 'A beautiful hardcover photo book to celebrate your new pet arrival. 24 pages of premium matte paper with lay-flat binding.' },
  { id: 'pb_classic_soft', title: 'Classic Softcover', subtitle: 'All pets \u00b7 Softcover', price: 29, rating: 4.2, reviewCount: 89, imageUrl: 'https://images.unsplash.com/photo-1596854407944-bf87f6fdd49e?w=600&h=400&fit=crop', category: 'all' },
  { id: 'pb_first_year', title: 'First Year Journal', subtitle: 'All pets \u00b7 Layflat', price: 55, rating: 4.8, reviewCount: 56, imageUrl: 'https://images.unsplash.com/photo-1561948955-570b270e7c36?w=600&h=400&fit=crop', category: 'all', badge: 'new' },
  { id: 'pb_whisker_tales', title: 'Whisker Tales', subtitle: 'Cat collection \u00b7 Hardcover', price: 38, rating: 4.6, reviewCount: 203, imageUrl: 'https://images.unsplash.com/photo-1533738363-b7f9aef128ce?w=600&h=400&fit=crop', category: 'cat' },
  { id: 'pb_paw_prints', title: 'Paw Prints Album', subtitle: 'All pets \u00b7 Premium layflat', price: 65, rating: 4.9, reviewCount: 78, imageUrl: 'https://images.unsplash.com/photo-1543852786-1cf6624b9987?w=600&h=400&fit=crop', category: 'all' },
  { id: 'pb_kitten_cuddles', title: 'Kitten Cuddles', subtitle: 'Cat collection \u00b7 Softcover', price: 32, rating: 4.4, reviewCount: 167, imageUrl: 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=600&h=400&fit=crop', category: 'cat' },
  { id: 'pb_playful_paws', title: 'Playful Paws', subtitle: 'Cat collection \u00b7 Hardcover', price: 45, rating: 4.7, reviewCount: 92, imageUrl: 'https://images.unsplash.com/photo-1592194996308-7b43878e84a6?w=600&h=400&fit=crop', category: 'cat' },
  { id: 'pb_good_boy', title: 'Good Boy Chronicles', subtitle: 'Dog collection \u00b7 Hardcover', price: 42, rating: 4.8, reviewCount: 145, imageUrl: 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=600&h=400&fit=crop', category: 'dog' },
  { id: 'pb_fetch_tales', title: 'Fetch & Tales', subtitle: 'Dog collection \u00b7 Softcover', price: 29, rating: 4.3, reviewCount: 71, imageUrl: 'https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=600&h=400&fit=crop', category: 'dog' },
  { id: 'pb_best_friend', title: 'Best Friend Forever', subtitle: 'Dog collection \u00b7 Premium', price: 58, rating: 4.9, reviewCount: 199, imageUrl: 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=600&h=400&fit=crop', category: 'dog', badge: 'bestseller' },
  { id: 'pb_hoppy_days', title: 'Hoppy Days', subtitle: 'Small pets \u00b7 Softcover', price: 26, rating: 4.1, reviewCount: 34, imageUrl: 'https://images.unsplash.com/photo-1425082661705-1834bfd09dca?w=600&h=400&fit=crop', category: 'all' },
  { id: 'pb_feathered_friends', title: 'Feathered Friends', subtitle: 'Bird collection \u00b7 Hardcover', price: 39, rating: 4.5, reviewCount: 47, imageUrl: 'https://images.unsplash.com/photo-1606567595334-d39972c85dbe?w=600&h=400&fit=crop', category: 'all' },
]
