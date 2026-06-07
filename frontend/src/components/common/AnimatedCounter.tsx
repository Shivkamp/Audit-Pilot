import { useEffect, useRef, useState } from 'react'
import { useReducedMotion } from 'motion/react'

interface AnimatedCounterProps {
  value: number | string | undefined | null
  /** Placeholder shown when value is not yet loaded */
  placeholder?: string
  /** Duration of the count animation in ms */
  duration?: number
  /** Optional suffix like '+' or '%' */
  suffix?: string
  className?: string
}

/**
 * Animated count-up number display.
 * - If value is a string or undefined/null, shows as-is with a subtle fade.
 * - If value is a number, animates from previous value to new value.
 * - Respects prefers-reduced-motion: no animation if reduced motion preferred.
 */
export function AnimatedCounter({
  value,
  placeholder = '—',
  duration = 600,
  suffix = '',
  className,
}: AnimatedCounterProps) {
  const prefersReduced = useReducedMotion() ?? false
  const [displayValue, setDisplayValue] = useState<number | string>(
    typeof value === 'number' ? 0 : (value ?? placeholder),
  )
  const frameRef = useRef<number | null>(null)
  const startTimeRef = useRef<number | null>(null)
  const startValueRef = useRef<number>(0)
  const targetRef = useRef<number>(0)

  useEffect(() => {
    if (value == null) {
      setDisplayValue(placeholder)
      return
    }
    if (typeof value === 'string') {
      setDisplayValue(value)
      return
    }

    if (prefersReduced) {
      setDisplayValue(value)
      return
    }

    const from = typeof displayValue === 'number' ? displayValue : 0
    startValueRef.current = from
    targetRef.current = value
    startTimeRef.current = null

    if (frameRef.current != null) cancelAnimationFrame(frameRef.current)

    const animate = (timestamp: number) => {
      if (startTimeRef.current == null) startTimeRef.current = timestamp
      const elapsed = timestamp - startTimeRef.current
      const progress = Math.min(elapsed / duration, 1)
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      const current = Math.round(startValueRef.current + (targetRef.current - startValueRef.current) * eased)
      setDisplayValue(current)

      if (progress < 1) {
        frameRef.current = requestAnimationFrame(animate)
      }
    }

    frameRef.current = requestAnimationFrame(animate)

    return () => {
      if (frameRef.current != null) cancelAnimationFrame(frameRef.current)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value, prefersReduced])

  const shown = displayValue === placeholder ? placeholder : `${displayValue}${suffix}`

  return (
    <span
      className={className}
      aria-live="polite"
      aria-atomic="true"
    >
      {shown}
    </span>
  )
}
