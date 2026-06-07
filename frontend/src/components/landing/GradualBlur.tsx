import { useMemo } from 'react'

interface GradualBlurProps {
  position?: 'top' | 'bottom'
  height?: string
  strength?: number
  divCount?: number
  curve?: 'linear' | 'bezier' | 'ease-in'
  exponential?: boolean
  opacity?: number
  target?: 'parent' | 'page'
  className?: string
  style?: React.CSSProperties
}

export default function GradualBlur({
  position = 'bottom',
  height = '6rem',
  strength = 2,
  divCount = 5,
  curve = 'linear',
  exponential = false,
  opacity = 1,
  target = 'parent',
  className = '',
  style = {},
}: GradualBlurProps) {
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

  return (
    <div
      className={className}
      style={{
        position: target === 'page' ? 'fixed' : 'absolute',
        [position]: 0,
        left: 0,
        right: 0,
        height,
        pointerEvents: 'none',
        zIndex: 10,
        ...style,
      }}
    >
      {layers.map((layer, i) => {
        const clipPath =
          position === 'bottom'
            ? `inset(${layer.clipStart}% 0 ${100 - layer.clipEnd}% 0)`
            : `inset(${100 - layer.clipEnd}% 0 ${layer.clipStart}% 0)`

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              inset: 0,
              backdropFilter: `blur(${layer.blur}px)`,
              WebkitBackdropFilter: `blur(${layer.blur}px)`,
              clipPath,
              opacity,
            }}
          />
        )
      })}
    </div>
  )
}
