"""
React components for extension
"""
// Sidebar Navigation Component
export function Sidebar() {
  return (
    <aside className="w-64 bg-white shadow-sm">
      {/* Sidebar content */}
    </aside>
  )
}

// Header Component
export function Header() {
  return (
    <header className="bg-white shadow-sm border-b">
      {/* Header content */}
    </header>
  )
}

// Card Component
export function Card({ children, className }: any) {
  return (
    <div className={`bg-white rounded-lg shadow p-6 ${className || ''}`}>
      {children}
    </div>
  )
}

// Button Component
export function Button({ 
  children, 
  variant = 'primary', 
  size = 'md',
  onClick,
  disabled = false,
  className }: any) {
  const baseClasses = 'font-medium rounded-lg transition'
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    danger: 'bg-red-600 text-white hover:bg-red-700',
  }
  const sizes = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  }

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className || ''} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      {children}
    </button>
  )
}

// Loading Spinner Component
export function LoadingSpinner() {
  return (
    <div className="flex justify-center items-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  )
}

// Notification Badge Component
export function NotificationBadge({ count }: any) {
  if (count === 0) return null
  
  return (
    <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
      {count > 99 ? '99+' : count}
    </span>
  )
}

// Status Badge Component
export function StatusBadge({ status, variant }: any) {
  const variants = {
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800',
  }

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded-full ${variants[variant]}`}>
      {status}
    </span>
  )
}
