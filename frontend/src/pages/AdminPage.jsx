import { useCallback, useEffect, useState } from 'react'
import { addTestToCentre, createCentre, createTest, getCentres, getTests } from '../api/catalogue.js'
import { getApiError } from '../api/client.js'
import LoadingState from '../components/ui/LoadingState.jsx'
import Notice from '../components/ui/Notice.jsx'

const emptyCentre = { name: '', location: '', description: '', is_active: true }
const emptyTest = { name: '', code: '', description: '', category: '', is_active: true }

export default function AdminPage() {
  const [centres, setCentres] = useState([])
  const [tests, setTests] = useState([])
  const [centreForm, setCentreForm] = useState(emptyCentre)
  const [testForm, setTestForm] = useState(emptyTest)
  const [association, setAssociation] = useState({ centre_id: '', test_id: '', price: '', is_available: true })
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const refreshCatalogue = useCallback(async () => {
    const [centreResponse, testResponse] = await Promise.all([
      getCentres({ page: 1, page_size: 100, active_only: false }),
      getTests({ page: 1, page_size: 100 }),
    ])
    setCentres(centreResponse.data.items)
    setTests(testResponse.data.items)
  }, [])

  useEffect(() => {
    let active = true
    async function loadCatalogue() {
      try {
        const [centreResponse, testResponse] = await Promise.all([
          getCentres({ page: 1, page_size: 100, active_only: false }),
          getTests({ page: 1, page_size: 100 }),
        ])
        if (active) {
          setCentres(centreResponse.data.items)
          setTests(testResponse.data.items)
        }
      } catch (requestError) {
        if (active) setError(getApiError(requestError))
      } finally {
        if (active) setLoading(false)
      }
    }
    loadCatalogue()
    return () => { active = false }
  }, [])

  async function submitAction(action, request) {
    setBusy(action)
    setError('')
    setSuccess('')
    try {
      await request()
      await refreshCatalogue()
      setSuccess(action === 'centre' ? 'Diagnostic centre created.' : action === 'test' ? 'Diagnostic test created.' : 'Test association saved.')
      if (action === 'centre') setCentreForm(emptyCentre)
      if (action === 'test') setTestForm(emptyTest)
    } catch (requestError) {
      setError(getApiError(requestError))
    } finally {
      setBusy('')
    }
  }

  return (
    <div className="page-container">
      <div className="page-hero compact-page-hero admin-page-hero"><div><span className="eyebrow">CAREBOOK ADMIN</span><h1>Manage your catalogue.</h1><p>Create diagnostic centres and tests, then set location-specific pricing and availability.</p></div><span className="page-hero-symbol">✚</span></div>
      <Notice>{error}</Notice><Notice tone="success">{success}</Notice>
      {loading ? <LoadingState label="Loading catalogue" /> : (
        <>
          <div className="admin-form-grid">
            <form className="form-card form-stack" onSubmit={(event) => { event.preventDefault(); submitAction('centre', () => createCentre(centreForm)) }}>
              <div className="form-section-heading"><span>01</span><div><h2>Create a centre</h2><p>Add a diagnostic location to your catalogue.</p></div></div>
              <label>Centre name<input required value={centreForm.name} onChange={(e) => setCentreForm({ ...centreForm, name: e.target.value })} placeholder="e.g. CareBook Diagnostics" /></label>
              <label>Location<input required value={centreForm.location} onChange={(e) => setCentreForm({ ...centreForm, location: e.target.value })} placeholder="City or neighbourhood" /></label>
              <label>Description <span className="optional-label">Optional</span><textarea rows="3" value={centreForm.description} onChange={(e) => setCentreForm({ ...centreForm, description: e.target.value })} placeholder="A short introduction to this centre" /></label>
              <button className="button button-primary button-full" disabled={busy === 'centre'}>{busy === 'centre' ? 'Saving…' : 'Create centre'}</button>
            </form>
            <form className="form-card form-stack" onSubmit={(event) => { event.preventDefault(); submitAction('test', () => createTest(testForm)) }}>
              <div className="form-section-heading"><span>02</span><div><h2>Create a test</h2><p>Add a diagnostic test to your catalogue.</p></div></div>
              <label>Test name<input required value={testForm.name} onChange={(e) => setTestForm({ ...testForm, name: e.target.value })} placeholder="e.g. Complete Blood Count" /></label>
              <div className="field-row"><label>Test code<input required value={testForm.code} onChange={(e) => setTestForm({ ...testForm, code: e.target.value })} placeholder="e.g. CBC" /></label><label>Category<input value={testForm.category} onChange={(e) => setTestForm({ ...testForm, category: e.target.value })} placeholder="e.g. Blood Test" /></label></div>
              <label>Description <span className="optional-label">Optional</span><textarea rows="3" value={testForm.description} onChange={(e) => setTestForm({ ...testForm, description: e.target.value })} placeholder="What does this test cover?" /></label>
              <button className="button button-primary button-full" disabled={busy === 'test'}>{busy === 'test' ? 'Saving…' : 'Create test'}</button>
            </form>
          </div>
          <form className="form-card form-stack association-form" onSubmit={(event) => {
            event.preventDefault()
            const centreId = association.centre_id || String(centres[0]?.id || '')
            const testId = association.test_id || String(tests[0]?.id || '')
            submitAction('association', () => addTestToCentre(centreId, {
              test_id: Number(testId),
              price: Number(association.price),
              is_available: association.is_available,
            }))
          }}>
            <div className="form-section-heading"><span>03</span><div><h2>Set centre pricing</h2><p>Associate a catalogue test with a centre and set its price and availability.</p></div></div>
            {!centres.length || !tests.length ? <Notice tone="error">Create at least one active centre and diagnostic test before associating them.</Notice> : (
              <>
                <div className="association-fields">
                  <label>Centre<select required value={association.centre_id || String(centres[0]?.id || '')} onChange={(e) => setAssociation({ ...association, centre_id: e.target.value })}>{centres.map((centre) => <option value={centre.id} key={centre.id}>{centre.name} — {centre.location}</option>)}</select></label>
                  <label>Test<select required value={association.test_id || String(tests[0]?.id || '')} onChange={(e) => setAssociation({ ...association, test_id: e.target.value })}>{tests.map((test) => <option value={test.id} key={test.id}>{test.name} ({test.code})</option>)}</select></label>
                  <label>Price (₹)<input type="number" min="0.01" step="0.01" required value={association.price} onChange={(e) => setAssociation({ ...association, price: e.target.value })} placeholder="500" /></label>
                </div>
                <label className="checkbox-label"><input type="checkbox" checked={association.is_available} onChange={(e) => setAssociation({ ...association, is_available: e.target.checked })} /> Available for booking</label>
                <button className="button button-primary" disabled={busy === 'association'}>{busy === 'association' ? 'Saving…' : 'Save centre pricing'}</button>
              </>
            )}
          </form>
          <section className="catalogue-overview">
            <div className="section-heading"><div><span className="eyebrow">04 · CURRENT CATALOGUE</span><h2>Centres and tests</h2></div></div>
            <div className="catalogue-columns">
              <div className="catalogue-list"><h3>Diagnostic centres <span>{centres.length}</span></h3>{centres.length ? centres.map((centre) => <div className="catalogue-row" key={centre.id}><span className="catalogue-row-icon">⌂</span><span><strong>{centre.name}</strong><small>{centre.location}</small></span><small className={centre.is_active ? 'active-label' : 'inactive-label'}>{centre.is_active ? 'Active' : 'Inactive'}</small></div>) : <p className="muted">No centres yet.</p>}</div>
              <div className="catalogue-list"><h3>Diagnostic tests <span>{tests.length}</span></h3>{tests.length ? tests.map((test) => <div className="catalogue-row" key={test.id}><span className="catalogue-row-icon test-row-icon">✚</span><span><strong>{test.name}</strong><small>{test.code} · {test.category || 'Uncategorised'}</small></span><small className={test.is_active ? 'active-label' : 'inactive-label'}>{test.is_active ? 'Active' : 'Inactive'}</small></div>) : <p className="muted">No tests yet.</p>}</div>
            </div>
          </section>
        </>
      )}
    </div>
  )
}
