import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import type { Recommendation } from '@/store/hooks/use-products'

interface NbaPanelProps {
  recommendations: Recommendation[]
}

export default function NbaPanel({ recommendations }: NbaPanelProps) {
  return (
    <motion.aside
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="hidden lg:block w-64 shrink-0 bg-gradient-to-b from-[#EB1600]/5 dark:from-[#C4A87A]/5 to-transparent border border-[#EB1600]/20 dark:border-[#C4A87A]/20 ring-1 ring-[#EB1600]/10 dark:ring-gold/10 rounded-xl p-5 space-y-4 self-start"
    >
      {/* Header */}
      <div className="flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse ring-2 ring-green-500/20" />
        <span className="text-[10px] font-bold tracking-widest text-muted-foreground">
          AI RECOMMENDATIONS
        </span>
      </div>

      {/* Customer card */}
      <div className="bg-secondary/50 rounded-lg p-4 mb-4 space-y-1.5">
        <p className="font-serif text-sm">Welcome, Cindy</p>
        <div className="space-y-0.5">
          <p className="text-[11px] text-muted-foreground flex items-center gap-1.5">
            <span className="w-1 h-1 rounded-full bg-[#EB1600] dark:bg-gold" />
            Repeat buyer
          </p>
          <p className="text-[11px] text-muted-foreground flex items-center gap-1.5">
            <span className="w-1 h-1 rounded-full bg-[#EB1600] dark:bg-gold" />
            Cat parent
          </p>
          <p className="text-[11px] text-muted-foreground flex items-center gap-1.5">
            <span className="w-1 h-1 rounded-full bg-[#EB1600] dark:bg-gold" />
            Whiskers
          </p>
        </div>
      </div>

      {/* Recommendations */}
      <div>
        <p className="text-[10px] font-bold tracking-widest text-muted-foreground mb-2.5">
          PICKED FOR YOU
        </p>
        <div className="space-y-2.5">
          {recommendations.map(rec => (
            <Link
              key={rec.id}
              to={`/store/product/${rec.id}`}
              className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-secondary/40 transition-colors cursor-pointer"
            >
              <div className="w-8 h-8 rounded-md bg-cream dark:bg-muted overflow-hidden shrink-0">
                <img
                  src={rec.image}
                  alt={rec.title}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium truncate">{rec.title}</p>
                <p className="text-[11px] text-[#EB1600] dark:text-gold font-semibold">{rec.matchPercent}% match</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Footer */}
      <p className="text-[10px] text-muted-foreground text-center pt-3 border-t border-border">
        Powered by Agent Bricks &middot; Real-time
      </p>
    </motion.aside>
  )
}
