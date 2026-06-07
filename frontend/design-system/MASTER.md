# TaxAudit AI — Design System MASTER

**Global Source of Truth**
Generated from ui-ux-pro-max for B2B SaaS / Indian Tax & Audit Intelligence Platform.
All page files in `design-system/pages/` inherit from this document and may override specific rules.

---

## Product Identity

| Attribute | Value |
|-----------|-------|
| Product | TaxAudit AI |
| Category | B2B SaaS — Tax & Audit Intelligence |
| Industry | Indian Tax / TDS / Compliance / Fintech |
| Target Users | CA firms, compliance teams, fintech tax teams, audit teams |
| Tone | Professional, trustworthy, precise, calm |
| Pattern | Financial Dashboard |
| Theme | Light mode first |

---

## Color Palette

| Token | Hex | Tailwind | Usage |
|-------|-----|----------|-------|
| `--color-primary` | `#0F172A` | `slate-900` | Sidebar bg, page headers, strong text |
| `--color-primary-hover` | `#1E293B` | `slate-800` | Sidebar hover, dark button hover |
| `--color-secondary` | `#334155` | `slate-700` | Sub-headings, icon stroke, borders |
| `--color-accent` | `#0369A1` | `sky-700` | CTA buttons, active nav, links, focus rings |
| `--color-accent-hover` | `#0284C7` | `sky-600` | Accent button hover |
| `--color-accent-light` | `#E0F2FE` | `sky-100` | Active nav bg, chip bg |
| `--color-bg` | `#F8FAFC` | `slate-50` | Page background |
| `--color-surface` | `#FFFFFF` | `white` | Cards, panels, modals |
| `--color-border` | `#E2E8F0` | `slate-200` | Card borders, dividers, input borders |
| `--color-border-strong` | `#CBD5E1` | `slate-300` | Focused input borders |
| `--color-text` | `#020617` | `slate-950` | Primary text |
| `--color-text-muted` | `#64748B` | `slate-500` | Secondary text, placeholders |
| `--color-text-faint` | `#94A3B8` | `slate-400` | Disabled text, hints |
| `--color-success` | `#16A34A` | `green-600` | Success states, positive findings |
| `--color-success-light` | `#DCFCE7` | `green-100` | Success chip background |
| `--color-warning` | `#D97706` | `amber-600` | Warning states, medium risk |
| `--color-warning-light` | `#FEF3C7` | `amber-100` | Warning chip background |
| `--color-danger` | `#DC2626` | `red-600` | Error states, high risk, destructive actions |
| `--color-danger-light` | `#FEE2E2` | `red-100` | Error chip background |
| `--color-info` | `#0EA5E9` | `sky-500` | Info states, processing status |
| `--color-info-light` | `#E0F2FE` | `sky-100` | Info chip background |

### Risk Severity Colors

| Severity | Color | Tailwind |
|----------|-------|----------|
| Critical | `#7C3AED` | `violet-700` |
| High | `#DC2626` | `red-600` |
| Medium | `#D97706` | `amber-600` |
| Low | `#16A34A` | `green-600` |
| Info | `#0EA5E9` | `sky-500` |

### Status Colors

| Status | Color | Tailwind |
|--------|-------|----------|
| Pending | `#D97706` | `amber-600` |
| Processing | `#0EA5E9` | `sky-500` |
| Completed | `#16A34A` | `green-600` |
| Failed | `#DC2626` | `red-600` |
| Open | `#DC2626` | `red-600` |
| Reviewed | `#D97706` | `amber-600` |
| Resolved | `#16A34A` | `green-600` |
| Dismissed | `#94A3B8` | `slate-400` |

---

## Typography

| Token | Value |
|-------|-------|
| Font Family | Plus Jakarta Sans |
| Weights | 300 (light), 400 (regular), 500 (medium), 600 (semibold), 700 (bold) |
| Google Fonts URL | `https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap` |

### Type Scale

