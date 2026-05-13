import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, Sparkles } from 'lucide-react'
import CampaignPanel from './components/CampaignPanel'
import ReasoningTrace from './components/ReasoningTrace'
import DecisionPanel from './components/DecisionPanel'
import WorkflowTimeline from './components/WorkflowTimeline'
import EmailPreview from './components/EmailPreview'

// ── Phase state machine ───────────────────────────────────────────────────────
type Phase = 'idle' | 'narrative' | 'panels' | 'workflow' | 'email_preview' | 'delivered'

// ── Interfaces ────────────────────────────────────────────────────────────────
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

interface EmailData {
  subject: string
  body_html: string
  hero_image_url: string
  cta_text: string
  cta_url: string
}

// ── Tool call mapping (for ReasoningTrace) ────────────────────────────────────
function mapToolCalls(artifact: Artifact) {
  const tools: Array<{ tool: string; icon: string; output: string; highlight?: 'warn' | 'ok' }> = [
    { tool: 'read_profile',          icon: '👤', output: 'Profile loaded' },
    { tool: 'read_cart',             icon: '🛒', output: 'Cart retrieved' },
    { tool: 'list_active_campaigns', icon: '📢', output: `${artifact.decisions?.length ?? 0} campaigns evaluated` },
  ]

  const freqSig = artifact.contributing_signals?.find(s => s.signal.includes('freq'))
  if (freqSig) {
    tools.push({ tool: 'check_frequency_cap', icon: '⚠️', output: `${freqSig.value} — weight ${freqSig.weight}`, highlight: 'warn' })
  }

  const propSig = artifact.contributing_signals?.find(s => s.signal.includes('prop'))
  if (propSig) {
    tools.push({ tool: 'score_propensity', icon: '📊', output: `${propSig.signal}: ${propSig.value}`, highlight: 'ok' })
  }

  tools.push(
    { tool: 'optimal_send_time',    icon: '⏰', output: 'Send window calculated' },
    { tool: 'persist_journey_state', icon: '💾', output: 'Journey state persisted' },
  )

  return tools
}

// ── Narrative steps with enterprise domain labels ────────────────────────────
const NARRATIVE_STEPS = [
  { icon: '👤', domain: 'Identity Resolution',     text: 'Who are they?',                      detail: 'Loading customer profile — Cindy Chen, gold tier, tabby kitten Whiskers' },
  { icon: '🛒', domain: 'Commerce / Orders',        text: 'What did they leave behind?',         detail: 'Abandoned cart — "Welcome Home, Whiskers" photo book, $42' },
  { icon: '📅', domain: 'Supply Chain',             text: 'Can we still ship it?',              detail: 'Checking production calendar — 4-day turnaround, standard shipping feasible' },
  { icon: '📢', domain: 'Campaign Management',      text: 'What campaigns are they in?',         detail: 'Found 4 active campaigns — Spring Seasonal, Cart Recovery, VIP Loyalty, Reactivation' },
  { icon: '⚠️', domain: 'Contact Policy',           text: 'Would another email breach the cap?', detail: 'Frequency cap: 2/week — current 1, queued 1 (Spring Seasonal) → BREACH' },
  { icon: '🎫', domain: 'Customer Service',         text: 'Any recent complaints?',              detail: 'Support history clean — no open tickets in 30 days' },
  { icon: '📊', domain: 'Predictive Analytics',     text: 'How likely are they to convert?',     detail: 'Propensity score: 0.81 — high confidence for cart recovery' },
  { icon: '⏰', domain: 'Send Optimization',        text: 'When should we reach out?',           detail: 'Optimal send: 8:00 AM CT — adjusted from 11:48 PM (quiet hours)' },
  { icon: '💾', domain: 'Journey Orchestration',    text: 'Lock the decision — durably.',        detail: 'Persisting journey state to Lakebase via DBOS' },
]

