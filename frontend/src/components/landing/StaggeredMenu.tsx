import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { useNavigate } from 'react-router-dom'

interface MenuItem {
  label: string
  ariaLabel?: string
  link: string
}

interface SocialItem {
  label: string
  link: string
}

interface StaggeredMenuProps {
  position?: 'left' | 'right'
  items: MenuItem[]
  socialItems?: SocialItem[]
  displaySocials?: boolean
  displayItemNumbering?: boolean
  menuButtonColor?: string
  openMenuButtonColor?: string
  changeMenuColorOnOpen?: boolean
  colors?: string[]
  accentColor?: string
  onMenuOpen?: () => void
  onMenuClose?: () => void
  className?: string
}

const EASE_EXPO: [number, number, number, number] = [0.76, 0, 0.24, 1]
const EASE_OUT_QUINT: [number, number, number, number] = [0.16, 1, 0.3, 1]

export default function StaggeredMenu({
  position = 'right',
  items = [],
  socialItems = [],
  displaySocials = false,
  displayItemNumbering = true,
  menuButtonColor = '#ffffff',
  openMenuButtonColor = '#ffffff',
  changeMenuColorOnOpen = true,
  colors = ['#0F172A', '#2563EB'],
  accentColor = '#2563EB',
  onMenuOpen,
  onMenuClose,
  className = '',
}: StaggeredMenuProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)
  const navigate = useNavigate()

  const toggleMenu = useCallback(() => {
    setIsOpen((prev) => {
      const next = !prev
      if (next) {
        onMenuOpen?.()
        document.body.style.overflow = 'hidden'
      } else {
        onMenuClose?.()
        document.body.style.overflow = ''
      }
      return next
    })
  }, [onMenuOpen, onMenuClose])

  const handleItemClick = useCallback(
    (link: string) => {
      setIsOpen(false)
      document.body.style.overflow = ''
      onMenuClose?.()

      if (link.startsWith('#')) {
        setTimeout(() => {
          document.getElementById(link.slice(1))?.scrollIntoView({ behavior: 'smooth' })
        }, 500)
      } else {
        setTimeout(() => {
          navigate(link)
        }, 400)
      }
    },
    [navigate, onMenuClose],
  )

  const lineColor =
    changeMenuColorOnOpen && isOpen ? openMenuButtonColor : menuButtonColor

  return (
    <>
      {/* Hamburger / Close button */}
      <button
        onClick={toggleMenu}
        className={`relative z-[70] flex flex-col items-center justify-center w-10 h-10 gap-[6px] cursor-pointer ${className}`}
        aria-label={isOpen ? 'Close menu' : 'Open menu'}
        aria-expanded={isOpen}
      >
        <span
          className="block w-6 h-[2px] rounded-full transition-all duration-300 ease-out"
          style={{
            backgroundColor: lineColor,
            transform: isOpen ? 'translateY(8px) rotate(45deg)' : 'none',
          }}
        />
        <span
          className="block w-6 h-[2px] rounded-full transition-all duration-300 ease-out"
          style={{
            backgroundColor: lineColor,
            opacity: isOpen ? 0 : 1,
            transform: isOpen ? 'scaleX(0)' : 'scaleX(1)',
          }}
        />
        <span
          className="block w-6 h-[2px] rounded-full transition-all duration-300 ease-out"
          style={{
            backgroundColor: lineColor,
            transform: isOpen ? 'translateY(-8px) rotate(-45deg)' : 'none',
          }}
        />
      </button>

      {/* Full-screen overlay */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Staggered background layers */}
            {colors.map((color, i) => (
              <motion.div
                key={`bg-${i}`}
                className="fixed inset-0 z-50"
                style={{ backgroundColor: color }}
                initial={{
                  clipPath:
                    position === 'right'
                      ? 'inset(0 0 0 100%)'
                      : 'inset(0 100% 0 0)',
                }}
                animate={{ clipPath: 'inset(0 0 0 0)' }}
                exit={{
                  clipPath:
                    position === 'right'
                      ? 'inset(0 0 0 100%)'
                      : 'inset(0 100% 0 0)',
                }}
                transition={{
                  duration: 0.7,
                  delay: i * 0.08,
                  ease: EASE_EXPO,
                }}
              />
            ))}

            {/* Menu content */}
            <motion.div
              className="fixed inset-0 z-[55] flex"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3, delay: 0.2 }}
            >
              <div
                className={`flex flex-col justify-between w-full h-full px-8 sm:px-16 py-24 ${
                  position === 'right' ? 'items-end text-right' : 'items-start text-left'
                }`}
              >
                {/* Nav items */}
                <nav className="flex flex-col gap-2 sm:gap-3">
                  {items.map((item, i) => (
                    <motion.button
                      key={item.label}
                      initial={{ opacity: 0, y: 50 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{
                        duration: 0.6,
                        delay: 0.3 + i * 0.07,
                        ease: EASE_OUT_QUINT,
                      }}
                      onClick={() => handleItemClick(item.link)}
                      onMouseEnter={() => setHoveredIndex(i)}
                      onMouseLeave={() => setHoveredIndex(null)}
                      aria-label={item.ariaLabel || item.label}
                      className={`flex items-center gap-4 py-2 cursor-pointer group transition-colors duration-200 ${
                        position === 'right' ? 'flex-row-reverse' : 'flex-row'
                      }`}
                    >
                      {displayItemNumbering && (
                        <span className="text-xs font-mono text-white/30 tabular-nums">
                          {String(i + 1).padStart(2, '0')}
                        </span>
                      )}
                      <span
                        className="text-3xl sm:text-5xl lg:text-6xl font-bold text-white transition-colors duration-200"
                        style={{
                          color: hoveredIndex === i ? accentColor : undefined,
                        }}
                      >
                        {item.label}
                      </span>
                    </motion.button>
                  ))}
                </nav>

                {/* Social links */}
                {displaySocials && socialItems.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.5, delay: 0.5, ease: EASE_OUT_QUINT }}
                    className={`flex gap-6 ${
                      position === 'right' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {socialItems.map((social) => (
                      <a
                        key={social.label}
                        href={social.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-white/40 hover:text-white transition-colors duration-200"
                      >
                        {social.label}
                      </a>
                    ))}
                  </motion.div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
