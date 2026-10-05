import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getCurrentUser, login as requestLogin } from '../api/auth.js'
import api, { TOKEN_KEY } from '../api/client.js'
import AuthContext from './authContext.js'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(() => Boolean(localStorage.getItem(TOKEN_KEY)))
  const navigate = useNavigate()

  useEffect(() => {
    if (!localStorage.getItem(TOKEN_KEY)) return
    getCurrentUser()
      .then(({ data }) => setUser(data))
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY)
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  async function signIn(email, password) {
    const { data } = await requestLogin(email, password)
    localStorage.setItem(TOKEN_KEY, data.access_token)
    try {
      const profile = await getCurrentUser()
      setUser(profile.data)
      return profile.data
    } catch (error) {
      localStorage.removeItem(TOKEN_KEY)
      throw error
    }
  }

  async function signUp(payload) {
    return api.post('/auth/signup', payload)
  }

  function signOut() {
    localStorage.removeItem(TOKEN_KEY)
    setUser(null)
    navigate('/login')
  }

  return <AuthContext.Provider value={{ user, loading, signIn, signUp, signOut }}>{children}</AuthContext.Provider>
}
