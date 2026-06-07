import React, { useRef, useEffect, useState, useCallback } from 'react'

interface ScrollStackProps {
  children: React.ReactNode
  className?: string
  scrollBudgetVh?: number  // accepted for prop compat, unused
  itemDistance?: number    // accepted for prop compat, unused
  stackOffset?: number
  baseScale?: number
}

export function ScrollStack({
  children,
  className = '',
  stackOffset = 20,
  baseScale = 0.92,
}: ScrollStackProps) {
  const items = React.Children.toArray(children)
  const containerRef = useRef<HTMLDivElement>(null)
  const itemRefs = useRef<(HTMLDivElement | null)[]>([])
  const [scales, setScales] = useState<number[]>(items.map(() => 1))

  const handleScroll = useCallback(() => {
    if (!containerRef.current) return
    const newScales = itemRefs.current.map((el, i) => {
      if (!el) return 1
      const rect = el.getBoundingClientRect()
      const stickyTop = window.innerHeight * 0.15 + i * stackOffset
      if (rect.top <= stickyTop + 2) {
        const stackedAfter = itemRefs.current.slice(i + 1).filter((next) => {
          if (!next) return false
          const nr = next.getBoundingClientRect()
          return nr.top <= window.innerHeight * 0.15 + (itemRefs.current.indexOf(next)) * stackOffset + 2
        }).length
        return Math.max(baseScale, 1 - stackedAfter * (1 - baseScale))
      }
      return 1
    })
    setScales(newScales)
  }, [stackOffset, baseScale])

  useEffect(() => {
    window.addEventListener('scroll', handleScroll, { passive: true })
    handleScroll()
    return () => window.removeEventListener('scroll', handleScroll)
  }, [handleScroll])

  return (
    <div ref={containerRef} className={className}>
      {items.map((child, i) => (
        <div
          key={i}
          ref={(el) => { itemRefs.current[i] = el }}
          className="sticky transition-transform duration-300 ease-out"
          style={{
            top: `calc(15vh + ${i * stackOffset}px)`,
            marginBottom: i < items.length - 1 ? 20 : 0,
            zIndex: i + 1,
            transform: `scale(${scales[i]})`,
            transformOrigin: 'top center',
          }}
        >
          {child}
        </div>
      ))}
    </div>
  )
}

export function ScrollStackItem({
  children,
  className = '',
}: {
  children: React.ReactNode
  className?: string
}) {
  return <div className={className}>{children}</div>
}
