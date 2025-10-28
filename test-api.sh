#!/bin/bash

# API Test Script
# Bu script API endpoint'lerini test eder

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

API_URL="http://localhost:5000"
HAYSTACK_URL="http://localhost:8001"

echo "🧪 API Test Scripti"
echo "=================="
echo ""

# Test API Health
echo -e "${BLUE}[1/4]${NC} API health check..."
if curl -s -f "${API_URL}/api/chat/health" > /dev/null; then
    echo -e "${GREEN}✅ API is healthy${NC}"
else
    echo -e "${RED}❌ API is not responding${NC}"
    exit 1
fi

# Test Haystack Health
echo -e "${BLUE}[2/4]${NC} Haystack service health check..."
if curl -s -f "${HAYSTACK_URL}/health" > /dev/null; then
    echo -e "${GREEN}✅ Haystack service is healthy${NC}"
else
    echo -e "${RED}❌ Haystack service is not responding${NC}"
    exit 1
fi

# Test Chat Endpoint
echo -e "${BLUE}[3/4]${NC} Testing chat endpoint..."
CHAT_RESPONSE=$(curl -s -X POST "${API_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Merhaba"}')

if echo "$CHAT_RESPONSE" | grep -q "sessionId"; then
    echo -e "${GREEN}✅ Chat endpoint working${NC}"
    echo "Response: $CHAT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$CHAT_RESPONSE"
else
    echo -e "${RED}❌ Chat endpoint failed${NC}"
    echo "Response: $CHAT_RESPONSE"
fi

# Test Document Upload
echo -e "${BLUE}[4/4]${NC} Testing document upload endpoint..."
# Create a test file
echo "Bu bir test dokümanidir. Chatbot sistemi test ediliyor." > /tmp/test-document.txt

UPLOAD_RESPONSE=$(curl -s -X POST "${API_URL}/api/documents/upload" \
  -F "file=@/tmp/test-document.txt")

if echo "$UPLOAD_RESPONSE" | grep -q "id"; then
    echo -e "${GREEN}✅ Document upload working${NC}"
    echo "Response: $UPLOAD_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$UPLOAD_RESPONSE"
else
    echo -e "${RED}❌ Document upload failed${NC}"
    echo "Response: $UPLOAD_RESPONSE"
fi

# Cleanup
rm -f /tmp/test-document.txt

echo ""
echo -e "${GREEN}✅ Tüm testler tamamlandı!${NC}"

