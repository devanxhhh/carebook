import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { createBooking } from '../api/bookings.js'
import { getCentre } from '../api/catalogue.js'
import { getApiError } from '../api/client.js'
import LoadingState from '../components/ui/LoadingState.jsx'
import Notice from '../components/ui/Notice.jsx'

function defaultAppointment() {
  const date = new Date(Date.now() + 48 * 60 * 60 * 1000)
  date.setMinutes(Math.ceil(date.getMinutes() / 15) * 15, 0, 0)
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16)
}

function minimumAppointment() {
  const date = new Date()
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16)
}

export default function BookingPage() {
  const { centreId, testId } = useParams()
  const navigate = useNavigate()
  const [centre, setCentre] = useState(null)
  const [appointmentAt, setAppointmentAt] = useState(defaultAppointment)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    getCentre(centreId)
      .then(({ data }) => setCentre(data))
      .catch((requestError) => setError(getApiError(requestError)))
      .finally(() => setLoading(false))
  }, [centreId])

  const offering = useMemo(
    () => centre?.centre_tests?.find((item) => String(item.test_id) === String(testId) && item.is_available && item.test?.is_active),
    [centre, testId],
  )

  async function handleSubmit(event) {
    event.preventDefault()
    if (!offering) return
    setError('')
    setSubmitting(true)
    try {
      const { data } = await createBooking({
        centre_id: Number(centreId),
        test_id: Number(testId),
        appointment_at: new Date(appointmentAt).toISOString(),
      })
      navigate(`/payment/${data.id}`, { state: { booking: data, centre, test: offering.test } })
    } catch (requestError) {
      setError(getApiError(requestError))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="page-container narrow-container">
      <Link className="back-link" to={`/centres/${centreId}/tests`}>← Back to available tests</Link>
      <div className="page-title-block"><span className="eyebrow">YOUR APPOINTMENT</span><h1>Book your test</h1><p>Choose a time that works for you. You can review everything before confirming.</p></div>
      {loading ? <LoadingState label="Loading booking details" /> : error && !centre ? <Notice>{error}</Notice> : !offering ? <div className="empty-state"><h3>This test is not available here</h3><p>It may have been removed or is no longer bookable.</p><Link className="button button-outline" to="/centres">Browse centres</Link></div> : (
        <div className="booking-form-layout">
          <form className="form-card form-stack" onSubmit={handleSubmit}>
            <Notice>{error}</Notice>
            <div className="form-section-heading"><span>01</span><div><h2>Appointment details</h2><p>All fields are required to place a booking.</p></div></div>
            <label>Date and time<input type="datetime-local" required min={minimumAppointment()} value={appointmentAt} onChange={(e) => setAppointmentAt(e.target.value)} /></label>
            <div className="booking-terms"><span>i</span><p>Your appointment time is sent to CareBook with your booking request. The backend validates the selected centre, test availability, and date.</p></div>
            <button className="button button-primary button-full" type="submit" disabled={submitting}>{submitting ? 'Creating booking…' : 'Confirm booking'} <span aria-hidden="true">→</span></button>
          </form>
          <aside className="order-card">
            <span className="eyebrow">BOOKING SUMMARY</span><h2>Review your test</h2>
            <div className="order-item"><span className="order-icon">✚</span><div><strong>{offering.test.name}</strong><small>{offering.test.code} · {offering.test.category || 'Diagnostic test'}</small></div></div>
            <div className="order-detail"><span>Centre</span><strong>{centre.name}</strong></div>
            <div className="order-detail"><span>Location</span><strong>{centre.location}</strong></div>
            <div className="order-total"><span>Total</span><strong>₹{Number(offering.price).toLocaleString('en-IN')}</strong></div>
            <small className="snapshot-note">The booking price is confirmed from the centre’s current listed price.</small>
          </aside>
        </div>
      )}
    </div>
  )
}
