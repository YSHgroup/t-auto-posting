// This script runs on web pages
// Currently minimal functionality, can be expanded for page context

console.log('Telegram Intelligence Bot content script loaded')

// Listen for messages from background
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Content script received:', request)
})
