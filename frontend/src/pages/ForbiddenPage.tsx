import { useNavigate } from 'react-router-dom'
import { Lock, ArrowLeft } from 'lucide-react'

export function ForbiddenPage() {
  const navigate = useNavigate()

  return (
    <div className="flex flex-col items-center justify-center h-full py-24 px-6 text-center">
      <div className="w-14 h-14 rounded-2xl bg-red-100 flex items-center justify-center mb-4">
        <Lock className="w-7 h-7 text-red-500" />
      </div>
      <h1 className="text-2xl font-bold text-slate-900 mb-2">Access Denied</h1>
      <p className="text-sm text-slate-500 mb-8 max-w-sm">
        You don't have permission to access this resource. Contact your workspace admin for help.
      </p>
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors cursor-pointer"
      >
        <ArrowLeft className="w-4 h-4" />
        Go back
      </button>
    </div>
  )
}
