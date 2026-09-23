# Development Roadmap

## Phase 1: ✅ Core Infrastructure (COMPLETE)

### ✅ Backend Setup
- [x] FastAPI application structure
- [x] Database models (SQLAlchemy)
- [x] Alembic migrations setup
- [x] Authentication (JWT)
- [x] Configuration management
- [x] API route structure
- [x] Pydantic schemas
- [x] Security utilities

### ✅ Chrome Extension Setup
- [x] React + TypeScript + Vite setup
- [x] Manifest V3 configuration
- [x] State management (Zustand)
- [x] API client service
- [x] Component structure
- [x] Page routing
- [x] Tailwind CSS setup

### ✅ Infrastructure
- [x] Docker & Docker Compose
- [x] Database (PostgreSQL)
- [x] Message Queue (Redis)
- [x] Celery workers
- [x] Celery Beat scheduler
- [x] Environment configuration

### ✅ Documentation
- [x] README.md
- [x] SETUP.md
- [x] ARCHITECTURE.md
- [x] .gitignore

---

## Phase 2: 🔄 Telegram & AI Integration (IN PROGRESS)

### Telegram Integration (Priority 1)
**Goal**: Enable full Telegram group operations
**Timeline**: Week 1-2

#### Tasks:
```
Backend Tasks:
  - [ ] Install pyrogram dependencies
  - [ ] Implement TelegramService methods
      - [ ] login_with_phone() - OTP flow
      - [ ] search_groups(query) - keyword search
      - [ ] get_group_info(group_id)
      - [ ] get_recent_messages(group_id, limit)
      - [ ] send_message(group_id, text)
      - [ ] delete_message(group_id, message_id)
      - [ ] join_group(group_link)
      - [ ] leave_group(group_id)
  - [ ] Create TelegramAccount model for session storage
  - [ ] Implement session encryption/decryption
  - [ ] Add Telegram login API endpoint
  - [ ] Add phone OTP verification endpoint
  - [ ] Add session persistence
  - [ ] Error handling for rate limits
  - [ ] Telegram flood-wait backoff
  - [ ] Unit tests for Telegram client

Extension Tasks:
  - [ ] Create Settings page (Telegram section)
  - [ ] Implement login flow
  - [ ] Handle OTP input
  - [ ] Display connection status
  - [ ] Add disconnect button
```

#### Critical Implementation Points:
1. **Session Management**:
   ```python
   # Encrypt session before storing
   session_string = client.export_session_string()
   encrypted = encrypt_credentials(session_string)
   telegram_account.session_string = encrypted
   db.commit()
   
   # Decrypt when using
   decrypted = decrypt_credentials(telegram_account.session_string)
   client = TelegramService().get_client(session_string=decrypted)
   ```

2. **Phone Login OTP Flow**:
   ```
   Frontend: User enters phone number
   Backend: Send code request to Telegram
   Telegram: Sends code to user's app
   Frontend: User enters code
   Backend: Verify code
   Backend: Ask for 2FA password if needed
   Backend: Return session string
   Frontend: Connection successful
   ```

3. **Error Handling**:
   ```python
   try:
       await client.send_message(group_id, text)
   except FloodWait as fw:
       # Wait fw.value seconds before retry
       logger.warning(f"Flood wait: {fw.value}s")
       raise
   except AuthBytesInvalid:
       # Session expired, need re-login
       raise HTTPException(401, "Session expired")
   except Exception as e:
       logger.error(f"Telegram error: {e}")
       raise
   ```

### AI Integration (Priority 2)
**Goal**: Enable group analysis with OpenAI & Claude
**Timeline**: Week 2-3

#### Tasks:
```
Backend Tasks:
  - [ ] Implement OpenAIProvider
      - [ ] analyze_group() method
      - [ ] recommend_post() method
      - [ ] analyze_messages_for_opportunities() method
      - [ ] Error handling for API errors
      - [ ] Token counting
  - [ ] Implement ClaudeProvider
      - [ ] analyze_group() method
      - [ ] recommend_post() method
      - [ ] analyze_messages_for_opportunities() method
      - [ ] Error handling
  - [ ] Create AISettings model for per-user config
  - [ ] Implement provider factory
  - [ ] Add /api/settings/ai endpoints
  - [ ] Test AI response validation (Pydantic)
  - [ ] Implement retry logic for failed analyses
  - [ ] Cache analyses for same group

Extension Tasks:
  - [ ] Create Settings > AI section
  - [ ] Provider selection (OpenAI/Claude)
  - [ ] API key input with encryption
  - [ ] Model selection dropdown
  - [ ] Temperature/token configuration
  - [ ] Save settings to backend
```

