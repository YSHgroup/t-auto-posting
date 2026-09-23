# Architecture Overview

## System Components

### 1. Chrome Extension (Frontend)
- **Technology**: React 18 + TypeScript + Vite
- **Features**:
  - User authentication & dashboard
  - Group search and discovery UI
  - Post creation and management
  - Feed ordering (drag-drop)
  - Scheduler configuration
  - Notifications display
  - Opportunity viewer
  - Statistics dashboard

- **Key Files**:
  - `manifest.json` - Chrome extension configuration
  - `src/main.tsx` - React entry point
  - `src/services/api.ts` - Backend API client
  - `src/stores/index.ts` - State management (Zustand)

### 2. FastAPI Backend
- **Technology**: FastAPI + SQLAlchemy + PostgreSQL
- **Features**:
  - RESTful API for all operations
  - JWT authentication
  - Database models & migrations (Alembic)
  - Async request handling
  - CORS support

- **Key Files**:
  - `app/main.py` - FastAPI application
  - `app/models/__init__.py` - Database models
  - `app/api/` - API route handlers
  - `app/core/` - Configuration & security

### 3. Background Workers (Celery)
- **Technology**: Celery + Redis + Celery Beat
- **Jobs**:
  - Group analysis (AI)
  - Automatic posting
  - Reply monitoring
  - Opportunity analysis
  - Statistics aggregation
  - Scheduled cleanup

- **Key Files**:
  - `app/workers/celery_app.py` - Celery configuration & tasks
  - `app/workers/tasks.py` - Task definitions

### 4. Telegram Integration
- **Technology**: pyrogram (Telegram Client API)
- **Features**:
  - Group search & discovery
  - Message retrieval
  - Posting to groups
  - Reply monitoring
  - Member info retrieval

- **Key Files**:
  - `app/telegram/client.py` - Telegram service wrapper

### 5. AI Integration
- **Technology**: OpenAI & Anthropic Claude
- **Features**:
  - Group analysis
  - Post recommendations
  - Opportunity identification
  - Configurable per-user providers

- **Key Files**:
  - `app/ai/providers.py` - AI provider abstractions

### 6. Database (PostgreSQL)
- **Features**:
  - User & authentication
  - Groups & analyses
  - Posts & scheduling
  - Posting history & statistics
  - Replies & notifications
  - Opportunities

- **Key Files**:
  - `app/models/__init__.py` - SQLAlchemy models
  - `migrations/` - Alembic database versions

## Data Flow

### User Authentication Flow
```
Extension (Login Form)
    ↓
Backend API (/auth/login)
    ↓
Validate credentials & generate JWT
    ↓
Return access_token + refresh_token
    ↓
Extension stores tokens in Chrome Storage
    ↓
All subsequent requests include JWT
```

### Group Discovery Flow
```
Extension (Search Groups)
    ↓
Backend API (/groups/search?q=keyword)
    ↓
Telegram Client (pyrogram)
    ↓
Search public groups via Telegram API
    ↓
Return results to Extension
    ↓
User adds groups to feed
```

### Posting Flow
```
Scheduler Check (every minute)
    ↓
Get active users with auto-posting enabled
    ↓
Queue posting tasks to Celery
    ↓
Worker picks up task
    ↓
Check skip conditions:
  - Time since last post < 60 sec?
  - Messages between posts < 20?
  - Rate limited?
    ↓
If eligible:
  - Fetch recommended post
  - Send to Telegram
  - Delete previous post
  - Record in post_history
    ↓
If skipped:
  - Record reason in post_history
    ↓
Return status to caller
    ↓
Extension polls for status updates
```

### AI Analysis Flow
```
User clicks "Analyze Group"
    ↓
Extension -> Backend API
    ↓
Queue Celery task (group_analysis)
    ↓
Worker gets group messages via Telegram
    ↓
Call AI provider (OpenAI/Claude)
    ↓
Parse & validate JSON response
    ↓
Store analysis in GroupAnalysis table
    ↓
Extension polls for completion
    ↓
Display results
```

### Reply Monitoring Flow
```
Celery Beat Scheduler (configurable interval)
    ↓
Trigger monitor_replies_task
    ↓
Get all active users
    ↓
For each user:
  - Get their Telegram account
  - Fetch new messages in groups
  - Check if replies to user's posts
    ↓
Create Reply records
    ↓
Create Notification records
    ↓
Extension polls for new notifications
    ↓
Display badge with unread count
```