| Role | Class | Size | Weight | Usage |
|------|-------|------|--------|-------|
| `heading-xl` | `text-3xl font-bold` | 1.875rem | 700 | Page titles |
| `heading-lg` | `text-2xl font-semibold` | 1.5rem | 600 | Section headers |
| `heading-md` | `text-xl font-semibold` | 1.25rem | 600 | Card headers, modal titles |
| `heading-sm` | `text-lg font-semibold` | 1.125rem | 600 | Sub-section titles |
| `label` | `text-sm font-medium` | 0.875rem | 500 | Form labels, table headers |
| `body` | `text-sm font-normal` | 0.875rem | 400 | Default body text |
| `body-md` | `text-base font-normal` | 1rem | 400 | Readable body text |
| `caption` | `text-xs font-normal` | 0.75rem | 400 | Hints, timestamps, badges |
| `code` | `font-mono text-sm` | 0.875rem | 400 | Code, IDs, technical values |

---

## Spacing System

Uses Tailwind default 4px base unit.

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | 4px (p-1) | Tight internal padding |
| `sm` | 8px (p-2) | Icon padding, badge padding |
| `md` | 12px (p-3) | Standard input padding |
| `lg` | 16px (p-4) | Card padding (compact) |
| `xl` | 24px (p-6) | Card padding (standard) |
| `2xl` | 32px (p-8) | Page section padding |
| `3xl` | 48px (p-12) | Large section gaps |

---

## Layout

### App Shell

```
+---------------------------+
| Topbar (h-14)             |
+------+--------------------+
|      |                    |
| Side |   Main Content     |
| bar  |   (scrollable)     |
| 240px|                    |
|      |                    |
+------+--------------------+
```

- Sidebar width: `240px` (fixed, no collapse for MVP)
- Topbar height: `56px` (`h-14`)
- Main content: `flex-1 overflow-y-auto`
- Page content padding: `p-6` or `p-8`
- Max content width: `max-w-7xl mx-auto` on wider screens

### Grid

- Dashboard cards: `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4`
- Two-column layouts: `grid grid-cols-1 lg:grid-cols-2 gap-6`
- Form layouts: `max-w-2xl`

---

## Component Design Tokens

### Cards

```
bg-white border border-slate-200 rounded-lg shadow-sm
Padding: p-6
Header: text-lg font-semibold text-slate-900
Body: text-sm text-slate-600
```

### Buttons

| Variant | Classes |
|---------|---------|
| Primary | `bg-sky-700 hover:bg-sky-600 text-white font-medium px-4 py-2 rounded-lg transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2` |
| Secondary | `bg-white hover:bg-slate-50 text-slate-700 font-medium px-4 py-2 rounded-lg border border-slate-300 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2` |
| Danger | `bg-red-600 hover:bg-red-700 text-white font-medium px-4 py-2 rounded-lg transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2` |
| Ghost | `hover:bg-slate-100 text-slate-600 font-medium px-4 py-2 rounded-lg transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2` |
| Disabled | `opacity-50 cursor-not-allowed pointer-events-none` |

Button sizes:
- `sm`: `px-3 py-1.5 text-xs`
- `md` (default): `px-4 py-2 text-sm`
- `lg`: `px-5 py-2.5 text-base`

### Inputs

```
w-full px-3 py-2 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg
placeholder:text-slate-400
focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500
transition-colors duration-150
Error: border-red-500 focus:ring-red-500
```

### Tables

```
Table wrapper: overflow-hidden border border-slate-200 rounded-lg
Table: w-full text-sm
Thead: bg-slate-50 border-b border-slate-200
Th: px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider
Tbody: divide-y divide-slate-100
Td: px-4 py-3 text-sm text-slate-700
Hover row: hover:bg-slate-50 transition-colors duration-100
```

### Badges / Chips

```
inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium
```

### Form Sections

```
Space between fields: space-y-4
Field label: block text-sm font-medium text-slate-700 mb-1
Error message: mt-1 text-xs text-red-600
Helper text: mt-1 text-xs text-slate-500
```

---

## Sidebar Design

```
Background: bg-slate-900
Width: w-60 (240px)
Brand logo area: h-14 border-b border-slate-800
Nav items: default text-slate-400, icon stroke text-slate-500
Active item: bg-sky-900/30 text-sky-400 icon text-sky-400
Hover item: bg-slate-800 text-slate-200
Divider: border-t border-slate-800
Section label: text-xs font-semibold text-slate-500 uppercase tracking-widest
```

### Sidebar Nav Item Structure

```
px-3 py-2 mx-2 rounded-lg flex items-center gap-3 text-sm font-medium
Icon: w-4 h-4
```

