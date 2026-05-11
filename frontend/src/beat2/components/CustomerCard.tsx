import { User, MapPin, Mail, Award } from 'lucide-react'

export default function CustomerCard() {
  return (
    <div className="bg-card border border-[var(--color-gold)]/20 rounded-xl p-4 mb-4">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[var(--color-gold)]/30 to-[var(--color-mocha)]/20 flex items-center justify-center shrink-0">
          <User size={18} className="text-[var(--color-gold)]" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <p className="font-serif text-base text-card-foreground">Cindy Chen</p>
            <span className="inline-flex items-center gap-1 bg-[var(--color-gold)]/15 text-[var(--color-gold)] text-[10px] font-bold tracking-wider px-2 py-0.5 rounded-full">
              <Award size={10} />
              GOLD
            </span>
          </div>
          <p className="text-[11px] text-muted-foreground font-mono">cust_88241</p>
        </div>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-2">
        <div className="flex items-center gap-1.5">
          <span className="text-sm">🐱</span>
          <span className="text-[11px] text-muted-foreground">Whiskers (tabby)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <MapPin size={11} className="text-muted-foreground shrink-0" />
          <span className="text-[11px] text-muted-foreground">America/Chicago</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Mail size={11} className="text-muted-foreground shrink-0" />
          <span className="text-[11px] text-muted-foreground">Email preferred</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500 shrink-0" />
          <span className="text-[11px] text-muted-foreground">Repeat buyer</span>
        </div>
      </div>
    </div>
  )
}
