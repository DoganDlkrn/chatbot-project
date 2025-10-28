#!/bin/bash

# Chatbot Project Setup Script
# Bu script projeyi local ortamda çalıştırmak için gerekli adımları gerçekleştirir

set -e

echo "🤖 Chatbot Projesi Kurulum Scripti"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Docker
echo -e "${BLUE}[1/7]${NC} Docker kontrolü..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker yüklü değil! Lütfen Docker'ı yükleyin.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker bulundu${NC}"

# Check Docker Compose
echo -e "${BLUE}[2/7]${NC} Docker Compose kontrolü..."
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose yüklü değil! Lütfen Docker Compose'u yükleyin.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose bulundu${NC}"

# Check .NET
echo -e "${BLUE}[3/7]${NC} .NET SDK kontrolü..."
if ! command -v dotnet &> /dev/null; then
    echo -e "${YELLOW}⚠️  .NET SDK bulunamadı. Docker ile çalışılacak.${NC}"
else
    echo -e "${GREEN}✅ .NET SDK bulundu: $(dotnet --version)${NC}"
fi

# Check Python
echo -e "${BLUE}[4/7]${NC} Python kontrolü..."
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python3 bulunamadı. Docker ile çalışılacak.${NC}"
else
    echo -e "${GREEN}✅ Python bulundu: $(python3 --version)${NC}"
fi

# Create .env file if not exists
echo -e "${BLUE}[5/7]${NC} Environment dosyası oluşturuluyor..."
if [ ! -f .env ]; then
    cat > .env << EOF
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chatbot_db

# SMTP (Gmail örneği)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_EMAIL=admin@example.com

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
EOF
    echo -e "${GREEN}✅ .env dosyası oluşturuldu (lütfen düzenleyin)${NC}"
else
    echo -e "${GREEN}✅ .env dosyası zaten mevcut${NC}"
fi

# Create uploads directory
echo -e "${BLUE}[6/7]${NC} Upload klasörü oluşturuluyor..."
mkdir -p uploads
mkdir -p ChatbotAPI/uploads
mkdir -p HaystackService/uploads
echo -e "${GREEN}✅ Upload klasörleri oluşturuldu${NC}"

# Start Docker containers
echo -e "${BLUE}[7/7]${NC} Docker container'ları başlatılıyor..."
docker-compose up -d

echo ""
echo -e "${GREEN}✅ Kurulum tamamlandı!${NC}"
echo ""
echo "📋 Servisler:"
echo "  - PostgreSQL:        http://localhost:5432"
echo "  - Elasticsearch:     http://localhost:9200"
echo "  - Chatbot API:       http://localhost:5000"
echo "  - Haystack Service:  http://localhost:8001"
echo ""
echo "📖 Swagger UI:         http://localhost:5000/swagger"
echo ""
echo "🔍 Servislerin durumunu kontrol etmek için:"
echo "   docker-compose ps"
echo ""
echo "📝 Logları görmek için:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Servisleri durdurmak için:"
echo "   docker-compose down"
echo ""
echo -e "${YELLOW}⚠️  .env dosyasını düzenlemeyi unutmayın!${NC}"

