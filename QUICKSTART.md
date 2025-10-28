# 🚀 Hızlı Başlangıç Rehberi

## 5 Dakikada Başlayın!

### Adım 1: Projeyi İndirin

```bash
cd /Users/dogandalkiran/Desktop/chatbot
```

### Adım 2: Servisleri Başlatın

```bash
# Otomatik kurulum (önerilen)
chmod +x setup.sh
./setup.sh

# VEYA manuel
docker-compose up -d
```

### Adım 3: Servislerin Hazır Olmasını Bekleyin

```bash
# Logları izleyin (30 saniye bekleyin)
docker-compose logs -f

# Servis durumunu kontrol edin
docker-compose ps
```

Beklenen çıktı:
```
✅ chatbot_postgres       running   5432/tcp
✅ chatbot_elasticsearch  running   9200/tcp
✅ chatbot_haystack       running   8001/tcp
✅ chatbot_api            running   5000/tcp
```

### Adım 4: Web Arayüzünü Açın

```bash
# Web client'ı açın
open web-client/index.html

# VEYA basit HTTP server ile
cd web-client
python3 -m http.server 8080
# Tarayıcıda: http://localhost:8080
```

### Adım 5: Test Edin!

**1. Chatbot ile Konuşun:**
- Web arayüzünde "Merhaba" yazın
- "Nasılsın?" sorusunu sorun

**2. PDF Yükleyin:**
- "Doküman Yükle" sekmesine gidin
- Bir PDF dosyası yükleyin
- Chatbot'a yüklediğiniz PDF hakkında soru sorun

**3. API'yi Test Edin:**
```bash
# Health check
curl http://localhost:5000/api/chat/health

# Test mesajı gönder
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Merhaba"}'

# Dokümanları listele
curl http://localhost:5000/api/documents
```

## Jenkins CI/CD Kurulumu (Opsiyonel)

### Adım 1: Jenkins'i Başlatın

```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

### Adım 2: İlk Admin Şifresini Alın

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Adım 3: Jenkins'i Yapılandırın

1. Tarayıcıda `http://localhost:8080` açın
2. Admin şifresini girin
3. "Install suggested plugins" seçin
4. Admin kullanıcı oluşturun

### Adım 4: Pipeline Oluşturun

1. **New Item** → **Pipeline** → İsim: `chatbot-pipeline`
2. **Pipeline** bölümünde:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `<your-git-url>`
   - Branch: `*/dev`
   - Script Path: `Jenkinsfile`
3. **Save**

### Adım 5: E-mail Ayarlarını Yapın

**Manage Jenkins** → **Configure System** → **Extended E-mail Notification**:
```
SMTP Server: smtp.gmail.com
SMTP Port: 587
Username: your-email@gmail.com
Password: your-app-password
```

### Adım 6: Test Edin!

```bash
# Dev branch'e push yapın
git checkout dev
git commit --allow-empty -m "test: trigger jenkins"
git push origin dev

# Jenkins'te build'i izleyin
# http://localhost:8080/job/chatbot-pipeline/
```

## Git Workflow Başlangıcı

### Repository Oluşturma

```bash
# GitHub/GitLab'da repository oluşturun

# Local'de git başlatın
cd /Users/dogandalkiran/Desktop/chatbot
git init
git add .
git commit -m "feat: initial commit"

# Remote ekleyin
git remote add origin <your-repository-url>

# Branch'leri oluşturun
git branch -M main
git checkout -b dev

# Push edin
git push -u origin main
git push -u origin dev
```

### Günlük Kullanım

```bash
# Dev branch'e geç
git checkout dev

# Değişiklik yap
# ... kodlama ...

# Commit et
git add .
git commit -m "feat: new feature"

# Push et (Jenkins otomatik çalışır!)
git push origin dev
```

## Sorun Giderme

### Servisler Başlamıyor

```bash
# Container'ları durdur ve temizle
docker-compose down
docker system prune -f

# Yeniden başlat
docker-compose up -d
```

### Port Çakışması

