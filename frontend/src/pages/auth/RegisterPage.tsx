import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link, useNavigate } from 'react-router-dom'
import { AlertCircle, Eye, EyeOff } from 'lucide-react'
import { useState } from 'react'
import { authApi } from '../../lib/api/auth'
import { useAuth } from '../../hooks/useAuth'
import { extractErrorMessage } from '../../lib/utils'
import { LoadingSpinner } from '../../components/common/LoadingState'
import { cn } from '../../lib/utils'

const schema = z
  .object({
    full_name: z.string().trim().optional(),
    email: z.string().email('Enter a valid email address'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirm_password: z.string().min(1, 'Please confirm your password'),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  })

type FormValues = z.infer<typeof schema>

export function RegisterPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [showPassword, setShowPassword] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const onSubmit = async (values: FormValues) => {
    setServerError(null)
    try {
      const res = await authApi.register({
        email: values.email,
        password: values.password,
        full_name: values.full_name || undefined,
      })
      login(res.access_token, res.user)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setServerError(extractErrorMessage(err))
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4 py-12">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-white border border-slate-200 rounded-2xl shadow-lg px-8 py-10">
          {/* Brand */}
          <div className="flex flex-col items-center mb-8">
            <img src="/app-icon.png" alt="AuditPilot" className="w-12 h-12 rounded-xl object-contain mb-4" />
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">AuditPilot</h1>
            <p className="text-sm text-slate-500 mt-1">Create your account</p>
          </div>

          {/* Server error */}
          {serverError && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-xl p-3 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
              <p className="text-sm text-red-700">{serverError}</p>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
            {/* Full name */}
            <div>
              <label
                htmlFor="reg-name"
                className="block text-sm font-medium text-slate-700 mb-1"
              >
                Full name{' '}
                <span className="text-slate-400 font-normal">(optional)</span>
              </label>
              <input
                id="reg-name"
                type="text"
                autoComplete="name"
                placeholder="Priya Sharma"
                {...register('full_name')}
                className="w-full px-3 py-2.5 text-sm text-slate-900 bg-white border border-slate-300 rounded-lg placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-150"
              />
            </div>

            {/* Email */}
            <div>
              <label
                htmlFor="reg-email"
                className="block text-sm font-medium text-slate-700 mb-1"
              >
                Email address
              </label>
              <input
                id="reg-email"
                type="email"
                autoComplete="email"
                placeholder="you@company.com"
                {...register('email')}
                className={cn(
                  'w-full px-3 py-2.5 text-sm text-slate-900 bg-white border rounded-lg placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-150',
                  errors.email ? 'border-red-500 focus:ring-red-500' : 'border-slate-300',
                )}
              />
              {errors.email && (
                <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="reg-password"
                className="block text-sm font-medium text-slate-700 mb-1"
              >
                Password
              </label>
              <div className="relative">
                <input
                  id="reg-password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  placeholder="Min. 8 characters"
                  {...register('password')}
                  className={cn(
                    'w-full px-3 py-2.5 pr-10 text-sm text-slate-900 bg-white border rounded-lg placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-150',
                    errors.password ? 'border-red-500 focus:ring-red-500' : 'border-slate-300',
                  )}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password ? (
                <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>
              ) : (
                <p className="mt-1 text-xs text-slate-400">Minimum 8 characters</p>
              )}
            </div>

            {/* Confirm password */}
            <div>
              <label
                htmlFor="reg-confirm"
                className="block text-sm font-medium text-slate-700 mb-1"
              >
                Confirm password
              </label>
              <input
                id="reg-confirm"
                type="password"
                autoComplete="new-password"
                placeholder="Re-enter password"
                {...register('confirm_password')}
                className={cn(
                  'w-full px-3 py-2.5 text-sm text-slate-900 bg-white border rounded-lg placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-150',
                  errors.confirm_password
                    ? 'border-red-500 focus:ring-red-500'
                    : 'border-slate-300',
                )}
              />
              {errors.confirm_password && (
                <p className="mt-1 text-xs text-red-600">{errors.confirm_password.message}</p>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-xl transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer mt-2"
            >
              {isSubmitting && <LoadingSpinner className="w-4 h-4 border-white border-t-blue-300" />}
              {isSubmitting ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          {/* Footer */}
          <p className="mt-6 text-center text-sm text-slate-500">
            Already have an account?{' '}
            <Link
              to="/login"
              className="font-medium text-blue-600 hover:text-blue-700 transition-colors"
            >
              Sign in
            </Link>
          </p>
        </div>

        <p className="text-center text-xs text-slate-400 mt-6">
          Intelligent TDS &amp; Compliance Analysis for Indian Tax Professionals
        </p>
      </div>
    </div>
  )
}
