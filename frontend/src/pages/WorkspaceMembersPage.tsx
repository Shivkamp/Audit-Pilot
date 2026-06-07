import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Users, UserPlus } from 'lucide-react'
import { PageHeader } from '../components/common/PageHeader'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingState } from '../components/common/LoadingState'
import { ErrorState } from '../components/common/ErrorState'
import { ConfirmDialog } from '../components/common/ConfirmDialog'
import { PermissionDeniedCard } from '../components/common/PermissionDeniedCard'
import { RoleBadge } from '../components/common/RoleBadge'
import { AddMemberDialog } from '../components/members/AddMemberDialog'
import { UpdateMemberRoleDialog } from '../components/members/UpdateMemberRoleDialog'
import {
  useWorkspaceMembers,
  useRemoveMember,
} from '../hooks/useWorkspaceMembers'
import { useMyWorkspaceRole } from '../hooks/useMyWorkspaceRole'
import { useAuth } from '../hooks/useAuth'
import { canManageMembers } from '../lib/auth/permissions'
import { formatDate } from '../lib/utils'
import type { WorkspaceMember } from '../types/workspaceMember'

export function WorkspaceMembersPage() {
  const { workspaceId = '' } = useParams<{ workspaceId: string }>()
  const { currentUser, currentWorkspaceRole, setCurrentWorkspace } = useAuth()
  const { role: derivedRole } = useMyWorkspaceRole(workspaceId)
  const role = derivedRole ?? currentWorkspaceRole

  const { data: members, isLoading, error, refetch } = useWorkspaceMembers(workspaceId)
  const removeMember = useRemoveMember(workspaceId)

  const [showAddDialog, setShowAddDialog] = useState(false)
  const [editMember, setEditMember] = useState<WorkspaceMember | null>(null)
  const [removeTarget, setRemoveTarget] = useState<WorkspaceMember | null>(null)

  const canManage = canManageMembers(role)

  // Hydrate role from real membership data when members load
  useEffect(() => {
    if (!workspaceId || !members || !currentUser) return
    const me = members.find((m) => m.user_id === currentUser.id)
    if (me && me.role !== currentWorkspaceRole) {
      setCurrentWorkspace(workspaceId, me.role)
    }
  }, [workspaceId, members, currentUser, currentWorkspaceRole, setCurrentWorkspace])

  const handleRemoveConfirm = () => {
    if (!removeTarget) return
    const isSelf = removeTarget.user_id === currentUser?.id
    removeMember.mutate(removeTarget.id, {
      onSuccess: () => {
        setRemoveTarget(null)
        if (isSelf) {
          // Removing ourselves — clear role
          setCurrentWorkspace(workspaceId, null)
        }
      },
    })
  }

  const getMemberName = (member: WorkspaceMember) =>
    member.user?.full_name ?? member.user?.email ?? 'Unknown'

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <PageHeader
        title="Workspace Members"
        subtitle="Manage who has access to this workspace"
        actions={
          canManage ? (
            <button
              onClick={() => setShowAddDialog(true)}
              className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              <UserPlus className="w-4 h-4" />
              Add Member
            </button>
          ) : undefined
        }
      />

      {!canManage && role !== null && (
        <PermissionDeniedCard
          message="Only workspace owners and admins can manage members. You can view the member list."
          requiredRoles={['owner', 'admin']}
          className="mb-4"
        />
      )}

      {isLoading && <LoadingState />}
      {!!error && <ErrorState error={error as Error} onRetry={() => refetch()} className="mb-4" />}

      {!isLoading && !error && members?.length === 0 && (
        <EmptyState
          icon={<Users className="w-12 h-12" />}
          title="No members yet"
          body="Add team members to collaborate on this workspace."
          action={
            canManage ? (
              <button
                onClick={() => setShowAddDialog(true)}
                className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer"
              >
                <UserPlus className="w-4 h-4" />
                Add Member
              </button>
            ) : undefined
          }
        />
      )}

      {!isLoading && members && members.length > 0 && (
        <div className="overflow-hidden border border-slate-200 rounded-xl bg-white shadow-card">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Member</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">Role</th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">Added</th>
                {canManage && (
                  <th scope="col" className="px-4 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">Actions</th>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {members.map((member) => {
                const isSelf = member.user_id === currentUser?.id
                const isOwner = member.role === 'owner'
                // Admins cannot modify owners; and you can't change your own role here
                const canEdit = canManage && !isOwner && !isSelf
                const canRemove = canManage && !isOwner && !isSelf

                return (
                  <tr key={member.id} className="hover:bg-slate-50 transition-colors duration-100">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2.5">
                        <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-semibold flex-shrink-0 select-none">
                          {getMemberName(member)
                            .split(' ')
                            .map((p) => p[0])
                            .join('')
                            .slice(0, 2)
                            .toUpperCase()}
                        </div>
                        <div>
                          <p className="font-medium text-slate-900">
                            {getMemberName(member)}
                            {isSelf && (
                              <span className="ml-1.5 text-xs text-slate-400">(you)</span>
                            )}
                          </p>
                          {member.user?.full_name && (
                            <p className="text-xs text-slate-500">{member.user.email}</p>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <RoleBadge role={member.role} />
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500 hidden md:table-cell">
                      {formatDate(member.created_at)}
                    </td>
                    {canManage && (
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end gap-2">
                          {canEdit && (
                            <button
                              onClick={() => setEditMember(member)}
                              className="text-xs font-medium text-blue-600 hover:text-blue-800 cursor-pointer"
                            >
                              Change Role
                            </button>
                          )}
                          {canRemove && (
                            <button
                              onClick={() => setRemoveTarget(member)}
                              className="text-xs font-medium text-red-600 hover:text-red-700 cursor-pointer"
                            >
                              Remove
                            </button>
                          )}
                        </div>
                      </td>
                    )}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      <AddMemberDialog
        workspaceId={workspaceId}
        open={showAddDialog}
        onClose={() => setShowAddDialog(false)}
      />

      {editMember && (
        <UpdateMemberRoleDialog
          workspaceId={workspaceId}
          memberId={editMember.id}
          memberName={getMemberName(editMember)}
          currentRole={editMember.role}
          open={!!editMember}
          onClose={() => setEditMember(null)}
        />
      )}

      <ConfirmDialog
        open={!!removeTarget}
        title="Remove Member"
        description={removeTarget ? `Remove ${getMemberName(removeTarget)} from this workspace? They will lose access immediately.` : ''}
        confirmLabel="Remove"
        variant="danger"
        isLoading={removeMember.isPending}
        onConfirm={handleRemoveConfirm}
        onCancel={() => setRemoveTarget(null)}
      />
    </div>
  )
}
