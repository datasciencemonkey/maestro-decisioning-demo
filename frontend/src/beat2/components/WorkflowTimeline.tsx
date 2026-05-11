import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { Brain, Database, Timer, PartyPopper, Play } from 'lucide-react'

type StepState = 'pending' | 'active' | 'done'

interface Step {
  id: string
  label: string
  icon: React.ReactNode
  state: StepState
}

interface WorkflowTimelineProps {
  artifact?: object
}

const INITIAL_STEPS: Step[] = [
  { id: 'agent', label: 'Agent', icon: <Brain size={16} />, state: 'pending' },
  { id: 'persist', label: 'Persist', icon: <Database size={16} />, state: 'pending' },
  { id: 'sleep', label: 'Sleep 15s', icon: <Timer size={16} />, state: 'pending' },
  { id: 'complete', label: 'Complete', icon: <PartyPopper size={16} />, state: 'pending' },
]

export default function WorkflowTimeline({ artifact }: WorkflowTimelineProps) {
  const [steps, setSteps] = useState<Step[]>(INITIAL_STEPS)
  const [running, setRunning] = useState(false)
  const [workflowId, setWorkflowId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Advance local step display based on backend status
  const advanceSteps = (status: string) => {
    setSteps(prev => {
      const next = [...prev]
      if (status === 'PENDING') {
        next[0] = { ...next[0], state: 'done' }
        next[1] = { ...next[1], state: 'done' }
        next[2] = { ...next[2], state: 'active' }
        next[3] = { ...next[3], state: 'pending' }
      } else if (status === 'SUCCESS') {
        return next.map(s => ({ ...s, state: 'done' as StepState }))
      }
      return next
    })
  }

  const startWorkflow = async () => {
    setRunning(true)
    setError(null)
    setSteps(prev => prev.map((s, i) => ({ ...s, state: i === 0 ? 'active' : 'pending' })))

    try {
      const res = await fetch('/api/workflow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision: artifact ?? {}, delay: 15 }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setWorkflowId(data.workflow_id)

      // Mark agent + persist done, sleep active
      setSteps(prev => {
        const next = [...prev]
        next[0] = { ...next[0], state: 'done' }
        next[1] = { ...next[1], state: 'done' }
        next[2] = { ...next[2], state: 'active' }
        return next
      })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to start workflow')
      setRunning(false)
      setSteps(INITIAL_STEPS)
    }
  }

  // Poll for completion once we have a workflowId
  useEffect(() => {
    if (!workflowId) return
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`/api/workflow/${workflowId}`)
        if (!res.ok) return
        const data = await res.json()
        advanceSteps(data.status)
        if (data.status === 'SUCCESS') {
          clearInterval(pollRef.current!)
          setRunning(false)
        }
      } catch {
        // silently retry
      }
    }, 2000)
    return () => { if (pollRef.current) clearInterval(pollRef.current) }
  }, [workflowId])

  const stepBorder = (state: StepState) => {
    if (state === 'active') return 'border-orange-400 shadow-[0_0_12px_rgba(251,146,60,0.35)]'
    if (state === 'done') return 'border-green-500 shadow-[0_0_8px_rgba(34,197,94,0.2)]'
    return 'border-border'
  }

  const stepBg = (state: StepState) => {
    if (state === 'active') return 'bg-orange-500/10 text-orange-400'
    if (state === 'done') return 'bg-green-500/10 text-green-400'
    return 'bg-muted text-muted-foreground'
  }

  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-[10px] font-bold tracking-widest text-muted-foreground">DBOS DURABLE WORKFLOW</p>
          <p className="text-xs text-muted-foreground mt-0.5">Beat 2.5 — persisted execution on Lakebase</p>
        </div>
        {!running ? (
          <button
            onClick={startWorkflow}
            className="inline-flex items-center gap-1.5 bg-[var(--color-gold)] text-[var(--color-espresso)] text-sm font-bold px-4 py-2 rounded-lg hover:bg-[var(--color-gold-light)] transition-colors"
          >
            <Play size={13} />
            Run DBOS Workflow
          </button>
        ) : (
          <span className="text-xs text-muted-foreground animate-pulse">Running…</span>
        )}
      </div>

      {error && (
        <p className="text-xs text-red-400 mb-3">{error}</p>
      )}

      {/* Steps row */}
      <div className="flex items-center gap-2">
        {steps.map((step, i) => (
          <div key={step.id} className="flex items-center gap-2 flex-1 min-w-0">
            <motion.div
              animate={step.state === 'active' ? { scale: [1, 1.06, 1] } : { scale: 1 }}
              transition={{ duration: 1.2, repeat: step.state === 'active' ? Infinity : 0 }}
              className={`flex items-center gap-2 flex-1 min-w-0 border rounded-lg px-3 py-2.5 ${stepBorder(step.state)}`}
            >
              <div className={`shrink-0 ${stepBg(step.state)}`}>
                {step.icon}
              </div>
              <span className={`text-xs font-semibold truncate ${stepBg(step.state)}`}>
                {step.label}
              </span>
              {step.state === 'active' && (
                <span className="ml-auto w-1.5 h-1.5 rounded-full bg-orange-400 animate-pulse shrink-0" />
              )}
              {step.state === 'done' && (
                <span className="ml-auto w-1.5 h-1.5 rounded-full bg-green-400 shrink-0" />
              )}
            </motion.div>
            {i < steps.length - 1 && (
              <span className="text-muted-foreground text-xs shrink-0">→</span>
            )}
          </div>
        ))}
      </div>

      {workflowId && (
        <p className="text-[10px] text-muted-foreground font-mono mt-3">
          workflow_id: {workflowId}
        </p>
      )}
    </div>
  )
}