// ── AgentNarrative sub-component ─────────────────────────────────────────────
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
        <p className="text-lg font-serif font-semibold text-card-foreground">9 Domains. 1 Decision.</p>
        <p className="text-sm text-muted-foreground mt-2 max-w-lg mx-auto leading-relaxed">
          Watch the agent reason across Identity, Commerce, Supply Chain, Campaign Management,
          Contact Policy, CRM, Predictive Analytics, Send Optimization, and Journey Orchestration
          — in a single pass.
        </p>
      </div>

      {NARRATIVE_STEPS.map((s, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: i <= step ? 1 : 0.15, x: i <= step ? 0 : -20 }}
          transition={{ duration: 0.4 }}
          className={`flex items-start gap-3 p-3 rounded-lg transition-colors ${
            i === step
              ? 'bg-[var(--color-gold)]/10 border border-[var(--color-gold)]/20'
              : i < step
              ? 'bg-card border border-border'
              : ''
          }`}
        >
          <span className="text-lg mt-0.5">{s.icon}</span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className={`text-[10px] font-bold tracking-wider px-1.5 py-0.5 rounded-full border ${
                i === step
                  ? 'bg-[var(--color-databricks-cyan)]/15 text-[var(--color-databricks-cyan)] border-[var(--color-databricks-cyan)]/30'
                  : i < step
                  ? 'bg-muted text-muted-foreground border-border'
                  : 'bg-transparent text-muted-foreground/40 border-transparent'
              }`}>
                {s.domain}
              </span>
              <p className={`text-sm font-medium ${i === step ? 'text-[var(--color-gold)]' : 'text-card-foreground'}`}>
                {s.text}
              </p>
            </div>
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

// ── Main page ─────────────────────────────────────────────────────────────────
export default function Beat2Page() {
  const [phase, setPhase] = useState<Phase>('idle')
  const [workflowId, setWorkflowId] = useState<string | null>(null)
  const [delaySeconds, setDelaySeconds] = useState(17)
  const [artifact, setArtifact] = useState<Artifact | null>(null)
  const [campaigns, setCampaigns] = useState<Campaign[] | null>(null)
  const [latency, setLatency] = useState<number | null>(null)
  const [email, setEmail] = useState<EmailData | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Auto-start unified workflow on mount
  useEffect(() => {
    const startWorkflow = async () => {
      setPhase('narrative')
      try {
        const res = await fetch('/api/workflow', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({}),
        })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        setWorkflowId(data.workflow_id)
        setDelaySeconds(data.delay ?? 17)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Workflow start failed')
        // Narrative still plays; panels will show via /api/run below
      }
    }
    startWorkflow()
  }, [])

  // Fetch agent result via /api/run for immediate panel data in parallel
  useEffect(() => {
    const fetchAgentResult = async () => {
      try {
        const t0 = performance.now()
        const res = await fetch('/api/run', { method: 'POST' })
        if (!res.ok) return
        const json: ApiResponse = await res.json()
        setArtifact(json.artifact)
        setCampaigns(json.campaigns)
        setLatency(json.latency_s ?? (performance.now() - t0) / 1000)

        // Agent data arrived — transition from narrative to panels
        setTimeout(() => setPhase('panels'), 1000)
        // Brief pause, then advance to workflow view
        setTimeout(() => setPhase('workflow'), 3500)
      } catch {
        // Fallback: let narrative finish, then transition
        const narrativeDuration = NARRATIVE_STEPS.length * 3000 + 1000
        setTimeout(() => setPhase('panels'), narrativeDuration)
        setTimeout(() => setPhase('workflow'), narrativeDuration + 3000)
      }
    }
    fetchAgentResult()
  }, [])

  // WorkflowTimeline onComplete callback — fires when all 6 steps are done
  const handleWorkflowComplete = useCallback((_result: Record<string, unknown>) => {
    setEmail({
      subject: 'Whiskers is waiting for their photo book!',
      body_html:
        '<h1>Hi Cindy,</h1>' +
        '<p>We noticed you left something special behind — a "Welcome Home" photo book for Whiskers. ' +
        'As a Gold member, we saved your cart and your $42 photo book is ready to go.</p>' +
        '<p>Whiskers deserves to be celebrated — and free shipping sweetens the deal.</p>',
      hero_image_url: '/whiskers.jpg',
      cta_text: 'Complete Your Order',
      cta_url: 'https://fluttershy.com/cart/resume?cid=cust_88241',
    })
    setPhase('email_preview')
    setTimeout(() => setPhase('delivered'), 3000)
  }, [])

  // ── Visibility derived from phase ─────────────────────────────────────────
  const showNarrative = phase === 'narrative'
  const showPanels    = phase !== 'idle' && phase !== 'narrative'
  const showWorkflow  = phase === 'workflow' || phase === 'email_preview' || phase === 'delivered'
  const showEmail     = phase === 'email_preview' || phase === 'delivered'

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
              <p className="text-sm font-semibold text-card-foreground font-sans">Marketing Ops</p>
              <p className="text-[10px] text-muted-foreground">Unified Beat 2 → 2.5 → 3 — Cross-Campaign Optimization</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {showNarrative && (
              <span className="inline-flex items-center gap-1.5 text-[11px] text-[var(--color-gold)] animate-pulse">
                <Sparkles size={12} />
                Agent reasoning across 9 domains…
              </span>
            )}
            {showPanels && latency != null && (
              <span className="inline-flex items-center gap-1.5 bg-[var(--color-status-triggered)]/10 border border-[var(--color-status-triggered)]/30 text-[var(--color-status-triggered)] text-[11px] px-3 py-1 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-status-triggered)]" />
                Decision ready · {latency.toFixed(1)}s
              </span>
            )}
            {error && (
              <span className="text-[11px]" style={{ color: 'var(--color-status-suppressed)' }}>
                Error: {error}
              </span>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-[1400px] mx-auto px-6 py-6 space-y-5">
        {/* Narrative — plays during agent reasoning */}
        <AnimatePresence>
          {showNarrative && <AgentNarrative />}
        </AnimatePresence>

        {/* 3-panel layout — stays visible through all phases after panels */}
        {showPanels && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="grid grid-cols-1 lg:grid-cols-[240px_1fr_320px] gap-4"
          >
            {/* Left: Campaigns */}
            <div className="bg-card border border-border rounded-xl p-4">
              <CampaignPanel campaigns={campaigns ?? undefined} />
            </div>

            {/* Center: Reasoning trace */}
            <div className="bg-card border border-border rounded-xl p-4 overflow-y-auto max-h-[calc(100vh-180px)]">
              <ReasoningTrace
                toolCalls={toolCalls as Parameters<typeof ReasoningTrace>[0]['toolCalls']}
                rationale={artifact?.rationale}
                latency={latency ?? undefined}
              />
            </div>

            {/* Right: Decision */}
            <div className="bg-card border border-border rounded-xl p-4 overflow-y-auto max-h-[calc(100vh-180px)]">
              <DecisionPanel
                verdict={artifact?.verdict}
                decisions={artifact?.decisions}
                signals={artifact?.contributing_signals}
              />
            </div>
          </motion.div>
        )}

        {/* DBOS workflow pipeline — visible from workflow phase onward */}
        {showWorkflow && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.15 }}
          >
            <WorkflowTimeline
              workflowId={workflowId}
              delaySeconds={delaySeconds}
              onComplete={handleWorkflowComplete}
            />
          </motion.div>
        )}

        {/* Cinematic email reveal — after workflow completes */}
        {showEmail && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <EmailPreview
              email={email ?? undefined}
              visible={showEmail}
              delivered={phase === 'delivered'}
            />
          </motion.div>
        )}
      </main>
    </div>
  )
}
