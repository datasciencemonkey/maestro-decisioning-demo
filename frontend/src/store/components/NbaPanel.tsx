import { cn } from '@/lib/utils'
import type { Recommendation } from '@/store/hooks/use-products'

interface NbaPanelProps {
  recommendations: Recommendation[]
}

export default function NbaPanel({ recommendations }: NbaPanelProps) {
  return (
    <aside
      className={cn(
        'w-60 shrink-0 rounded-lg border border-gold/20',
        'bg-card dark:bg-card p-4 space-y-4 self-start'
      )}
    >
      {/* Header */}
      <div className="flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
        <span className="text-[10px] font-bold tracking-widest text-muted-foreground">
          AI RECOMMENDATIONS
        </span>
      </div>

      {/* Customer card */}
      <div className="rounded-lg bg-secondary/50 dark:bg-secondary/30 p-3 space-y-1.5">
        <p className="font-serif text-sm">Welcome, Cindy</p>
        <div className="space-y-0.5">
          <p className="text-[11px] text-muted-foreground flex items-center gap-1.5">
            <span className="w-1 h-1 rounded-full bg-gold" />
            Repeat buyer
          </p>
          <p className="text-[11px] text-muted-foreground flex items-center gap-1.5">
            <span className="w-1 h-1 rounded-full bg-gold" />
            Cat parent
          </p>
          <p className="text-[11px] text-muted-foreground flex items-center gap-1.5">
            <span className="w-1 h-1 rounded-full bg-gold" />
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
            <div
              key={rec.id}
              className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-secondary/40 transition-colors cursor-pointer"
            >
              <div className="w-10 h-10 rounded-md bg-cream dark:bg-muted overflow-hidden shrink-0">
                <img
                  src={rec.image}
                  alt={rec.title}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium truncate">{rec.title}</p>
                <p className="text-[11px] text-gold font-semibold">{rec.matchPercent}% match</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <p className="text-[9px] text-muted-foreground/60 text-center pt-2 border-t border-border">
        Powered by Agent Bricks &middot; Real-time
      </p>
    </aside>
  )
}
