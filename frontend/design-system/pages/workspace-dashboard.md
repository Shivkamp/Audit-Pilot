# Workspace Dashboard Page — Design Override
Inherits from `design-system/MASTER.md`. Overrides listed below.

Route: `/workspaces/:workspaceId`

---

## Layout

- Page padding: `p-6 max-w-7xl mx-auto`
- Workspace info card above action cards
- Section label "Quick Actions" between cards

---

## Workspace Info Card

- Container: `bg-white border border-slate-200 rounded-xl p-5 shadow-sm mb-6`
- Inner layout: `flex flex-wrap gap-x-8 gap-y-4`
- Each field group:
  - Label: `text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1`
  - Value: `text-sm font-medium text-slate-900`
- Fields shown: Status (StatusBadge), Financial Year, Assessment Year, Created date
- Only show optional fields (FY, AY) if they have values

---

## Section Heading

- "Quick Actions": `text-base font-semibold text-slate-900 mb-3`

---

## Action Cards

Grid: `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4`

Each card:
- Container: `bg-white border rounded-xl p-5 text-left transition-all duration-150 cursor-pointer w-full`
- Default: `border-slate-200 hover:border-slate-300 hover:shadow-sm`
- Primary variant: `border-sky-200 hover:border-sky-400 hover:shadow-md`
- Disabled: `opacity-50 cursor-not-allowed border-slate-200`
- Icon container: `w-9 h-9 rounded-lg flex items-center justify-center mb-3`
  - Default bg: `bg-slate-100`, icon: `text-slate-600`
  - Primary bg: `bg-sky-100`, icon: `text-sky-700`
- Label: `text-sm font-semibold text-slate-900`
- Description: `text-xs text-slate-500 mt-0.5`

### Action Cards Defined

| Label | Icon | Route | Variant | Permission |
|-------|------|-------|---------|------------|
| Upload Documents | Upload | /documents | primary | canUploadDocuments |
| Processing Jobs | Briefcase | /jobs | default | (always) |
| Run Risk Check | ShieldAlert | /risks | default | canRunRiskCheck |
| Configure Risk Rules | Settings2 | /settings/risk-rules | default | canConfigureRiskRules |
| Knowledge Search | BookOpen | /knowledge | default | canRebuildKnowledgeIndex |
| Ask AI Agent | Bot | /agent | primary | canUseAgent |
| Manage Members | Users | /members | default | (always) |

---

## Set Current Workspace

- `useEffect(() => { if (workspaceId) setCurrentWorkspace(workspaceId) }, [workspaceId])`
- This ensures sidebar and topbar reflect current workspace even if navigated directly

---

## Loading State

- Show `<LoadingState />` while workspace fetch is in progress
- Once loaded, show full layout

---

## Error/Not Found

- If workspace fetch fails: show `<ErrorState />` with retry
