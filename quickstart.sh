#!/bin/bash

# Halal Checker - Quick Start Script

echo "🕌 Halal Checker API - Quick Start"
echo "===================================="
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating .env file from template..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env and add your GEMINI_API_KEY"
    echo "   Get your API key from: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Press Enter after adding your API key to continue..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "🏗️  Building and starting containers..."
docker compose up --build -d

echo ""
echo "✅ Halal Checker API is starting!"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🌐 Frontend: http://localhost:3000"
echo "💚 Health Check: http://localhost:8000/health"
echo ""
echo "📋 Useful commands:"
echo "  make logs         - View logs"
echo "  make logs-backend - View backend logs only"
echo "  make down         - Stop services"
echo "  make restart      - Restart services"
echo "  make test         - Test the API"
echo ""
echo "🔍 Checking services..."
sleep 5

# Check if backend is up
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running!"
else
    echo "⚠️  Backend is starting... (check logs with: make logs-backend)"
fi

echo ""
echo "🎉 Setup complete! Visit http://localhost:8000/docs to try the API"

