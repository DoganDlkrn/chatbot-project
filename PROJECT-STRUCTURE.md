# Proje Yapısı

```
chatbot/
│
├── ChatbotAPI/                      # C# ASP.NET Core Web API
│   ├── Controllers/                 # API Controllers
│   │   ├── ChatController.cs        # Chat endpoint'leri
│   │   └── DocumentsController.cs   # Doküman yönetimi
│   │
│   ├── Data/                        # Database Context
│   │   └── ChatbotDbContext.cs      # EF Core DbContext
│   │
│   ├── Models/                      # Data Models
│   │   ├── Document.cs              # Doküman modeli
│   │   ├── ChatSession.cs           # Session modeli
│   │   ├── ChatMessage.cs           # Mesaj modeli
│   │   ├── KnowledgeBase.cs         # Bilgi bankası
│   │   └── DTOs/                    # Data Transfer Objects
│   │       ├── ChatRequest.cs
│   │       ├── ChatResponse.cs
│   │       └── HaystackRequest.cs
│   │
│   ├── Services/                    # Business Logic
│   │   ├── IChatService.cs          # Chat service interface
│   │   ├── ChatService.cs           # Chat implementasyonu
│   │   ├── IDocumentService.cs      # Doküman service interface
│   │   ├── DocumentService.cs       # PDF okuma, upload
│   │   ├── IHaystackService.cs      # Haystack service interface
│   │   ├── HaystackService.cs       # Haystack API client
│   │   ├── IEmailService.cs         # Email service interface
│   │   └── EmailService.cs          # Email bildirimleri
│   │
│   ├── Program.cs                   # Ana entry point
│   ├── appsettings.json             # Konfigürasyon
│   ├── ChatbotAPI.csproj            # Project dosyası
│   ├── Dockerfile                   # Docker image definition
│   └── .dockerignore                # Docker ignore patterns
│
├── HaystackService/                 # Python Haystack Service
│   ├── app.py                       # FastAPI application
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Docker image definition
│   └── .dockerignore                # Docker ignore patterns
│
├── uploads/                         # Yüklenen dosyalar (ignored)
│
├── .git/                            # Git repository
├── .gitignore                       # Git ignore patterns
│
├── docker-compose.yml               # Docker orchestration
├── init-db.sql                      # Database initialization
│
├── Jenkinsfile                      # CI/CD Pipeline definition
│
├── setup.sh                         # Otomatik kurulum scripti
├── test-api.sh                      # API test scripti
│
├── README.md                        # Ana dokümantasyon
├── jenkins-setup.md                 # Jenkins kurulum rehberi
├── git-workflow.md                  # Git workflow rehberi
├── HAYSTACK-GUIDE.md                # Haystack kullanım rehberi
├── DEPLOYMENT.md                    # Deployment rehberi
├── API-EXAMPLES.md                  # API kullanım örnekleri
└── PROJECT-STRUCTURE.md             # Bu dosya
```

## Detaylı Açıklamalar

### ChatbotAPI/ (C# Backend)

