// Header component
import { Bell, User, Menu } from 'lucide-react'
import { useDataStore } from '../stores'

export default function Header() {
  const statistics = useDataStore((state) => state.statistics)
  const unreadReplies = statistics?.unread_replies || 0

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
      </div>

      <div className="flex items-center gap-6">
        {/* Notification Bell */}
        <div className="relative">
          <button className="relative p-2 text-gray-600 hover:text-gray-900">
            <Bell size={24} />
            {unreadReplies > 0 && (
              <span className="absolute top-1 right-1 bg-red-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {unreadReplies > 99 ? '99+' : unreadReplies}
              </span>
            )}
          </button>
        </div>

        {/* User Menu */}
        <button className="p-2 text-gray-600 hover:text-gray-900">
          <User size={24} />
        </button>
      </div>
    </header>
  )
}
