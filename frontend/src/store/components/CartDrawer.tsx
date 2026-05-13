import { useState, useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { X, Trash2, ShoppingBag, Loader2 } from 'lucide-react'
import type { CartItem } from '@/store/hooks/use-cart'
import { cn } from '@/lib/utils'

interface CartDrawerProps {
  isOpen: boolean
  onClose: () => void
  items: CartItem[]
  total: number
  onRemoveItem: (id: string) => void
}

export default function CartDrawer({ isOpen, onClose, items, total, onRemoveItem }: CartDrawerProps) {
  const shipping: number = 0 // FREE
  const [abandonState, setAbandonState] = useState<'idle' | 'loading' | 'flash' | 'sent'>('idle')

  useEffect(() => {
    if (abandonState === 'sent') {
      const t = setTimeout(() => setAbandonState('idle'), 2000)
      return () => clearTimeout(t)
    }
    if (abandonState === 'flash') {
      const t = setTimeout(() => setAbandonState('sent'), 400)
      return () => clearTimeout(t)
    }
  }, [abandonState])

  async function handleAbandonCart() {
    setAbandonState('loading')
    try {
      await fetch('/api/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_type: 'cart_abandoned',
          customer_id: 'cust_88241',
          cart_id: 'cart_demo',
          abandoned_at: new Date().toISOString(),
          cart_total: total,
          items: items.map(i => ({ id: i.id, name: i.name, price: i.price, quantity: i.quantity })),
          tier1_clearance: true,
        }),
      })
    } catch (err) {
      console.error('Failed to send cart_abandoned event (backend may not be running):', err)
    }
    setAbandonState('flash')
    // Navigate to Beat 2 after a brief flash
    setTimeout(() => { window.location.href = '/beat2' }, 800)
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
            className="fixed inset-0 bg-[#0D0B09]/40 z-40 cursor-pointer"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className={cn(
              'fixed top-0 right-0 h-full w-full sm:w-[380px] z-50 flex flex-col',
              'bg-card text-card-foreground shadow-2xl',
              'dark:border-l dark:border-border',
              'pb-[env(safe-area-inset-bottom)]'
            )}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-5 border-b border-border">
              <div className="flex items-center gap-2">
                <ShoppingBag size={18} className="text-foreground dark:text-gold" />
                <h2 className="font-sans font-bold text-lg">Your Cart</h2>
              </div>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg hover:bg-secondary transition-colors cursor-pointer"
                aria-label="Close cart"
              >
                <X size={18} />
              </button>
            </div>

            {/* Items */}
            <div className="flex-1 overflow-y-auto px-6 py-4">
              {items.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                  <ShoppingBag size={40} className="mb-3 opacity-40" />
                  <p className="text-sm">Your cart is empty</p>
                </div>
              ) : (
                <ul className="space-y-4">
                  {items.map(item => (
                    <li key={item.id} className="flex gap-4 p-3 rounded-xl bg-secondary/50">
                      {item.image ? (
                        <div className="w-16 h-16 rounded-lg bg-cream dark:bg-muted overflow-hidden shrink-0">
                          <img src={item.image} alt={item.name} className="w-full h-full object-cover" />
                        </div>
                      ) : (
                        <div className="w-16 h-16 rounded-lg bg-cream dark:bg-muted shrink-0" />
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{item.name}</p>
                        <p className="text-xs text-muted-foreground mt-0.5">Qty: {item.quantity}</p>
                        <p className="text-sm font-semibold text-foreground dark:text-gold mt-1">
                          ${(item.price * item.quantity).toFixed(2)}
                        </p>
                      </div>
                      <button
                        onClick={() => onRemoveItem(item.id)}
                        className="p-1.5 rounded-lg hover:bg-destructive/10 hover:text-destructive transition-colors self-start cursor-pointer"
                        aria-label={`Remove ${item.name}`}
                      >
                        <Trash2 size={14} />
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Summary */}
            {items.length > 0 && (
              <div className="px-6 py-4 border-t border-border space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Subtotal</span>
                  <span className="font-medium">${total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Shipping</span>
                  <span className="font-medium text-green-600 dark:text-green-400">
                    {shipping === 0 ? 'FREE' : `$${shipping.toFixed(2)}`}
                  </span>
                </div>
                <div className="flex justify-between text-base font-semibold pt-2 border-t border-border">
                  <span>Total</span>
                  <span>${(total + shipping).toFixed(2)}</span>
                </div>
                <button
                  className={cn(
                    'w-full mt-3 py-3 rounded-lg font-semibold text-sm tracking-wide',
                    'text-white cursor-pointer',
                    'bg-[#EB1600] dark:bg-gold dark:text-[#0D0B09]',
                    'hover:shadow-lg hover:shadow-[#EB1600]/25 dark:hover:shadow-gold/25 hover:-translate-y-0.5',
                    'active:translate-y-0 transition-all duration-200'
                  )}
                >
                  Proceed to Checkout
                </button>
              </div>
            )}

            {/* Demo control */}
            <div className="px-6 py-4 bg-[#0B2026] dark:bg-[#0D0B09]/60 border-t border-white/10">
              <p className="text-[10px] font-bold tracking-[2px] text-white/40 mb-3">DEMO CONTROL</p>
              <button
                onClick={handleAbandonCart}
                disabled={abandonState === 'loading'}
                className={cn(
                  'w-full py-2.5 rounded-xl text-sm font-semibold tracking-wide cursor-pointer transition-all duration-200',
                  abandonState === 'flash'
                    ? 'bg-[#EB1600] text-white dark:bg-gold dark:text-[#0D0B09] border border-[#EB1600] dark:border-gold shadow-lg shadow-[#EB1600]/40 dark:shadow-gold/40'
                    : abandonState === 'sent'
                      ? 'bg-green-600/20 text-green-400 border border-green-500/40'
                      : 'bg-[#EB1600]/15 text-[#EB1600] border border-[#EB1600]/30 dark:bg-gold/15 dark:text-gold dark:border-gold/30 hover:bg-[#EB1600]/25 hover:border-[#EB1600]/50 dark:hover:bg-gold/25 dark:hover:border-gold/50',
                  abandonState === 'loading' && 'opacity-70 cursor-wait'
                )}
              >
                {abandonState === 'loading' && <Loader2 size={14} className="inline animate-spin mr-1.5" />}
                {abandonState === 'sent'
                  ? 'Event Sent!'
                  : abandonState === 'flash'
                    ? 'Event Sent!'
                    : <>Abandon Cart &rarr; Launch Beat 2</>}
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
