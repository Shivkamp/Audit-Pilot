export const APP_NAME = 'AuditPilot'
export const APP_VERSION = '0.1.0'

export const TOKEN_STORAGE_KEY = 'taxaudit_access_token'
export const USER_STORAGE_KEY = 'taxaudit_current_user'
export const CURRENT_WORKSPACE_KEY = 'taxaudit_current_workspace'

export const DEFAULT_PAGE_SIZE = 20

export const POLLING_INTERVAL_MS = 5000

export const RISK_SEVERITY_ORDER = ['critical', 'high', 'medium', 'low', 'info'] as const

export const ACCEPTED_FILE_TYPES = [
  'application/pdf',
  'text/csv',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-excel',
]
export const ACCEPTED_FILE_EXTENSIONS = '.pdf,.csv,.xlsx,.xls'
