import api from './client.js'

export const getBookings = (params = {}) => api.get('/bookings', { params })
export const getBooking = (bookingId) => api.get(`/bookings/${bookingId}`)
export const createBooking = (payload) => api.post('/bookings', payload)
export const cancelBooking = (bookingId) => api.post(`/bookings/${bookingId}/cancel`)
