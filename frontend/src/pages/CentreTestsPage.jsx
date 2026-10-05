import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getCentre } from '../api/catalogue.js'
import { getApiError } from '../api/client.js'
import LoadingState from '../components/ui/LoadingState.jsx'
import Notice from '../components/ui/Notice.jsx'

export default function CentreTestsPage() {
  const { centreId } = useParams()
  const [centre, setCentre] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getCentre(centreId)
      .then(({ data }) => setCentre(data))
      .catch((requestError) => setError(getApiError(requestError)))
      .finally(() => setLoading(false))
  }, [centreId])

  const offerings = centre?.centre_tests?.filter((item) => item.is_available && item.test?.is_active) || []

  return (
    <div className="page-container">
      <Link className="back-link" to="/centres">← All centres</Link>
      {loading ? <LoadingState label="Loading centre tests" /> : error ? <Notice>{error}</Notice> : (
        <>
          <div className="page-hero compact-page-hero centre-detail-hero"><div><span className="eyebrow">TESTS AT THIS CENTRE</span><h1>{centre.name}</h1><p><span>⌖</span> {centre.location}</p></div><span className="page-hero-symbol">✚</span></div>
          {offerings.length ? (
            <div className="card-grid test-grid">
              {offerings.map((offering) => (
                <article className="test-card" key={offering.id}>
                  <div className="test-card-top"><span className="test-icon">✚</span><span className="availability-tag">Available</span></div>
                  <span className="test-category">{offering.test.category || 'Diagnostic test'}</span>
                  <h2>{offering.test.name}</h2>
                  <span className="test-code">CODE {offering.test.code}</span>
                  <p>{offering.test.description || 'A diagnostic test from this centre. Book an appointment at a time that works for you.'}</p>
                  <div className="test-card-footer"><div><small>PRICE</small><strong>₹{Number(offering.price).toLocaleString('en-IN')}</strong></div><Link className="button button-primary" to={`/book/${centre.id}/${offering.test_id}`}>Book test <span aria-hidden="true">→</span></Link></div>
                </article>
              ))}
            </div>
          ) : <div className="empty-state"><span className="empty-illustration">✚</span><h3>No tests available right now</h3><p>This centre doesn’t currently list any available tests.</p><Link className="text-link" to="/centres">Explore another centre →</Link></div>}
        </>
      )}
    </div>
  )
}
