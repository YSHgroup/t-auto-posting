import { useEffect, useState } from 'react'
import api from '../services/api'

export default function Feed() {
  const [items, setItems] = useState<any[]>([])
  const load = () => api.getFeed().then((response) => setItems(response.data))
  useEffect(() => { load() }, [])
  const toggle = async (id: number) => { await api.toggleFeedItem(id); load() }
  const remove = async (id: number) => { await api.removeFromFeed(id); load() }
  return <main className="p-6 space-y-6"><header><h1 className="text-2xl font-semibold">Posting feed</h1><p className="text-gray-500">Groups are processed in this order by the scheduler.</p></header><section className="grid gap-3">{items.map((item) => <article className="border p-4 flex items-center justify-between" key={item.id}><div><h2 className="font-semibold">{item.group_name}</h2><p className="text-sm text-gray-500">{item.member_count} members · {item.post_count} posts · {item.reply_count} replies</p></div><div className="flex gap-2"><button className="border px-3 py-2" onClick={() => toggle(item.id)}>{item.is_enabled ? 'Pause' : 'Enable'}</button><button className="border px-3 py-2" onClick={() => remove(item.id)}>Remove</button></div></article>)}{items.length === 0 && <p className="text-gray-500">Add groups to start building your feed.</p>}</section></main>
}
