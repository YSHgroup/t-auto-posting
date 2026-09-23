import { useEffect, useState } from 'react'
import api from '../services/api'

export default function Opportunities() {
  const [items, setItems] = useState<any[]>([])
  const load = () => api.getOpportunities().then((response) => setItems(response.data))
  useEffect(() => { load() }, [])
  const update = async (id: number, status: string) => { await api.updateOpportunityStatus(id, status); load() }
  return <main className="p-6 space-y-4"><h1 className="text-2xl font-semibold">Opportunities</h1>{items.map((item) => <article className="border p-4 space-y-2" key={item.id}><div className="flex justify-between"><strong>{item.opportunity_type} in {item.group_name}</strong><select value={item.status} onChange={(event) => update(item.id, event.target.value)}><option>new</option><option>reviewed</option><option>contacted</option><option>dismissed</option></select></div><p>{item.evidence}</p><p className="text-sm text-gray-500">{item.relevance_reason}</p></article>)}</main>
}
