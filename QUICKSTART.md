# Quick Start: Phase 2 in 5 Minutes

## The Fastest Way to Get Running

### Prerequisites
- Docker & Docker Compose installed
- Python 3.11+ (if running locally)
- Telegram account (for testing login)

### Step 1: Clone & Configure (2 minutes)

```bash
cd d:\ysh\t-bot

# Copy environment template
copy .env.example .env

# Edit .env with your values:
# - TELEGRAM_API_ID=your_id_from_my.telegram.org
# - TELEGRAM_API_HASH=your_hash_from_my.telegram.org  
# - OPENAI_API_KEY=your_openai_key (optional)
# - ANTHROPIC_API_KEY=your_claude_key (optional)
# - SECRET_KEY=generate_random_32_char_string
```

### Step 2: Start Services (1 minute)

```bash
# Start everything
docker-compose up -d

# Verify all running
docker-compose ps
# Should show: postgres ✓, redis ✓, backend ✓, celery_worker ✓, celery_beat ✓
```

### Step 3: Initialize Database (1 minute)

```bash
# Create tables
docker-compose exec backend alembic upgrade head

# Verify
docker-compose exec backend psql -U telegram_user -d telegram_bot -c "\dt"
```

### Step 4: Access the API (1 minute)

```bash
# Open in browser
http://localhost:8000/docs

# Or curl to test
curl http://localhost:8000/health
```

**Done! System is running.** 🎉

---

## Testing the API (Step by Step)

### 1. Create an Account

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# Response: {"access_token": "eyJ...", "refresh_token": "eyJ..."}
export TOKEN="eyJ..."  # Save token for next requests
```

### 2. Connect Telegram

```bash
# Step 1: Request code
curl -X POST http://localhost:8000/api/telegram/login/request-code \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890"}'

# You'll receive code in Telegram app

# Step 2: Verify code
curl -X POST http://localhost:8000/api/telegram/login/verify-code \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890", "code": "12345"}'

# If 2FA enabled, you need:
# curl -X POST http://localhost:8000/api/telegram/login/verify-2fa \
#   -H "Authorization: Bearer $TOKEN" \
#   -H "Content-Type: application/json" \
#   -d '{"password": "youraccountpassword"}'

# Step 3: Check status
curl -X GET http://localhost:8000/api/telegram/status \
  -H "Authorization: Bearer $TOKEN"

# Response: {"connected": true, "phone": "+1234567890", "first_name": "John"}
```

### 3. Search Groups

```bash
curl -X GET "http://localhost:8000/api/groups/search?q=python&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Response: List of 10 public Python groups with members count, verification, etc.
```

### 4. Analyze a Group

```bash
# First, add a group to your groups list
curl -X POST http://localhost:8000/api/groups/manual-add \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": 1,
    "name": "Python Developers",
    "username": "python_dev",
    "telegram_id": -1001234567890
  }'

# Then analyze it
curl -X POST http://localhost:8000/api/groups/1/analyze \
  -H "Authorization: Bearer $TOKEN"

# Response: {"status": "analysis_queued", "task_id": "abc123def456"}

# Monitor progress in logs
docker-compose logs -f celery_worker
```

---

## Key Endpoints Reference

### Authentication
```
POST   /api/auth/register          Register new user
POST   /api/auth/login             Login
POST   /api/auth/refresh           Refresh token
POST   /api/auth/logout            Logout
GET    /api/auth/me                Get current user
```

### Telegram Connection
```
POST   /api/telegram/login/request-code     Start login
POST   /api/telegram/login/verify-code      Verify SMS code
POST   /api/telegram/login/verify-2fa       Verify 2FA password
GET    /api/telegram/status                 Check connection
POST   /api/telegram/logout                 Disconnect
```

### Group Management
```
GET    /api/groups/search                   Search public groups
GET    /api/groups/{id}                     Get group details
POST   /api/groups/{id}/analyze             Start AI analysis
POST   /api/groups/{id}/add-to-feed         Add to your feed
POST   /api/groups/manual-add               Manually add group
```

### Feed Management
```
GET    /api/feed                            Get your feed
POST   /api/feed/add                        Add group to feed
PUT    /api/feed/reorder                    Reorder groups
PUT    /api/feed/{id}/toggle                Enable/disable group
DELETE /api/feed/{id}                       Remove from feed
```

---

## Common Tasks

### Task: Check if Telegram is Connected

```bash
curl http://localhost:8000/api/telegram/status \
  -H "Authorization: Bearer $TOKEN"
```

### Task: View Celery Tasks Running

```bash
docker-compose exec celery_worker celery -A app.workers.celery_app inspect active
```

### Task: View Task Queue

```bash
docker-compose exec redis redis-cli LLEN celery
```

### Task: Clear All Redis Cache

```bash
docker-compose exec redis redis-cli FLUSHALL
```

### Task: View Database

```bash
docker-compose exec postgres psql -U telegram_user -d telegram_bot

