import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, Sparkles } from 'lucide-react'
import CampaignPanel from './components/CampaignPanel'
import ReasoningTrace from './components/ReasoningTrace'
import DecisionPanel from './components/DecisionPanel'
import WorkflowTimeline from './components/WorkflowTimeline'

interface Campaign {
  name: string
  campaign_id: string
  status: 'suppressed' | 'prioritized' | 'active' | 'triggered' | 'paused' | 'dormant'
}

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

interface Artifact {
  verdict: string
  decisions: DecisionRow[]
  contributing_signals: Signal[]
  rationale: string
}

interface ApiResponse {
  artifact: Artifact
  campaigns: Campaign[]
  latency_s: number
}

// Map backend tool call structure to display format
function mapToolCalls(artifact: Artifact) {
  const iconMap: Record<string, { icon: string; highlight?: 'warn' | 'ok' }> = {
    read_profile: { icon: '👤' },
    read_cart: { icon: '🛒' },
    check_production_feasibility: { icon: '🏭' },
    list_active_campaigns: { icon: '📢' },
    check_frequency_cap: { icon: '⚠️', highlight: 'warn' },
    score_propensity: { icon: '📊', highlight: 'ok' },
    optimal_send_time: { icon: '⏰' },
    persist_journey_state: { icon: '💾' },
  }

  // Build from contributing signals and decisions as proxy for tool calls
  const tools = [
    { tool: 'read_profile', icon: '👤', output: 'Profile loaded' },
    { tool: 'read_cart', icon: '🛒', output: 'Cart retrieved' },
    { tool: 'list_active_campaigns', icon: '📢', output: `${artifact.decisions?.length ?? 0} campaigns evaluated` },
  ]

  // Add frequency cap signal if present
  const freqSig = artifact.contributing_signals?.find(s => s.signal.includes('freq'))
  if (freqSig) {
    tools.push({ tool: 'check_frequency_cap', icon: '⚠️', output: `${freqSig.value} — weight ${freqSig.weight}`, highlight: 'warn' } as typeof tools[0] & { highlight: 'warn' })
  }

  // Add propensity signal
  const propSig = artifact.contributing_signals?.find(s => s.signal.includes('prop'))
  if (propSig) {
    tools.push({ tool: 'score_propensity', icon: '📊', output: `${propSig.signal}: ${propSig.value}`, highlight: 'ok' } as typeof tools[0] & { highlight: 'ok' })
  }

  tools.push(
    { tool: 'optimal_send_time', icon: '⏰', output: 'Send window calculated' },
    { tool: 'persist_journey_state', icon: '💾', output: 'Journey state persisted' },
  )

  return tools
  // Avoid unused warning on iconMap — it's used structurally above
  void iconMap
}

const NARRATIVE_STEPS = [
  { icon: '👤', text: 'Who are they?', detail: 'Loading customer profile — Cindy Chen, gold tier, tabby kitten Whiskers' },
  { icon: '🛒', text: 'What did they leave behind?', detail: 'Abandoned cart — "Welcome Home, Whiskers" photo book, $42' },
  { icon: '📅', text: 'Can we still ship it?', detail: 'Checking production calendar — 4-day turnaround, standard shipping feasible' },
  { icon: '📢', text: 'What campaigns are they in?', detail: 'Found 4 active campaigns — Spring Seasonal, Cart Recovery, VIP Loyalty, Reactivation' },
  { icon: '⚠️', text: 'Would another email breach the cap?', detail: 'Frequency cap: 2/week — current 1, queued 1 (Spring Seasonal) → BREACH' },
  { icon: '🎫', text: 'Any recent complaints?', detail: 'Support history clean — no open tickets in 30 days' },
  { icon: '📊', text: 'How likely are they to convert?', detail: 'Propensity score: 0.81 — high confidence for cart recovery' },
  { icon: '⏰', text: 'When should we reach out?', detail: 'Optimal send: 8:00 AM CT — adjusted from 11:48 PM (quiet hours)' },
  { icon: '💾', text: 'Lock the decision — durably.', detail: 'Persisting journey state to Lakebase via DBOS' },
]

