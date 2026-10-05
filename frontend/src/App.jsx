import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import './App.css'
import { AuthProvider } from './context/AuthContext.jsx'
import AppLayout from './components/AppLayout.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import AdminPage from './pages/AdminPage.jsx'
import BookingPage from './pages/BookingPage.jsx'
import BookingDetailsPage from './pages/BookingDetailsPage.jsx'
import CentreTestsPage from './pages/CentreTestsPage.jsx'
import CentresPage from './pages/CentresPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import LandingPage from './pages/LandingPage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import PaymentPage from './pages/PaymentPage.jsx'
import SignupPage from './pages/SignupPage.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route element={<AppLayout />}>
            <Route index element={<LandingPage />} />
            <Route path="login" element={<LoginPage />} />
            <Route path="signup" element={<SignupPage />} />
            <Route element={<ProtectedRoute />}>
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="centres" element={<CentresPage />} />
              <Route path="centres/:centreId/tests" element={<CentreTestsPage />} />
              <Route path="book/:centreId/:testId" element={<BookingPage />} />
              <Route path="payment/:bookingId" element={<PaymentPage />} />
              <Route path="bookings/:bookingId" element={<BookingDetailsPage />} />
            </Route>
            <Route element={<ProtectedRoute role="ADMIN" />}>
              <Route path="admin" element={<AdminPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
