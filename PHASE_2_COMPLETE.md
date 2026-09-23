# Phase 2 Implementation Guide - Telegram & AI Integration

**Status**: 🟢 Core Implementation Complete  
**Date**: 2026-09-22  
**Timeline**: 2-3 weeks to full production

---

## What's Been Implemented in Phase 2

### ✅ Telegram Service (Complete)

**File**: `backend/app/telegram/client.py`

**Methods Implemented**:
- ✅ `login_with_phone()` - Initiates phone login
- ✅ `verify_code()` - Verifies SMS code with 2FA support
- ✅ `verify_2fa()` - Handles 2FA password verification
- ✅ `search_groups()` - Searches public groups by keyword
- ✅ `get_group_info()` - Retrieves detailed group information
- ✅ `get_recent_messages()` - Fetches last N messages from group
- ✅ `send_message()` - Sends message with FloodWait retry logic
- ✅ `delete_message()` - Deletes a message from group
- ✅ `get_member_count()` - Gets group member count
- ✅ `join_group()` - Joins a group via link
- ✅ `leave_group()` - Leaves a group
- ✅ `close()` - Gracefully closes connection

**Error Handling**:
- ✅ FloodWait with exponential backoff
- ✅ Session expiration detection
- ✅ RPC error handling
- ✅ Connection state management

### ✅ Telegram Authentication API (Complete)

**File**: `backend/app/api/telegram_auth.py`

**Endpoints Implemented**:
- ✅ `POST /telegram/login/request-code` - Request login code
- ✅ `POST /telegram/login/verify-code` - Verify code
- ✅ `POST /telegram/login/verify-2fa` - Verify 2FA password
- ✅ `GET /telegram/status` - Check connection status
- ✅ `POST /telegram/logout` - Disconnect Telegram

**Security**:
- ✅ Encrypted session storage
- ✅ JWT authentication required
- ✅ Per-user session isolation
- ✅ Proper error messages

### ✅ Groups API (Complete)

**File**: `backend/app/api/groups.py`

**Endpoints Implemented**:
- ✅ `GET /api/groups/search` - Search public groups
- ✅ `GET /api/groups/{id}` - Get group details
- ✅ `POST /api/groups/{id}/analyze` - Trigger AI analysis
- ✅ `POST /api/groups/{id}/add-to-feed` - Add to user feed
- ✅ `POST /api/groups/manual-add` - Manually add group

**Features**:
- ✅ Feed management (ordering, enable/disable)
- ✅ Duplicate detection
- ✅ Error handling
- ✅ Logging

### ✅ AI Provider Integration (Complete)

**File**: `backend/app/ai/providers.py`

**Providers Implemented**:
- ✅ OpenAI (ChatGPT-4)
- ✅ Anthropic (Claude)

**Methods**:
- ✅ `analyze_group()` - AI group analysis
- ✅ `recommend_post()` - Post recommendation
- ✅ `analyze_messages_for_opportunities()` - Opportunity detection

**Features**:
- ✅ JSON response parsing
- ✅ Pydantic validation
- ✅ Error handling
- ✅ Prompt templating
- ✅ Per-provider configuration

### ✅ Celery Tasks (Complete)

**File**: `backend/app/workers/implementations.py`

**Tasks Implemented**:
1. ✅ `analyze_group_task` - AI analysis with retry
2. ✅ `post_to_group_task` - Posting with FloodWait handling
3. ✅ `monitor_replies_task` - Reply monitoring
4. ✅ `analyze_opportunities_task` - Opportunity analysis
5. ✅ `cleanup_old_logs` - Log cleanup (daily)
6. ✅ `check_scheduler` - Scheduler trigger (every minute)
7. ✅ `aggregate_statistics` - Statistics aggregation (hourly)

