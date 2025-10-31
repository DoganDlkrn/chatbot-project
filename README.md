# Intelligent Chatbot System

## Proje Hakkında

Bu proje, PDF ve diğer dokümanları yükleyebilen, içeriklerini Haystack ile analiz eden ve veritabanından akıllı cevaplar döndüren bir chatbot sistemidir.

## Özellikler

- 🤖 C# ASP.NET Core Web API backend
- 📄 PDF ve doküman yükleme/okuma
- 🔍 Haystack ile doküman arama ve soru-cevap
- 🐳 Docker ile konteynerize edilmiş servisler
- 🗄️ PostgreSQL veritabanı
- 🚀 Jenkins CI/CD pipeline
- 📧 E-mail bildirimleri (deploy başarısızlık durumunda)
- 🌿 Git workflow (dev/main branches)

## Teknolojiler

- **Backend:** C# / ASP.NET Core 8.0
- **AI/ML:** Python + Haystack Framework
- **Veritabanı:** PostgreSQL
- **Konteynerizasyon:** Docker & Docker Compose
- **CI/CD:** Jenkins
- **E-mail:** SMTP

## Kurulum

### Gereksinimler

- .NET 8.0 SDK (opsiyonel - Docker kullanılabilir)
- Python 3.11+ (opsiyonel - Docker kullanılabilir)
- Docker & Docker Compose ✅ **Gerekli**
- Jenkins (CI/CD için)
- Git

### Hızlı Başlangıç (Önerilen)

```bash
# 1. Repository'yi klonlayın
git clone <repository-url>
cd chatbot

# 2. Otomatik kurulum scriptini çalıştırın
chmod +x setup.sh
./setup.sh

# 3. Web arayüzünü açın
open web-client/index.html
# veya
cd web-client && python3 -m http.server 8080
```

### Manuel Kurulum

1. Repository'yi klonlayın:
```bash
git clone <repository-url>
cd chatbot
```

2. Environment dosyasını oluşturun:
```bash
cp .env.example .env
# .env dosyasını düzenleyin (SMTP ayarları vb.)
```

3. Docker container'ları başlatın:
```bash
docker-compose up -d
```

4. Servislerin hazır olmasını bekleyin:
```bash
docker-compose logs -f
# CTRL+C ile çıkın
```

5. API'yi test edin:
```bash
chmod +x test-api.sh
./test-api.sh
```

## API Endpoints

- `POST /api/chat` - Chatbot ile sohbet et
- `POST /api/documents/upload` - PDF/doküman yükle
- `GET /api/documents` - Yüklenen dokümanları listele
- `DELETE /api/documents/{id}` - Doküman sil

## Jenkins Pipeline

Pipeline otomatik olarak:
1. Kodu test eder
2. Docker image'ları build eder
3. Testleri çalıştırır
4. Deploy eder
5. Başarısız olursa e-mail gönderir

## Branching Strategy

- `main` - Production branch
- `dev` - Development branch (Jenkins trigger)
- `feature/*` - Feature branches

## Konfigürasyon

`.env` dosyası oluşturun:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chatbot_db
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_EMAIL=admin@example.com
```

## Lisans

MIT

Test için basit değişiklik
