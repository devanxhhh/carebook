import api from './client.js'

export const payForBooking = (bookingId) => api.post('/payments/', { booking_id: bookingId })

export function savePaymentStatus(bookingId, status) {
  localStorage.setItem(`carebook.payment.${bookingId}`, status)
}

export function getPaymentStatus(bookingId) {
  return localStorage.getItem(`carebook.payment.${bookingId}`)
}
