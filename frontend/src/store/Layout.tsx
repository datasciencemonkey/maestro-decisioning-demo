import { useState, useEffect, useRef, useCallback } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { Search, ShoppingCart, Sun, Moon, Menu, X } from 'lucide-react'
import { useTheme } from '@/hooks/use-theme'
import { useCart, CartProvider } from '@/store/hooks/use-cart'
import CartDrawer from '@/store/components/CartDrawer'
import { cn } from '@/lib/utils'

const navLinks = [
  { label: 'Photo Books', to: '/store/photo-books' },
  { label: 'Cards', to: '/store/cards' },
  { label: 'Prints', to: '/store/prints' },
  { label: 'Gifts', to: '/store/gifts' },
]

const narratorModes = ['Free', 'Guided', 'Auto'] as const

const demoScenes = [
  { label: 'SCENE 1', text: 'Meet Cindy \u2014 back on Fluttershy for her kitten Whiskers', route: '/store' },
  { label: 'SCENE 2', text: 'Cindy browses cat-themed photo book templates', route: '/store/photo-books' },
  { label: 'SCENE 3', text: 'She uploads a reference photo of Whiskers', route: '/store/photo-books' },
  { label: 'SCENE 4', text: 'Tabby-pattern templates surface to the top', route: '/store/product/pb_welcome_home_24pp' },
  { label: 'SCENE 5', text: 'She adds the Welcome Home template to cart', route: '/store/product/pb_welcome_home_24pp' },
  { label: 'SCENE 6', text: 'She abandons cart \u2014 triggering the agent...', route: '/store/photo-books' },
]

function pageNameFromPath(pathname: string): string {
  if (pathname === '/store') return 'Home'
  if (pathname === '/store/photo-books') return 'Photo Books'
  if (pathname.startsWith('/store/product/')) return 'Product Detail'
  if (pathname === '/store/cards') return 'Cards'
  if (pathname === '/store/prints') return 'Prints'
  if (pathname === '/store/gifts') return 'Gifts'
  return 'Store'
}

