import { useEffect, useRef } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { X } from 'lucide-react'
import { LoadingSpinner } from '../common/LoadingState'

const workspaceSchema = z.object({
  name: z.string().min(1, 'Name is required').max(200, 'Name too long'),
  financial_year: z.string().trim().min(1, 'Financial Year is required').max(20),
  assessment_year: z.string().max(20).optional().or(z.literal('')),
})

export type WorkspaceFormData = z.infer<typeof workspaceSchema>

interface WorkspaceFormProps {
  open: boolean
  defaultValues?: Partial<WorkspaceFormData>
  isLoading?: boolean
  onClose: () => void
  onSubmit: (data: WorkspaceFormData) => void
}

export function WorkspaceForm({
  open,
  defaultValues,
  isLoading = false,
  onClose,
  onSubmit,
}: WorkspaceFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<WorkspaceFormData>({
    resolver: zodResolver(workspaceSchema),
    defaultValues: { name: '', financial_year: '', assessment_year: '', ...defaultValues },
  })

  useEffect(() => {
    if (open) {
      reset({ name: '', financial_year: '', assessment_year: '', ...defaultValues })
    }
  }, [open, defaultValues, reset])

  const titleRef = useRef<HTMLHeadingElement>(null)
  useEffect(() => {
    if (open) setTimeout(() => titleRef.current?.focus(), 0)
  }, [open])

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
      aria-labelledby="workspace-form-title"
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
            id="workspace-form-title"
            ref={titleRef}
            tabIndex={-1}
            className="text-lg font-semibold text-slate-900 outline-none"
          >
            {isEdit ? 'Edit Workspace' : 'New Workspace'}
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
            <label className="block text-sm font-medium text-slate-700 mb-1" htmlFor="wf-name">
              Workspace Name <span className="text-red-500" aria-hidden="true">*</span>
            </label>
            <input
              id="wf-name"
              type="text"
              placeholder="e.g. FY 2024-25 TDS Audit"
              {...register('name')}
              className="w-full px-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            />
            {errors.name && (
              <p className="mt-1 text-xs text-red-500" role="alert">{errors.name.message}</p>
            )}
          </div>

          {/* Financial Year */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1" htmlFor="wf-fy">
              Financial Year <span className="text-red-500" aria-hidden="true">*</span>
            </label>
            <input
              id="wf-fy"
              type="text"
              placeholder="e.g. 2024-25"
              {...register('financial_year')}
              className="w-full px-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            />
            {errors.financial_year && (
              <p className="mt-1 text-xs text-red-500" role="alert">{errors.financial_year.message}</p>
            )}
          </div>

          {/* Assessment Year */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1" htmlFor="wf-ay">
              Assessment Year{' '}
              <span className="text-slate-400 font-normal">(optional)</span>
            </label>
            <input
              id="wf-ay"
              type="text"
              placeholder="e.g. 2025-26"
              {...register('assessment_year')}
              className="w-full px-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            />
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
              {isEdit ? 'Save Changes' : 'Create Workspace'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
