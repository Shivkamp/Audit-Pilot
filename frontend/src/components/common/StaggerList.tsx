import { type ReactNode } from 'react'
import { motion, useReducedMotion } from 'motion/react'
import { staggerItem, staggerItemTransition } from '../../lib/animation'

interface StaggerListProps {
  children: ReactNode
  className?: string
  as?: 'div' | 'ul' | 'ol'
  staggerDelay?: number
}

/**
 * Staggers entrance of children.
 * Reduced-motion safe: disables stagger animation, children just fade in.
 */
export function StaggerList({
  children,
  className,
  as: Tag = 'div',
  staggerDelay = 0.06,
}: StaggerListProps) {
  const prefersReduced = useReducedMotion() ?? false

  if (prefersReduced) {
    // No stagger — just render directly
    const El = Tag
    return <El className={className}>{children}</El>
  }

  const containerVariants = {
    animate: {
      transition: {
        staggerChildren: staggerDelay,
        delayChildren: 0.04,
      },
    },
  }

  return (
    <motion.div
      initial="initial"
      animate="animate"
      variants={containerVariants}
      className={className}
    >
      {children}
    </motion.div>
  )
}

interface StaggerItemProps {
  children: ReactNode
  className?: string
}

/**
 * Child item of StaggerList.
 */
export function StaggerItem({ children, className }: StaggerItemProps) {
  const prefersReduced = useReducedMotion() ?? false

  if (prefersReduced) {
    return <div className={className}>{children}</div>
  }

  return (
    <motion.div
      variants={staggerItem}
      transition={staggerItemTransition}
      className={className}
    >
      {children}
    </motion.div>
  )
}
