# Setup and Installation Guide

## Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (recommended)

## Environment Setup

### 1. Clone Repository

```bash
cd /path/to/t-bot
```

### 2. Create .env File

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Telegram API credentials
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE_NUMBER=+1234567890

# AI Provider (choose one)
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql://telegram_user:telegram_password@localhost:5432/telegram_bot

# Redis
REDIS_URL=redis://localhost:6379

# JWT Secret (generate a strong random string, min 32 chars)
SECRET_KEY=your-super-secret-key-min-32-chars

# Extension
EXTENSION_ID=your-extension-id-from-chrome
```

### 3. Get Telegram Credentials

Visit https://my.telegram.org/auth to get:
- API ID
- API Hash

You'll need your Telegram account to log in.

## Docker Setup (Recommended)

### Start Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI backend (port 8000)
- Celery worker
- Celery beat scheduler

### Run Migrations

```bash
docker-compose exec backend alembic upgrade head
```

### View Logs

```bash
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

### Stop Services

```bash
docker-compose down
```

## Manual Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Celery Worker

In a separate terminal:

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start worker
celery -A app.workers.celery_app worker --loglevel=info
```

### Celery Beat (Scheduler)

In another terminal:

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Start beat scheduler
celery -A app.workers.celery_app beat --loglevel=info
```

### Chrome Extension Setup

```bash
cd extension

# Install dependencies
npm install

# Development mode (with hot reload)
npm run dev

# Build for production
npm run build
```

### Load Extension in Chrome

1. Open `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select `extension/dist` directory

## Database Migrations

### Create New Migration

```bash
docker-compose exec backend alembic revision --autogenerate -m "Description"
```

### Apply Migration

```bash
docker-compose exec backend alembic upgrade head
```

### Rollback Migration

```bash
docker-compose exec backend alembic downgrade -1
```

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

## API Documentation

Once backend is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Development Workflow

### Phase 1: Core Infrastructure ✅
- [x] Database schema
- [x] Authentication system
- [x] Basic API routes
- [x] Docker setup
- [ ] Test coverage

### Phase 2: Telegram & AI Integration 🔄
- [ ] Complete Telegram client integration
- [ ] OpenAI provider implementation
- [ ] Claude provider implementation
- [ ] Group analysis tasks

### Phase 3: Post Management
- [ ] Post recommendation engine
- [ ] AI post selection
- [ ] Feed management

### Phase 4: Scheduler & Posting
- [ ] Scheduler logic
- [ ] Automatic posting
- [ ] Rate limiting
- [ ] Skip logic

### Phase 5: Monitoring
- [ ] Reply monitoring
- [ ] Notifications
- [ ] Statistics

### Phase 6: Advanced Features
- [ ] Opportunity analysis
- [ ] Investor identification
- [ ] Advanced filtering

## Troubleshooting

### Database Connection Error

```bash
# Check database is running
docker-compose ps

# View database logs
docker-compose logs postgres

# Recreate database
docker-compose down -v
docker-compose up -d
```

### Redis Connection Error

```bash
# Check Redis is running
docker-compose ps

# Test Redis connection
redis-cli ping
```

### Extension Not Connecting

1. Check backend is running: `curl http://localhost:8000/health`
2. Open DevTools (F12) in extension popup
3. Check Console for errors
4. Verify CORS configuration in `.env`

### API Returns 401 Unauthorized

- Token may have expired
- Check .env SECRET_KEY matches deployment
- Try logging out and back in

## Production Deployment

### Before Deploying

- [ ] Change SECRET_KEY to strong random value
- [ ] Set ENVIRONMENT=production
- [ ] Enable HTTPS
- [ ] Configure firewall
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Run full test suite

### Docker Production Deploy

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Security Checklist

- [ ] HTTPS/TLS enabled
- [ ] Strong SECRET_KEY configured
- [ ] Database credentials rotated
- [ ] API keys stored securely
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Audit logging enabled
- [ ] Backups configured

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Review API docs: http://localhost:8000/docs
3. Check GitHub issues
4. Contact support

## License

Proprietary - All rights reserved
