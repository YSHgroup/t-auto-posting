import { useEffect, useState } from 'react'
import api from '../services/api'

export default function Scheduler() {
  const [status, setStatus] = useState<any>(null)
  const [config, setConfig] = useState<any>(null)
  const load = async () => { const [currentConfig, currentStatus] = await Promise.all([api.getSchedulerConfig(), api.getSchedulerStatus()]); setConfig(currentConfig.data); setStatus(currentStatus.data) }
  useEffect(() => { load() }, [])
  if (!config || !status) return <main className="p-6">Loading scheduler...</main>
  const toggle = async () => { if (status.is_running) await api.pauseScheduler(); else await api.startScheduler(); load() }
  return <main className="p-6 space-y-6"><header><h1 className="text-2xl font-semibold">Automatic posting</h1><p className="text-gray-500">Control the scheduler and review its current limits.</p></header><button className="bg-slate-900 text-white px-4 py-2" onClick={toggle}>{status.is_running ? 'Pause posting' : 'Start posting'}</button><section className="grid grid-cols-2 md:grid-cols-4 gap-3">{[['Mode', status.posting_mode], ['Today', status.posts_today], ['This hour', status.posts_this_hour], ['Window', `${config.active_start_time} - ${config.active_end_time}`]].map(([label, value]) => <div className="border p-4" key={label as string}><div className="text-sm text-gray-500">{label}</div><div className="text-xl font-semibold">{value}</div></div>)}</section></main>
}