function AgentNarrative() {
  const [step, setStep] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setStep(s => (s < NARRATIVE_STEPS.length - 1 ? s + 1 : s))
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  return (
    <motion.div
      key="narrative"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="max-w-2xl mx-auto py-12 space-y-3"
    >
      <div className="text-center mb-8">
        <p className="text-lg font-serif font-semibold text-card-foreground">
          One decision. Nine domains.
        </p>
        <p className="text-sm text-muted-foreground mt-1">
          Watch the agent think…
        </p>
      </div>

      {NARRATIVE_STEPS.map((s, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -20 }}
          animate={{
            opacity: i <= step ? 1 : 0.15,
            x: i <= step ? 0 : -20,
          }}
          transition={{ duration: 0.4, delay: i <= step ? 0 : 0 }}
          className={`flex items-start gap-3 p-3 rounded-lg transition-colors ${
            i === step
              ? 'bg-[var(--color-gold)]/10 border border-[var(--color-gold)]/20'
              : i < step
              ? 'bg-card border border-border'
              : ''
          }`}
        >
          <span className="text-lg mt-0.5">{s.icon}</span>
          <div>
            <p className={`text-sm font-medium ${
              i === step ? 'text-[var(--color-gold)]' : 'text-card-foreground'
            }`}>
              {s.text}
            </p>
            {i <= step && (
              <motion.p
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="text-xs text-muted-foreground mt-0.5"
              >
                {s.detail}
              </motion.p>
            )}
          </div>
          {i === step && (
            <motion.div
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, repeat: Infinity }}
              className="ml-auto w-2 h-2 rounded-full bg-[var(--color-gold)] mt-2"
            />
          )}
        </motion.div>
      ))}
    </motion.div>
  )
}

export default function Beat2Page() {
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState<ApiResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const run = async () => {
      try {
        const res = await fetch('/api/run', { method: 'POST' })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const json: ApiResponse = await res.json()
        setData(json)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }
    run()
  }, [])

  const artifact = data?.artifact
  const toolCalls = artifact ? mapToolCalls(artifact) : undefined

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-[1400px] mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-[var(--color-gold)]/20 flex items-center justify-center">
              <Brain size={15} className="text-[var(--color-gold)]" />
            </div>
            <div>
              <p className="text-sm font-semibold text-card-foreground">Marketing Ops</p>
              <p className="text-[10px] text-muted-foreground">Beat 2 — Cross-Campaign Optimization</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {loading && (
              <span className="inline-flex items-center gap-1.5 text-[11px] text-[var(--color-gold)] animate-pulse">
                <Sparkles size={12} />
                Agent reasoning across 9 domains…
              </span>
            )}
            {!loading && data && (
              <span className="inline-flex items-center gap-1.5 bg-green-500/10 border border-green-500/30 text-green-400 text-[11px] px-3 py-1 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
                Decision ready · {data.latency_s?.toFixed(1)}s
              </span>
            )}
            {error && (
              <span className="text-[11px] text-red-400">Error: {error} — showing demo data</span>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-[1400px] mx-auto px-6 py-6 space-y-5">
        {/* Narrative loading — shows what the agent is doing step by step */}
        <AnimatePresence>
          {loading && <AgentNarrative />}
        </AnimatePresence>

        {/* 3-panel layout — visible once loaded (or on error, shows fallback data) */}
        {!loading && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="grid grid-cols-1 lg:grid-cols-[240px_1fr_320px] gap-4"
          >
            {/* Left: Campaign Panel */}
            <div className="bg-card border border-border rounded-xl p-4">
              <CampaignPanel campaigns={data?.campaigns} />
            </div>

            {/* Center: Reasoning Trace */}
            <div className="bg-card border border-border rounded-xl p-4 overflow-y-auto max-h-[calc(100vh-180px)]">
              <ReasoningTrace
                toolCalls={toolCalls as Parameters<typeof ReasoningTrace>[0]['toolCalls']}
                rationale={artifact?.rationale}
                latency={data?.latency_s}
              />
            </div>

            {/* Right: Decision Panel */}
            <div className="bg-card border border-border rounded-xl p-4 overflow-y-auto max-h-[calc(100vh-180px)]">
              <DecisionPanel
                verdict={artifact?.verdict}
                decisions={artifact?.decisions}
                signals={artifact?.contributing_signals}
              />
            </div>
          </motion.div>
        )}

        {/* Workflow Timeline */}
        {!loading && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.15 }}
          >
            <WorkflowTimeline workflowId={null} delaySeconds={17} />
          </motion.div>
        )}
      </main>
    </div>
  )
}
