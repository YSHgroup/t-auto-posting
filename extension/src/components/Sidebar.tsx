"""
Sidebar component
"""
import { Link } from 'react-router-dom'
import { useUIStore } from '../stores'
import { useAuthStore } from '../stores'
import {
  BarChart3,
  Search,
  FileText,
  Zap,
  MessageCircle,
  Lightbulb,
  Settings,
  LogOut,
  Home,
} from 'lucide-react'

export default function Sidebar() {
  const { currentPage, setCurrentPage } = useUIStore()
  const logout = useAuthStore((state) => state.logout)

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home, path: '/' },
    { id: 'groups', label: 'Groups', icon: Search, path: '/groups' },
    { id: 'posts', label: 'Posts', icon: FileText, path: '/posts' },
    { id: 'feed', label: 'Feed', icon: Zap, path: '/feed' },
    { id: 'scheduler', label: 'Scheduler', icon: BarChart3, path: '/scheduler' },
    { id: 'replies', label: 'Replies', icon: MessageCircle, path: '/replies' },
    { id: 'opportunities', label: 'Opportunities', icon: Lightbulb, path: '/opportunities' },
  ]

  return (
    <aside className="w-64 bg-gray-900 text-white shadow-lg flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-xl font-bold">🤖 T-Bot</h1>
        <p className="text-xs text-gray-400 mt-1">Telegram Intelligence</p>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 overflow-y-auto py-4">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = currentPage === item.id

          return (
            <Link
              key={item.id}
              to={item.path}
              onClick={() => setCurrentPage(item.id)}
              className={`flex items-center gap-3 px-6 py-3 transition ${
                isActive
                  ? 'bg-blue-600 border-l-4 border-blue-400'
                  : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-gray-800 p-4">
        <Link
          to="/settings"
          onClick={() => setCurrentPage('settings')}
          className="flex items-center gap-3 px-6 py-3 text-gray-300 hover:bg-gray-800 transition"
        >
          <Settings size={20} />
          <span>Settings</span>
        </Link>
        <button
          onClick={async () => {
            await logout()
          }}
          className="w-full flex items-center gap-3 px-6 py-3 text-gray-300 hover:bg-red-600 transition mt-2"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  )
}
