# AI Agent Chat Page — Design Override
Inherits from `design-system/MASTER.md`. Overrides listed below.

## Layout

- Two-column on desktop: chat area (flex-1) + context panel (w-80)
- Single column on mobile
- Full height minus topbar: `h-[calc(100vh-56px)]`

## Chat Area

- Messages container: `flex-1 overflow-y-auto p-4 space-y-4`
- Input area: fixed bottom, `border-t border-slate-200 p-4 bg-white`
- Input: multiline textarea, `resize-none rounded-xl border border-slate-300 px-4 py-3 text-sm`
- Send button: Primary icon button with `Send` icon, `rounded-xl`

## Message Bubbles

| Role | Style |
|------|-------|
| User | `bg-sky-700 text-white rounded-2xl rounded-br-md px-4 py-3 max-w-[75%] ml-auto` |
| Assistant | `bg-white border border-slate-200 text-slate-800 rounded-2xl rounded-bl-md px-4 py-3 max-w-[80%]` |
| System | `bg-slate-100 text-slate-500 text-xs rounded-lg px-3 py-2 mx-auto text-center` |

## Thinking State

- Animated dots indicator in assistant bubble position
- `text-slate-400 text-sm`

## Empty State (No messages)

- Centered in chat area
- Icon: `Bot` w-12 h-12 text-slate-300
- Title: "Ask TaxAudit AI"
- Body: "Ask questions about your documents, TDS mismatches, compliance issues..."
- Suggested prompts row (static chips)

## Context Panel

- Header: "Evidence Context" `text-sm font-semibold text-slate-700`
- Placeholder: "Select a risk finding or ask a question to see relevant evidence"
- Evidence chunks displayed as cards with source info

## Empty/No Workspace

- Full page empty state: "Select a workspace to use the AI agent"