#### Critical Implementation Points:
1. **Prompt Engineering**:
   - Keep prompts concise
   - Request JSON output
   - Specify expected schema
   - Include confidence scoring

2. **Response Validation**:
   ```python
   # Use Pydantic to validate AI response
   class GroupAnalysisResponse(BaseModel):
       group_types: List[str]
       partnership_suitability: str
       confidence_score: int
   
   try:
       response_data = json.loads(ai_response)
       validated = GroupAnalysisResponse(**response_data)
   except ValidationError as e:
       logger.error(f"Invalid AI response: {e}")
       # Retry or fallback
   ```

3. **Cost Optimization**:
   - Cache analyses for 30 days
   - Batch similar requests
   - Use smaller models for simple tasks

### Celery Task Implementation
**Goal**: Background job execution
**Timeline**: Ongoing (Week 1-3)

#### Tasks:
```
  - [ ] Implement analyze_group_task
  - [ ] Implement monitor_replies_task
  - [ ] Implement analyze_opportunities_task
  - [ ] Add task status tracking
  - [ ] Add error handling & retries
  - [ ] Add task result storage
  - [ ] Implement task progress updates
  - [ ] Add logs to system_logs table
```

---

## Phase 3: 📝 Post Management (Week 3-4)

### Tasks:
```
Backend:
  - [ ] Complete posts CRUD API
  - [ ] Implement post recommendation logic
  - [ ] Create group-post assignment table
  - [ ] Add duplicate post functionality
  - [ ] Add post templates/snippets
  - [ ] Implement post history tracking
  - [ ] Add post analytics

Extension:
  - [ ] Create Posts page
  - [ ] Post creation form
  - [ ] Post editing form
  - [ ] Post deletion confirmation
  - [ ] Post preview
  - [ ] Post type selection
  - [ ] Tags & links management
  - [ ] Duplicate functionality
  - [ ] Usage statistics per post
```

### Critical Features:
1. **Post Recommendation Engine**:
   - Compare group type with post content
   - Score compatibility (0-100)
   - Rank available posts
   - Explain why recommended

2. **Draft Saving**:
   - Auto-save while editing
   - Recover unsaved drafts
   - Version history

---

## Phase 4: ⏰ Scheduler & Automatic Posting (Week 4-5)

### Tasks:
```
Backend:
  - [ ] Implement SchedulerSettings model
  - [ ] Implement scheduler API endpoints
  - [ ] Implement posting eligibility check
  - [ ] Implement skip logic (20 messages rule)
  - [ ] Implement rate limiting
  - [ ] Queue posting tasks to Celery
  - [ ] Record posting results
  - [ ] Handle Telegram errors gracefully
  - [ ] Implement message deletion
  - [ ] Add scheduler status endpoint
  - [ ] Add posting history view

Extension:
  - [ ] Create Scheduler page
  - [ ] Mode selection (Manual/Automatic)
  - [ ] Time range picker
  - [ ] Day selection checkboxes
  - [ ] Timezone selector
  - [ ] Min messages config
  - [ ] Max posts/hour config
  - [ ] Max posts/day config
  - [ ] Start/pause buttons
  - [ ] Show next scheduled post
  - [ ] Show recent posting history
```

### Critical Implementation:
1. **Skip Logic**:
   ```python
   def should_skip_posting(user_id, group_id):
       last_post = db.query(PostHistory).filter(
           PostHistory.user_id == user_id,
           PostHistory.group_id == group_id,
           PostHistory.status == "success"
       ).order_by(PostHistory.created_at.desc()).first()
       
       if not last_post:
           return False, ""  # Never posted
       
       # Check time limit (60 seconds)
       if datetime.utcnow() - last_post.posted_at < timedelta(seconds=60):
           return True, "Posted < 60 seconds ago"
       
       # Check message count (20 messages minimum)
       # TODO: Get actual message count from Telegram
       # For now, use time-based estimation
       
       return False, ""
   ```

2. **Celery Beat Scheduler**:
   ```python
   # In celery_app.conf.beat_schedule
   'check-scheduler-every-minute': {
       'task': 'app.workers.tasks.check_scheduler',
       'schedule': crontab(minute='*/1'),
   }
   
   @celery_app.task
   def check_scheduler():
       settings_list = db.query(SchedulerSettings).filter(
           SchedulerSettings.posting_mode == "automatic"
       ).all()
       
       for setting in settings_list:
           if is_in_active_window(setting):
               # Queue posting tasks
               for group in get_feed_groups(setting.user_id):
                   if should_skip_posting(setting.user_id, group.id):
                       continue
                   post_to_group_task.delay(...)
   ```

