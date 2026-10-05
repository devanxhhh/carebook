import axios from 'axios'

export const TOKEN_KEY = 'carebook.access_token'
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && localStorage.getItem(TOKEN_KEY)) {
      localStorage.removeItem(TOKEN_KEY)
      if (window.location.pathname !== '/login') {
        window.location.assign('/login?session=expired')
      }
    }
    return Promise.reject(error)
  },
)

export function getApiError(error) {
  const status = error.response?.status
  const detail = error.response?.data?.detail
  if (Array.isArray(detail)) {
    return detail.map((item) => `${item.loc?.slice(-1)[0] || 'Field'}: ${item.msg}`).join(' ')
  }
  if (detail) return detail
  if (status === 403) return 'You do not have permission to perform this action.'
  if (status === 409) return 'This record conflicts with existing data. Check the details and try again.'
  if (status === 422) return 'Some submitted information is invalid. Please review the form.'
  if (status === 502 || status === 503 || status === 504) {
    return 'CareBook’s API is currently unavailable. Please try again when the server is running.'
  }
  if (!error.response) return 'Could not reach CareBook. Check that the API server is running.'
  return 'Something went wrong. Please try again.'
}

export default api
