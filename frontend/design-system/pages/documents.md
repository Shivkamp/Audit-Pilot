# Documents Page — Design Override
Inherits from `design-system/MASTER.md`.

## Route
`/workspaces/:workspaceId/documents`

## Page Header
- Title: "Documents"
- Subtitle: "Upload and manage your audit documents"
- Right action: Refresh icon button (slate, not primary — upload is in the body)

## Upload Section (top of page)
- Role-gated: owner/admin/editor see `MultiFileUploader`
- Viewer sees `PermissionDeniedCard` with message: "You can view documents, but your current workspace role does not allow uploading files."
- Upload section is always visible (not hidden); viewer just sees the notice

## MultiFileUploader
- Drag/drop zone: dashed border, bg-slate-50, hover:bg-slate-100
- Drop zone icon: Upload (Lucide), text-slate-300 default → text-sky-500 on drag-over
- Caption: "Drop files here, or browse" / "Accepted: PDF, CSV, XLSX, XLS"
- File queue: max-h-64 scrollable list
- Each queue item: file icon (colored by type), filename, size, status badge, retry/remove buttons
- Actions bar: "Clear Queue" (ghost, danger hover) + "Upload All (N)" (primary, disabled when uploading)

## File Type Icons
- PDF: `FileText` text-red-400
- CSV: `FileSpreadsheet` text-green-500
- XLSX/XLS: `FileSpreadsheet` text-emerald-500
- Unknown: `FileText` text-slate-400

## Upload Queue Statuses
See `StatusBadge` for all status colors.
- queued → slate
- uploading → sky (with spinner)
- uploaded → green (with CheckCircle2)
- failed → red (with AlertCircle, shows error inline)
- retrying → amber (with spinner)

## Document Table
- Columns: File, Size (hidden sm), Detected Type (hidden md), Status, Uploaded (hidden lg), Actions
- Table: standard MASTER table styles + `rounded-xl` wrapper
- File column: file type icon + filename + truncated ID in mono xs
- Detected type: shows `—` if `unknown`

## Document Actions (per row)
- Download: `Download` icon button, hover:text-sky-600
- Metadata: `Info` icon button → opens `DocumentMetadataDrawer`
- Jobs: `Briefcase` icon button → navigates to /workspaces/:id/jobs
- Delete: `Trash2` icon button, hover:text-red-600, only shown if canDeleteDocuments(role)

## DocumentMetadataDrawer
- Slide-in from right, max-w-sm
- Backdrop: bg-black/20
- Sections: Document header + status badge, File (name/ext/content-type/size/storage), Classification (type/confidence), Timeline (uploaded/updated)
- Each section has a subtle header with icon + uppercase label
- MetaRow: 2-col grid, label text-xs text-slate-500, value text-xs text-slate-800

## Delete Confirm Dialog
- Uses `ConfirmDialog` variant="danger"
- Title: "Delete Document"
- Description mentions filename

## Empty State
- Icon: `FileText`
- Title: "No documents uploaded yet"
- Body: "Upload your first document above to start processing and risk analysis."

## Error Handling
- 403 on download: toast.error with filename
- Network errors: toast.error
- Backend 403 on delete: handled by ErrorState/toast
