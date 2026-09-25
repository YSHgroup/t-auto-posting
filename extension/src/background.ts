// Background service worker for extension

// Listen for messages from popup/content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background received:', request)

  if (request.type === 'GET_TOKEN') {
    chrome.storage.local.get(['accessToken'], (result) => {
      sendResponse({ token: result.accessToken })
    })
    return true
  }

  if (request.type === 'LOGOUT') {
    chrome.storage.local.remove(['accessToken', 'refreshToken'])
    sendResponse({ success: true })
    return true
  }
})

// Update badge with unread notifications count
function updateNotificationBadge() {
  chrome.storage.local.get(['accessToken'], async (result) => {
    if (!result.accessToken) return

    try {
      const response = await fetch('http://localhost:8000/api/notifications/unread-count', {
        headers: {
          'Authorization': `Bearer ${result.accessToken}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        const count = data.unread_count

        if (count > 0) {
          chrome.action.setBadgeText({ text: String(count) })
          chrome.action.setBadgeBackgroundColor({ color: '#FF6B6B' })
        } else {
          chrome.action.setBadgeText({ text: '' })
        }
      }
    } catch (error) {
      console.error('Failed to fetch unread count:', error)
    }
  })
}

// Check for unread notifications every minute
chrome.alarms.create('updateNotificationBadge', { periodInMinutes: 1 })
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'updateNotificationBadge') {
    updateNotificationBadge()
  }
})

// Update on startup
updateNotificationBadge()
