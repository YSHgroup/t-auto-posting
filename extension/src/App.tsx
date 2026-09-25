// Main App component
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { useAuthStore, useUIStore } from './stores'
import { useEffect } from 'react'

import Dashboard from './pages/Dashboard'
import Groups from './pages/Groups'
import Posts from './pages/Posts'
import Feed from './pages/Feed'
import Scheduler from './pages/Scheduler'
import Replies from './pages/Replies'
import Opportunities from './pages/Opportunities'
import Settings from './pages/Settings'
import Login from './pages/Login'

import Sidebar from './components/Sidebar'
import Header from './components/Header'

function App() {
  const isLoggedIn = useAuthStore((state) => state.isLoggedIn)

  return (
    <Router>
      {!isLoggedIn ? <Login /> : <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex flex-col">
          <Header />
          <main className="flex-1 overflow-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/groups" element={<Groups />} />
              <Route path="/posts" element={<Posts />} />
              <Route path="/feed" element={<Feed />} />
              <Route path="/scheduler" element={<Scheduler />} />
              <Route path="/replies" element={<Replies />} />
              <Route path="/opportunities" element={<Opportunities />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>
      </div>}
    </Router>
  )
}

export default App
