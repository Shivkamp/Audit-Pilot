# Risk Rule Settings Page — Design Override
Inherits from `design-system/MASTER.md`. Overrides listed below.

## Page Header

- Title: "Risk Rule Configuration"
- Subtitle: "Customize thresholds and rules for this workspace"
- Right actions: 
  - "Initialize Rules" Secondary button (owner/admin only)
  - "Reset to Defaults" Danger ghost button (owner/admin only)

## Permission Gate

- Entire mutation UI (edit, initialize, reset) requires owner/admin role
- Viewer/editor: read-only, buttons hidden/disabled
- Show PermissionGate banner: "You need owner or admin role to edit risk rules."

## Rule Cards

- Grid: `grid grid-cols-1 lg:grid-cols-2 gap-4`
- Each card: `bg-white border border-slate-200 rounded-lg p-5 shadow-sm`
- Rule name: `text-base font-semibold text-slate-900`
- Rule description: `text-sm text-slate-500 mt-1`
- Threshold fields: inline number input with unit label
- Enabled toggle: standard checkbox or toggle switch (CSS only)
- Save button per card: Primary sm button (owner/admin only)

## Empty State

- Icon: `Settings2`
- Title: "No risk rules configured"
- Body: "Initialize rules to customize risk detection thresholds"
- CTA: "Initialize Rules" (owner/admin only)
