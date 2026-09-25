import { useEffect, useState } from 'react'
import api from '../services/api'

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null)
  useEffect(() => { api.getStatistics().then((response) => setStats(response.data)) }, [])
  if (!stats) return <main className="p-6">Loading dashboard...</main>
  const cards = [['Groups', stats.total_groups], ['Posts', stats.total_posts], ['Replies', stats.total_replies], ['Opportunities', stats.opportunities_identified]]
  return <main className="p-6 space-y-6"><header><h1 className="text-2xl font-semibold">Dashboard</h1><p className="text-gray-500">Posting activity and Telegram intelligence at a glance.</p></header><section className="grid grid-cols-2 md:grid-cols-4 gap-3">{cards.map(([label, value]) => <div className="border p-4" key={label as string}><div className="text-sm text-gray-500">{label}</div><div className="text-2xl font-semibold">{value}</div></div>)}</section><section className="border p-4"><h2 className="font-semibold">Recent activity</h2><p className="text-gray-500 mt-2">{stats.last_post_at ? `Last post: ${new Date(stats.last_post_at).toLocaleString()}` : 'No posts have been sent yet.'}</p></section></main>
}