function StoreShell() {
  const { theme, toggle } = useTheme()
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const cart = useCart()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const [narratorMode, setNarratorMode] = useState<'Free' | 'Guided' | 'Auto'>('Free')
  const [sceneIndex, setSceneIndex] = useState(0)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const clearAutoInterval = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }, [])

  // Auto mode: advance scenes every 4 seconds
  useEffect(() => {
    if (narratorMode !== 'Auto') {
      clearAutoInterval()
      return
    }
    // Start from scene 0 when entering auto mode
    setSceneIndex(0)
    navigate(demoScenes[0].route)

    let idx = 0
    intervalRef.current = setInterval(() => {
      idx += 1
      if (idx >= demoScenes.length) {
        clearAutoInterval()
        return
      }
      setSceneIndex(idx)
      navigate(demoScenes[idx].route)
    }, 4000)

    return clearAutoInterval
  }, [narratorMode, navigate, clearAutoInterval])

  const handleNextScene = useCallback(() => {
    setSceneIndex(prev => {
      const next = Math.min(prev + 1, demoScenes.length - 1)
      navigate(demoScenes[next].route)
      return next
    })
  }, [navigate])

  // Derive narrator display values
  const narratorLabel = narratorMode === 'Free'
    ? pageNameFromPath(pathname).toUpperCase()
    : `${demoScenes[sceneIndex].label} / ${demoScenes.length}`
  const narratorText = narratorMode === 'Free'
    ? 'Browse freely'
    : demoScenes[sceneIndex].text

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground">
      {/* Promo bar */}
      <div
        className="py-2 text-center text-white text-xs tracking-widest bg-[#0B2026]"
      >
        <span className="inline-block w-1.5 h-1.5 rounded-full bg-white/60 mr-2" />Free shipping on pet photo books this week
      </div>

      {/* Nav bar */}
      <header className="bg-white dark:bg-card border-b border-border sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center gap-6 px-4 md:px-8 py-3">
          {/* Hamburger (mobile only) */}
          <button
            onClick={() => setMobileNavOpen(prev => !prev)}
            className="p-2 rounded-lg hover:bg-secondary transition-colors cursor-pointer md:hidden"
            aria-label="Toggle navigation"
          >
            {mobileNavOpen ? <X size={20} /> : <Menu size={20} />}
          </button>

          {/* Logo */}
          <Link to="/store" className="flex items-center gap-2 shrink-0 cursor-pointer group">
            <span className="text-2xl transition-transform group-hover:scale-110 inline-block">🦋</span>
            <span className="font-sans font-bold text-xl text-foreground">Fluttershy</span>
          </Link>

          {/* Nav links (desktop) */}
          <nav className="hidden md:flex items-center gap-1 ml-4">
            {navLinks.map(link => (
              <Link
                key={link.to}
                to={link.to}
                className={cn(
                  'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors cursor-pointer',
                  pathname === link.to
                    ? 'bg-secondary text-foreground font-semibold'
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Spacer */}
          <div className="flex-1" />

          {/* Search (hidden on mobile) */}
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-secondary/60 border border-border w-52">
            <Search size={14} className="text-muted-foreground shrink-0" />
            <input
              type="text"
              placeholder="Search..."
              className="bg-transparent text-sm outline-none w-full placeholder:text-muted-foreground"
            />
          </div>

          {/* Theme toggle */}
          <button
            onClick={toggle}
            className="p-2 rounded-lg hover:bg-secondary transition-colors cursor-pointer"
            aria-label="Toggle theme"
          >
            {theme === 'dark'
              ? <Sun size={18} className="text-[#EB1600] dark:text-gold" />
              : <Moon size={18} className="text-foreground" />
            }
          </button>

          {/* Cart icon */}
          <button
            onClick={cart.toggle}
            className="relative p-2 rounded-lg hover:bg-secondary transition-colors cursor-pointer"
            aria-label="Open cart"
          >
            <ShoppingCart size={18} className="text-foreground" />
            {cart.itemCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4.5 h-4.5 rounded-full bg-primary text-primary-foreground text-[10px] font-bold flex items-center justify-center leading-none">
                {cart.itemCount}
              </span>
            )}
          </button>
        </div>

        {/* Mobile nav drawer */}
        {mobileNavOpen && (
          <nav className="md:hidden border-t border-border bg-white dark:bg-card px-4 py-3 space-y-1">
            {navLinks.map(link => (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setMobileNavOpen(false)}
                className={cn(
                  'block px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  pathname === link.to
                    ? 'bg-secondary text-foreground'
                    : 'text-muted-foreground hover:text-foreground'
                )}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        )}
      </header>

      {/* Page content */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Store footer */}
      <footer className="bg-secondary/30 dark:bg-card/50 border-t border-border py-8 px-4 md:px-8">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-2 md:gap-0 text-center md:text-left text-xs text-muted-foreground">
          <span>Fluttershy — Made with love for pets everywhere</span>
          <div className="flex gap-6">
            <span className="hover:text-foreground cursor-pointer transition-colors">Help</span>
            <span className="hover:text-foreground cursor-pointer transition-colors">Privacy</span>
            <span className="hover:text-foreground cursor-pointer transition-colors">Terms</span>
          </div>
        </div>
      </footer>

      {/* Narrator strip */}
      <div className="h-[52px] bg-[#0B2026] dark:bg-[#0D0B09]/80 border-t border-white/10 flex items-center justify-between px-6">
        <div className="flex items-center gap-3 min-w-0">
          <span className="shrink-0 inline-flex items-center px-2.5 py-0.5 rounded-full bg-[#EB1600]/15 text-[#EB1600] dark:bg-gold/20 dark:text-gold text-[10px] font-bold tracking-wider border border-[#EB1600]/20 dark:border-gold/30">
            {narratorLabel}
          </span>
          <p className="text-white/50 text-xs truncate">
            {narratorText}
          </p>
        </div>
        <div className="flex items-center gap-1 shrink-0">
          {narratorModes.map(mode => (
            <button
              key={mode}
              onClick={() => setNarratorMode(mode as 'Free' | 'Guided' | 'Auto')}
              className={cn(
                'px-3 py-1 rounded-full text-[10px] font-semibold tracking-wider transition-colors cursor-pointer',
                mode === narratorMode
                  ? 'bg-[#EB1600]/15 text-[#EB1600] border border-[#EB1600]/20 dark:bg-gold/20 dark:text-gold dark:border-gold/30'
                  : 'text-white/30 hover:text-white/50 hover:bg-white/5'
              )}
            >
              {mode}
            </button>
          ))}
          {narratorMode === 'Guided' && (
            <button
              onClick={handleNextScene}
              disabled={sceneIndex >= demoScenes.length - 1}
              className="ml-2 px-3 py-1 rounded-full bg-primary text-primary-foreground text-[10px] font-bold tracking-wider cursor-pointer hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Next →
            </button>
          )}
          {narratorMode === 'Auto' && (
            <span className="ml-2 flex items-center gap-1.5 text-[10px] text-green-400">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              Playing...
            </span>
          )}
        </div>
      </div>

      {/* Cart drawer */}
      <CartDrawer
        isOpen={cart.isOpen}
        onClose={cart.close}
        items={cart.items}
        total={cart.total}
        onRemoveItem={cart.removeItem}
      />
    </div>
  )
}

export default function Layout() {
  return (
    <CartProvider>
      <StoreShell />
    </CartProvider>
  )
}
