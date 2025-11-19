# 🚀 Quick Start Guide

## Start the Application

### Using Docker (Easiest)
```bash
cd /Users/admin/Projects/StartApps/Halal-Check
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs

### Using Local Dev Servers

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate  # if using venv
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
- Frontend: http://localhost:5173
- Backend: http://localhost:8000/docs

---

## ⚠️ Before First Run

1. **Add Gemini API Key** to `backend/.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```
   Get key from: https://makersuite.google.com/app/apikey

2. **Install Frontend Dependencies** (if not done):
   ```bash
   cd frontend
   npm install
   ```

---

## Quick Test

### 1. Open Browser
http://localhost:5173 (or :3000 for Docker)

### 2. Test Text Analysis
- Click "Type Text"
- Enter: `Gelatin, Pork Extract, E120 (Carmine)`
- Click "Analyze Text"
- Should show: **Haram ✗**

### 3. Test Image Analysis
- Click "Scan Image"
- Upload any product label image
- Click "Analyze Image"
- Should show: OCR + Analysis

---

## API Test Commands

### Health Check
```bash
curl http://localhost:8000/health
```

### Text Analysis
```bash
curl -X POST http://localhost:8000/api/v1/halal-check/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Water, Sugar, Gelatin", "device_id": "test123"}'
```

### Image Analysis
```bash
curl -X POST http://localhost:8000/api/v1/halal-check/analyze-image \
  -F "image=@/path/to/image.jpg" \
  -F "device_id=test123"
```

---

## Project Structure

```
✅ Backend  → /backend/app/
   ├── main.py (entry point)
   ├── routers/halal_check.py (all endpoints)
   ├── models/halal_check.py (database)
   ├── schemas/halal_check.py (validation)
   └── utils/gemini.py (AI service)

✅ Frontend → /frontend/src/
   └── App.tsx (main component)

✅ Database → /data/halal_check.db
```

---

## Features

### Text Analysis
- Input: Product description or ingredients
- Output: Halal/Haram/Doubtful status + details

### Image Analysis  
- Input: Product label photo (max 10MB)
- Output: OCR + Halal analysis

### History Tracking
- All analyses saved by device_id
- View past checks per device

---

## Status Indicators

- 🟢 **Halal ✓** - Safe to consume
- 🔴 **Haram ✗** - Forbidden  
- 🟡 **Doubtful ⚠** - Needs verification

---

## Troubleshooting

### Backend Error: "GEMINI_API_KEY not set"
→ Add key to `backend/.env`

### Frontend Error: "Network Error"
→ Ensure backend is running on port 8000

### Frontend Error: "Cannot resolve lucide-react"
→ Run `npm install` in frontend folder

### Docker Error: "Cannot connect to Docker daemon"
→ Start Docker Desktop

---

## Documentation

- `COMPLETE_SETUP_SUMMARY.md` - Full setup guide
- `FRONTEND_INTEGRATION.md` - Frontend details
- `CLEANUP_SUMMARY.md` - Code cleanup log
- `QUICK_START.md` - This file

---

## Support

- Backend API Docs: http://localhost:8000/docs
- Test endpoints in Swagger UI
- Check Docker logs: `docker-compose logs -f`

---

**Ready to analyze! 🕌✨**

