# Risk Findings Page — Design Override
Inherits from `design-system/MASTER.md`. Overrides listed below.

## Page Header

- Title: "Risk Findings"
- Right actions: "Run Risk Check" Primary button (editor+ only)

## Summary Bar

- Row of 4 chips: Total, Critical, High, Medium showing counts
- Chip: `bg-white border border-slate-200 rounded-lg px-4 py-2 text-sm font-medium`

## Risk Table

- Columns: Severity, Rule Name, Description, Amount, Status, Document, Actions
- Severity: SeverityBadge component
- Status: StatusBadge component
- Actions: "Update Status" dropdown (editor+ only)

## Severity Badge Colors

Per MASTER risk severity table:
- Critical: `bg-violet-100 text-violet-700`
- High: `bg-red-100 text-red-600`
- Medium: `bg-amber-100 text-amber-600`
- Low: `bg-green-100 text-green-600`
- Info: `bg-sky-100 text-sky-600`

## Status Badge Colors

Per MASTER status table:
- Open: red
- Reviewed: amber
- Resolved: green
- Dismissed: slate

## Empty State

- Icon: `ShieldCheck`
- Title: "No risk findings"
- Body: "Run a risk check on your documents to detect issues"

## Filters (Skeleton placeholder)

- Filter row: severity filter, status filter, document filter
- Each as a `<select>` with MASTER input styling
