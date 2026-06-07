import { useRef, useEffect } from 'react'
import { X } from 'lucide-react'
import { motion, AnimatePresence, useReducedMotion } from 'motion/react'
import { cn } from '../../lib/utils'
import { LoadingSpinner } from './LoadingState'
import {
  overlayVariants, overlayTransition,
  dialogVariants, dialogTransition,
} from '../../lib/animation'

interface ConfirmDialogProps {
  open: boolean
  title: string
  description?: string
  confirmLabel?: string
  cancelLabel?: string
  variant?: 'danger' | 'primary'
  isLoading?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  variant = 'danger',
  isLoading = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const cancelRef = useRef<HTMLButtonElement>(null)
  const prefersReduced = useReducedMotion() ?? false

  useEffect(() => {
    if (open) cancelRef.current?.focus()
  }, [open])

  const dVariants = prefersReduced
    ? { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 } }
    : dialogVariants

  return (
    <AnimatePresence>
      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="confirm-dialog-title"
        >
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-black/30 backdrop-blur-[2px]"
            variants={overlayVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={overlayTransition}
            onClick={onCancel}
          />

          {/* Panel */}
          <motion.div
            className="relative bg-white rounded-2xl shadow-dialog w-full max-w-md p-6 z-10"
            variants={dVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={prefersReduced ? { duration: 0.15 } : dialogTransition}
          >
            <div className="flex items-start justify-between gap-3 mb-3">
              <h2 id="confirm-dialog-title" className="text-base font-semibold text-slate-900">
                {title}
              </h2>
              <button
                onClick={onCancel}
                className="p-1 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer flex-shrink-0"
                aria-label="Close dialog"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {description && (
              <p className="text-sm text-slate-600 mb-5 leading-relaxed">{description}</p>
            )}

            <div className="flex justify-end gap-2">
              <button
                ref={cancelRef}
                onClick={onCancel}
                disabled={isLoading}
                className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
              >
                {cancelLabel}
              </button>
              <button
                onClick={onConfirm}
                disabled={isLoading}
                className={cn(
                  'px-4 py-2 text-sm font-medium text-white rounded-xl transition-colors cursor-pointer disabled:opacity-50 flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-offset-1',
                  variant === 'danger'
                    ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
                    : 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500',
                )}
              >
                {isLoading && <LoadingSpinner className="w-3.5 h-3.5 border-white border-t-transparent" />}
                {confirmLabel}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
