import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import useAuth from '../context/useAuth.js'

const currentYear = new Date().getFullYear()

export default function AppLayout() {
  const { user, signOut } = useAuth()
  const location = useLocation()
  const isLanding = location.pathname === '/'

  return (
    <div className="site-shell">
      <header className="site-header">
        <div className="header-inner">
          <Link className="brand" to="/" aria-label="CareBook home">
            <span className="brand-mark">+</span>
            <span>Care<span>Book</span></span>
          </Link>
          <nav className="main-nav" aria-label="Main navigation">
            {user ? (
              <>
                <NavLink to="/dashboard">Dashboard</NavLink>
                <NavLink to="/centres">Find a test</NavLink>
                {user.role === 'ADMIN' && <NavLink to="/admin">Admin</NavLink>}
              </>
            ) : (
              <>
                <a href={isLanding ? '#how-it-works' : '/#how-it-works'}>How it works</a>
                <a href={isLanding ? '#why-carebook' : '/#why-carebook'}>Why CareBook</a>
              </>
            )}
          </nav>
          <div className="header-actions">
            {user ? (
              <>
                <span className="header-greeting">Hi, {user.name.split(' ')[0]}</span>
                <button className="button button-quiet button-small" onClick={signOut}>Sign out</button>
              </>
            ) : (
              <>
                <Link className="header-login" to="/login">Log in</Link>
                <Link className="button button-primary button-small" to="/signup">Get started</Link>
              </>
            )}
          </div>
        </div>
      </header>
      <main className="site-main"><Outlet /></main>
      <footer className="site-footer">
        <div className="footer-inner">
          <Link className="brand brand-footer" to="/">
            <span className="brand-mark">+</span><span>Care<span>Book</span></span>
          </Link>
          <p>Diagnostic test bookings, in one place.</p>
          <span>© {currentYear} CareBook</span>
        </div>
      </footer>
    </div>
  )
}
