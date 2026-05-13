import { motion } from 'framer-motion'
import { CheckCircle2, TrendingUp } from 'lucide-react'

interface DecisionRow {
  type: string
  target: string
  reason: string
}

interface Signal {
  signal: string
  value: string
  weight: number
}

interface DecisionPanelProps {
  verdict?: string
  decisions?: DecisionRow[]
  signals?: Signal[]
}

const FALLBACK_DECISIONS: DecisionRow[] = [
  { type: 'suppress_from', target: 'campaign_sp_2026', reason: 'Frequency cap breach' },
  { type: 'prioritize_in', target: 'campaign_ac_2026', reason: 'High cart recovery propensity (0.81)' },
  { type: 'tone', target: 'warm + personal', reason: 'Cat photo book context' },
  { type: 'send_time', target: '8:00 AM CT', reason: 'Optimal engagement window' },
  { type: 'channel', target: 'email', reason: 'Preferred channel on record' },
]

const FALLBACK_SIGNALS: Signal[] = [
  { signal: 'frequency_cap', value: 'breach', weight: 1.0 },
  { signal: 'cart_propensity', value: '0.81', weight: 0.9 },
  { signal: 'seasonal_propensity', value: '0.34', weight: 0.3 },
  { signal: 'support_tickets', value: 'none recent', weight: 0.0 },
]

const typeColors: Record<string, string> = {
  suppress_from: 'bg-[var(--color-status-suppressed)]/15 text-[var(--color-status-suppressed)] border-[var(--color-status-suppressed)]/30',
  prioritize_in: 'bg-[var(--color-status-triggered)]/15 text-[var(--color-status-triggered)] border-[var(--color-status-triggered)]/30',
  tone: 'bg-[var(--color-status-active)]/15 text-[var(--color-status-active)] border-[var(--color-status-active)]/30',
  send_time: 'bg-[var(--color-gold)]/15 text-[var(--color-gold)] border-[var(--color-gold)]/30',
  channel: 'bg-purple-500/15 text-purple-400 border-purple-500/30',
}

export default function DecisionPanel({ verdict, decisions, signals }: DecisionPanelProps) {
  const rows = decisions && decisions.length > 0 ? decisions : FALLBACK_DECISIONS
  const sigs = signals && signals.length > 0 ? signals : FALLBACK_SIGNALS
  const displayVerdict = verdict ?? 're-prioritize'

  return (
    <div className="flex flex-col h-full">
      <p className="text-[10px] font-bold tracking-widest text-muted-foreground mb-3">DECISION</p>

      {/* Verdict */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="flex items-center gap-2 bg-[var(--color-status-triggered)]/10 border border-[var(--color-status-triggered)]/30 rounded-xl px-4 py-3 mb-4"
      >
        <CheckCircle2 size={18} className="text-[var(--color-status-triggered)] shrink-0" />
        <div>
          <p className="text-[10px] font-bold tracking-widest text-[var(--color-status-triggered)]/70 uppercase">Verdict</p>
          <p className="font-serif text-lg text-[var(--color-status-triggered)] leading-tight">{displayVerdict}</p>
        </div>
      </motion.div>

      {/* Decision rows */}
      <div className="flex flex-col gap-2 mb-4">
        {rows.map((d, i) => (
          <motion.div
            key={`${d.type}-${i}`}
            initial={{ opacity: 0, x: 12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.1 + i * 0.08 }}
            className="flex items-start gap-2 bg-card border border-border rounded-lg p-2.5"
          >
            <span
              className={`inline-flex shrink-0 items-center border text-[10px] font-bold tracking-wider px-1.5 py-0.5 rounded-full whitespace-nowrap ${typeColors[d.type] ?? 'bg-muted text-muted-foreground border-border'}`}
            >
              {d.type}
            </span>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-card-foreground truncate">{d.target}</p>
              <p className="text-[11px] text-muted-foreground leading-snug">{d.reason}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Contributing signals */}
      <div>
        <div className="flex items-center gap-1.5 mb-2">
          <TrendingUp size={11} className="text-[var(--color-gold)]" />
          <p className="text-[10px] font-bold tracking-widest text-muted-foreground">SIGNALS</p>
        </div>
        <div className="flex flex-col gap-1.5">
          {sigs.map((s, i) => (
            <motion.div
              key={s.signal}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.25, delay: 0.5 + i * 0.06 }}
              className="flex items-center justify-between gap-2"
            >
              <span className="text-[11px] text-muted-foreground font-mono truncate">{s.signal}</span>
              <div className="flex items-center gap-1.5 shrink-0">
                <span className="text-[11px] text-card-foreground">{s.value}</span>
                <span
                  className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                    s.weight >= 0.8
                      ? 'bg-[var(--color-status-suppressed)]/15 text-[var(--color-status-suppressed)]'
                      : s.weight >= 0.5
                      ? 'bg-[var(--color-gold)]/15 text-[var(--color-gold)]'
                      : 'bg-muted text-muted-foreground'
                  }`}
                >
                  {s.weight.toFixed(1)}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
