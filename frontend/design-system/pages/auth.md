# Auth Pages — Design Override
Inherits from `design-system/MASTER.md`. Overrides listed below.

## Layout

- Centered auth card on full-height page
- Background: `bg-slate-50` with subtle texture (none for MVP)
- Auth card: `bg-white border border-slate-200 rounded-xl shadow-lg`
- Card width: `w-full max-w-md`
- Vertical centering: `min-h-screen flex items-center justify-center px-4`

## Brand Header

- Product name: `TaxAudit AI`
- Style: `text-2xl font-bold text-slate-900`
- Sub-tagline: `text-sm text-slate-500`
- Shield or CheckCircle icon from Lucide in sky-700, `w-8 h-8`

## Form

- Fields: stacked vertically, `space-y-4`
- Labels: `text-sm font-medium text-slate-700`
- Inputs: MASTER input style
- Submit button: full-width Primary button `w-full`
- Link: `text-sm text-sky-700 hover:text-sky-600 font-medium`

## Error Display

- Form-level error: `bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2 text-sm text-red-700`
- Icon: `AlertCircle w-4 h-4 text-red-500`

## Loading State

- Submit button shows spinner + "Signing in..." / "Creating account..."
- Button is disabled during loading

## Login Page Specific

- Heading: "Sign in to TaxAudit AI"
- Fields: Email, Password
- Footer link: "Don't have an account? Register"
- No "Forgot password" (not in MVP scope)

## Register Page Specific

- Heading: "Create your account"
- Fields: Full Name (optional), Email, Password, Confirm Password
- Password hint: "Minimum 8 characters"
- Footer link: "Already have an account? Sign in"
- Confirm password validation: must match password

## Security Considerations

- No autocomplete="off" (let browser manage)
- Password fields use `type="password"`
- Token stored after success, redirect to /dashboard
