import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getApiError } from '../api/client.js'
import useAuth from '../context/useAuth.js'
import Notice from '../components/ui/Notice.jsx'

export default function SignupPage() {
  const { signUp } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await signUp(form)
      navigate('/login', { replace: true, state: { message: 'Your account is ready. Please log in.' } })
    } catch (requestError) {
      setError(getApiError(requestError))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="auth-page">
      <div className="auth-aside signup-aside">
        <span className="eyebrow">CREATE AN ACCOUNT</span>
        <h1>Book diagnostic<br /><em>tests online.</em></h1>
        <p>Create an account to compare centres, choose a time, and manage your appointments.</p>
        <div className="auth-aside-note"><span>✓</span> Keep your bookings together in one account.</div>
      </div>
      <div className="auth-card">
        <div className="eyebrow">MAKE IT YOURS</div>
        <h2>Create account</h2><p className="form-intro">It only takes a moment to get started.</p>
        <Notice>{error}</Notice>
        <form onSubmit={handleSubmit} className="form-stack">
          <label>Full name<input type="text" autoComplete="name" required minLength="1" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Your name" /></label>
          <label>Email address<input type="email" autoComplete="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder="you@example.com" /></label>
          <label>Password<input type="password" autoComplete="new-password" minLength="8" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="At least 8 characters" /><small className="field-hint">Use at least 8 characters.</small></label>
          <button className="button button-primary button-full" type="submit" disabled={submitting}>{submitting ? 'Creating account…' : 'Create account'} <span aria-hidden="true">→</span></button>
        </form>
        <p className="auth-switch">Already have an account? <Link to="/login">Log in</Link></p>
      </div>
    </section>
  )
}
