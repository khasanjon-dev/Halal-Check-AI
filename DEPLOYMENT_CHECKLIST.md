# 🚀 Halal Checker API - Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. Code & Configuration

- [ ] All code tested locally
- [ ] Environment variables configured
- [ ] Database migrations (if any) prepared
- [ ] API documentation up to date
- [ ] Error handling implemented
- [ ] Logging configured properly

### 2. Security

- [ ] `.env` file not in git repository
- [ ] API keys secured
- [ ] CORS settings configured for production domains
- [ ] Rate limiting implemented (recommended)
- [ ] Input validation in place
- [ ] SQL injection prevention (using SQLAlchemy ORM ✅)
- [ ] HTTPS enabled for production

### 3. Docker & Infrastructure

- [ ] Dockerfile optimized for production
- [ ] docker-compose.yml configured for production
- [ ] Health checks configured
- [ ] Resource limits set (CPU, memory)
- [ ] Proper volume mounts for data persistence
- [ ] Backup strategy for database

### 4. Database

- [ ] Production database configured (PostgreSQL recommended)
- [ ] Database backups automated
- [ ] Database connection pooling configured
- [ ] Database credentials secured

### 5. Monitoring & Logging

- [ ] Error logging to file/service
- [ ] Performance monitoring
- [ ] Uptime monitoring
- [ ] Alert system for failures

## 🔧 Production Configuration Changes

### 1. Update `.env` for Production

```env
DEBUG=False
SQL_URL=postgresql+asyncpg://user:password@db:5432/halal_check
GEMINI_API_KEY=your_production_api_key
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. Update `docker-compose.yml`

```yaml
services:
  backend:
    restart: always
    environment:
      - DEBUG=False
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 3. Add Rate Limiting

Install dependencies:
```bash
pip install slowapi
```

Add to `backend/app/main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### 4. Use PostgreSQL (Recommended)

```bash
# Add to docker-compose.yml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: halal_check
      POSTGRES_USER: halal_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  backend:
    depends_on:
      - db
    environment:
      - SQL_URL=postgresql+asyncpg://halal_user:secure_password@db:5432/halal_check

volumes:
  postgres_data:
```

### 5. Setup Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 6. SSL/TLS with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.yourdomain.com
```

## 🌐 Deployment Platforms

### Option 1: DigitalOcean/Linode/AWS EC2

1. Create a VPS instance
2. Install Docker & Docker Compose
3. Clone repository
4. Set environment variables
5. Run: `docker compose up -d`
6. Configure firewall (allow ports 80, 443)
7. Setup domain DNS

### Option 2: Google Cloud Run

1. Build container: `docker build -t gcr.io/PROJECT/halal-api .`
2. Push: `docker push gcr.io/PROJECT/halal-api`
3. Deploy: `gcloud run deploy --image gcr.io/PROJECT/halal-api`

### Option 3: AWS ECS/Fargate

1. Create ECR repository
2. Build and push image
3. Create ECS task definition
4. Create ECS service
5. Configure load balancer

### Option 4: Heroku

```bash
# Install Heroku CLI
# Login: heroku login
heroku create halal-checker-api
heroku container:push web
heroku container:release web
heroku config:set GEMINI_API_KEY=your_key
```

### Option 5: Railway/Render

1. Connect GitHub repository
2. Configure environment variables
3. Deploy automatically

## 📊 Monitoring Setup

### Option 1: Sentry (Error Tracking)

```bash
pip install sentry-sdk[fastapi]
```

```python
# In main.py
import sentry_sdk
sentry_sdk.init(dsn="your_sentry_dsn")
```

### Option 2: Prometheus + Grafana

Add metrics endpoint and configure Prometheus scraping.

### Option 3: Uptime Monitoring

- UptimeRobot (free)
- Pingdom
- Better Uptime
- StatusCake

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and push Docker image
        run: |
          docker build -t halal-api .
          docker push your-registry/halal-api
      - name: Deploy to server
        run: ssh user@server "cd /app && docker compose pull && docker compose up -d"
```

## 📈 Performance Optimization

- [ ] Enable response caching
- [ ] Use CDN for static assets
- [ ] Optimize database queries
- [ ] Add database indexes
- [ ] Use connection pooling
- [ ] Enable gzip compression
- [ ] Implement request batching

## 🔐 Security Hardening

- [ ] Keep dependencies updated
- [ ] Use security headers
- [ ] Implement request validation
- [ ] Add authentication (if needed)
- [ ] Enable HTTPS only
- [ ] Configure CORS properly
- [ ] Use secrets management
- [ ] Regular security audits

## 📝 Post-Deployment

- [ ] Test all endpoints in production
- [ ] Monitor logs for errors
- [ ] Check performance metrics
- [ ] Set up alerts
- [ ] Document API for users
- [ ] Create API usage guide
- [ ] Setup backup and recovery procedures

## 🆘 Rollback Plan

If something goes wrong:

```bash
# Quick rollback
docker compose down
git checkout previous-working-commit
docker compose up -d

# Or use tagged images
docker compose down
docker compose up -d --force-recreate backend:v1.0.0
```

## 📞 Support & Maintenance

- [ ] Set up support channels
- [ ] Create runbook for common issues
- [ ] Document troubleshooting steps
- [ ] Schedule regular maintenance
- [ ] Plan for scaling

---

**Ready for production?** Review this checklist carefully before deploying!

For local development, just run: `make build` 🚀