# Then in psql:
\dt                        # List all tables
SELECT * FROM users;       # View users
SELECT * FROM telegram_groups;  # View groups
\q                         # Exit
```

### Task: View Logs

```bash
# Backend logs
docker-compose logs -f backend

# Celery worker logs
docker-compose logs -f celery_worker

# Celery beat logs
docker-compose logs -f celery_beat

# Database logs
docker-compose logs -f postgres

# Redis logs
docker-compose logs -f redis
```

---

## Troubleshooting

### "Telegram account not connected"
**Solution**: Make sure you completed the login flow:
1. POST to /telegram/login/request-code
2. POST to /telegram/login/verify-code
3. Verify with /telegram/status

### "Connection refused" when accessing API
**Solution**: Check if backend is running:
```bash
docker-compose ps backend   # Should show "Up"
docker-compose logs backend  # Check for errors
```

### "Task not executing" in Celery
**Solution**: Check if Celery worker is running:
```bash
docker-compose ps celery_worker  # Should show "Up"
docker-compose logs celery_worker # Check for errors
```

### "Database connection error"
**Solution**: Restart database:
```bash
docker-compose restart postgres
docker-compose exec backend alembic upgrade head
```

### "API returns 401 Unauthorized"
**Solution**: Your token expired. Get a new one:
```bash
# Login again to get new token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'
```

---

## Extension Usage

The Chrome extension connects to this backend. To use it:

### 1. Load Extension in Chrome

```bash
cd extension
npm install
npm run build

# Then in Chrome:
# 1. Open chrome://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select: t-bot/extension/dist
```

### 2. Configure in Extension

```
Settings → Telegram Connection
- Click "Connect to Telegram"
- Follow phone verification
- Grant permissions

Settings → AI Provider
- Select: OpenAI or Claude
- Enter API key
- Save
```

### 3. Use Extension

```
1. Dashboard: View stats and recent activity
2. Groups: Search and add public groups
3. Posts: Manage your message templates
4. Feed: Reorder groups for posting
5. Scheduler: Set up automatic posting
6. Replies: View incoming replies to your posts
7. Opportunities: Find investor/partner opportunities
```

---

## Development Commands

```bash
# Start development backend with auto-reload
docker-compose exec backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start development extension with hot reload
cd extension && npm run dev

# Run tests
docker-compose exec backend pytest -v
cd extension && npm run test

# Format code
docker-compose exec backend black app/
docker-compose exec backend isort app/

# Lint code
docker-compose exec backend flake8 app/
cd extension && npm run lint

# Type check
docker-compose exec backend mypy app/
cd extension && npm run type-check
```

---

## What's Working in Phase 2

✅ **Telegram Integration**
- Login with phone OTP
- 2FA password handling
- Search public groups
- Get group info
- Send/delete messages
- Join/leave groups

✅ **AI Analysis**
- Group suitability assessment
- Post recommendations
- Opportunity detection (investor/partner)

✅ **Background Jobs**
- Analyze groups with AI
- Post to groups with rate limiting
- Monitor for replies
- Find opportunities
- Clean up old logs

✅ **API**
- All endpoints documented
- Error handling
- Authentication/authorization
- Rate limiting ready

---

## What's Next (Phase 3+)

🔲 **Post Management**
- Create/edit/delete post templates
- AI post recommendations
- Group-specific post variants

🔲 **Scheduler**
- Configure posting schedule
- Automatic posting at specific times
- Manual posting override

🔲 **Monitoring**
- Reply notifications
- Statistics dashboard
- Activity feed

🔲 **Opportunities**
- Investor/partner scoring
- Automated outreach suggestions
- Opportunity management

---

## Production Deployment

When ready to deploy to production:

```bash
# 1. Use environment variables from vault/secrets manager
export SECRET_KEY=<strong_random_key>
export DATABASE_URL=<prod_database>
export REDIS_URL=<prod_redis>
# ... etc

# 2. Use production docker-compose file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 3. Set up monitoring
# - Prometheus for metrics
# - Grafana for dashboards
# - ELK stack for logs

# 4. Configure backups
# - Daily database backups
# - Redis data persistence
# - Code versioning

# 5. Enable HTTPS
# - Let's Encrypt SSL certificates
# - Auto-renewal via certbot
# - Redirect HTTP to HTTPS
```

---

## Support

For detailed information:
- **API Documentation**: http://localhost:8000/docs
- **Setup Guide**: [SETUP.md](SETUP.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Phase 2 Details**: [PHASE_2_COMPLETE.md](PHASE_2_COMPLETE.md)
- **Development Roadmap**: [DEVELOPMENT.md](DEVELOPMENT.md)

---

## TL;DR - Get it Running NOW

```bash
# 1. Configure
cp .env.example .env
# Edit .env with your Telegram API ID/Hash

# 2. Start
docker-compose up -d

# 3. Initialize
docker-compose exec backend alembic upgrade head

# 4. Open
http://localhost:8000/docs

# 5. Test
# Use the Swagger UI to test endpoints
```

That's it! System is ready for testing. 🚀

---

**Phase 2 Complete - Ready to Test!**

*For questions, check the documentation files or review the code comments.*
