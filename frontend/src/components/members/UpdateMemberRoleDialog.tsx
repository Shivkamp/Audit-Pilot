import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { X } from 'lucide-react'
import { LoadingSpinner } from '../common/LoadingState'
import { useUpdateMemberRole } from '../../hooks/useWorkspaceMembers'
import type { WorkspaceRole } from '../../types/workspaceMember'

const schema = z.object({
  role: z.enum(['admin', 'editor', 'viewer'], {
    required_error: 'Select a role',
  }),
})

type FormValues = z.infer<typeof schema>

interface UpdateMemberRoleDialogProps {
  workspaceId: string
  memberId: string
  memberName: string
  currentRole: WorkspaceRole
  open: boolean
  onClose: () => void
}

export function UpdateMemberRoleDialog({
  workspaceId,
  memberId,
  memberName,
  currentRole,
  open,
  onClose,
}: UpdateMemberRoleDialogProps) {
  const updateRole = useUpdateMemberRole(workspaceId)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      role: currentRole === 'owner' ? 'admin' : currentRole,
    },
  })

  useEffect(() => {
    if (open) {
      reset({ role: currentRole === 'owner' ? 'admin' : currentRole })
    }
  }, [open, currentRole, reset])

  const onSubmit = async (values: FormValues) => {
    await updateRole.mutateAsync({ memberId, data: { role: values.role } })
    onClose()
  }

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="update-role-title"
    >
      <div className="absolute inset-0 bg-black/30 backdrop-blur-[2px]" onClick={onClose} />

      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-sm p-6 z-10">
        <div className="flex items-start justify-between gap-3 mb-5">
          <h2 id="update-role-title" className="text-base font-semibold text-slate-900">
            Update Role
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <p className="text-sm text-slate-600 mb-4">
          Changing role for <strong className="text-slate-900">{memberName}</strong>.
        </p>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          <div>
            <label htmlFor="update-role" className="block text-sm font-medium text-slate-700 mb-1">
              New Role
            </label>
            <select
              id="update-role"
              className="w-full px-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              {...register('role')}
            >
              <option value="viewer">Viewer</option>
              <option value="editor">Editor</option>
              <option value="admin">Admin</option>
            </select>
            {errors.role && (
              <p className="mt-1 text-xs text-red-600" role="alert">
                {errors.role.message}
              </p>
            )}
          </div>

          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              disabled={updateRole.isPending}
              className="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={updateRole.isPending}
              className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {updateRole.isPending && (
                <LoadingSpinner className="w-3.5 h-3.5 border-white border-t-transparent" />
              )}
              Update Role
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
