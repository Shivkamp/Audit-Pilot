import { type ReactNode } from 'react'
import { motion, useReducedMotion } from 'motion/react'
import { cn } from '../../lib/utils'
import { cardVariants, cardTransition } from '../../lib/animation'

interface AnimatedCardProps {
  children: ReactNode
  className?: string
  delay?: number
  /**
   * When true, adds a lift + shadow-increase hover effect.
   * Disable on data-heavy table rows.
   */
  hoverLift?: boolean
  onClick?: () => void
  as?: 'div' | 'button' | 'li'
}

/**
 * Animated card with entrance animation and optional hover lift.
 * Reduced-motion safe: entrance becomes opacity-only, hover lift is disabled.
 */
export function AnimatedCard({
  children,
  className,
  delay = 0,
  hoverLift = true,
  onClick,
  as: Tag = 'div',
}: AnimatedCardProps) {
  const prefersReduced = useReducedMotion() ?? false

  const motionProps = {
    initial: prefersReduced ? { opacity: 0 } : cardVariants.initial,
    animate: prefersReduced ? { opacity: 1 } : cardVariants.animate,
    transition: prefersReduced
      ? { duration: 0.15, delay }
      : { ...cardTransition, delay },
    whileHover:
      hoverLift && !prefersReduced
        ? { y: -2, transition: { duration: 0.16, ease: [0.16, 1, 0.3, 1] as [number, number, number, number] } }
        : undefined,
    whileTap: onClick ? { scale: 0.98 } : undefined,
    onClick,
    className,
  }

  if (Tag === 'button') {
    return <motion.button {...motionProps}>{children}</motion.button>
  }
  if (Tag === 'li') {
    return <motion.li {...motionProps}>{children}</motion.li>
  }
  return <motion.div {...motionProps}>{children}</motion.div>
}

interface StatsCardProps {
  label: string
  value: ReactNode
  icon?: ReactNode
  iconBg?: string
  trend?: 'up' | 'down' | 'neutral'
  onClick?: () => void
  className?: string
  delay?: number
}

/**
 * Premium stat card for dashboard.
 */
export function StatsCard({
  label,
  value,
  icon,
  iconBg = 'bg-primary-light',
  onClick,
  className,
  delay,
}: StatsCardProps) {
  return (
    <AnimatedCard
      as={onClick ? 'button' : 'div'}
      onClick={onClick}
      delay={delay}
      hoverLift={!!onClick}
      className={cn(
        'bg-white border border-slate-200 rounded-xl p-5 shadow-card text-left w-full',
        onClick && 'cursor-pointer hover:border-blue-300 hover:shadow-card-hover',
        className,
      )}
    >
      {icon && (
        <div className={cn('w-10 h-10 rounded-xl flex items-center justify-center mb-3', iconBg)}>
          {icon}
        </div>
      )}
      <div className="text-2xl font-bold text-slate-900 tabular-nums">{value}</div>
      <div className="text-sm text-slate-500 mt-0.5 font-medium">{label}</div>
    </AnimatedCard>
  )
}
