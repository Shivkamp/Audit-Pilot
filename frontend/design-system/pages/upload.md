# Upload / Documents Page — Design Override
Inherits from `design-system/MASTER.md`. Overrides listed below.

## Page Header

- Title: "Documents"
- Right action: "Upload Documents" Primary button with `Upload` icon

## Document Table

- Columns: Name, Type, Size, Status, Uploaded, Actions
- Status badge using StatusBadge component (MASTER colors)
- Actions: Download URL icon button, Delete icon button (danger, owner/admin/editor only)

## Upload State

- Upload trigger: hidden `<input type="file">` triggered by styled button
- Accept: common file types (CSV, PDF, XLSX)
- During upload: progress indication via job status
- After upload: toast "Document uploaded. Processing started."

## Empty State

- Icon: `FileText` from Lucide
- Title: "No documents uploaded yet"
- Body: "Upload your first document to start processing"
- CTA: "Upload Documents"

## Document Row

- File icon colored by type:
  - PDF: `text-red-500`
  - CSV: `text-green-600`
  - XLSX: `text-emerald-600`
- File name: `font-medium text-slate-900`
- File size: `text-xs text-slate-500`