3. **Persistent State**:
   - Store scheduler state in DB
   - Survive backend restarts
   - Track last group posted to
   - Resume from last position

---

## Phase 5: 💬 Reply Monitoring (Week 5-6)

### Tasks:
```
Backend:
  - [ ] Implement reply monitoring task
  - [ ] Get recent messages for each group
  - [ ] Filter replies to user's posts
  - [ ] Create Reply records
  - [ ] Create Notification records
  - [ ] Add unread count endpoint
  - [ ] Add mark as read functionality
  - [ ] Add mark all as read
  - [ ] Add reply detail view

Extension:
  - [ ] Create Replies/Notifications page
  - [ ] Show unread count badge
  - [ ] List all notifications
  - [ ] Filter by group
  - [ ] Filter by status (read/unread)
  - [ ] Show reply detail
  - [ ] Mark as read button
  - [ ] Mark all as read button
  - [ ] Delete notification
  - [ ] Link to original post
```

### Critical Implementation:
1. **Reply Detection**:
   ```python
   # Get messages since last check
   messages = telegram_service.get_recent_messages(group_id, limit=100)
   
   for msg in messages:
       # Check if reply to user's post
       if msg.reply_to_message_id:
           original = db.query(PostHistory).filter(
               PostHistory.telegram_message_id == str(msg.reply_to_message_id)
           ).first()
           
           if original:
               # This is a reply to user's post
               reply = Reply(...)
               db.add(reply)
   ```

---

## Phase 6: 🎯 Advanced Features (Week 6-7)

### Opportunity Analysis
**Goal**: Identify potential investors and partners

#### Tasks:
```
Backend:
  - [ ] Implement opportunity analysis task
  - [ ] Call AI to analyze messages
  - [ ] Parse AI response for opportunities
  - [ ] Create Opportunity records
  - [ ] Store evidence & reasoning
  - [ ] Add confidence scoring
  - [ ] Add /api/opportunities endpoints
  - [ ] Add opportunity filtering
  - [ ] Add opportunity status tracking

Extension:
  - [ ] Create Opportunities page
  - [ ] Show opportunity list
  - [ ] Filter by type (Investment/Partnership)
  - [ ] Filter by confidence level
  - [ ] Show opportunity details
  - [ ] Show evidence message
  - [ ] Mark status (new/reviewed/contacted/dismissed)
  - [ ] Export opportunities list
```

#### Implementation:
```python
# AI Prompt for Opportunity Analysis
async def analyze_opportunities(messages):
    prompt = f"""
    Analyze these messages for investment and partnership opportunities.
    
    Messages:
    {json.dumps(messages, indent=2)}
    
    For each person who might be:
    1. An investor (looks for startups to invest in)
    2. A partner (looks for business partnerships)
    
    Return JSON:
    {{
        "opportunities": [
            {{
                "user_id": "...",
                "type": "Investment|Partnership",
                "evidence": "...",
                "confidence": "High|Medium|Low",
                "reason": "..."
            }}
        ]
    }}
    """
    
    response = await ai_provider.analyze_messages_for_opportunities(messages)
    
    for opp in response:
        record = Opportunity(
            user_id=user_id,
            group_id=group_id,
            telegram_user_id=opp['user_id'],
            opportunity_type=opp['type'],
            evidence=opp['evidence'],
            confidence=opp['confidence'],
            relevance_reason=opp['reason'],
            status='new'
        )
        db.add(record)
    
    db.commit()
```

### Dashboard & Statistics
#### Tasks:
```
Backend:
  - [ ] Implement statistics aggregation
  - [ ] Cache stats for performance
  - [ ] Add /api/statistics endpoint
  - [ ] Add posting trend data
  - [ ] Add success rate metrics
  - [ ] Add reply rate metrics

Extension:
  - [ ] Create Dashboard page
  - [ ] Show key metrics (cards)
  - [ ] Show posting trend chart
  - [ ] Show reply trends
  - [ ] Show success/skip/fail breakdown
  - [ ] Show next scheduled post
  - [ ] Show recent activity feed
  - [ ] Show scheduler status
  - [ ] Show Telegram connection status
```

---

## Implementation Checklist for Each Feature

