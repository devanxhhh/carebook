import api from './client.js'

export const getCentres = (params = {}) => api.get('/centres', { params })
export const getCentre = (centreId) => api.get(`/centres/${centreId}`)
export const createCentre = (payload) => api.post('/centres', payload)
export const getTests = (params = {}) => api.get('/tests', { params })
export const createTest = (payload) => api.post('/tests', payload)
export const addTestToCentre = (centreId, payload) =>
  api.post(`/centres/${centreId}/tests`, payload)
