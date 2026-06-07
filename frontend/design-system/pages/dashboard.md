# Dashboard Page — Design Override
Inherits from `design-system/MASTER.md`. Overrides listed below.

## Layout

- Page padding: `p-6` inside AppShell main content
- Stats row: `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 mb-8`
- Quick action section below stats

## Stat Cards

- Background: `bg-white border border-slate-200 rounded-lg p-5 shadow-sm`
- Icon container: `w-10 h-10 rounded-lg flex items-center justify-center` (bg varies by type)
- Metric value: `text-2xl font-bold text-slate-900 mt-3`
- Metric label: `text-sm text-slate-500`
- Icon colors per card type:
  - Clients: `bg-sky-100 text-sky-700`
  - Documents: `bg-violet-100 text-violet-700`
  - Risk Findings: `bg-red-100 text-red-600`
  - Jobs: `bg-amber-100 text-amber-600`

## Quick Actions

- Section heading: "Quick Actions" `text-lg font-semibold text-slate-900 mb-4`
- Button row: `flex flex-wrap gap-3`
- Buttons use Secondary variant with icon

## Empty State

- When no workspace is selected: show centered guidance card
- Title: "Select or create a workspace to begin"
- CTA: "Go to Clients" button

## Skeleton Loading

- Stat card skeletons: same grid, each `bg-slate-200 animate-pulse rounded-lg h-24`
