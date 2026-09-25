# Telegram Intelligence & Automated Posting System

A Chrome Extension + FastAPI backend for discovering, analyzing, and automatically posting to Telegram groups with AI-powered recommendations. Core workflows are implemented; production deployment still requires real Telegram/AI credentials and dependency installation.

## Features

### Core
- 🔍 **Group Discovery**: Search and discover Telegram groups by keywords
- 🧠 **AI Analysis**: Analyze groups using OpenAI or Claude to determine posting suitability
- 📊 **Dashboard**: Professional SaaS-style dashboard with analytics
- 📝 **Post Management**: Create, edit, and manage reusable posts
- 🤖 **AI Recommendations**: Get AI-recommended posts for each group
- ⏰ **Smart Scheduler**: Schedule automatic posting with configurable rules
- 💬 **Reply Monitoring**: Track and manage replies to your posts
- 🎯 **Opportunity Discovery**: Identify potential investors and partners in group conversations
- 📈 **Statistics**: Track posting history, success rates, and engagement

### Security
- ✅ Fernet-encrypted Telegram session storage
- ✅ JWT-based authentication
- ✅ Backend-only Telegram access
- ✅ Rate limiting and anti-spam protection
- ✅ Audit logging

## Architecture

```
Chrome Extension (React + TypeScript)
    ↓ HTTPS + JWT
FastAPI Backend
    ├── REST API
    ├── Telegram Client (pyrogram)
    └── Job Queue (Celery + Redis)
    ↓
PostgreSQL + Redis
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for extension development)
- Python 3.11+
- Telegram API credentials (from https://my.telegram.org)

### 1. Clone & Setup

```bash
cd t-bot
cp .env.example .env
# Edit .env with your credentials
```

### 2. Start Backend Services

```bash
docker-compose up -d
```

Docker reads integration settings from `.env`. Set `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `SECRET_KEY`, and at least one AI provider key before using those features.

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI backend (port 8000)
- Celery worker
- Celery beat (scheduler)

### 3. Run Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### 4. Build Chrome Extension

```bash
cd extension
npm install
npm run build
```

Load the extension in Chrome:
1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `extension/dist`

### 5. Access Dashboard

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Extension: Click extension icon in toolbar

## Project Structure

```
t-bot/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   ├── workers/          # Celery tasks
│   │   ├── ai/               # AI provider abstractions
│   │   ├── telegram/         # Telegram integration
│   │   ├── core/             # Core utilities
│   │   └── main.py           # FastAPI app
│   ├── migrations/           # Alembic migrations
│   ├── tests/                # Test suite
│   ├── requirements.txt
│   └── Dockerfile
│
├── extension/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── hooks/            # Custom hooks
│   │   ├── services/         # API client
│   │   ├── stores/           # State management
│   │   ├── types/            # TypeScript types
│   │   └── main.tsx          # Entry point
│   ├── public/
│   │   ├── manifest.json
│   │   └── icons/
│   ├── package.json
│   └── vite.config.ts
│
├── docker-compose.yml
├── .env.example
└── README.md
```

## Development

### Backend Development

```bash
# Start backend with hot-reload
docker-compose up backend

# Run migrations
docker-compose exec backend alembic revision --autogenerate -m "description"
docker-compose exec backend alembic upgrade head

# Run tests
docker-compose exec backend pytest

# Access API docs
curl http://localhost:8000/docs
```

### Extension Development

```bash
cd extension

# Install dependencies
npm install

# Development with hot-reload
npm run dev

# Build for production
npm run build

# Run tests
npm run test
```

## API Documentation

Full OpenAPI documentation available at `/docs` endpoint.

Key endpoints:

```
POST   /api/auth/login              # User login
GET    /api/groups/search           # Search Telegram groups
POST   /api/groups/{id}/analyze     # Analyze group with AI
GET    /api/feed                    # Get user's group feed
POST   /api/posts                   # Create new post
GET    /api/scheduler               # Get scheduler config
POST   /api/scheduler/start         # Start auto-posting
GET    /api/notifications           # Get notifications
GET    /api/opportunities           # Get identified opportunities
GET    /api/statistics              # Get posting statistics
```

## Database

Migrations are handled with Alembic:

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Configuration

All configuration is managed via `.env` file:

- `DATABASE_URL`: PostgreSQL connection
- `REDIS_URL`: Redis connection
- `TELEGRAM_API_ID`: From https://my.telegram.org
- `TELEGRAM_API_HASH`: From https://my.telegram.org
- `OPENAI_API_KEY`: For OpenAI integration
- `ANTHROPIC_API_KEY`: For Claude integration
- `SECRET_KEY`: For JWT signing (min 32 chars)

## Testing

### Backend Tests

```bash
docker-compose exec backend pytest -v
```

### Extension Tests

```bash
cd extension
npm run test
```

## Deployment

### Production Checklist

- [ ] Update `.env` with production credentials
- [ ] Set `ENVIRONMENT=production`
- [ ] Use strong `SECRET_KEY` (32+ random chars)
- [ ] Enable HTTPS
- [ ] Configure firewall
- [ ] Set up monitoring/logging
- [ ] Run database migrations
- [ ] Test all critical flows

### Docker Production Deployment

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

The production override enables restart policies and runs Alembic before starting the API. Put the deployment behind HTTPS and provide a strong `SECRET_KEY`.

## Security Notes

⚠️ **Important:**
- Never commit `.env` file with real credentials
- Telegram API credentials are sensitive - rotate if compromised
- All credentials are encrypted at rest
- Extension never accesses Telegram credentials directly
- All external API calls go through backend
- Enable HTTPS in production
- Use strong, unique SECRET_KEY

## Rate Limiting

The system respects Telegram's rate limits:
- Automatic exponential backoff on `flood_wait` errors
- Configurable minimum posting interval (default: 60 seconds)
- Per-group message threshold before reposting (default: 20 messages)
- Daily post limits configurable per user

## Logging

All operations are logged for audit trails:

```
2026-09-22 10:32:15 [INFO] POST group_123456 successful
2026-09-22 10:33:02 [WARN] Rate limited, backing off
2026-09-22 10:35:20 [ERROR] Failed to analyze group_789
```

Sensitive information (credentials, API keys) is never logged.

## Troubleshooting

### Backend won't start
```bash
# Check database connection
docker-compose logs postgres

# Check migrations
docker-compose exec backend alembic current
docker-compose exec backend alembic history
```

### Extension can't connect to backend
```bash
# Verify CORS configuration in .env
# Check extension console for errors: F12 > Console
# Verify backend is running: curl http://localhost:8000/health
```

### No Telegram connection
```bash
# Verify credentials in .env
# Check Telegram API ID/hash from https://my.telegram.org
# Review backend logs: docker-compose logs backend
```

## Support & Issues

For issues, check:
1. Backend logs: `docker-compose logs backend`
2. Extension console: Press F12 in extension popup
3. Database: `docker-compose exec postgres psql -U telegram_user telegram_bot`

## License

Proprietary - All rights reserved

## Contributing

Internal development only.

---

Built with ❤️ | FastAPI • PostgreSQL • React • Telegram API • OpenAI • Anthropic
