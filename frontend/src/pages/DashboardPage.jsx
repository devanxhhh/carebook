import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getBookings } from '../api/bookings.js'
import { getCentres, getTests } from '../api/catalogue.js'
import { getApiError } from '../api/client.js'
import { getPaymentStatus } from '../api/payments.js'
import useAuth from '../context/useAuth.js'
import LoadingState from '../components/ui/LoadingState.jsx'
import Notice from '../components/ui/Notice.jsx'
import StatusBadge from '../components/ui/StatusBadge.jsx'

export default function DashboardPage() {
  const { user } = useAuth()
  const [bookings, setBookings] = useState([])
  const [centres, setCentres] = useState({})
  const [tests, setTests] = useState({})
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getBookings({ page: 1, page_size: 10 }),
      getCentres({ page: 1, page_size: 100 }),
      getTests({ page: 1, page_size: 100 }),
    ])
      .then(([bookingResponse, centreResponse, testResponse]) => {
        setBookings(bookingResponse.data.items)
        setCentres(Object.fromEntries(centreResponse.data.items.map((item) => [item.id, item])))
        setTests(Object.fromEntries(testResponse.data.items.map((item) => [item.id, item])))
      })
      .catch((requestError) => setError(getApiError(requestError)))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="page-container dashboard-page">
      <div className="dashboard-welcome">
        <div><span className="eyebrow">YOUR ACCOUNT</span><h1>Welcome back, {user?.name.split(' ')[0]}.</h1><p>Your bookings and account details.</p></div>
        <Link className="button button-primary" to="/centres">Find a test <span aria-hidden="true">→</span></Link>
      </div>
      <div className="dashboard-summary">
        <div className="summary-card"><span className="summary-icon mint">✚</span><span><small>YOUR ACCOUNT</small><strong>{user?.role === 'ADMIN' ? 'Administrator' : 'CareBook member'}</strong></span></div>
        <div className="summary-card"><span className="summary-icon blue">◷</span><span><small>YOUR BOOKINGS</small><strong>{loading ? 'Loading…' : bookings.length}</strong></span></div>
        <div className="summary-card"><span className="summary-icon peach">⌕</span><span><small>QUICK ACTION</small><strong>Browse diagnostic tests</strong></span></div>
      </div>
      <div className="section-heading dashboard-section-heading">
        <div><span className="eyebrow">YOUR APPOINTMENTS</span><h2>Recent bookings</h2></div>
        <Link className="text-link" to="/centres">Explore tests <span aria-hidden="true">→</span></Link>
      </div>
      <Notice>{error}</Notice>
      {loading ? <LoadingState label="Loading your bookings" /> : bookings.length ? (
        <div className="booking-list">
          {bookings.map((booking) => (
            <article className="booking-row" key={booking.id}>
              <div className="booking-date-mark"><span>{new Date(booking.appointment_at).toLocaleDateString('en', { month: 'short' })}</span><strong>{new Date(booking.appointment_at).getDate()}</strong></div>
              <div className="booking-main"><Link to={`/bookings/${booking.id}`} className="booking-title">{tests[booking.test_id]?.name || `Diagnostic test #${booking.test_id}`}</Link><span>{centres[booking.centre_id]?.name || `Centre #${booking.centre_id}`} · {new Date(booking.appointment_at).toLocaleString()}</span></div>
              <div className="booking-amount"><strong>₹{Number(booking.amount).toLocaleString('en-IN')}</strong><small>Booking #{booking.id}</small></div>
              <div className="booking-statuses"><StatusBadge>{booking.status}</StatusBadge><span className="payment-hint">Payment: {getPaymentStatus(booking.id) || 'Not available'}</span></div>
              <Link className="icon-link" to={`/bookings/${booking.id}`} aria-label={`View booking ${booking.id}`}>→</Link>
            </article>
          ))}
        </div>
      ) : (
        <div className="empty-state"><span className="empty-illustration">◷</span><h3>No bookings yet</h3><p>Browse diagnostic centres to find a test and appointment time.</p><Link className="button button-primary" to="/centres">Browse diagnostic centres</Link></div>
      )}
      <p className="quiet-note">Payment status is shown when available in this browser.</p>
    </div>
  )
}
