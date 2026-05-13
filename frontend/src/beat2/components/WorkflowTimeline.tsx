import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, Database, Timer, RefreshCw, Mail, Send } from 'lucide-react'

type StepState = 'pending' | 'active' | 'done' | 'error'

interface Step {
  id: string
  label: string
  icon: React.ReactNode
  state: StepState
}

interface PhaseData {
  status: string
  data?: Record<string, unknown>
}

interface WorkflowTimelineProps {
  workflowId: string | null
  delaySeconds: number
  onPhasesUpdate?: (phases: Record<string, PhaseData>) => void
  onComplete?: (result: Record<string, unknown>) => void
}

const INITIAL_STEPS: Step[] = [
  { id: 'agent',       label: 'Agent',       icon: <Brain size={15} />,     state: 'pending' },
  { id: 'persist',     label: 'Persist',     icon: <Database size={15} />,  state: 'pending' },
  { id: 'sleep',       label: 'Sleep',       icon: <Timer size={15} />,     state: 'pending' },
  { id: 're_evaluate', label: 'Re-evaluate', icon: <RefreshCw size={15} />, state: 'pending' },
  { id: 'email',       label: 'Compose',     icon: <Mail size={15} />,      state: 'pending' },
  { id: 'send',        label: 'Deliver',     icon: <Send size={15} />,      state: 'pending' },
]

// ── Style helpers — use CSS variables throughout ──────────────────────────────

const stepBorderStyle = (state: StepState): React.CSSProperties => {
  if (state === 'active')
    return {
      borderColor: 'var(--color-status-active)',
      boxShadow: '0 0 14px rgba(64,209,245,0.28)',
    }
  if (state === 'done')
    return {
      borderColor: 'var(--color-status-triggered)',
      boxShadow: '0 0 8px rgba(34,197,94,0.18)',
    }
  if (state === 'error')
    return {
      borderColor: 'var(--color-status-suppressed)',
      boxShadow: '0 0 8px rgba(235,22,0,0.18)',
    }
  return {}
}

const stepIconColor = (state: StepState): string => {
  if (state === 'active') return 'var(--color-status-active)'
  if (state === 'done')   return 'var(--color-status-triggered)'
  if (state === 'error')  return 'var(--color-status-suppressed)'
  return 'var(--color-muted-foreground)'
}

const stepLabelColor = (state: StepState): string => stepIconColor(state)

// ── Component ─────────────────────────────────────────────────────────────────

