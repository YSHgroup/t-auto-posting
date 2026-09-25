import { FormEvent, useEffect, useState } from 'react'
import api from '../services/api'

export default function Settings() {
  const [phone, setPhone] = useState('')
  const [code, setCode] = useState('')
  const [status, setStatus] = useState<any>(null)
  const [message, setMessage] = useState('')
  useEffect(() => { api.getTelegramStatus().then((response) => setStatus(response.data)).catch(() => setStatus({ connected: false })) }, [])
  const requestCode = async (event: FormEvent) => { event.preventDefault(); await api.requestTelegramCode(phone); setMessage('Code sent. Enter it below.') }
  const verify = async (event: FormEvent) => { event.preventDefault(); await api.verifyTelegramCode(phone, code); setMessage('Telegram connected.'); setStatus({ connected: true, phone }) }
  return <main className="p-6 space-y-6"><header><h1 className="text-2xl font-semibold">Settings</h1><p className="text-gray-500">Manage the Telegram account used by the backend.</p></header><section className="border p-4 max-w-xl space-y-4"><div className="font-semibold">Telegram connection</div><div>{status?.connected ? `Connected: ${status.phone}` : 'Not connected'}</div><form onSubmit={requestCode} className="flex gap-2"><input className="border p-2 flex-1" placeholder="+15551234567" value={phone} onChange={(event) => setPhone(event.target.value)} /><button className="border px-3" type="submit">Send code</button></form><form onSubmit={verify} className="flex gap-2"><input className="border p-2 flex-1" placeholder="Verification code" value={code} onChange={(event) => setCode(event.target.value)} /><button className="bg-slate-900 text-white px-3" type="submit">Verify</button></form>{message && <p className="text-sm text-green-700">{message}</p>}</section></main>
}
