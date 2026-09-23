import { useEffect, useState } from 'react'
import api from '../services/api'

export default function Replies() {
  const [items, setItems] = useState<any[]>([])
  useEffect(() => { api.getNotifications().then((response) => setItems(response.data)) }, [])
  return <main className="p-6 space-y-4"><h1 className="text-2xl font-semibold">Replies</h1>{items.map((item) => <article className="border p-4" key={item.id}><div className="font-semibold">{item.group_name}</div><div className="text-sm text-gray-500">{item.telegram_user_name}</div><p className="mt-2">{item.message_text}</p></article>)}</main>
}
