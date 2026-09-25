// TypeScript types for extension
export interface User {
  id: number
  email: string
  username: string
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface TelegramGroup {
  telegram_group_id: string
  name: string
  username?: string
  member_count: number
  description?: string
  is_public: boolean
}

export interface Post {
  id: number
  title: string
  content: string
  post_type: string
  tags?: string[]
  links?: string[]
  is_active: boolean
  created_at: string
}

export interface FeedItem {
  id: number
  position: number
  group_name: string
  group_username?: string
  member_count: number
  is_enabled: boolean
  category?: string
  post_count: number
  reply_count: number
}

export interface Notification {
  id: number
  group_name: string
  telegram_user_name: string
  message_text: string
  received_at: string
  is_read: boolean
}

export interface Opportunity {
  id: number
  group_name: string
  telegram_user_name: string
  opportunity_type: 'Investment' | 'Partnership'
  evidence: string
  confidence: 'High' | 'Medium' | 'Low'
  relevance_reason: string
  status: 'new' | 'reviewed' | 'contacted' | 'dismissed'
}

export interface Statistics {
  total_groups: number
  active_groups: number
  total_posts: number
  posts_this_week: number
  skipped_posts: number
  failed_posts: number
  total_replies: number
  unread_replies: number
  opportunities_identified: number
  last_post_at?: string
  next_scheduled_post?: string
}

export interface SchedulerConfig {
  posting_mode: 'manual' | 'automatic'
  active_start_time: string
  active_end_time: string
  active_days: string
  timezone: string
  min_messages_between_posts: number
  max_posts_per_hour: number
  max_posts_per_day: number
}
