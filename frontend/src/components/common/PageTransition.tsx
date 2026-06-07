import { type ReactNode } from 'react'
import { motion, useReducedMotion } from 'motion/react'
import { getPageVariants } from '../../lib/animation'

interface PageTransitionProps {
  children: ReactNode
  className?: string
}

/**
 * Wraps page-level content in a subtle fade+slide entrance animation.
 * Respects prefers-reduced-motion: falls back to opacity-only fade.
 */
export function PageTransition({ children, className }: PageTransitionProps) {
  const prefersReduced = useReducedMotion() ?? false
  const { variants, transition } = getPageVariants(prefersReduced)

  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={variants}
      transition={transition}
      className={className}
    >
      {children}
    </motion.div>
  )
}

interface FadeInProps {
  children: ReactNode
  className?: string
  delay?: number
  duration?: number
}

/**
 * Simple fade-in wrapper. Reduced-motion safe.
 */
export function FadeIn({ children, className, delay = 0, duration = 0.22 }: FadeInProps) {
  const prefersReduced = useReducedMotion() ?? false

  return (
    <motion.div
      initial={{ opacity: 0, y: prefersReduced ? 0 : 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: prefersReduced ? 0.15 : duration,
        delay,
        ease: [0.16, 1, 0.3, 1],
      }}
      className={className}
    >
      {children}
    </motion.div>
  )
}