export default function WorkflowTimeline({
  workflowId,
  delaySeconds,
  onPhasesUpdate,
  onComplete,
}: WorkflowTimelineProps) {
  const [steps, setSteps] = useState<Step[]>(INITIAL_STEPS)
  const [countdown, setCountdown] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isDone, setIsDone] = useState(false)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const countdownRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const countdownStarted = useRef(false)

  // Countdown fires when sleep step becomes active
  useEffect(() => {
    const sleepStep = steps.find(s => s.id === 'sleep')
    if (sleepStep?.state === 'active' && !countdownStarted.current) {
      countdownStarted.current = true
      setCountdown(delaySeconds)
      countdownRef.current = setInterval(() => {
        setCountdown(prev => {
          if (prev === null || prev <= 1) {
            if (countdownRef.current) clearInterval(countdownRef.current)
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }
    return () => {
      if (countdownRef.current) clearInterval(countdownRef.current)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [steps])

  // Poll /api/workflow/{id}/phases every 2s when workflowId is set
  useEffect(() => {
    if (!workflowId) return

    // Immediately show agent as active
    setSteps(prev => prev.map((s, i) => ({ ...s, state: i === 0 ? 'active' : 'pending' })))
    setError(null)
    setIsDone(false)
    countdownStarted.current = false

    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`/api/workflow/${workflowId}/phases`)
        if (!res.ok) return
        const data: {
          workflow_id: string
          workflow_status: string
          current_phase: string
          phases: Record<string, PhaseData>
        } = await res.json()

        onPhasesUpdate?.(data.phases)

        setSteps(prev =>
          prev.map(step => {
            const phase = data.phases[step.id]
            if (!phase) return step
            let state: StepState = step.state
            if (phase.status === 'done')        state = 'done'
            else if (phase.status === 'active') state = 'active'
            return { ...step, state }
          })
        )

        if (data.current_phase === 'done' || data.workflow_status === 'SUCCESS') {
          if (pollRef.current) clearInterval(pollRef.current)
          setSteps(prev => prev.map(s => ({ ...s, state: 'done' })))
          setIsDone(true)
          onComplete?.(data as unknown as Record<string, unknown>)
        } else if (
          data.workflow_status === 'ERROR' ||
          data.workflow_status === 'RETRIES_EXCEEDED'
        ) {
          if (pollRef.current) clearInterval(pollRef.current)
          setError('Workflow error — check server logs')
        }
      } catch {
        // silently retry
      }
    }, 2000)

    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [workflowId, onPhasesUpdate, onComplete])

  const sleepProgress = isDone
    ? 100
    : countdown !== null && delaySeconds > 0
      ? ((delaySeconds - countdown) / delaySeconds) * 100
      : 0

  const sleepStep = steps.find(s => s.id === 'sleep')
  const sleepVisible =
    !isDone &&
    (sleepStep?.state === 'active') &&
    countdown !== null

  return (
    <div
      className="rounded-xl border p-5"
      style={{ background: 'var(--color-card)', borderColor: 'var(--color-border)' }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <p
            className="text-[10px] font-bold tracking-[0.15em] uppercase"
            style={{ color: 'var(--color-muted-foreground)' }}
          >
            DBOS Durable Workflow
          </p>
          <p className="text-xs mt-0.5" style={{ color: 'var(--color-muted-foreground)' }}>
            Durable execution on Lakebase
          </p>
        </div>

        {workflowId && !isDone && (
          <motion.span
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 1.6, repeat: Infinity }}
            className="text-[11px]"
            style={{ color: 'var(--color-status-active)' }}
          >
            Running…
          </motion.span>
        )}
        {isDone && (
          <span
            className="text-[11px] font-semibold"
            style={{ color: 'var(--color-status-triggered)' }}
          >
            Complete
          </span>
        )}
      </div>

      {/* Error banner */}
      {error && (
        <p className="text-xs mb-3" style={{ color: 'var(--color-status-suppressed)' }}>
          {error}
        </p>
      )}

      {/* 6-step pipeline */}
      <div className="flex items-center gap-1">
        {steps.map((step, i) => (
          <div key={step.id} className="flex items-center gap-1 flex-1 min-w-0">
            <motion.div
              animate={step.state === 'active' ? { scale: [1, 1.04, 1] } : { scale: 1 }}
              transition={{
                duration: 1.4,
                repeat: step.state === 'active' ? Infinity : 0,
                ease: 'easeInOut',
              }}
              className="flex flex-col items-center gap-1 flex-1 min-w-0 border rounded-lg px-1.5 py-2.5"
              style={{
                borderColor: 'var(--color-border)',
                ...stepBorderStyle(step.state),
              }}
            >
              {/* Icon */}
              <div style={{ color: stepIconColor(step.state) }}>{step.icon}</div>

              {/* Label — shows live countdown during sleep */}
              <span
                className="text-[9px] font-bold tracking-wide truncate w-full text-center"
                style={{ color: stepLabelColor(step.state) }}
              >
                {step.id === 'sleep' && step.state === 'active' && countdown !== null
                  ? `${countdown}s`
                  : step.label}
              </span>

              {/* State dot */}
              {step.state === 'active' && (
                <motion.span
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1, repeat: Infinity }}
                  className="w-1.5 h-1.5 rounded-full shrink-0"
                  style={{ background: 'var(--color-status-active)' }}
                />
              )}
              {step.state === 'done' && (
                <span
                  className="w-1.5 h-1.5 rounded-full shrink-0"
                  style={{ background: 'var(--color-status-triggered)' }}
                />
              )}
              {step.state === 'pending' && (
                <span
                  className="w-1.5 h-1.5 rounded-full shrink-0 opacity-20"
                  style={{ background: 'var(--color-muted-foreground)' }}
                />
              )}
            </motion.div>

            {/* Arrow connector */}
            {i < steps.length - 1 && (
              <span
                className="text-[9px] shrink-0"
                style={{ color: 'var(--color-muted-foreground)' }}
              >
                →
              </span>
            )}
          </div>
        ))}
      </div>

      {/* Sleep progress bar — shown during and right after sleep step */}
      <AnimatePresence>
        {sleepVisible && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="mt-3 overflow-hidden"
          >
            <div className="flex items-center justify-between mb-1">
              <span
                className="text-[10px]"
                style={{ color: 'var(--color-muted-foreground)' }}
              >
                Optimal send window: 8:00 AM CT
              </span>
              {countdown !== null && countdown > 0 && (
                <span
                  className="text-[10px] font-mono"
                  style={{ color: 'var(--color-gold)' }}
                >
                  {countdown}s remaining
                </span>
              )}
            </div>

            <div
              className="h-1 rounded-full overflow-hidden"
              style={{ background: 'var(--color-muted)' }}
            >
              <motion.div
                className="h-full rounded-full"
                style={{ background: 'var(--color-gold)' }}
                initial={{ width: '0%' }}
                animate={{ width: `${sleepProgress}%` }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Workflow ID — mono, subtle */}
      {workflowId && (
        <p
          className="text-[10px] font-mono mt-3 truncate"
          style={{ color: 'var(--color-muted-foreground)' }}
        >
          workflow_id: {workflowId}
        </p>
      )}
    </div>
  )
}
