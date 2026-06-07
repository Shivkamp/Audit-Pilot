import { useRef, useState, useCallback } from 'react'
import { motion, useReducedMotion } from 'motion/react'

interface BentoCardProps {
  children: React.ReactNode
  className?: string
  /** Span multiple columns: 1 or 2 */
  colSpan?: 1 | 2
  /** Span multiple rows: 1 or 2 */
  rowSpan?: 1 | 2
  /** Enable spotlight cursor-following effect */
  enableSpotlight?: boolean
  /** Spotlight radius in pixels */
  spotlightRadius?: number
  /** RGB string for glow color, e.g. "37, 99, 235" */
  glowColor?: string
  /** Enable border glow effect */
  enableBorderGlow?: boolean
}

export function BentoCard({
  children,
  className = '',
  colSpan = 1,
  rowSpan = 1,
  enableSpotlight = true,
  spotlightRadius = 350,
  glowColor = '37, 99, 235',
  enableBorderGlow = true,
}: BentoCardProps) {
  const cardRef = useRef<HTMLDivElement>(null)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const [isHovered, setIsHovered] = useState(false)
  const prefersReduced = useReducedMotion()

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (prefersReduced || !cardRef.current) return
      const rect = cardRef.current.getBoundingClientRect()
      setMousePos({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      })
    },
    [prefersReduced],
  )

  const spanClass =
    (colSpan === 2 ? 'sm:col-span-2' : '') +
    (rowSpan === 2 ? ' sm:row-span-2' : '')

  return (
    <motion.div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      initial={{ opacity: 0, y: prefersReduced ? 0 : 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className={`relative rounded-2xl overflow-hidden ${spanClass} ${className}`}
      style={{
        background: 'rgba(15, 23, 42, 0.6)',
        border: '1px solid rgba(255, 255, 255, 0.06)',
      }}
    >
      {/* Spotlight gradient */}
      {enableSpotlight && isHovered && !prefersReduced && (
        <div
          className="absolute inset-0 pointer-events-none z-0 transition-opacity duration-300"
          style={{
            background: `radial-gradient(${spotlightRadius}px circle at ${mousePos.x}px ${mousePos.y}px, rgba(${glowColor}, 0.08) 0%, transparent 100%)`,
          }}
        />
      )}

      {/* Border glow */}
      {enableBorderGlow && isHovered && !prefersReduced && (
        <div
          className="absolute inset-0 pointer-events-none z-0 rounded-2xl"
          style={{
            background: `radial-gradient(${spotlightRadius * 0.6}px circle at ${mousePos.x}px ${mousePos.y}px, rgba(${glowColor}, 0.15) 0%, transparent 100%)`,
            mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            maskComposite: 'exclude',
            WebkitMaskComposite: 'xor',
            padding: '1px',
          }}
        />
      )}

      {/* Content */}
      <div className="relative z-[1] h-full">{children}</div>
    </motion.div>
  )
}

interface BentoGridProps {
  children: React.ReactNode
  className?: string
}

export function BentoGrid({ children, className = '' }: BentoGridProps) {
  return (
    <div
      className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 ${className}`}
    >
      {children}
    </div>
  )
}