## Security Architecture

### Credential Protection
```
Frontend (Extension)
  - Never stores Telegram credentials
  - Never stores API keys
  - Only stores JWT tokens
  
Backend
  - Encrypts Telegram session at rest
  - Encrypts API keys at rest
  - Uses Fernet (symmetric encryption)
  - Keys stored in .env (not in DB)
  
Environment Variables (.env)
  - Never committed to git
  - .gitignore protects it
  - Production uses secret management (e.g., vault)
```

### Authentication Flow
```
User logs in
  ↓
Backend validates credentials
  ↓
Generates JWT (short-lived: 24h)
  ↓
Also generates Refresh Token (long-lived: 30d)
  ↓
Extension stores both in Chrome Storage (encrypted)
  ↓
Every API request includes: Authorization: Bearer {access_token}
  ↓
When access_token expires:
    - Extension uses refresh_token to get new access_token
    - If refresh fails → redirect to login
```

## Rate Limiting Strategy

### Per-Group Limits
- Minimum 60 seconds between posts to same group
- Minimum 20 messages between user's posts in a group
- Configurable per-user

### Per-Account Limits
- Respects Telegram's `FloodWait` errors
- Exponential backoff (2, 4, 8, 16... seconds)
- Max 5 retries before failure
- Max configurable posts/hour and /day

### Redis-Based Rate Limiter
```
Key: f"group_post:{group_id}:{user_id}"
Limit: 1 post per 60 seconds

Key: f"daily_posts:{user_id}"
Limit: configured max per day (default 50)
Window: 24 hours
```

## Deployment Architecture

### Docker Compose (Development)
```
nginx (optional reverse proxy)
  ↓
FastAPI backend (port 8000)
  ↓ 
PostgreSQL (port 5432)
Celery Worker
Celery Beat
  ↓
Redis (port 6379)
```

### Production Deployment
```
Domain (HTTPS)
  ↓
Load Balancer (nginx/Cloudflare)
  ↓
FastAPI Instances (multiple)
  ↓
PostgreSQL (replicated)
Celery Workers (scaled)
Celery Beat (single)
  ↓
Redis (sentinel/cluster)
  ↓
Monitoring (Prometheus/Grafana)
Logging (ELK/Loki)
Backups (automated)
```

## Error Handling Strategy

### Telegram Errors
```
FloodWait
  → Exponential backoff
  → Record in DB
  → Pause scheduler if repeated

Unauthorized
  → Session expired
  → Request re-authentication
  → Log for audit trail

Rate Limited
  → Backoff & retry
  → Alert user if persistent
  → Auto-disable posting if necessary
```

### API Errors
```
400 Bad Request
  → Validation error
  → Return detailed message

401 Unauthorized
  → Token missing/invalid
  → Redirect to login

403 Forbidden
  → User doesn't have permission
  → Log security event

404 Not Found
  → Resource doesn't exist
  → Return friendly message

500 Internal Server Error
  → Log full traceback
  → Return generic message to user
  → Alert ops team
```

### Database Errors
```
Connection Error
  → Retry with exponential backoff
  → Fallback to cached data if available
  → Alert ops team

Transaction Conflict
  → Retry operation
  → Log for debugging
  → Return 409 Conflict to user
```

## Testing Strategy

### Unit Tests
- Security utilities
- Database models
- Service logic
- API schemas

### Integration Tests
- API endpoints
- Database transactions
- Celery tasks
- Telegram mock

### End-to-End Tests
- Complete posting flow
- Reply monitoring
- Scheduler logic
- UI interactions

## Monitoring & Logging

### Metrics to Track
- API response times
- Database query times
- Celery task execution time
- Posting success rate
- Reply mention rate
- Error rates

### Logs to Collect
- API access logs
- Telegram API errors
- Database errors
- Celery task logs
- Authentication events (audit)
- User actions (audit)

## Scalability Considerations

### Horizontal Scaling
- Stateless FastAPI instances
- Multiple Celery workers
- Database replication
- Redis clustering

### Vertical Scaling
- Increase worker concurrency
- Increase DB connection pool
- Optimize queries with indexes
- Cache frequently accessed data

### Performance Optimization
- Lazy load messages (pagination)
- Cache group analyses
- Batch API requests
- Use connection pooling
