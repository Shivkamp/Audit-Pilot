import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { X, UserPlus } from 'lucide-react'
import { LoadingSpinner } from '../common/LoadingState'
import { useAddMember } from '../../hooks/useWorkspaceMembers'

const schema = z.object({
  email: z.string().trim().email('Enter a valid email address'),
  role: z.enum(['admin', 'editor', 'viewer'], {
    required_error: 'Select a role',
  }),
})

type FormValues = z.infer<typeof schema>

interface AddMemberDialogProps {
  workspaceId: string
  open: boolean
  onClose: () => void
}

export function AddMemberDialog({ workspaceId, open, onClose }: AddMemberDialogProps) {
  const addMember = useAddMember(workspaceId)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { role: 'viewer' },
  })

  useEffect(() => {
    if (!open) reset()
  }, [open, reset])

  const onSubmit = async (values: FormValues) => {
    await addMember.mutateAsync({ email: values.email, role: values.role })
    onClose()
    reset()
  }

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="add-member-title"
    >
      <div className="absolute inset-0 bg-black/30 backdrop-blur-[2px]" onClick={onClose} />

      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-md p-6 z-10">
        <div className="flex items-start justify-between gap-3 mb-5">
          <div className="flex items-center gap-2.5">
            <UserPlus className="w-4 h-4 text-slate-500" />
            <h2 id="add-member-title" className="text-base font-semibold text-slate-900">
              Add Member
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          <div>
            <label htmlFor="member-email" className="block text-sm font-medium text-slate-700 mb-1">
              Email address <span className="text-red-500">*</span>
            </label>
            <input
              id="member-email"
              type="email"
              autoComplete="off"
              placeholder="colleague@example.com"
              className="w-full px-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              {...register('email')}
            />
            {errors.email && (
              <p className="mt-1 text-xs text-red-600" role="alert">
                {errors.email.message}
              </p>
            )}
          </div>

          <div>
            <label htmlFor="member-role" className="block text-sm font-medium text-slate-700 mb-1">
              Role <span className="text-red-500">*</span>
            </label>
            <select
              id="member-role"
              className="w-full px-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              {...register('role')}
            >
              <option value="viewer">Viewer — read-only access</option>
              <option value="editor">Editor — can upload and process documents</option>
              <option value="admin">Admin — full access except ownership transfer</option>
            </select>
            {errors.role && (
              <p className="mt-1 text-xs text-red-600" role="alert">
                {errors.role.message}
              </p>
            )}
          </div>

          <p className="text-xs text-slate-500">
            The user must already have an account. Owner role must be assigned at workspace creation.
          </p>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={addMember.isPending}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={addMember.isPending}
              className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {addMember.isPending && <LoadingSpinner className="w-3.5 h-3.5 border-white border-t-transparent" />}
              Add Member
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
