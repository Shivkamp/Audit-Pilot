import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

// Health check uses a public endpoint — no auth header needed
export const healthApi = {
  check: async (): Promise<{ status: string }> => {
    const res = await axios.get<{ status: string }>(`${BASE_URL}/health`, { timeout: 5000 })
    return res.data
  },
}