**Features**:
- ✅ Retry logic with exponential backoff
- ✅ Error handling and logging
- ✅ Task status tracking
- ✅ Async operation support
- ✅ Rate limit awareness

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Chrome Extension (React)                 │
│  - User Login Form                                          │
│  - Telegram Connection UI                                   │
│  - Group Search & Discovery                                 │
│  - Post Management                                          │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/JWT
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Backend (Python)                    │
│  ┌─────────────────────────────────────────────────────────┐│
│  │            Authentication Endpoints                     ││
│  │  - /auth/login, /auth/register, /auth/refresh          ││
│  │  - /auth/logout                                         ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │          Telegram Integration (NEW!)                   ││
│  │  - /telegram/login/request-code                        ││
│  │  - /telegram/login/verify-code                         ││
│  │  - /telegram/login/verify-2fa                          ││
│  │  - /telegram/status                                    ││
│  │  - /telegram/logout                                    ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │          Group Management (UPDATED!)                   ││
│  │  - /groups/search (now uses Telegram API)              ││
│  │  - /groups/{id}                                        ││
│  │  - /groups/{id}/analyze (queues Celery task)           ││
│  │  - /groups/{id}/add-to-feed                            ││
│  │  - /groups/manual-add                                  ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │      Services & Business Logic                         ││
│  │  - PostingService (skip logic, history)                ││
│  │  - GroupService (eligibility check)                    ││
│  │  - ReplyService (notification mgmt)                    ││
│  │  - SchedulerService (active window)                    ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │    Telegram Integration Layer                          ││
│  │  - TelegramService (pyrogram wrapper)                  ││
│  │  - Session management & encryption                     ││
│  │  - FloodWait handling                                  ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │      AI Provider Layer                                 ││
│  │  - OpenAIProvider (ChatGPT integration)                ││
│  │  - ClaudeProvider (Anthropic integration)              ││
│  │  - Prompt templating & response parsing                ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
         │                          │                    │
    SQLAlchemy ORM          Celery Worker           Redis Cache
         │                          │                    │
         ▼                          ▼                    ▼
┌─────────────┐  ┌──────────────────────────┐  ┌──────────────┐
│ PostgreSQL  │  │  Celery Worker + Beat    │  │    Redis     │
│ Database    │  │  - Task Queue            │  │  - Message   │
│ - Users     │  │  - Task Scheduling       │  │    Queue     │
│ - Sessions  │  │  - Retry Logic           │  │  - Cache     │
│ - Groups    │  │  - Error Handling        │  │  - Session   │
│ - Posts     │  └──────────────────────────┘  │    Storage   │
│ - History   │                                  └──────────────┘
└─────────────┘
         │                          │
         └──────────┬───────────────┘
                    ▼
         ┌────────────────────────┐
         │   Telegram API         │
         │  - Search groups       │
         │  - Get messages        │
         │  - Send messages       │
         │  - Delete messages     │
         └────────────────────────┘
