/**
 * Animation primitives for AuditPilot
 * Enterprise-grade, reduced-motion-safe defaults.
 * All durations in seconds (Motion for React convention).
 */

// ─── Duration constants ───────────────────────────────────────────────────────
export const DURATION = {
  micro: 0.12,
  fast: 0.18,
  normal: 0.22,
  enter: 0.30,
  drawer: 0.22,
  chat: 0.18,
  counter: 0.8,
} as const

// ─── Easing presets ──────────────────────────────────────────────────────────
export const EASE = {
  enterprise: [0.16, 1, 0.3, 1] as [number, number, number, number],
  standard: [0.4, 0, 0.2, 1] as [number, number, number, number],
  decelerate: [0, 0, 0.2, 1] as [number, number, number, number],
  spring: { type: 'spring' as const, stiffness: 400, damping: 30 },
} as const

// ─── Page / route transition ─────────────────────────────────────────────────
export const pageVariants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -4 },
}

export const pageTransition = {
  duration: DURATION.normal,
  ease: EASE.enterprise,
}

// Reduced-motion version: opacity only
export const pageVariantsReduced = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
}

export const pageTransitionReduced = {
  duration: DURATION.fast,
  ease: EASE.standard,
}

// ─── Card entrance ───────────────────────────────────────────────────────────
export const cardVariants = {
  initial: { opacity: 0, y: 6 },
  animate: { opacity: 1, y: 0 },
}

export const cardTransition = {
  duration: DURATION.normal,
  ease: EASE.enterprise,
}

// ─── Stagger children ────────────────────────────────────────────────────────
export const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.06,
      delayChildren: 0.05,
    },
  },
}

export const staggerItem = {
  initial: { opacity: 0, y: 6 },
  animate: { opacity: 1, y: 0 },
}

export const staggerItemTransition = {
  duration: DURATION.normal,
  ease: EASE.enterprise,
}

// ─── Drawer / slide-in panel ─────────────────────────────────────────────────
export const drawerVariants = {
  initial: { opacity: 0, x: 24 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 24 },
}

export const drawerTransition = {
  duration: DURATION.drawer,
  ease: EASE.enterprise,
}

export const drawerVariantsReduced = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
}

// ─── Modal overlay ───────────────────────────────────────────────────────────
export const overlayVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
}

export const overlayTransition = {
  duration: DURATION.fast,
  ease: EASE.standard,
}

// ─── Modal dialog content ────────────────────────────────────────────────────
export const dialogVariants = {
  initial: { opacity: 0, scale: 0.96, y: 4 },
  animate: { opacity: 1, scale: 1, y: 0 },
  exit: { opacity: 0, scale: 0.96, y: 4 },
}

export const dialogTransition = {
  duration: DURATION.normal,
  ease: EASE.enterprise,
}

// ─── Chat message ────────────────────────────────────────────────────────────
export const chatMessageVariants = {
  initial: { opacity: 0, y: 6 },
  animate: { opacity: 1, y: 0 },
}

export const chatMessageTransition = {
  duration: DURATION.chat,
  ease: EASE.enterprise,
}

// ─── Fade only ───────────────────────────────────────────────────────────────
export const fadeVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
}

export const fadeTransition = {
  duration: DURATION.fast,
  ease: EASE.standard,
}

// ─── Button tap feedback ─────────────────────────────────────────────────────
export const buttonTap = { scale: 0.97 } as const

// ─── Animated card hover ─────────────────────────────────────────────────────
export const cardHover = {
  y: -2,
  transition: { duration: DURATION.fast, ease: EASE.enterprise },
}

// ─── Utility: pick reduced vs full variant based on prefersReducedMotion ──────
export function getPageVariants(prefersReducedMotion: boolean) {
  return {
    variants: prefersReducedMotion ? pageVariantsReduced : pageVariants,
    transition: prefersReducedMotion ? pageTransitionReduced : pageTransition,
  }
}

export function getDrawerVariants(prefersReducedMotion: boolean) {
  return {
    variants: prefersReducedMotion ? drawerVariantsReduced : drawerVariants,
    transition: prefersReducedMotion ? { duration: DURATION.fast } : drawerTransition,
  }
}
