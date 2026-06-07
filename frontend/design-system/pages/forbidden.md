# Forbidden / 403 UX — Design Reference

## Two-Level Forbidden System

### 1. Full-Page: `ForbiddenState`
Used when an entire page is inaccessible.

- Background: full `min-h-screen` gray-50
- Center card: white rounded-xl shadow, max-w-md
- Icon: `ShieldX` (Lucide), text-red-400, w-12 h-12
- Title: bold, dark slate
- Message: text-sm text-slate-600
- Optional "Required roles" row with role badges
- Optional "Go back" ghost button

### 2. Inline: `PermissionDeniedCard`
Used when a section (not full page) is restricted.

- Amber card: bg-amber-50 border border-amber-200 rounded-xl p-4
- Icon: `Lock` (Lucide) w-4 h-4 text-amber-600
- Heading + message (text-sm)
- Optional "Requires:" role list in text-xs text-amber-700

### 3. Tiny: `RoleRequiredNotice`
Used inline as a note near disabled buttons.

- Small text: "Requires: Owner · Admin" in text-xs text-slate-500
- Useful for tooltips or below-button notes

## 403 Behavior Rules
- **403 does NOT log out the user** (user is authenticated; just not authorized for this action)
- Display `ForbiddenState` or `PermissionDeniedCard` depending on scope
- The API interceptor should only log out on **401 Unauthorized**, not 403

## 401 Behavior Rules
- **401 Always logs out** and redirects to `/login`
- Auth context clears token
- Handled in global `apiClient` request interceptor

## Examples
| Scenario | Component |
|----------|-----------|
| User navigates to workspace they are NOT a member of | `ForbiddenState` on the route |
| Viewer visits Documents page (can view, can't upload) | `PermissionDeniedCard` in upload section |
| Viewer visits Jobs page (can view, can't retry) | `PermissionDeniedCard` above table |
| Viewer visits Members page (can view, can't manage) | `PermissionDeniedCard` above table |
| User not logged in hits any route | Redirect → `/login` (401 behavior) |
