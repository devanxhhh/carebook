import api from './client.js'

export const signup = (payload) => api.post('/auth/signup', payload)
export const getCurrentUser = () => api.get('/auth/me')

export function login(email, password) {
  const body = new URLSearchParams({ username: email, password })
  return api.post('/auth/login', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}
