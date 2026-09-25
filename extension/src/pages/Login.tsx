import { FormEvent, useState } from 'react'
import { useAuthStore } from '../stores'

export default function Login() {
  const login = useAuthStore((state) => state.login)
  const isLoading = useAuthStore((state) => state.isLoading)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setError('')
    try { await login(email, password) } catch { setError('Invalid email or password') }
  }
  return <main className="min-h-screen grid place-items-center bg-slate-100 p-6"><form onSubmit={submit} className="bg-white border p-6 w-full max-w-md space-y-4"><h1 className="text-2xl font-semibold">Sign in to T-Bot</h1>{error && <p className="text-red-600">{error}</p>}<input className="border p-2 w-full" type="email" required placeholder="Email" value={email} onChange={(event) => setEmail(event.target.value)} /><input className="border p-2 w-full" type="password" required placeholder="Password" value={password} onChange={(event) => setPassword(event.target.value)} /><button className="bg-slate-900 text-white px-4 py-2 w-full" disabled={isLoading}>{isLoading ? 'Signing in...' : 'Sign in'}</button></form></main>
}
