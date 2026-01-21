#!/bin/bash

# Halal Checker API Startup Script

echo "🕌 Halal Checker API - Initialization"
echo "======================================"
echo ""

# Check if .env file exists
if [ ! -f "/app/.env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env file with default values..."
    echo "Please update GEMINI_API_KEY in backend/.env"
    cat > /app/.env << 'ENVEOF'
DEBUG=True
SQL_URL=sqlite+aiosqlite:///./halal_check.db
GEMINI_API_KEY=
ENVEOF
fi

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY is not set!"
    echo "Please add your Gemini API key to backend/.env"
    echo "Get your key from: https://makersuite.google.com/app/apikey"
    echo ""
fi


# Start the application
echo "🚀 Starting Halal Checker API..."
echo "📚 API Docs will be available at: http://localhost:8000/docs"
echo ""

# Run uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

