import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import useAuth from '../context/useAuth.js'
import { getApiError } from '../api/client.js'
import Notice from '../components/ui/Notice.jsx'

export default function LoginPage() {
  const { signIn } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ email: '', password: '' })
  const [message, setMessage] = useState(
    location.search.includes('session=expired')
      ? { text: 'Your session expired. Please sign in again.', tone: 'error' }
      : location.state?.message
        ? { text: location.state.message, tone: 'success' }
        : null,
  )
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setMessage(null)
    setSubmitting(true)
    try {
      const user = await signIn(form.email, form.password)
      navigate(user.role === 'ADMIN' ? '/admin' : '/dashboard', { replace: true })
    } catch (requestError) {
      setMessage({ text: getApiError(requestError), tone: 'error' })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="auth-page">
      <div className="auth-aside">
        <span className="eyebrow">CAREBOOK ACCOUNT</span>
        <h1>Manage your<br /><em>bookings.</em></h1>
        <p>Sign in to view appointments, book tests, and manage your account.</p>
        <div className="auth-aside-note"><span>✚</span> Your bookings and test details in one place.</div>
      </div>
      <div className="auth-card">
        <div className="eyebrow">YOUR CAREBOOK ACCOUNT</div>
        <h2>Log in</h2><p className="form-intro">Enter your details to continue.</p>
        <Notice tone={message?.tone}>{message?.text}</Notice>
        <form onSubmit={handleSubmit} className="form-stack">
          <label>Email address<input type="email" autoComplete="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="you@example.com" /></label>
          <label>Password<input type="password" autoComplete="current-password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Your password" /></label>
          <button className="button button-primary button-full" type="submit" disabled={submitting}>{submitting ? 'Signing in…' : 'Log in'} <span aria-hidden="true">→</span></button>
        </form>
        <p className="auth-switch">New to CareBook? <Link to="/signup">Create an account</Link></p>
      </div>
    </section>
  )
}