---

## Topbar Design

```
Background: bg-white border-b border-slate-200 h-14
Left: workspace switcher / breadcrumb
Right: refresh, settings, user menu
User avatar: w-8 h-8 rounded-full bg-sky-700 text-white text-xs font-semibold flex items-center justify-center
```

---

## Empty States

```
Container: flex flex-col items-center justify-center py-16 px-6 text-center
Icon: w-12 h-12 text-slate-300 mb-4
Title: text-lg font-semibold text-slate-700 mb-1
Body: text-sm text-slate-500 mb-6
CTA button: Primary button variant
```

---

## Loading States

- Skeleton: `animate-pulse bg-slate-200 rounded` blocks
- Spinner: `animate-spin w-5 h-5 border-2 border-slate-300 border-t-sky-600 rounded-full`
- Button loading: replace icon with spinner, disable button

---

## Error States

```
Container: rounded-lg border border-red-200 bg-red-50 p-4 flex items-start gap-3
Icon: AlertCircle w-5 h-5 text-red-500 mt-0.5 flex-shrink-0
Title: text-sm font-semibold text-red-800
Body: text-sm text-red-700 mt-0.5
```

---

## Toast Notifications

Use `react-hot-toast`.

| Type | Style |
|------|-------|
| Success | Green, CheckCircle icon |
| Error | Red, XCircle icon |
| Info | Sky blue, Info icon |
| Warning | Amber, AlertTriangle icon |

Config:
```tsx
position: 'top-right'
duration: 4000
```

---

## Icons

- Library: **Lucide React** only
- Size default: `w-4 h-4` (16px)
- Size medium: `w-5 h-5` (20px)
- Size large: `w-6 h-6` (24px)
- No emojis as UI icons
- Stroke width: `1.5` (Lucide default)

---

## Animation

- Transitions: `transition-colors duration-150` (hover) and `transition-all duration-200` (expand)
- No decorative animations on data or charts for MVP
- Respect `prefers-reduced-motion`
- Skeleton pulse: `animate-pulse`

---

## Accessibility

- Minimum contrast: 4.5:1 for body text (WCAG AA)
- Focus rings: `focus:ring-2 focus:ring-sky-500 focus:ring-offset-2`
- All interactive elements: `cursor-pointer`
- Form inputs: labeled via `htmlFor` / `aria-label`
- Modal dialogs: focus trap, `role="dialog"`, `aria-modal="true"`
- Tables: `scope="col"` on `<th>`, row key prop

---

## Responsiveness

Breakpoints (Tailwind defaults):

| Breakpoint | Min Width | Usage |
|------------|-----------|-------|
| `sm` | 640px | Single-column to two-column |
| `md` | 768px | Tablet layout |
| `lg` | 1024px | Desktop layout, sidebar visible |
| `xl` | 1280px | Wide desktop, more columns |
| `2xl` | 1536px | Ultra-wide, max-content-width clamp |

- Mobile (< 1024px): sidebar hidden (menu toggle not implemented in Module 1, accepted limitation)
- Desktop (≥ 1024px): sidebar fixed left

---

## Design Anti-Patterns (AVOID)

- Excessive animations / bouncing elements
- Dark mode by default
- Emojis as UI icons
- Random gradients per page
- Inconsistent card styles
- Inline color styles (use Tailwind tokens only)
- Hover effects that shift layout (use color/opacity only)
- Missing focus states
- Raw error stack traces in UI

---

## Figma-Equivalent Component Inventory

| Component | File |
|-----------|------|
| AppShell | `components/layout/AppShell.tsx` |
| Sidebar | `components/layout/Sidebar.tsx` |
| Topbar | `components/layout/Topbar.tsx` |
| PageHeader | `components/common/PageHeader.tsx` |
| EmptyState | `components/common/EmptyState.tsx` |
| LoadingState | `components/common/LoadingState.tsx` |
| ErrorState | `components/common/ErrorState.tsx` |
| StatusBadge | `components/common/StatusBadge.tsx` |
| SeverityBadge | `components/common/SeverityBadge.tsx` |
| PermissionGate | `components/common/PermissionGate.tsx` |
| ConfirmDialog | `components/common/ConfirmDialog.tsx` |
