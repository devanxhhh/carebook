import { Navigate, Outlet } from 'react-router-dom'
import useAuth from '../context/useAuth.js'
import LoadingState from './ui/LoadingState.jsx'

export default function ProtectedRoute({ role }) {
  const { user, loading } = useAuth()
  if (loading) return <LoadingState label="Checking your account" />
  if (!user) return <Navigate to="/login" replace />
  if (role && user.role !== role) return <Navigate to="/dashboard" replace />
  return <Outlet />
}
