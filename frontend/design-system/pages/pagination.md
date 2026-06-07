# Pagination Component

## Location
`src/components/common/Pagination.tsx`

## Usage

```tsx
import { Pagination } from '../components/common/Pagination'

<Pagination
  page={page}
  pageSize={pageSize}
  totalItems={total}
  onPageChange={setPage}
  onPageSizeChange={(size) => { setPageSize(size); setPage(1) }}
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `page` | `number` | required | Current 1-based page number |
| `pageSize` | `number` | required | Items per page |
| `totalItems` | `number` | required | Total item count (after filtering) |
| `pageSizeOptions` | `number[]` | `[10, 25, 50, 100]` | Options for the page size selector |
| `onPageChange` | `(page: number) => void` | required | Called when user navigates pages |
| `onPageSizeChange` | `(pageSize: number) => void` | required | Called when user changes page size |
| `className` | `string` | `''` | Additional Tailwind classes for the wrapper |

## Behavior

- Shows "Showing X–Y of Z" range text.
- Prev/Next buttons are disabled at the bounds.
- When `totalItems` is 0, the component renders nothing.
- The component does **not** manage state — all state lives in the parent.

## Pattern: reset page when filters/sort change

Always reset `page` to `1` when any filter or sort changes:

```tsx
const handleFilterChange = (apply: () => void) => {
  apply()
  setPage(1)
}
```

## Where it's used

- `RiskFindingsPage` — paginates the filtered+sorted findings table
- `KnowledgeSearchPage` — paginates the chunks browser tab
