# 🕌 Halal Checker API - Quick Reference

## 🚀 Quick Start Commands

```bash
# Start everything
make build

# Stop everything  
make down

# View logs
make logs

# Test API
make test
```

## 📡 API Endpoints

### Base URL: `http://localhost:8000/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/halal-check/analyze` | Analyze product for halal compliance |
| GET | `/halal-check/history/{device_id}` | Get user's check history |
| GET | `/halal-check/check/{check_id}` | Get specific check details |
| GET | `/health` | Health check |
| GET | `/docs` | Interactive API documentation |

## 📝 Request Format

```json
{
  "text": "Product description or ingredients list",
  "device_id": "unique-device-identifier"
}
```

## 📊 Response Format

```json
{
  "id": 1,
  "device_id": "device-123",
  "product_name": "Product Name",
  "is_halal": "true/false/doubtful",
  "is_edible": true,
  "result": {
    "product_name": "Product Name",
    "is_halal": "true/false/doubtful",
    "halal_reason": "Detailed explanation...",
    "is_edible": true,
    "edible_reason": "Safety explanation...",
    "detected_ingredients": ["ingredient1", "ingredient2"],
    "harmful_or_suspicious": ["suspicious1"],
    "allergens": ["allergen1"],
    "overall_summary": "Brief summary..."
  },
  "created_at": "2025-11-18T10:30:00"
}
```

## 🧪 Test Examples

### Example 1: Halal Product
```bash
curl -X POST "http://localhost:8000/api/v1/halal-check/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Fresh Chicken Breast - 100% Halal Certified",
    "device_id": "test-123"
  }'
```

### Example 2: Doubtful Product
```bash
curl -X POST "http://localhost:8000/api/v1/halal-check/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Doritos Chips - Ingredients: Corn, Cheese, Whey, Natural Flavors",
    "device_id": "test-123"
  }'
```

### Example 3: Haram Product
```bash
curl -X POST "http://localhost:8000/api/v1/halal-check/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Gummy Bears - Contains: Gelatin (from pork)",
    "device_id": "test-123"
  }'
```

## 🔧 Configuration

### Required Environment Variables (.env)
```env
DEBUG=True
SQL_URL=sqlite+aiosqlite:///./halal_check.db
GEMINI_API_KEY=your_api_key_here
```

### Get Gemini API Key
https://makersuite.google.com/app/apikey

## 🐳 Docker Commands

```bash
# Build and start
docker compose up --build -d

# Stop
docker compose down

# View logs
docker compose logs -f backend

# Restart
docker compose restart

# Remove everything including data
docker compose down -v
```

## 🛠️ Development

```bash
# Run locally (without Docker)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Verify installation
python backend/verify_installation.py

# Test Gemini integration
python backend/test_halal_checker.py
```

## 📚 Documentation URLs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🐛 Common Issues

### "GEMINI_API_KEY is not set"
➡️ Add your API key to `backend/.env`

### "Port 8000 is already in use"
➡️ Stop other services: `lsof -i :8000` then `kill <PID>`

### "Database locked"
➡️ Restart services: `make restart`

### API not responding
➡️ Check logs: `make logs-backend`

## 📊 Database

**Location**: `backend/halal_check.db` (SQLite)

**Tables**:
- `users` - Device-based user tracking
- `productchecks` - Analysis results storage

## 🎯 Status Codes

- `200` - Success
- `400` - Bad request (invalid input)
- `404` - Not found
- `500` - Server error

## 🔒 Security

- Never commit `.env` file
- Keep API keys secret
- Add rate limiting for production
- Use HTTPS in production

## 💡 Tips

1. Use meaningful device_id for tracking
2. Check history before analyzing duplicate products
3. Use Swagger UI for testing during development
4. Monitor logs for debugging
5. Keep API key secure

## 📞 Support

- Full API Docs: `backend/API_DOCUMENTATION.md`
- Setup Guide: `SETUP_SUMMARY.md`
- Main README: `README.md`

---

**Last Updated**: November 18, 2025
**Version**: 1.0.0

