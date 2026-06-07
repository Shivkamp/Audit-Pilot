# Members Page — Design Override
Inherits from `design-system/MASTER.md`.

## Route
`/workspaces/:workspaceId/members`

## Page Header
- Title: "Workspace Members"
- Subtitle: "Manage who has access to this workspace"
- Right action: "Add Member" button (primary sky) — only shown when `canManageMembers(role) = true`

## Role Source
`useMyWorkspaceRole(workspaceId)` → falls back to `useAuth().currentWorkspaceRole`

## Permission Notice
- Viewers see `PermissionDeniedCard`:
  - Message: "Only workspace owners and admins can manage members. You can view the member list."
  - requiredRoles: ['owner', 'admin']
- Notice shown above table (viewer can still VIEW members)

## Member Table
- Columns: Member, Role, Added (hidden md), Actions (hidden if !canManage)
- Member column: avatar initials circle (bg-sky-700, white text, w-7 h-7) + full_name + email below + "(you)" tag if self
- Role: `RoleBadge` component (owner=violet, admin=sky, editor=amber, viewer=slate)
- Actions:
  - "Change Role" (text-sky-700) — only if `canManage && member.role !== 'owner' && !isSelf`
  - "Remove" (text-red-600) — only if `canManage && member.role !== 'owner' && !isSelf`
  - Owners are always non-editable (no actions shown for owner row)
  - Self rows are not removable/editable via UI (prevents accidental self-removal)

## Dialogs

### AddMemberDialog
- Modal via Headless UI or manual fixed overlay
- Fields: Email (text, required, email format), Role (select: admin/editor/viewer — NOT owner)
- Submit: calls `useAddMember(workspaceId).mutateAsync({email, role})`
- On success: `setShowAddDialog(false)`, query invalidation happens in hook
- RHF + Zod validation

### UpdateMemberRoleDialog
- Pre-fills with current role (defaults to 'admin' if current role is 'owner' to avoid re-assigning owner)
- Role options: admin/editor/viewer
- Submit: calls `useUpdateMemberRole`
- On success: `setEditMember(null)`

### Remove Confirm Dialog
- Uses `ConfirmDialog` variant="danger"
- Title: "Remove Member"
- Description: "Remove [name] from this workspace? They will lose access immediately."

## Empty State
- Icon: `Users`
- Title: "No members yet"
- Body: "Add team members to collaborate on this workspace."
- Action: "Add Member" button shown if canManage

## Self-Removal
Hook `useRemoveMember` already invalidates `['myWorkspaceRole', workspaceId]`.
After self-removal, `setCurrentWorkspace(workspaceId, null)` is called from page to clear auth context.