```

---

## Data Flow Examples

### Example 1: User Logs in to Telegram (3-step flow)

```
User (Extension)
  │
  ├─→ POST /telegram/login/request-code
  │   {"phone": "+1234567890"}
  │
  ├─→ [Telegram sends code to user's app]
  │
  ├─→ User enters code in Extension
  │
  ├─→ POST /telegram/login/verify-code
  │   {"phone": "+1234567890", "code": "12345"}
  │
  ├─→ [If 2FA enabled: asks for password]
  │   POST /telegram/login/verify-2fa
  │   {"password": "mypassword"}
  │
  └─→ Session stored encrypted in DB
      User can now search groups and post
```

### Example 2: Search & Analyze Group

```
User Extension
  │
  ├─→ GET /api/groups/search?q=python&limit=50
  │
  ├─→ Backend queries Telegram API
  │   (via TelegramService.search_groups())
  │
  ├─→ Returns 50 public groups matching "python"
  │
  ├─→ User clicks "Analyze"
  │
  ├─→ POST /api/groups/{id}/analyze
  │
  ├─→ Backend queues Celery task:
  │   analyze_group_task.delay(user_id, group_id)
  │
  ├─→ Worker receives task:
  │   1. Fetches recent messages from group (Telegram)
  │   2. Calls AI provider (OpenAI/Claude)
  │   3. Stores analysis result
  │
  └─→ Task completes, UI shows results
      (partnership suitability, job fit, confidence score)
```

### Example 3: Automatic Posting with FloodWait Retry

```
Celery Beat (every minute)
  │
  ├─→ check_scheduler task runs
  │
  ├─→ For each user with auto-posting enabled:
  │   - Check if in active time window
  │   - Queue post_to_group_task for each group
  │
  ├─→ Worker receives post_to_group_task:
  │   1. Check skip conditions (60s interval, 20 messages)
  │   2. Fetch post content
  │   3. Send message via Telegram
  │   4. On FloodWait:
  │      - Record wait time
  │      - Retry after N seconds (exponential backoff)
  │      - Max 5 retries
  │   5. Record result in post_history
  │
  └─→ Task completes, statistics updated
```

---

## Running Phase 2

### 1. Setup Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your credentials:
# - TELEGRAM_API_ID: Get from my.telegram.org
# - TELEGRAM_API_HASH: Get from my.telegram.org
# - OPENAI_API_KEY: OpenAI API key (optional)
# - ANTHROPIC_API_KEY: Claude API key (optional)
# - SECRET_KEY: Generate random 32+ char string
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Verify all healthy
docker-compose ps
# Expected: postgres, redis, backend, celery_worker, celery_beat all ✓

# Check logs
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

### 3. Initialize Database

```bash
# Create database tables
docker-compose exec backend alembic upgrade head

# Verify tables created
docker-compose exec backend psql -U telegram_user -d telegram_bot -c "\dt"
```

### 4. Test Telegram Integration

```bash
# Access API documentation
curl http://localhost:8000/docs

# Try Telegram login flow:
# 1. POST /telegram/login/request-code
# 2. POST /telegram/login/verify-code
# 3. GET /telegram/status
```

### 5. Test Group Search

```bash
# Search for groups
curl -X GET "http://localhost:8000/api/groups/search?q=python&limit=10" \
  -H "Authorization: Bearer {your_jwt_token}"
```

### 6. Test AI Analysis

```bash
# Trigger group analysis
curl -X POST "http://localhost:8000/api/groups/1/analyze" \
  -H "Authorization: Bearer {your_jwt_token}"

# Check Celery worker logs for analysis progress
docker-compose logs -f celery_worker
```

---

## Code Examples

### Adding Telegram to Your Extension

```typescript
// src/services/api.ts

// Request login code
async loginTelegram(phone: string) {
  return axios.post('/telegram/login/request-code', { phone });
}

// Verify code
async verifyTelegramCode(phone: string, code: string) {
  return axios.post('/telegram/login/verify-code', { phone, code });
}

// Verify 2FA if needed
async verifyTelegram2FA(password: string) {
  return axios.post('/telegram/login/verify-2fa', { password });
}

// Get status
async getTelegramStatus() {
  return axios.get('/telegram/status');
}

// Search groups
async searchGroups(query: string, limit = 50) {
  return axios.get('/groups/search', { params: { q: query, limit } });
}

// Analyze group
async analyzeGroup(groupId: number) {
  return axios.post(`/groups/${groupId}/analyze`);
}
```

### Using Telegram Service

```python
# In any backend code

from app.telegram.client import get_telegram_service
from app.models import TelegramAccount
from app.core.database import SessionLocal

db = SessionLocal()
telegram_account = db.query(TelegramAccount).filter_by(user_id=1).first()

if telegram_account.session_string:
    service = get_telegram_service(telegram_account.session_string)
    
    # Search groups
    results = await service.search_groups("python", limit=50)
    
    # Get group info
    info = await service.get_group_info(group_id)
    
    # Send message
    msg_id = await service.send_message(group_id, "Hello group!")
    
    # Get recent messages
    messages = await service.get_recent_messages(group_id, limit=100)
```

### Using AI Provider

```python
# In any backend code

from app.ai.providers import OpenAIProvider, ClaudeProvider
from app.core.config import settings

# Initialize provider
ai = OpenAIProvider(settings.OPENAI_API_KEY)
# or
ai = ClaudeProvider(settings.ANTHROPIC_API_KEY)

# Analyze group
analysis = await ai.analyze_group({
    "name": "Python Developers",
    "member_count": 5000,
    "description": "A group for Python programmers",
    "messages_text": "..."
})

# Example response:
# {
#   "group_types": ["developer", "programming"],
#   "partnership_suitability": "Suitable",
#   "confidence_score": 85,
#   "posting_style": ["professional", "technical"],
#   "risks": ["spam"],
#   "communication_style": ["formal"]
# }
```

---

## Testing Checklist

### Telegram Integration Tests
- [ ] Phone login flow works
- [ ] Code verification works
- [ ] 2FA password handling works
- [ ] Session persistence works
- [ ] FloodWait backoff works
- [ ] Group search returns results
- [ ] Group info retrieval works
- [ ] Message sending works
- [ ] Message deletion works

### AI Integration Tests
- [ ] OpenAI provider connects
- [ ] Claude provider connects
- [ ] Group analysis returns valid JSON
- [ ] Post recommendation works
- [ ] Opportunity detection works
- [ ] Error handling for API failures

### Celery Task Tests
- [ ] analyze_group_task completes
- [ ] post_to_group_task sends messages
- [ ] monitor_replies_task detects replies
- [ ] Retry logic works on FloodWait
- [ ] check_scheduler queues tasks
- [ ] cleanup_old_logs removes old entries

### API Integration Tests
- [ ] Telegram login endpoints work
- [ ] Group search endpoint works
- [ ] Analysis endpoint queues task
- [ ] Feed management works
- [ ] Error responses are correct

---

## Troubleshooting

### Telegram Connection Issues

```bash
# Check if Telegram API credentials are correct
curl -X POST http://localhost:8000/api/telegram/login/request-code \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890"}'

# If 401: Check SECRET_KEY in .env
# If 403: Telegram credentials wrong, check API_ID and API_HASH
# If 5xx: Check backend logs
docker-compose logs backend
```

### Celery Task Not Running

```bash
# Check if Celery worker is running
docker-compose ps celery_worker

# Check worker logs
docker-compose logs celery_worker

# Check if task was queued
docker-compose exec redis redis-cli KEYS "*"

# Check Celery status
docker-compose exec celery_worker celery -A app.workers.celery_app inspect active
```

### Database Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check if tables were created
docker-compose exec backend psql -U telegram_user -d telegram_bot -c "\dt"

# If tables missing, run migration
docker-compose exec backend alembic upgrade head

# Check migration status
docker-compose exec backend alembic current
```

### Redis Issues

```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping

# Clear Redis cache (if needed)
docker-compose exec redis redis-cli FLUSHALL
```

---

## Performance Optimization Tips

1. **Telegram API Calls**:
   - Cache group info for 24 hours
   - Batch message fetches to reduce API calls
   - Use pagination for large groups

2. **AI Provider Calls**:
   - Cache analysis results for 30 days
   - Batch multiple groups if possible
   - Use smaller models for simple tasks

3. **Database**:
   - Add indexes on frequently queried fields
   - Archive old posting history (>90 days)
   - Use connection pooling

4. **Celery**:
   - Increase worker concurrency
   - Implement priority queues
   - Monitor queue depth

---

## Security Reminders

✅ Telegram sessions are encrypted before storage  
✅ All API credentials are in .env (not in code)  
✅ Extension never sees Telegram credentials  
✅ JWT tokens required for all API calls  
✅ Per-user data isolation enforced  
✅ Rate limiting on auth endpoints  
✅ Input validation on all endpoints  

---

## Next Steps: Phase 3

After Phase 2 is working:

1. **Post Recommendation Engine**
   - Implement smart post-group matching
   - Score compatibility (0-100)
   - Rank available posts

2. **Scheduler Improvements**
   - Implement "dry run" mode
   - Add posting history analytics
   - Implement group rotation logic

3. **UI Completion**
   - Implement all page components
   - Add real-time status updates
   - Add export functionality

4. **Monitoring & Analytics**
   - Real-time statistics
   - Posting trend charts
   - Reply rate analytics

---

## Phase 2 Completion Status

**✅ COMPLETE**

All core Phase 2 functionality has been implemented:
- ✅ Telegram service with full API support
- ✅ Telegram authentication endpoints
- ✅ Group search and management
- ✅ AI provider integration (OpenAI & Claude)
- ✅ Celery task implementations
- ✅ Error handling and retry logic
- ✅ Database schema ready
- ✅ Comprehensive logging

**Ready for**: Testing, bug fixes, performance optimization

**Estimated time to Phase 3**: 1-2 weeks after comprehensive testing

---

**Phase 2 Implemented by**: GitHub Copilot  
**Timeline**: Completed 2026-09-22  
**Status**: 🟢 Production Ready for Testing
