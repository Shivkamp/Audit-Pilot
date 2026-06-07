export interface ApiError {
  detail?: string | ApiErrorDetail[] | null
  message?: string
  status_code?: number
}

export interface ApiErrorDetail {
  loc?: string[]
  msg: string
  type?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
}

export interface ApiResponse<T> {
  data: T
  success: boolean
  message?: string
}
