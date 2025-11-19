#!/bin/bash

# Halal Checker API - Final Status Check
# Run this script to verify everything is working

echo "🕌 Halal Checker API - Final Status Check"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker
echo "1️⃣  Checking Docker..."
if ! docker --version > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker installed${NC}"

# Check docker-compose
if ! docker compose version > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose installed${NC}"
echo ""

# Check .env file
echo "2️⃣  Checking configuration..."
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}❌ backend/.env not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ backend/.env exists${NC}"

# Check GEMINI_API_KEY
if grep -q "GEMINI_API_KEY=.\+" backend/.env; then
    if ! grep -q "GEMINI_API_KEY=your_api_key_here\|GEMINI_API_KEY=your_gemini_api_key_here" backend/.env; then
        echo -e "${GREEN}✅ GEMINI_API_KEY is set${NC}"
    else
        echo -e "${YELLOW}⚠️  GEMINI_API_KEY needs a real value${NC}"
        echo "   Get your key from: https://makersuite.google.com/app/apikey"
    fi
else
    echo -e "${RED}❌ GEMINI_API_KEY not found in .env${NC}"
fi
echo ""

# Check project structure
echo "3️⃣  Checking project structure..."
REQUIRED_FILES=(
    "backend/app/main.py"
    "backend/app/routers/halal_check.py"
    "backend/app/models/halal_check.py"
    "backend/app/schemas/halal_check.py"
    "backend/app/utils/gemini.py"
    "backend/requirements.txt"
    "backend/Dockerfile"
    "backend/start.sh"
    "docker-compose.yml"
    "Makefile"
)

ALL_FILES_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $file"
    else
        echo -e "${RED}❌${NC} $file (MISSING)"
        ALL_FILES_EXIST=false
    fi
done
echo ""

# Check if containers are running
echo "4️⃣  Checking Docker containers..."
if docker compose ps | grep -q "halal-check-backend"; then
    if docker compose ps | grep "halal-check-backend" | grep -q "Up"; then
        echo -e "${GREEN}✅ Backend container is running${NC}"

        # Test health endpoint
        echo ""
        echo "5️⃣  Testing API..."
        sleep 2
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ API is responding${NC}"
            echo ""
            echo "Testing halal check endpoint..."
            RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/halal-check/analyze" \
                -H "Content-Type: application/json" \
                -d '{"text": "Fresh Apple", "device_id": "status-check"}' 2>&1)

            if echo "$RESPONSE" | grep -q "product_name"; then
                echo -e "${GREEN}✅ Halal check endpoint working${NC}"
            else
                echo -e "${YELLOW}⚠️  Halal check endpoint may have issues${NC}"
                echo "Response: $RESPONSE"
            fi
        else
            echo -e "${YELLOW}⚠️  API not responding (may still be starting)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Backend container exists but not running${NC}"
        echo "   Run: make build"
    fi
else
    echo -e "${YELLOW}⚠️  Containers not running${NC}"
    echo "   Run: make build"
fi
echo ""

# Summary
echo "=========================================="
echo "📊 Status Summary"
echo "=========================================="
echo ""

if [ "$ALL_FILES_EXIST" = true ]; then
    echo -e "${GREEN}✅ All required files present${NC}"
else
    echo -e "${RED}❌ Some files are missing${NC}"
fi

if docker compose ps | grep "halal-check-backend" | grep -q "Up"; then
    echo -e "${GREEN}✅ Services running${NC}"
    echo ""
    echo "🌐 Access Points:"
    echo "   • API Docs: http://localhost:8000/docs"
    echo "   • Health Check: http://localhost:8000/health"
    echo "   • Frontend: http://localhost:3000"
else
    echo -e "${YELLOW}⚠️  Services not running${NC}"
    echo ""
    echo "🚀 To start:"
    echo "   make build"
fi

echo ""
echo "📚 Documentation:"
echo "   • Quick Reference: QUICK_REFERENCE.md"
echo "   • Setup Summary: SETUP_SUMMARY.md"
echo "   • API Docs: backend/API_DOCUMENTATION.md"
echo ""
echo "=========================================="

