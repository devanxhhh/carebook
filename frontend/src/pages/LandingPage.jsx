import { Link } from 'react-router-dom'

const benefits = [
  { number: '01', title: 'Find a test', body: 'Browse available diagnostic tests and centre-specific pricing.' },
  { number: '02', title: 'Choose a time', body: 'Select a centre and appointment time that works for you.' },
  { number: '03', title: 'Confirm your booking', body: 'Review your appointment and complete the simulated payment.' },
]

export default function LandingPage() {
  return (
    <>
      <section className="hero-section">
        <div className="hero-copy">
          <div className="eyebrow"><span className="eyebrow-dot" /> CAREBOOK DIAGNOSTICS</div>
          <h1>Diagnostic testing,<br />made <em>simpler.</em></h1>
          <p className="hero-description">
            Find a test, compare centres, choose a convenient time, and book in a few minutes.
          </p>
          <div className="hero-actions">
            <Link className="button button-primary button-large" to="/centres">Find a diagnostic test <span aria-hidden="true">→</span></Link>
            <Link className="button button-outline button-large" to="/dashboard">View dashboard</Link>
          </div>
          <div className="hero-proof">
            <span className="proof-icon">✓</span>
            <span>Centre-specific prices · Convenient appointment times</span>
          </div>
        </div>
        <div className="hero-art" aria-label="Illustration of a healthcare professional" role="img">
          <div className="art-orbit orbit-one" />
          <div className="art-orbit orbit-two" />
          <div className="art-sun" />
          <div className="art-card art-card-top">
            <span className="art-card-icon">✚</span><span><strong>Care, simplified</strong><small>Every step, together</small></span>
          </div>
          <div className="art-person">
            <div className="person-hair" />
            <div className="person-face"><span className="person-eye eye-left" /><span className="person-eye eye-right" /><span className="person-smile" /></div>
            <div className="person-neck" />
            <div className="person-body"><span className="coat-line" /><span className="coat-pocket" /><span className="stethoscope" /></div>
          </div>
          <div className="art-card art-card-bottom"><span className="check-circle">✓</span><span><strong>Appointment booked</strong><small>One less thing to worry about</small></span></div>
          <span className="art-spark spark-one">✳</span><span className="art-spark spark-two">✦</span>
        </div>
        <div className="hero-bottom-note"><span>CAREBOOK</span><span className="note-rule" /><span>DIAGNOSTIC TEST BOOKING</span></div>
      </section>

      <section className="steps-section" id="how-it-works">
        <div className="section-heading">
          <div><div className="eyebrow">HOW IT WORKS</div><h2>From search to booking.</h2></div>
        </div>
        <div className="steps-grid">
          {benefits.map((benefit) => (
            <article className="step-card" key={benefit.number}>
              <span className="step-number">{benefit.number}</span>
              <h3>{benefit.title}</h3><p>{benefit.body}</p>
            </article>
          ))}
        </div>
      </section>
    </>
  )
}
