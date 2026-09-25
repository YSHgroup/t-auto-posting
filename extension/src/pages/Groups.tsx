import { FormEvent, useState } from 'react'
import api from '../services/api'

export default function Groups() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<any[]>([])
  const [error, setError] = useState('')
  const search = async (event: FormEvent) => { event.preventDefault(); setError(''); try { const response = await api.searchGroups(query); setResults(response.data) } catch { setError('Telegram must be connected before searching groups') } }
  const add = async (group: any) => { await api.addGroup({ telegram_id: Number(group.telegram_group_id), name: group.name, username: group.username }); setResults((current) => current.filter((item) => item.telegram_group_id !== group.telegram_group_id)) }
  return <main className="p-6 space-y-6"><header><h1 className="text-2xl font-semibold">Discover groups</h1><p className="text-gray-500">Search Telegram and add groups to your posting feed.</p></header><form onSubmit={search} className="flex gap-2"><input className="border p-2 flex-1" required placeholder="Search keyword" value={query} onChange={(event) => setQuery(event.target.value)} /><button className="bg-slate-900 text-white px-4" type="submit">Search</button></form>{error && <p className="text-red-600">{error}</p>}<section className="grid gap-3">{results.map((group) => <article className="border p-4 flex justify-between items-center" key={group.telegram_group_id}><div><h2 className="font-semibold">{group.name}</h2><p className="text-sm text-gray-500">{group.member_count} members {group.username ? `@${group.username}` : ''}</p></div><button className="border px-3 py-2" onClick={() => add(group)}>Add group</button></article>)}</section></main>
}
