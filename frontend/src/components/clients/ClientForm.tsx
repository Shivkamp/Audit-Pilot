import { useEffect, useRef } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { X } from 'lucide-react'
import { LoadingSpinner } from '../common/LoadingState'

const clientSchema = z.object({
  name: z.string().min(1, 'Name is required').max(200, 'Name too long'),
  pan: z
    .string()
    .max(10, 'PAN must be 10 characters')
    .optional()
    .or(z.literal('')),
  gstin: z
    .string()
    .max(15, 'GSTIN must be 15 characters')
    .optional()
    .or(z.literal('')),
})

export type ClientFormData = z.infer<typeof clientSchema>

interface ClientFormProps {
  open: boolean
  defaultValues?: Partial<ClientFormData>
  isLoading?: boolean
  onClose: () => void
  onSubmit: (data: ClientFormData) => void
}

export function ClientForm({
  open,
  defaultValues,
  isLoading = false,
  onClose,
  onSubmit,
}: ClientFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ClientFormData>({
    resolver: zodResolver(clientSchema),
    defaultValues: { name: '', pan: '', gstin: '', ...defaultValues },
  })

  // Re-populate form when defaultValues change (edit mode)
  useEffect(() => {
    if (open) {
      reset({ name: '', pan: '', gstin: '', ...defaultValues })
    }
  }, [open, defaultValues, reset])

  const titleRef = useRef<HTMLHeadingElement>(null)
  useEffect(() => {
    if (open) setTimeout(() => titleRef.current?.focus(), 0)
  }, [open])

  // Close on Escape
  useEffect(() => {
    if (!open) return
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [open, onClose])

  if (!open) return null

  const isEdit = !!(defaultValues?.name)

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="client-form-title"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/30 backdrop-blur-[2px]"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="relative bg-white rounded-2xl shadow-drawer w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between px-6 pt-5 pb-4 border-b border-slate-100">
          <h2
            id="client-form-title"
            ref={titleRef}
            tabIndex={-1}
            className="text-lg font-semibold text-slate-900 outline-none"
          >
            {isEdit ? 'Edit Client' : 'New Client'}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="px-6 py-5 space-y-4" noValidate>
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1" htmlFor="cf-name">
              Client Name <span className="text-red-500" aria-hidden="true">*</span>
            </label>
            <input
              id="cf-name"
              type="text"
              autoComplete="organization"
              placeholder="e.g. Acme Corp"
              {...register('name')}
              className="w-full px-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            />
            {errors.name && (
              <p className="mt-1 text-xs text-red-500" role="alert">{errors.name.message}</p>
            )}
          </div>

          {/* PAN */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1" htmlFor="cf-pan">
              PAN{' '}
              <span className="text-slate-400 font-normal">(optional)</span>
            </label>
            <input
              id="cf-pan"
              type="text"
              placeholder="e.g. ABCDE1234F"
              {...register('pan')}
              className="w-full px-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors uppercase"
            />
            {errors.pan && (
              <p className="mt-1 text-xs text-red-500" role="alert">{errors.pan.message}</p>
            )}
          </div>

          {/* GSTIN */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1" htmlFor="cf-gstin">
              GSTIN{' '}
              <span className="text-slate-400 font-normal">(optional)</span>
            </label>
            <input
              id="cf-gstin"
              type="text"
              placeholder="e.g. 22AAAAA0000A1Z5"
              {...register('gstin')}
              className="w-full px-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors uppercase"
            />
            {errors.gstin && (
              <p className="mt-1 text-xs text-red-500" role="alert">{errors.gstin.message}</p>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 pt-2 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 bg-white border border-slate-200 hover:border-slate-300 rounded-xl transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex items-center gap-2 px-5 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              {isLoading && <LoadingSpinner className="w-3.5 h-3.5 border-white/30 border-t-white" />}
              {isEdit ? 'Save Changes' : 'Create Client'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
