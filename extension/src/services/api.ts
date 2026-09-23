"""
API client service for extension
"""
import axios, { AxiosInstance } from 'axios'

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api'

class APIClient {
  private client: AxiosInstance
  private accessToken: string | null = null

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Load token from storage
    this.loadToken()

    // Add token to requests
    this.client.interceptors.request.use((config) => {
      if (this.accessToken) {
        config.headers.Authorization = `Bearer ${this.accessToken}`
      }
      return config
    })

    // Handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired, refresh
          await this.refreshToken()
        }
        return Promise.reject(error)
      }
    )
  }

  private loadToken() {
    chrome.storage.local.get(['accessToken'], (result) => {
      this.accessToken = result.accessToken || null
    })
  }

  async refreshToken() {
    try {
      const refreshToken = await this.getRefreshToken()
      if (!refreshToken) return

      const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
        refresh_token: refreshToken,
      })

      this.accessToken = response.data.access_token
      await this.saveToken(this.accessToken, response.data.refresh_token)
    } catch (error) {
      console.error('Token refresh failed:', error)
      // Redirect to login
      this.clearTokens()
    }
  }

  private async getRefreshToken(): Promise<string | null> {
    return new Promise((resolve) => {
      chrome.storage.local.get(['refreshToken'], (result) => {
        resolve(result.refreshToken || null)
      })
    })
  }

  private async saveToken(accessToken: string, refreshToken: string) {
    return new Promise<void>((resolve) => {
      chrome.storage.local.set({ accessToken, refreshToken }, () => {
        resolve()
      })
    })
  }

  private clearTokens() {
    chrome.storage.local.remove(['accessToken', 'refreshToken'])
    this.accessToken = null
  }

  // Auth endpoints
  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', { email, password })
    await this.saveToken(response.data.access_token, response.data.refresh_token)
    this.accessToken = response.data.access_token
    return response.data
  }

  async register(email: string, username: string, password: string) {
    return this.client.post('/auth/register', { email, username, password })
  }

  async logout() {
    this.clearTokens()
  }

  // Group endpoints
  async searchGroups(query: string, limit: number = 50) {
    return this.client.get('/groups/search', { params: { q: query, limit } })
  }

  async getGroup(groupId: string) {
    return this.client.get(`/groups/${groupId}`)
  }

  async analyzeGroup(groupId: string) {
    return this.client.post(`/groups/${groupId}/analyze`)
  }

  // Feed endpoints
  async getFeed() {
    return this.client.get('/feed')
  }

  async addToFeed(groupId: number) {
    return this.client.post('/feed/add', { group_id: groupId })
  }

  async reorderFeed(items: Array<{ id: number; position: number }>) {
    return this.client.put('/feed/reorder', { items })
  }

  async toggleFeedItem(feedItemId: number) {
    return this.client.put(`/feed/${feedItemId}/toggle`)
  }

  async removeFromFeed(feedItemId: number) {
    return this.client.delete(`/feed/${feedItemId}`)
  }

  // Post endpoints
  async getPosts() {
    return this.client.get('/posts')
  }

  async createPost(post: any) {
    return this.client.post('/posts', post)
  }

  async updatePost(postId: number, post: any) {
    return this.client.put(`/posts/${postId}`, post)
  }

  async deletePost(postId: number) {
    return this.client.delete(`/posts/${postId}`)
  }

  async duplicatePost(postId: number) {
    return this.client.post(`/posts/${postId}/duplicate`)
  }

  async sendPost(postId: number, groupId: number) {
    return this.client.post(`/posts/${postId}/send`, { group_id: groupId })
  }

  // Scheduler endpoints
  async getSchedulerConfig() {
    return this.client.get('/scheduler/config')
  }

  async updateSchedulerConfig(config: any) {
    return this.client.put('/scheduler/config', config)
  }

  async startScheduler() {
    return this.client.post('/scheduler/start')
  }

  async pauseScheduler() {
    return this.client.post('/scheduler/pause')
  }

  async getSchedulerStatus() {
    return this.client.get('/scheduler/status')
  }

  // Notification endpoints
  async getNotifications(unreadOnly: boolean = false) {
    return this.client.get('/notifications', { params: { unread_only: unreadOnly } })
  }

  async getFeedRecommendations(feedItemId: number) {
    return this.client.get(`/feed/${feedItemId}/recommendations`)
  }

  async getUnreadCount() {
    return this.client.get('/notifications/unread-count')
  }

  async markNotificationAsRead(notificationId: number) {
    return this.client.put(`/notifications/${notificationId}/read`)
  }

  async markAllAsRead() {
    return this.client.put('/notifications/read-all')
  }

  // Opportunities endpoints
  async getOpportunities(type?: string) {
    return this.client.get('/opportunities', { params: { opportunity_type: type } })
  }

  async analyzeOpportunities(groupId: number) {
    return this.client.post('/opportunities/analyze', { group_id: groupId })
  }

  async updateOpportunityStatus(opportunityId: number, status: string) {
    return this.client.put(`/opportunities/${opportunityId}/status`, { status })
  }

  // Statistics endpoints
  async getStatistics() {
    return this.client.get('/statistics')
  }
}

export default new APIClient()
