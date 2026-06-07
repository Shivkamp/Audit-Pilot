# Workspaces Page — Design Override
Inherits from `design-system/MASTER.md`. Overrides listed below.

Route: `/clients/:clientId/workspaces`

---

## Layout

- Page padding: `p-6 max-w-7xl mx-auto`
- Breadcrumb link above PageHeader: `flex items-center gap-1.5 text-sm text-slate-500 hover:text-sky-700 mb-5 cursor-pointer` with ArrowLeft icon + "Back to Clients"
- PageHeader: title = client name, subtitle = tagline
- Table below header

---

## Table

- Same container style as Clients page
- Columns: Name, Financial Year (`hidden md:table-cell`), Assessment Year (`hidden md:table-cell`), Status (`hidden sm:table-cell`), Created (`hidden lg:table-cell`), Actions
- Name: link style (same as clients)
- FY/AY: `text-sm text-slate-500` — show "—" if null
- Status badge: same as clients

### Action Buttons (per row)

| Button | Style |
|--------|-------|
| Open Workspace | ExternalLink icon + "Open" — same as clients Open |
| Edit | Pencil icon — same as clients Edit |
| Archive | Trash2 icon — same as clients Deactivate |

---

## Create / Edit Modal

- Same structure as ClientForm
- Panel max-width: `max-w-md`
- Fields: Name (required), Financial Year (optional, placeholder "2024-25"), Assessment Year (optional, placeholder "2025-26")

---

## Confirm Dialog (Archive)

- Title: `Archive "{workspace.name}"?`
- Description: "This workspace will be archived. Existing documents and findings will be preserved."
- Variant: `danger`
- Confirm label: `Archive`

---

## Empty State

- Icon: FolderOpen (w-12 h-12)
- Title: "No workspaces yet"
- Body: "Create a workspace to start uploading documents and running risk checks."
- CTA: New Workspace button (primary)

---

## Financial Year / Assessment Year Format

- Display format: `2024-25`, `2025-26`
- Input: plain text, placeholder shows example
- No validation beyond string length

---

## Current Workspace Selection

When user clicks "Open Workspace":
1. `setCurrentWorkspace(workspace.id)` called
2. `navigate('/workspaces/:id')` called
3. Topbar + sidebar update to reflect current workspace
