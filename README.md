# 🕌 Halal Checker App
AI-powered Halal compliance and food safety checker using Google Gemini Flash API.
## 🌟 Features
- ✅ **Halal Compliance Analysis** - Strict halal/haram determination
- 🔍 **Ingredient Detection** - Automatic ingredient identification
- ⚠️ **Allergen Detection** - Identifies common allergens
- 🛡️ **Safety Checks** - Food safety and edibility assessment
- 📱 **Device-Based Tracking** - User management via device ID
- 📝 **History** - Check previous product analyses
- 🤖 **AI-Powered** - Uses Google Gemini Flash for accurate analysis
## 🚀 Quick Start
### Prerequisites
- Docker & Docker Compose
- Google Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))
### 1. Clone & Setup
```bash
cd Halal-Check
```
### 2. Configure Environment
```bash
# Edit backend/.env and add your Gemini API key
nano backend/.env
```
Add your API key:
```env
DEBUG=True
SQL_URL=sqlite+aiosqlite:///./halal_check.db
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
### 3. Start the Application
```bash
# Build and start all services
make build
# Or manually:
docker compose up --build -d
```
### 4. Access the Application
- 📚 **API Documentation**: http://localhost:8000/docs
- 🌐 **Frontend**: http://localhost:3000  
- 💚 **Health Check**: http://localhost:8000/health
- 🔗 **API Base**: http://localhost:8000/api/v1
## 📖 API Usage
### Analyze Product
```bash
curl -X POST "http://localhost:8000/api/v1/halal-check/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Doritos Nacho Cheese - Ingredients: Corn, Vegetable Oil, Whey, Cheddar Cheese",
    "device_id": "my-device-123"
  }'
```
### Get History
```bash
curl "http://localhost:8000/api/v1/halal-check/history/my-device-123"
```
### Get Specific Check
```bash
curl "http://localhost:8000/api/v1/halal-check/check/1"
```
## 🛠️ Development Commands
```bash
make help          # Show all available commands
make build         # Build and start containers
make down          # Stop containers
make restart       # Restart all services
make logs          # Show all logs
make logs-backend  # Show backend logs only
make test          # Test the API
make dev           # Run backend in dev mode (local)
```
## 📁 Project Structure
```
Halal-Check/
├── backend/
│   ├── app/
│   │   ├── config/       # Configuration
│   │   ├── models/       # Database models
│   │   ├── routers/      # API endpoints
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── utils/        # Utilities (Gemini service)
│   │   └── main.py       # FastAPI app
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env              # Environment variables
├── frontend/             # Frontend application
├── docker-compose.yml    # Docker configuration
└── Makefile             # Development commands
```
## 🔧 Configuration
### Environment Variables (`backend/.env`)
```env
# Debug mode
DEBUG=True
# Database (SQLite for development)
SQL_URL=sqlite+aiosqlite:///./halal_check.db
# Google Gemini API Key (REQUIRED)
GEMINI_API_KEY=your_api_key_here
```
## 📊 Database Schema
### Users Table
- `id` - Primary key
- `device_id` - Unique device identifier
- `created_at` - Timestamp
### ProductChecks Table
- `id` - Primary key
- `user_id` - Foreign key to users
- `device_id` - Device identifier
- `product_name` - Product name
- `is_halal` - "true"/"false"/"doubtful"
- `is_edible` - Boolean
- `result_json` - Full analysis result
- `input_text` - Original input
- `created_at` - Timestamp
## 🤖 AI Response Format
```json
{
  "product_name": "Product name",
  "is_halal": "true/false/doubtful",
  "halal_reason": "Detailed explanation",
  "is_edible": true,
  "edible_reason": "Safety explanation",
  "detected_ingredients": ["ingredient1", "ingredient2"],
  "harmful_or_suspicious": ["suspicious item"],
  "allergens": ["allergen1"],
  "overall_summary": "Brief summary"
}
```
## 🐛 Troubleshooting
### API not starting?
```bash
# Check logs
make logs-backend
# Rebuild containers
make restart
```
### Database issues?
```bash
# Reset database
make down_v
make build
```
### Can't connect to API?
1. Check containers: `docker compose ps`
2. Check health: `curl http://localhost:8000/health`
3. Check logs: `make logs-backend`
### Gemini API errors?
1. Verify API key in `backend/.env`
2. Check key is valid at https://makersuite.google.com/app/apikey
3. Ensure no extra spaces in `.env` file
## 📚 Documentation
- [API Documentation](backend/API_DOCUMENTATION.md) - Complete API reference
- [Interactive API Docs](http://localhost:8000/docs) - Swagger UI
## 🔒 Security Notes
- Never commit `.env` file
- Store API keys securely
- Add rate limiting for production
- Enable HTTPS in production
