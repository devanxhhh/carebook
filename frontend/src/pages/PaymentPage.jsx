import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { getBooking } from '../api/bookings.js'
import { getCentre } from '../api/catalogue.js'
import { getApiError } from '../api/client.js'
import { getPaymentStatus, payForBooking, savePaymentStatus } from '../api/payments.js'
import LoadingState from '../components/ui/LoadingState.jsx'
import Notice from '../components/ui/Notice.jsx'
import StatusBadge from '../components/ui/StatusBadge.jsx'

export default function PaymentPage() {
  const { bookingId } = useParams()
  const location = useLocation()
  const [booking, setBooking] = useState(location.state?.booking || null)
  const [centre, setCentre] = useState(location.state?.centre || null)
  const [test, setTest] = useState(location.state?.test || null)
  const [paymentStatus, setPaymentStatus] = useState(getPaymentStatus(bookingId))
  const [loading, setLoading] = useState(!location.state?.booking)
  const [paying, setPaying] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    async function load() {
      try {
        const { data } = await getBooking(bookingId)
        if (!active) return
        setBooking(data)
        const centreResponse = await getCentre(data.centre_id)
        if (!active) return
        setCentre(centreResponse.data)
        const association = centreResponse.data.centre_tests?.find((item) => item.test_id === data.test_id)
        setTest(association?.test || null)
      } catch (requestError) {
        if (active) setError(getApiError(requestError))
      } finally {
        if (active) setLoading(false)
      }
    }
    load()
    return () => { active = false }
  }, [bookingId])

  async function handlePayment() {
    setError('')
    setPaying(true)
    try {
      const { data } = await payForBooking(bookingId)
      setPaymentStatus(data.status)
      savePaymentStatus(bookingId, data.status)
      if (data.status === 'SUCCESS') {
        setBooking((current) => current ? { ...current, status: 'CONFIRMED' } : current)
      } else if (data.status === 'FAILED') {
        setBooking((current) => current ? { ...current, status: 'FAILED' } : current)
      }
    } catch (requestError) {
      setError(getApiError(requestError))
    } finally {
      setPaying(false)
    }
  }

  if (loading) return <div className="page-container"><LoadingState label="Loading payment details" /></div>
  if (!booking) return <div className="page-container"><Notice>{error || 'Booking not found.'}</Notice><Link className="button button-outline" to="/dashboard">Back to dashboard</Link></div>

  const succeeded = paymentStatus === 'SUCCESS'
  return (
    <div className="page-container narrow-container payment-page">
      <div className={`payment-result ${succeeded ? 'payment-success' : paymentStatus === 'FAILED' ? 'payment-failed' : ''}`}>
        <div className="payment-result-icon">{succeeded ? '✓' : paymentStatus === 'FAILED' ? '!' : '↗'}</div>
        <span className="eyebrow">{succeeded ? 'PAYMENT COMPLETE' : paymentStatus === 'FAILED' ? 'PAYMENT NOT COMPLETED' : 'ONE LAST STEP'}</span>
        <h1>{succeeded ? "You're all booked." : paymentStatus === 'FAILED' ? 'Payment unsuccessful.' : 'Confirm your payment.'}</h1>
        <p>{succeeded ? 'Your simulated payment was successful. Your appointment is confirmed.' : paymentStatus === 'FAILED' ? 'The payment attempt failed. The backend has returned this result for your booking.' : 'Review your booking and complete the simulated payment to confirm your appointment.'}</p>
      </div>
      <Notice>{error}</Notice>
      <div className="payment-summary-card">
        <div className="payment-summary-header"><div><span className="eyebrow">BOOKING SUMMARY</span><h2>Booking #{booking.id}</h2></div><StatusBadge>{booking.status}</StatusBadge></div>
        <div className="payment-summary-line"><span>Test</span><strong>{test?.name || `Diagnostic test #${booking.test_id}`}</strong></div>
        <div className="payment-summary-line"><span>Centre</span><strong>{centre?.name || `Centre #${booking.centre_id}`}</strong></div>
        <div className="payment-summary-line"><span>Appointment</span><strong>{new Date(booking.appointment_at).toLocaleString()}</strong></div>
        <div className="payment-total"><span>Amount due</span><strong>₹{Number(booking.amount).toLocaleString('en-IN')}</strong></div>
        <div className="payment-summary-line"><span>Payment status</span><strong>{paymentStatus || 'Not attempted'}</strong></div>
      </div>
      <div className="payment-actions">
        {!paymentStatus && booking.status === 'PENDING' && <button className="button button-primary button-full" type="button" onClick={handlePayment} disabled={paying}>{paying ? 'Processing payment…' : 'Pay now'} <span aria-hidden="true">→</span></button>}
        {succeeded && <Link className="button button-primary button-full" to={`/bookings/${booking.id}`}>View booking details <span aria-hidden="true">→</span></Link>}
        {!succeeded && <Link className="button button-outline button-full" to={`/bookings/${booking.id}`}>Go to booking details</Link>}
      </div>
      <p className="quiet-note centered-note">CareBook uses a simulated payment flow. No card information is collected.</p>
    </div>
  )
}
