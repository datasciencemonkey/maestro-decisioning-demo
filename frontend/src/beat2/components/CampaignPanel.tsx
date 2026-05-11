import { motion, AnimatePresence } from 'framer-motion'
import { XCircle, Star, Circle, Pause } from 'lucide-react'

type CampaignStatus = 'suppressed' | 'prioritized' | 'active' | 'triggered' | 'paused' | 'dormant'

interface Campaign {
  name: string
  campaign_id: string
  status: CampaignStatus
}

const statusConfig: Record<CampaignStatus, { label: string; color: string; icon: React.ReactNode; glow?: boolean }> = {
  suppressed: {
    label: 'SUPPRESSED',
    color: 'bg-red-500/15 text-red-400 border-red-500/30',
    icon: <XCircle size={11} />,
  },
  prioritized: {
    label: 'PRIORITY',
    color: 'bg-green-500/15 text-green-400 border-green-500/30',
    icon: <Star size={11} className="fill-green-400" />,
    glow: true,
  },
  active: {
    label: 'ACTIVE',
    color: 'bg-[var(--color-gold)]/15 text-[var(--color-gold)] border-[var(--color-gold)]/30',
    icon: <Circle size={11} className="fill-current" />,
  },
  triggered: {
    label: 'TRIGGERED',
    color: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
    icon: <Circle size={11} className="fill-current" />,
  },
  paused: {
    label: 'PAUSED',
    color: 'bg-muted text-muted-foreground border-border',
    icon: <Pause size={11} />,
  },
  dormant: {
    label: 'DORMANT',
    color: 'bg-muted text-muted-foreground border-border',
    icon: <Circle size={11} />,
  },
}

const FALLBACK_CAMPAIGNS: Campaign[] = [
  { name: 'Spring Seasonal Promo', campaign_id: 'campaign_sp_2026', status: 'suppressed' },
  { name: 'Abandoned Cart Recovery', campaign_id: 'campaign_ac_2026', status: 'prioritized' },
  { name: 'VIP Loyalty Reward', campaign_id: 'campaign_vip_2026', status: 'active' },
  { name: 'Re-engagement Series', campaign_id: 'campaign_re_2026', status: 'dormant' },
]

export default function CampaignPanel({ campaigns }: { campaigns?: Campaign[] }) {
  const list = campaigns && campaigns.length > 0 ? campaigns : FALLBACK_CAMPAIGNS

  return (
    <div className="flex flex-col gap-1 h-full">
      <p className="text-[10px] font-bold tracking-widest text-muted-foreground mb-3">CAMPAIGNS</p>
      <AnimatePresence mode="popLayout">
        {list.map((c, i) => {
          const cfg = statusConfig[c.status] ?? statusConfig.dormant
          return (
            <motion.div
              key={c.campaign_id}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -12 }}
              transition={{ duration: 0.35, delay: i * 0.08 }}
              className={`relative rounded-lg border p-3 ${
                cfg.glow
                  ? 'border-green-500/40 shadow-[0_0_12px_rgba(34,197,94,0.15)]'
                  : 'border-border'
              } bg-card`}
            >
              {cfg.glow && (
                <motion.div
                  className="absolute inset-0 rounded-lg bg-green-500/5"
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              )}
              <div className="relative flex items-start justify-between gap-2">
                <p
                  className={`text-xs font-medium leading-snug ${
                    c.status === 'suppressed' ? 'line-through text-muted-foreground' : 'text-card-foreground'
                  }`}
                >
                  {c.name}
                </p>
                <span
                  className={`inline-flex items-center gap-1 shrink-0 border text-[10px] font-bold tracking-wider px-1.5 py-0.5 rounded-full ${cfg.color}`}
                >
                  {cfg.icon}
                  {cfg.label}
                </span>
              </div>
              <p className="relative text-[10px] text-muted-foreground font-mono mt-1">{c.campaign_id}</p>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}
