import { FormEvent, useEffect, useState } from 'react'
import api from '../services/api'

export default function Posts() {
  const [posts, setPosts] = useState<any[]>([])
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [postType, setPostType] = useState('General')

  const load = () => api.getPosts().then((response) => setPosts(response.data))
  useEffect(() => { load() }, [])

  const create = async (event: FormEvent) => {
    event.preventDefault()
    if (!title.trim() || !content.trim()) return
    await api.createPost({ title, content, post_type: postType })
    setTitle('')
    setContent('')
    load()
  }

  return <main className="p-6 space-y-6">
    <header><h1 className="text-2xl font-semibold">Post library</h1><p className="text-gray-500">Reusable messages for manual and scheduled delivery.</p></header>
    <form onSubmit={create} className="grid gap-3 max-w-2xl">
      <input className="border p-2" placeholder="Title" value={title} onChange={(event) => setTitle(event.target.value)} />
      <textarea className="border p-2 min-h-32" placeholder="Message content" value={content} onChange={(event) => setContent(event.target.value)} />
      <select className="border p-2" value={postType} onChange={(event) => setPostType(event.target.value)}><option>General</option><option>Partnership</option><option>Job</option><option>Business</option><option>Investor</option></select>
      <button className="bg-slate-900 text-white px-4 py-2 w-fit" type="submit">Create post</button>
    </form>
    <section className="grid gap-3">{posts.map((post) => <article className="border p-4" key={post.id}><div className="flex justify-between"><h2 className="font-semibold">{post.title}</h2><span className="text-sm text-gray-500">{post.post_type}</span></div><p className="mt-2 whitespace-pre-wrap">{post.content}</p></article>)}</section>
  </main>
}
