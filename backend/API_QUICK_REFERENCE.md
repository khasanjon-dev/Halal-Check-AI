# 🕌 Halal Checker API - Quick Reference

## Available Endpoints

### 1. Text Analysis
**POST** `/api/v1/halal-check/analyze`

```bash
curl -X POST "http://localhost:8000/api/v1/halal-check/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Chicken breast, salt, pepper",
    "device_id": "my-device-123"
  }'
```

### 2. Image Analysis (NEW!)
**POST** `/api/v1/halal-check/analyze-image`

```bash
curl -X POST "http://localhost:8000/api/v1/halal-check/analyze-image" \
  -F "image=@product_label.jpg" \
  -F "device_id=my-device-123"
```

### 3. Get History
**GET** `/api/v1/halal-check/history/{device_id}`

```bash
curl "http://localhost:8000/api/v1/halal-check/history/my-device-123"
```

### 4. Get Check Details
**GET** `/api/v1/halal-check/check/{check_id}`

```bash
curl "http://localhost:8000/api/v1/halal-check/check/1"
```

## Response Format (All Endpoints)

```json
{
  "id": 1,
  "device_id": "my-device-123",
  "product_name": "Product Name",
  "is_halal": "halal|haram|doubtful",
  "is_edible": true,
  "result": {
    "product_name": "Product Name",
    "is_halal": "halal",
    "halal_reason": "Explanation...",
    "is_edible": true,
    "edible_reason": "Safety info...",
    "detected_ingredients": ["ingredient1"],
    "harmful_or_suspicious": ["item1"],
    "allergens": ["allergen1"],
    "overall_summary": "Summary..."
  },
  "created_at": "2025-11-18T12:00:00"
}
```

## Image Requirements

- **Formats**: JPEG, PNG, GIF, WEBP
- **Max Size**: 10MB
- **Tip**: Clear, well-lit photos work best

## Testing

### With Test Scripts
```bash
# Text analysis
python backend/test_halal_checker.py

# Image analysis
python backend/test_image_api.py product_label.jpg
```

### With Swagger UI
http://localhost:8000/docs

## Start Server
```bash
cd backend
uvicorn app.main:app --reload
```

## API Documentation
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

