# Halal Checker API Documentation

## Overview

The Halal Checker API uses Google Gemini AI to analyze product descriptions and ingredient lists to determine if they are halal-compliant and safe for consumption.

## Features

- ✅ Halal compliance checking using AI (Gemini Flash)
- ✅ Food safety analysis
- ✅ Ingredient detection
- ✅ Allergen identification
- ✅ Device-based user management
- ✅ Product check history
- ✅ Detailed reasoning for each analysis

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and update with your credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

Get your Gemini API key from: https://makersuite.google.com/app/apikey

### 3. Run the Application

```bash
# From the backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or from the root directory
cd backend && uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

API Documentation (Swagger UI): `http://localhost:8000/docs`

## API Endpoints

### 1. Analyze Product

**Endpoint:** `POST /api/v1/halal-check/analyze`

Analyze a product description or ingredient list for halal compliance.

**Request Body:**
```json
{
  "text": "Doritos Nacho Cheese Chips - Ingredients: Corn, Vegetable Oil, Whey, Cheddar Cheese, Salt",
  "device_id": "unique-device-identifier-123"
}
```

**Response:**
```json
{
  "id": 1,
  "device_id": "unique-device-identifier-123",
  "product_name": "Doritos Nacho Cheese Chips",
  "is_halal": "doubtful",
  "is_edible": true,
  "result": {
    "product_name": "Doritos Nacho Cheese Chips",
    "is_halal": "doubtful",
    "halal_reason": "Contains cheese and whey which may be from non-halal sources...",
    "is_edible": true,
    "edible_reason": "Product is generally safe for human consumption",
    "detected_ingredients": [
      "Corn",
      "Vegetable Oil",
      "Whey",
      "Cheddar Cheese",
      "Salt"
    ],
    "harmful_or_suspicious": [
      "Whey - source unknown",
      "Cheddar Cheese - enzyme source unclear"
    ],
    "allergens": [
      "Milk (Whey, Cheese)"
    ],
    "overall_summary": "This product contains dairy ingredients..."
  },
  "created_at": "2025-11-18T10:30:00"
}
```

### 2. Get Product Check History

**Endpoint:** `GET /api/v1/halal-check/history/{device_id}`

Get the analysis history for a specific device.

**Parameters:**
- `device_id` (path): Unique device identifier
- `limit` (query, optional): Maximum number of results (default: 50)

**Response:**
```json
[
  {
    "id": 1,
    "product_name": "Doritos Nacho Cheese Chips",
    "is_halal": "doubtful",
    "is_edible": true,
    "created_at": "2025-11-18T10:30:00"
  },
  {
    "id": 2,
    "product_name": "Chicken Breast",
    "is_halal": "true",
    "is_edible": true,
    "created_at": "2025-11-18T09:15:00"
  }
]
```

### 3. Get Specific Check Details

**Endpoint:** `GET /api/v1/halal-check/check/{check_id}`

Get detailed information about a specific product check.

**Parameters:**
- `check_id` (path): The ID of the product check

**Response:**
Same structure as the analyze endpoint response.

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    device_id VARCHAR(255) UNIQUE NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME
);
```

### Product Checks Table
```sql
CREATE TABLE productchecks (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    device_id VARCHAR(255) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    is_halal VARCHAR(20),  -- 'true', 'false', or 'doubtful'
    is_edible BOOLEAN NOT NULL,
    result_json JSON NOT NULL,
    input_text TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Halal Analysis Response Format

The Gemini AI returns analysis in the following JSON structure:

```json
{
  "product_name": "Name of the product",
  "is_halal": "true/false/doubtful",
  "halal_reason": "Detailed explanation of halal status",
  "is_edible": true/false,
  "edible_reason": "Explanation of food safety",
  "detected_ingredients": ["ingredient1", "ingredient2"],
  "harmful_or_suspicious": ["suspicious ingredient1"],
  "allergens": ["allergen1", "allergen2"],
  "overall_summary": "Brief summary of the analysis"
}
```

## System Prompt (Gemini)

The system uses a strict prompt to ensure accurate halal compliance checking:

```
You are a strict and reliable Halal Compliance and Food Safety checker.
Your job is to analyze ANY product description, ingredient list, or textual 
product data and return a detailed halal/haram evaluation with clear explanations.

Rules:
1. Be accurate and strict about halal requirements
2. If an ingredient is unclear, treat it as "doubtful" and explain why
3. Do NOT guess - use reasoning based on general halal principles
4. Provide results ONLY in JSON format
5. Include human-edible safety checks (allergens, harmful substances)
6. Never include unnecessary text outside the JSON
```

## Example Usage (cURL)

```bash
# Analyze a product
curl -X POST "http://localhost:8000/api/v1/halal-check/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Coca Cola - Ingredients: Carbonated water, sugar, caramel color, phosphoric acid, natural flavors, caffeine",
    "device_id": "my-phone-123"
  }'

# Get history
curl "http://localhost:8000/api/v1/halal-check/history/my-phone-123"

# Get specific check
curl "http://localhost:8000/api/v1/halal-check/check/1"
```

## Error Handling

The API returns standard HTTP status codes:

- `200 OK` - Request successful
- `400 Bad Request` - Invalid input or API response
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "detail": "Error message here"
}
```

## Development

### Project Structure

```
backend/
├── app/
│   ├── config/
│   │   ├── core.py          # Settings and configuration
│   │   └── database.py      # Database session management
│   ├── models/
│   │   ├── halal_check.py   # User and ProductCheck models
│   │   └── texts.py         # Legacy models
│   ├── routers/
│   │   └── halal_check.py   # API endpoints
│   ├── schemas/
│   │   └── halal_check.py   # Pydantic schemas
│   ├── utils/
│   │   ├── database.py      # Database utilities
│   │   └── gemini.py        # Gemini AI service
│   └── main.py              # FastAPI application
├── .env                     # Environment variables
├── .env.example            # Example environment config
└── requirements.txt        # Python dependencies
```

### Adding New Features

1. **Add new endpoint**: Create or modify router in `app/routers/`
2. **Add new model**: Create model in `app/models/` and register in `__init__.py`
3. **Add new schema**: Create Pydantic schema in `app/schemas/`
4. **Modify AI behavior**: Update prompt in `app/utils/gemini.py`

## Security Notes

- Store API keys securely in `.env` file
- Never commit `.env` file to version control
- Use device_id to track users without requiring authentication
- Consider rate limiting for production use
- Add CORS configuration for frontend integration

## Production Deployment

For production deployment:

1. Use a production database (PostgreSQL recommended)
2. Set `DEBUG=False` in environment
3. Add proper CORS configuration
4. Implement rate limiting
5. Use HTTPS
6. Set up logging and monitoring
7. Configure proper error handling
8. Add authentication if needed

## Support

For issues or questions, please refer to the main project README or API documentation at `/docs`.

