import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getCentres } from '../api/catalogue.js'
import { getApiError } from '../api/client.js'
import LoadingState from '../components/ui/LoadingState.jsx'
import Notice from '../components/ui/Notice.jsx'

export default function CentresPage() {
  const [centres, setCentres] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getCentres({ page: 1, page_size: 100, active_only: true })
      .then(({ data }) => setCentres(data.items))
      .catch((requestError) => setError(getApiError(requestError)))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="page-container">
      <div className="page-hero compact-page-hero"><div><span className="eyebrow">CARE, CLOSE TO HOME</span><h1>Find a diagnostic centre.</h1><p>Explore trusted centres and the tests available at each location.</p></div><span className="page-hero-symbol">⌂</span></div>
      <Notice>{error}</Notice>
      {loading ? <LoadingState label="Finding centres" /> : centres.length ? (
        <div className="card-grid centres-grid">
          {centres.map((centre) => (
            <article className="centre-card" key={centre.id}>
              <div className="centre-card-top"><span className="centre-icon">⌂</span><span className="availability-dot">Active</span></div>
              <div className="eyebrow">DIAGNOSTIC CENTRE</div>
              <h2>{centre.name}</h2><p className="centre-location"><span>⌖</span> {centre.location}</p>
              <p className="centre-description">{centre.description && centre.description !== 'string' ? centre.description : 'View the diagnostic tests and pricing available at this location.'}</p>
              <Link className="button button-outline button-full" to={`/centres/${centre.id}/tests`}>View available tests <span aria-hidden="true">→</span></Link>
            </article>
          ))}
        </div>
      ) : <div className="empty-state"><span className="empty-illustration">⌂</span><h3>No centres found yet</h3><p>There are no active diagnostic centres to show right now.</p></div>}
    </div>
  )
}