**Controllers/**
- `ChatController.cs`: Chatbot mesajlaşma endpoint'leri
  - `POST /api/chat` - Mesaj gönder
  - `GET /api/chat/health` - Health check
  
- `DocumentsController.cs`: Doküman yönetimi
  - `POST /api/documents/upload` - Dosya yükle
  - `GET /api/documents` - Dokümanları listele
  - `GET /api/documents/{id}` - Doküman detayı
  - `DELETE /api/documents/{id}` - Doküman sil

**Data/**
- `ChatbotDbContext.cs`: Entity Framework Core database context
  - Documents tablosu
  - ChatSessions tablosu
  - ChatMessages tablosu
  - KnowledgeBase tablosu

**Models/**
- `Document.cs`: Yüklenen doküman bilgileri
- `ChatSession.cs`: Kullanıcı oturumları
- `ChatMessage.cs`: Chat mesajları
- `KnowledgeBase.cs`: Önceden tanımlı bilgi bankası

**Services/**
- `ChatService.cs`: Chat logic
  - Knowledge base'de arama
  - Haystack'e sorgu gönderme
  - Cevap üretme
  
- `DocumentService.cs`: Doküman işlemleri
  - PDF metin çıkarma
  - Dosya yükleme
  - Haystack'e indexleme
  
- `HaystackService.cs`: Haystack API client
  - HTTP istekleri
  - Doküman indexleme
  - Sorgu gönderme
  
- `EmailService.cs`: Email bildirimleri
  - SMTP ile email gönderme
  - Deployment failure notifications

### HaystackService/ (Python Backend)

**app.py**: FastAPI application
- `/health` - Health check endpoint
- `/api/query` - Doküman sorgulama
- `/api/index` - Doküman indexleme
- `/api/documents` - İndeksli dokümanları listele
- `/api/documents/{id}` - Doküman silme

**Özellikler:**
- InMemoryDocumentStore (geliştirme)
- BM25Retriever (keyword search)
- Document embedding
- Query processing

### Docker Services

**docker-compose.yml** şu servisleri çalıştırır:

1. **postgres** (Port 5432)
   - PostgreSQL 16
   - Veritabanı: chatbot_db
   - Otomatik init-db.sql çalıştırır

2. **elasticsearch** (Port 9200)
   - Elasticsearch 8.11
   - Haystack için document store
   - Single-node mode

3. **haystack-service** (Port 8001)
   - Python FastAPI
   - Haystack framework
   - Document processing

4. **chatbot-api** (Port 5000)
   - ASP.NET Core 8.0
   - Ana API
   - Swagger UI

### Scripts

**setup.sh**
- Otomatik kurulum
- Dependency kontrolü
- Docker container başlatma
- Environment dosyası oluşturma

**test-api.sh**
- API endpoint'leri test etme
- Health check'ler
- Sample request'ler

### CI/CD

**Jenkinsfile**
- Git checkout
- Docker build
- Test execution
- Deployment (dev branch)
- Health checks
- Email notifications (success/failure)

**Workflow:**
```
Git Push (dev) → Jenkins Trigger → Build → Test → Deploy → Notify
```

### Database Schema

**documents**
```sql
id, filename, original_filename, file_path, 
file_type, file_size, uploaded_at, indexed, content_hash
```

**chat_sessions**
```sql
id, session_id (UUID), created_at, last_activity
```

**chat_messages**
```sql
id, session_id, message_type, message, 
source, confidence, created_at
```

**knowledge_base**
```sql
id, question, answer, category, keywords, 
created_at, updated_at
```

## Veri Akışı

### Chat Flow

```
1. Client → POST /api/chat
2. ChatController → ChatService
3. ChatService → Knowledge Base Search
4. If not found → HaystackService
5. HaystackService → Haystack API (Python)
6. Haystack → Document Search → Answer
7. Response ← Client
```

### Document Upload Flow

```
1. Client → POST /api/documents/upload (PDF)
2. DocumentsController → DocumentService
3. DocumentService → Save file to disk
4. DocumentService → Extract text from PDF
5. DocumentService → HaystackService.IndexDocument
6. HaystackService → Haystack API
7. Haystack → Index in DocumentStore
8. Response ← Client
```

### Jenkins CI/CD Flow

```
1. Developer → git push origin dev
2. Jenkins → Poll SCM / Webhook
3. Jenkins → Checkout code
4. Jenkins → docker build (API + Haystack)
5. Jenkins → Run tests
6. Jenkins → docker-compose up
7. Jenkins → Health checks
8. Success → Email notification ✅
   Failure → Email notification with logs ❌
```

## Teknoloji Stack

### Backend
- **C#**: ASP.NET Core 8.0
- **Python**: 3.11 + FastAPI
- **Haystack**: 2.0.0 (Document AI)

### Database
- **PostgreSQL**: 16 (Ana veritabanı)
- **Elasticsearch**: 8.11 (Document store)

### DevOps
- **Docker**: Konteynerizasyon
- **Docker Compose**: Orchestration
- **Jenkins**: CI/CD

### Libraries
- **C# API**: 
  - EntityFrameworkCore
  - Npgsql (PostgreSQL)
  - iTextSharp (PDF reading)
  - MailKit (Email)
  - Swashbuckle (Swagger)

- **Python**:
  - haystack-ai
  - fastapi
  - uvicorn
  - psycopg2

## Port'lar

| Service          | Port | URL                          |
|------------------|------|------------------------------|
| Chatbot API      | 5000 | http://localhost:5000        |
| Haystack Service | 8001 | http://localhost:8001        |
| PostgreSQL       | 5432 | localhost:5432               |
| Elasticsearch    | 9200 | http://localhost:9200        |
| Jenkins          | 8080 | http://localhost:8080        |
| Swagger UI       | 5000 | http://localhost:5000/swagger|

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chatbot_db

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_EMAIL=admin@example.com

# Services
HAYSTACK_SERVICE_PORT=8001
API_PORT=5000
```

## Önemli Dosya Boyutları

```
ChatbotAPI.csproj         ~2 KB
Program.cs                ~2 KB
ChatService.cs            ~5 KB
DocumentService.cs        ~6 KB
app.py (Haystack)         ~8 KB
docker-compose.yml        ~3 KB
Jenkinsfile               ~7 KB
```

## Git Branch Yapısı

```
main (production)
  └── dev (development, Jenkins active)
        ├── feature/chatbot-improvements
        ├── feature/pdf-reader
        ├── bugfix/api-timeout
        └── hotfix/security-patch
```

## Geliştirme Workflow

1. Feature branch oluştur: `git checkout -b feature/new-feature`
2. Kod yaz ve test et
3. Dev'e merge: `git checkout dev && git merge feature/new-feature`
4. Dev'e push: `git push origin dev` ← **Jenkins otomatik çalışır**
5. Jenkins build, test, deploy yapar
6. Email bildirimi gelir (success/failure)
7. Production'a almak için: `git checkout main && git merge dev`

## Monitoring

- **Logs**: `docker-compose logs -f`
- **Health**: `/api/chat/health`, `/health`
- **Metrics**: Docker stats
- **Database**: pgAdmin veya DBeaver

## Güvenlik

- Passwords: `.env` dosyasında (git'te yok)
- CORS: Configured
- HTTPS: Nginx reverse proxy ile
- SQL Injection: Parameterized queries
- File Upload: Extension ve size kontrolü

## Scalability

- Horizontal scaling: `docker-compose up -d --scale chatbot-api=3`
- Load balancing: Nginx upstream
- Database: Connection pooling
- Caching: Redis (future)

## Bakım

- **Backup**: `pg_dump` daily cron
- **Logs**: Rotate with logrotate
- **Updates**: `docker-compose pull && docker-compose up -d`
- **Monitoring**: Prometheus + Grafana (future)

