# Evidence Viewer Components

## Overview

Three components form the evidence UX stack:

| Component | Location | Purpose |
|-----------|----------|---------|
| `EvidenceCard` | `src/components/evidence/EvidenceCard.tsx` | Single evidence item card |
| `EvidenceViewerDrawer` | `src/components/evidence/EvidenceViewerDrawer.tsx` | Drawer listing all evidence for a risk finding |
| `SourceTraceDrawer` | `src/components/evidence/SourceTraceDrawer.tsx` | Drawer showing source trace data for a chunk |

---

## EvidenceCard

```tsx
import { EvidenceCard } from '../components/evidence/EvidenceCard'

<EvidenceCard
  evidence={evidenceResult}
  onViewSourceTrace={(type, id) => sourceTrace.open(type, id)} // optional
/>
```

### Props

| Prop | Type | Description |
|------|------|-------------|
| `evidence` | `EvidenceResult` | The evidence item to render |
| `onViewSourceTrace` | `(type: string, id: string) => void` | Optional. Shows "View Source Trace" button when provided |

---

## EvidenceViewerDrawer

Opens a right-side drawer listing all evidence for a risk finding. Internally fetches via `useEvidenceViewer` and nests its own `SourceTraceDrawer`.

```tsx
import { EvidenceViewerDrawer } from '../components/evidence/EvidenceViewerDrawer'
import { useEvidenceViewer } from '../hooks/useAgentRetrieval'

const evidenceViewer = useEvidenceViewer(workspaceId)

// Open from button:
<button onClick={() => evidenceViewer.openForFinding(findingId)}>
  View Evidence
</button>

// Render drawer once at page root:
<EvidenceViewerDrawer
  state={evidenceViewer}
  onClose={evidenceViewer.close}
  workspaceId={workspaceId}
  title="Finding Evidence"       // optional, defaults to "Evidence"
/>
```

### `useEvidenceViewer` return shape

| Property | Type | Description |
|----------|------|-------------|
| `isOpen` | `boolean` | Whether the drawer is open |
| `evidence` | `EvidenceResult[] \| undefined` | Evidence items (populated after fetch) |
| `isLoading` | `boolean` | Fetch in progress |
| `error` | `Error \| null` | Fetch error |
| `openForFinding` | `(findingId: string) => void` | Opens drawer and triggers fetch |
| `close` | `() => void` | Closes drawer and clears state |

---

## SourceTraceDrawer

Shared drawer for source trace data. Used by `KnowledgeSearchPage`, `EvidenceViewerDrawer`, and anywhere a GitBranch button appears.

```tsx
import { SourceTraceDrawer } from '../components/evidence/SourceTraceDrawer'
import { useSourceTrace } from '../hooks/useAgentRetrieval'

const sourceTrace = useSourceTrace(workspaceId)

// Trigger from anywhere:
<button onClick={() => sourceTrace.open(sourceType, sourceId)}>
  <GitBranch />
</button>

// Render once at page root:
<SourceTraceDrawer state={sourceTrace} onClose={sourceTrace.close} />
```

### `useSourceTrace` return shape

| Property | Type | Description |
|----------|------|-------------|
| `source` | `{ type: string; id: string } \| null` | Active source; null when closed |
| `data` | `unknown` | Fetched trace data |
| `isLoading` | `boolean` | Fetch in progress |
| `error` | `Error \| null` | Fetch error |
| `open` | `(type: string, id: string) => void` | Opens drawer and triggers fetch |
| `close` | `() => void` | Closes drawer and clears data |

---

## Design notes

- Drawers use `z-50` with a `z-40` backdrop overlay.
- Nested drawers (source trace inside evidence viewer) use `z-60` / `z-50` to layer correctly.
- `EvidenceCard` score is displayed as a percentage: `(score * 100).toFixed(1)%`
- Severity colors follow the standard token map: violet=critical, red=high, amber=medium, green=low, sky=info.