```bash
# Çalışan servisleri kontrol et
lsof -i :5000
lsof -i :8001
lsof -i :5432

# Port'ları docker-compose.yml'de değiştir
```

### Database Bağlantı Hatası

```bash
# PostgreSQL'in hazır olduğundan emin olun
docker exec chatbot_postgres pg_isready

# Database'i yeniden oluştur
docker-compose down -v
docker-compose up -d
```

### CORS Hatası (Web Client)

API zaten CORS'u destekliyor, ancak eğer hata alıyorsanız:

```bash
# API'nin çalıştığını doğrulayın
curl http://localhost:5000/api/chat/health

# API loglarını kontrol edin
docker-compose logs chatbot-api
```

## Faydalı Komutlar

```bash
# Tüm logları göster
docker-compose logs -f

# Belirli servisin logları
docker-compose logs -f chatbot-api

# Servisi yeniden başlat
docker-compose restart chatbot-api

# Servis durumunu kontrol et
docker-compose ps

# Container'lara shell ile gir
docker exec -it chatbot_api bash
docker exec -it chatbot_postgres psql -U postgres chatbot_db

# Database backup
docker exec chatbot_postgres pg_dump -U postgres chatbot_db > backup.sql

# Servisleri durdur
docker-compose down

# Servisleri durdur ve volume'leri sil
docker-compose down -v
```

## Swagger UI

API dokümantasyonu için:
```
http://localhost:5000/swagger
```

Burada tüm endpoint'leri test edebilirsiniz.

## Haystack Service

Doğrudan Haystack API'sine erişim:
```
http://localhost:8001/docs
```

FastAPI otomatik dokümantasyonu.

## Veritabanı Erişimi

### pgAdmin ile (GUI)

```bash
docker run -d \
  --name pgadmin \
  -p 5050:80 \
  -e PGADMIN_DEFAULT_EMAIL=admin@admin.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  --network chatbot_chatbot_network \
  dpage/pgadmin4
```

Tarayıcıda: `http://localhost:5050`

**Bağlantı Ayarları:**
- Host: `postgres`
- Port: `5432`
- Database: `chatbot_db`
- Username: `postgres`
- Password: `postgres`

### psql ile (CLI)

```bash
docker exec -it chatbot_postgres psql -U postgres chatbot_db

# SQL sorguları
SELECT * FROM documents;
SELECT * FROM chat_messages ORDER BY created_at DESC LIMIT 10;
SELECT * FROM knowledge_base;
```

## İleri Seviye Konular

Detaylı bilgi için şu dosyalara bakın:

- **DEPLOYMENT.md** - Production deployment
- **jenkins-setup.md** - Jenkins detaylı kurulum
- **git-workflow.md** - Git workflow best practices
- **HAYSTACK-GUIDE.md** - Haystack framework rehberi
- **API-EXAMPLES.md** - API kullanım örnekleri
- **PROJECT-STRUCTURE.md** - Proje yapısı

## Önemli URL'ler

| Servis            | URL                              |
|-------------------|----------------------------------|
| Web Client        | web-client/index.html            |
| API               | http://localhost:5000            |
| Swagger UI        | http://localhost:5000/swagger    |
| Haystack API      | http://localhost:8001            |
| Haystack Docs     | http://localhost:8001/docs       |
| PostgreSQL        | localhost:5432                   |
| Elasticsearch     | http://localhost:9200            |
| Jenkins           | http://localhost:8080            |

## Destek

Sorun yaşarsanız:

1. **Logs kontrol edin:** `docker-compose logs -f`
2. **Health check yapın:** `curl http://localhost:5000/api/chat/health`
3. **Test script çalıştırın:** `./test-api.sh`
4. **GitHub Issues** açın (eğer repository varsa)

## Başarılar! 🎉

Artık çalışan bir chatbot sisteminiz var:
- ✅ C# Backend API
- ✅ Python Haystack Service
- ✅ PostgreSQL Database
- ✅ Docker Containers
- ✅ Web Client
- ✅ Jenkins CI/CD (opsiyonel)

Kod yazmaya başlayın ve Jenkins ile otomatik deploy edin! 🚀

