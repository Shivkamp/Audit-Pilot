import { useMemo, useEffect, useState } from 'react'

interface ScrollingBlurProps {
  height?: string
  strength?: number
  divCount?: number
  curve?: 'linear' | 'bezier' | 'ease-in'
  exponential?: boolean
  /** Distance from the page bottom (px) at which the blur starts fading out */
  footerHeight?: number
}

export default function ScrollingBlur({
  height = '10rem',
  strength = 4,
  divCount = 6,
  curve = 'bezier',
  exponential = false,
  footerHeight = 200,
}: ScrollingBlurProps) {
  const [opacity, setOpacity] = useState(1)

  useEffect(() => {
    const handleScroll = () => {
      const scrollBottom = document.documentElement.scrollHeight - window.innerHeight - window.scrollY
      if (scrollBottom < footerHeight) {
        setOpacity(Math.max(0, scrollBottom / footerHeight))
      } else {
        setOpacity(1)
      }
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    handleScroll()
    return () => window.removeEventListener('scroll', handleScroll)
  }, [footerHeight])

  const layers = useMemo(() => {
    return Array.from({ length: divCount }, (_, i) => {
      const t = divCount === 1 ? 1 : i / (divCount - 1)
      let progress: number
      if (exponential) {
        progress = Math.pow(t, 2)
      } else if (curve === 'bezier') {
        progress = t * t * (3 - 2 * t)
      } else if (curve === 'ease-in') {
        progress = t * t
      } else {
        progress = t
      }
      const blur = progress * strength * 4
      const clipStart = (i / divCount) * 100
      const clipEnd = ((i + 1) / divCount) * 100
      return { blur, clipStart, clipEnd }
    })
  }, [divCount, strength, curve, exponential])

  if (opacity <= 0) return null

  return (
    <div
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        height,
        pointerEvents: 'none',
        zIndex: 30,
        opacity,
        transition: 'opacity 0.2s ease-out',
      }}
    >
      {layers.map((layer, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            inset: 0,
            backdropFilter: `blur(${layer.blur}px)`,
            WebkitBackdropFilter: `blur(${layer.blur}px)`,
            clipPath: `inset(${layer.clipStart}% 0 ${100 - layer.clipEnd}% 0)`,
          }}
        />
      ))}
    </div>
  )
}
