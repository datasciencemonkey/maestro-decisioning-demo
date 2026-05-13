import { motion } from 'framer-motion'
import { Clock, AlertTriangle, CheckCircle } from 'lucide-react'
import CustomerCard from './CustomerCard'

interface ToolCall {
  tool: string
  icon: string
  output: string
  highlight?: 'warn' | 'ok'
}

interface ReasoningTraceProps {
  toolCalls?: ToolCall[]
  rationale?: string
  latency?: number
}

const TOOL_ICONS: Record<string, string> = {
  read_profile: '👤',
  read_cart: '🛒',
  check_production_feasibility: '🏭',
  list_active_campaigns: '📢',
  check_frequency_cap: '⚠️',
  score_propensity: '📊',
  optimal_send_time: '⏰',
  persist_journey_state: '💾',
}

const FALLBACK_TOOLS: ToolCall[] = [
  { tool: 'read_profile', icon: '👤', output: 'Cindy · Gold · tabby kitten Whiskers' },
  { tool: 'read_cart', icon: '🛒', output: '"Welcome Home" photo book · $42 · abandoned' },
  { tool: 'list_active_campaigns', icon: '📢', output: '4 active: Spring Seasonal, Cart Recovery, VIP, Re-engage' },
  { tool: 'check_frequency_cap', icon: '⚠️', output: 'BREACH — 2/week cap reached', highlight: 'warn' },
  { tool: 'score_propensity', icon: '📊', output: 'cart_recovery: 0.81 · seasonal: 0.34', highlight: 'ok' },
  { tool: 'optimal_send_time', icon: '⏰', output: '8:00 AM CT · email channel' },
  { tool: 'persist_journey_state', icon: '💾', output: 'journey_id: jrn_88241_ac · persisted' },
]

export default function ReasoningTrace({ toolCalls, rationale, latency }: ReasoningTraceProps) {
  const tools = toolCalls && toolCalls.length > 0 ? toolCalls : FALLBACK_TOOLS

  return (
    <div className="flex flex-col h-full">
      <CustomerCard />

      <div className="flex items-center justify-between mb-3">
        <p className="text-[10px] font-bold tracking-widest text-muted-foreground">AGENT REASONING</p>
        {latency != null && (
          <span className="inline-flex items-center gap-1 bg-muted text-muted-foreground text-[10px] px-2 py-0.5 rounded-full">
            <Clock size={10} />
            {latency.toFixed(1)}s
          </span>
        )}
      </div>

      {/* Tool call timeline */}
      <div className="relative flex flex-col gap-0">
        <div className="absolute left-[18px] top-3 bottom-3 w-px bg-border" />
        {tools.map((t, i) => (
          <motion.div
            key={`${t.tool}-${i}`}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: i * 0.12 }}
            className="relative flex items-start gap-3 py-2"
          >
            {/* Icon node */}
            <div
              className={`relative z-10 w-9 h-9 shrink-0 rounded-full flex items-center justify-center text-base border ${
                t.highlight === 'warn'
                  ? 'bg-[var(--color-status-suppressed)]/10 border-[var(--color-status-suppressed)]/40'
                  : t.highlight === 'ok'
                  ? 'bg-[var(--color-status-triggered)]/10 border-[var(--color-status-triggered)]/30'
                  : 'bg-card border-border'
              }`}
            >
              {t.icon || TOOL_ICONS[t.tool] || '🔧'}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0 pt-1.5">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-semibold text-card-foreground font-mono">{t.tool}</span>
                {t.highlight === 'warn' && (
                  <AlertTriangle size={11} className="text-[var(--color-status-suppressed)]" />
                )}
                {t.highlight === 'ok' && (
                  <CheckCircle size={11} className="text-[var(--color-status-triggered)]" />
                )}
              </div>
              <p
                className={`text-[11px] mt-0.5 ${
                  t.highlight === 'warn'
                    ? 'text-[var(--color-status-suppressed)] font-semibold'
                    : t.highlight === 'ok'
                    ? 'text-[var(--color-status-triggered)]'
                    : 'text-muted-foreground'
                }`}
              >
                {t.output}
              </p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Rationale block */}
      {rationale && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: tools.length * 0.12 + 0.1 }}
          className="mt-4 bg-[var(--color-gold)]/8 border border-[var(--color-gold)]/20 rounded-xl p-4"
        >
          <p className="text-[10px] font-bold tracking-widest text-[var(--color-gold)] mb-2">RATIONALE</p>
          <p className="text-xs text-card-foreground leading-relaxed">{rationale}</p>
        </motion.div>
      )}
    </div>
  )
}
