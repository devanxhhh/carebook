import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { cancelBooking, getBooking } from '../api/bookings.js'
import { getCentre } from '../api/catalogue.js'
import { getApiError } from '../api/client.js'
import { getPaymentStatus } from '../api/payments.js'
import LoadingState from '../components/ui/LoadingState.jsx'
import Notice from '../components/ui/Notice.jsx'
import StatusBadge from '../components/ui/StatusBadge.jsx'

export default function BookingDetailsPage() {
  const { bookingId } = useParams()
  const [booking, setBooking] = useState(null)
  const [centre, setCentre] = useState(null)
  const [test, setTest] = useState(null)
  const [paymentStatus] = useState(getPaymentStatus(bookingId))
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [cancelling, setCancelling] = useState(false)

  useEffect(() => {
    let active = true
    async function load() {
      try {
        const { data } = await getBooking(bookingId)
        if (!active) return
        setBooking(data)
        const { data: centreData } = await getCentre(data.centre_id)
        if (!active) return
        setCentre(centreData)
        setTest(centreData.centre_tests?.find((item) => item.test_id === data.test_id)?.test || null)
      } catch (requestError) {
        if (active) setError(getApiError(requestError))
      } finally {
        if (active) setLoading(false)
      }
    }
    load()
    return () => { active = false }
  }, [bookingId])

  async function handleCancel() {
    if (!window.confirm('Cancel this booking?')) return
    setError('')
    setCancelling(true)
    try {
      const { data } = await cancelBooking(bookingId)
      setBooking(data)
    } catch (requestError) {
      setError(getApiError(requestError))
    } finally {
      setCancelling(false)
    }
  }

  if (loading) return <div className="page-container"><LoadingState label="Loading booking" /></div>
  if (!booking) return <div className="page-container narrow-container"><Notice>{error || 'Booking not found.'}</Notice><Link className="button button-outline" to="/dashboard">Back to dashboard</Link></div>

  const canCancel = !['CANCELLED', 'FAILED'].includes(booking.status)
  return (
    <div className="page-container narrow-container">
      <Link className="back-link" to="/dashboard">← Back to dashboard</Link>
      <div className="page-title-block details-title"><span className="eyebrow">BOOKING DETAILS</span><h1>Your appointment</h1><p>Booking #{booking.id}</p></div>
      <Notice>{error}</Notice>
      <section className="details-card">
        <div className="details-card-header"><div><span className="eyebrow">CURRENT STATUS</span><h2>Booking #{booking.id}</h2></div><StatusBadge>{booking.status}</StatusBadge></div>
        <div className="detail-grid">
          <div><span>Diagnostic test</span><strong>{test?.name || `Test #${booking.test_id}`}</strong><small>{test?.code || ''}</small></div>
          <div><span>Centre</span><strong>{centre?.name || `Centre #${booking.centre_id}`}</strong><small>{centre?.location || ''}</small></div>
          <div><span>Appointment</span><strong>{new Date(booking.appointment_at).toLocaleString()}</strong></div>
          <div><span>Booking amount</span><strong>₹{Number(booking.amount).toLocaleString('en-IN')}</strong><small>Price captured at booking</small></div>
          <div><span>Payment status</span><strong>{paymentStatus || 'Not available from the booking endpoint'}</strong><small>Payment status is available here when recorded by this browser.</small></div>
          <div><span>Created</span><strong>{new Date(booking.created_at).toLocaleString()}</strong></div>
        </div>
        <div className="details-actions">
          {booking.status === 'PENDING' && !paymentStatus && <Link className="button button-primary" to={`/payment/${booking.id}`}>Continue to payment →</Link>}
          {canCancel && <button className="button button-outline button-danger" type="button" onClick={handleCancel} disabled={cancelling}>{cancelling ? 'Cancelling…' : 'Cancel booking'}</button>}
        </div>
      </section>
      <p className="quiet-note">Payment status is not included in the booking details API response. CareBook shows it when available from your payment session in this browser.</p>
    </div>
  )
}