### When implementing a feature, follow this checklist:

1. **Database**
   - [ ] Add/update model
   - [ ] Create migration
   - [ ] Add indexes if needed
   - [ ] Test migration

2. **Backend API**
   - [ ] Create schema (Pydantic)
   - [ ] Implement route
   - [ ] Add validation
   - [ ] Add error handling
   - [ ] Add tests
   - [ ] Update OpenAPI docs

3. **Services/Business Logic**
   - [ ] Implement core logic
   - [ ] Add error handling
   - [ ] Add logging
   - [ ] Add retry logic if needed
   - [ ] Unit tests

4. **Celery Tasks** (if async)
   - [ ] Define task
   - [ ] Add error handling
   - [ ] Add retries
   - [ ] Add logging
   - [ ] Test task

5. **Extension**
   - [ ] Create page component
   - [ ] Add API calls
   - [ ] Add state management
   - [ ] Add error handling
   - [ ] Add loading states
   - [ ] Add styling
   - [ ] Test user flow

6. **Testing**
   - [ ] Unit tests
   - [ ] Integration tests
   - [ ] End-to-end tests

7. **Documentation**
   - [ ] Update API docs
   - [ ] Add code comments
   - [ ] Update README if needed

---

## Testing Strategy

### Backend Testing
```bash
# Run all tests
docker-compose exec backend pytest -v

# Run specific test file
docker-compose exec backend pytest tests/test_core.py -v

# Run with coverage
docker-compose exec backend pytest --cov=app tests/
```

### Extension Testing
```bash
cd extension

# Run tests
npm run test

# Run with coverage
npm run test -- --coverage
```

### Manual Testing
1. Start all services: `docker-compose up -d`
2. Open extension in Chrome
3. Walk through each feature manually
4. Test error cases
5. Check logs for issues

---

## Deployment Steps

### 1. Pre-Deployment
```bash
# Run full test suite
docker-compose exec backend pytest -v
cd extension && npm run test

# Build extension
npm run build

# Generate database migrations
docker-compose exec backend alembic upgrade head
```

### 2. Docker Deployment
```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Push to registry
docker push your-registry/telegram-bot-backend
docker push your-registry/telegram-bot-worker

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Post-Deployment
```bash
# Check services
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Verify API
curl https://your-domain/health
```

---

## Performance Optimization

### Database
- [ ] Add indexes on frequently queried fields
- [ ] Use pagination for list endpoints
- [ ] Cache group analyses (30 day TTL)
- [ ] Archive old posting history

### API
- [ ] Add response caching headers
- [ ] Implement compression
- [ ] Use connection pooling
- [ ] Batch Telegram API calls

### Extension
- [ ] Lazy load pages
- [ ] Cache API responses locally
- [ ] Minify bundles
- [ ] Use service worker for offline

### Celery
- [ ] Increase worker concurrency
- [ ] Implement priority queues
- [ ] Monitor task queue depth
- [ ] Scale workers based on load

---

## Monitoring & Alerts

### Metrics to Track
- API response time (p50, p95, p99)
- Database query time
- Celery task duration
- Posting success rate
- Error rate by type
- Extension active users
- Message queue depth

### Alerts to Setup
- API latency > 1000ms
- Database connection errors
- Celery worker down
- Posting failure rate > 5%
- Queue depth > 1000
- Disk space < 10%

---

## Security Audit Checklist

Before going to production:
- [ ] All credentials in .env, never in code
- [ ] JWT secret is strong (32+ random chars)
- [ ] Database password is strong
- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (using ORM)
- [ ] Rate limiting on auth endpoints
- [ ] Audit logging for sensitive operations
- [ ] Secrets management in place
- [ ] Database backups automated
- [ ] Monitoring & alerting setup

---

## Next Immediate Actions

1. **Today**: Review all files, test project structure
2. **Day 1-2**: Implement Telegram login flow
3. **Day 3-4**: Implement Telegram group search
4. **Day 5-6**: Implement OpenAI & Claude providers
5. **Day 7**: Complete Phase 2 testing

Then continue with Phases 3-6 as outlined above.

---

## Questions & Considerations

- Should we support multiple Telegram accounts per user?
- Should we cache group lists locally for offline access?
- What's the rate limit before we auto-disable posting?
- Should we allow users to bulk import groups from CSV?
- Should we support group aliases/labels?
- Should we have a "dry run" mode for posting?

---

**Last Updated**: 2026-09-22
**Status**: Phase 1 Complete, Phase 2 Starting
