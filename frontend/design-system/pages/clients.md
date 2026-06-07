# Clients Page — Design Override
Inherits from `design-system/MASTER.md`. Overrides listed below.

---

## Layout

- Page padding: `p-6 max-w-7xl mx-auto` inside AppShell main content
- Header row: PageHeader with title "Clients", subtitle, and actions slot (Refresh + New Client)
- Primary table below header

---

## Table

- Container: `overflow-hidden border border-slate-200 rounded-xl bg-white shadow-sm`
- `<table className="w-full text-sm">`
- Header: `bg-slate-50 border-b border-slate-200`
- Column header: `px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider`
- Columns visible on all screens: Name, Actions
- Columns hidden on small: PAN (`hidden md:table-cell`), GSTIN (`hidden md:table-cell`), Status (`hidden sm:table-cell`), Created (`hidden lg:table-cell`)
- Row hover: `hover:bg-slate-50 transition-colors duration-100`
- Name cell: link style `text-sm font-semibold text-sky-700 hover:text-sky-600 cursor-pointer`
- PAN/GSTIN: `font-mono text-slate-500`

### Action Buttons (per row)

| Button | Style | Notes |
|--------|-------|-------|
| Open | `flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-sky-700 hover:bg-sky-50 rounded-lg` | ExternalLink icon + "Open" text |
| Edit | `p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-600` | Pencil icon |
| Deactivate | `p-1.5 rounded-lg text-slate-400 hover:bg-red-50 hover:text-red-600` | Trash2 icon |

---

## Status Badge Variants (this page)

| Value | Style |
|-------|-------|
| `active` | `bg-green-100 text-green-700` |
| `inactive` | `bg-slate-100 text-slate-500` |

---

## Create / Edit Modal

- Overlay: `fixed inset-0 z-50 flex items-center justify-center p-4`
- Backdrop: `absolute inset-0 bg-black/30 backdrop-blur-[2px]`
- Panel: `relative bg-white rounded-2xl shadow-2xl w-full max-w-md`
- Header: `flex items-center justify-between px-6 pt-5 pb-4 border-b border-slate-100`
- Title: `text-lg font-semibold text-slate-900`
- Close button: `p-1.5 rounded-lg text-slate-400 hover:bg-slate-100` with X icon
- Form body: `px-6 py-5 space-y-4`
- Labels: `text-sm font-medium text-slate-700 mb-1`
- Required indicator: `text-red-500` asterisk
- Optional label: `text-slate-400 font-normal`
- Inputs: `w-full px-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500 transition-colors`
- Error text: `mt-1 text-xs text-red-500`
- PAN/GSTIN inputs: add `uppercase` class
- Footer buttons: right-aligned row, Cancel (ghost) + Submit (primary)

---

## Confirm Dialog (Deactivate)

- Title: `Deactivate "{client.name}"?`
- Variant: `danger`
- Confirm label: `Deactivate`

---

## Empty State

- Icon: Building2 (w-12 h-12)
- Title: "No clients yet"
- Body: "Create your first client to start organizing workspaces and audits."
- CTA: New Client button (primary)

---

## Header Actions

- Refresh: `p-2 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50` with RefreshCw icon
- New Client: primary button with Plus icon
