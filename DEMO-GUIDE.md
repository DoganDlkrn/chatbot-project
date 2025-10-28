# 🎬 Chatbot Demo Rehberi - Görsel Anlatım

## 🚀 Başlamadan Önce

Bu rehber, chatbot'un nasıl çalıştığını **adım adım** ve **görsel olarak** gösterir.

---

## 📍 1. ADIM: Docker'ı Başlat

1. **Docker Desktop** uygulamasını aç (Mac'te Applications'dan)
2. Docker simgesinin menü çubuğunda görünmesini bekle
3. Yeşil olduğunda hazır! ✅

---

## 📍 2. ADIM: Servisleri Başlat

Terminal'i aç ve şunu çalıştır:

```bash
cd /Users/dogandalkiran/Desktop/chatbot

# Environment dosyası oluştur (sadece ilk seferde)
cat > .env << 'EOF'
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
NOTIFICATION_EMAIL=
EOF

# Servisleri başlat
docker-compose up -d
```

**Ne görmelisin:**
```
✔ Container chatbot_postgres       Started
✔ Container chatbot_elasticsearch  Started
✔ Container chatbot_haystack       Started
✔ Container chatbot_api            Started
```

**30 saniye bekle!** Servisler hazırlanıyor...

---

## 📍 3. ADIM: Swagger UI'da API'yi Gör

### Tarayıcında aç:
```
http://localhost:5000/swagger
```

### Ne göreceksin:

```
┌─────────────────────────────────────────────┐
│  Chatbot API - Swagger UI                  │
├─────────────────────────────────────────────┤
│                                             │
│  📁 Chat                                    │
│    └─ POST /api/chat                        │
│    └─ GET  /api/chat/health                 │
│                                             │
│  📁 Documents                               │
│    └─ POST   /api/documents/upload          │
│    └─ GET    /api/documents                 │
│    └─ GET    /api/documents/{id}            │
│    └─ DELETE /api/documents/{id}            │
│                                             │
└─────────────────────────────────────────────┘
```

### 🎯 İlk Testi Yap:

1. **"GET /api/chat/health"** endpoint'ine tıkla
2. **"Try it out"** butonuna bas
3. **"Execute"** butonuna bas

**Cevap göreceksin:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-22T10:30:00Z"
}
```

✅ **API çalışıyor!**

---

## 📍 4. ADIM: Chatbot ile Konuş (Swagger'da)

### 1. "POST /api/chat" endpoint'ini aç

### 2. "Try it out" tıkla

### 3. Request body'yi düzenle:
```json
{
  "message": "Merhaba, nasılsın?"
}
```

### 4. "Execute" tıkla

### 5. Response'u gör:
```json
{
  "sessionId": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Merhaba! Ben bir yapay zeka asistanıyım ve her zaman hazırım! Size nasıl yardımcı olabilirim?",
  "source": "database",
  "confidence": 95.0,
  "timestamp": "2025-10-22T10:31:00Z"
}
```

✅ **Chatbot çalışıyor ve cevap veriyor!**

---

## 📍 5. ADIM: Web Arayüzünü Aç (En Güzel Görünüm)

### Terminal'de:
```bash
cd /Users/dogandalkiran/Desktop/chatbot/web-client
python3 -m http.server 8080
```

### Tarayıcıda aç:
```
http://localhost:8080
```

### Ne göreceksin:

```
┌───────────────────────────────────────────────┐
│  🤖 Akıllı Chatbot Asistanı                   │
│  Sorularınızı sorun veya doküman yükleyin    │
├─────────────┬─────────────────────────────────┤
│ 💬 Sohbet   │  📄 Doküman Yükle              │
├─────────────┴─────────────────────────────────┤
│                                               │
│  🤖 Merhaba! Ben akıllı chatbot              │
│     asistanınızım. Size nasıl yardımcı       │
│     olabilirim?                              │
│                                               │
│                                               │
│                                               │
│                   Merhaba! 💬                │
│                                               │
│                                               │
├───────────────────────────────────────────────┤
│  Mesajınızı yazın...           [Gönder]      │
└───────────────────────────────────────────────┘
```

---

## 📍 6. ADIM: Web Arayüzünde Test Et

### Test 1: Basit Konuşma

1. **"Merhaba"** yaz → Gönder
   - 🤖 Cevap: "Merhaba! Ben bir yapay zeka..."
   - ✅ **Kaynak: Bilgi Bankası**

2. **"Nasılsın?"** yaz → Gönder
   - 🤖 Cevap: "Ben bir yapay zeka asistanıyım..."
   - ✅ **Kaynak: Bilgi Bankası**

3. **"Bugün hava nasıl?"** yaz → Gönder
   - 🤖 Cevap: "Üzgünüm, bu konuda yeterli bilgiye sahip değilim..."
   - ⚠️ **Kaynak: Yok** (çünkü knowledge base'de yok)

### Test 2: PDF Yükleme

1. **"📄 Doküman Yükle"** sekmesine geç

2. **Bir PDF dosyası yükle** (drag & drop veya tıkla)

3. Yükleme tamamlanınca:
   ```
   ✅ Dosya başarıyla yüklendi!
   ```

4. Doküman listesinde gör:
   ```
   📄 document.pdf
   245 KB • 22.10.2025 10:35
   [İndeksli] ✓
   ```

5. **"💬 Sohbet"** sekmesine dön

6. PDF hakkında soru sor:
   **"Yüklediğim PDF'de ne yazıyor?"**

7. Cevap al:
   - 🤖 "PDF dosyasında şu bilgiler var: ..."
   - ✅ **Kaynak: Doküman**

---

## 📍 7. ADIM: Haystack API'yi Gör

### Tarayıcıda aç:
```
http://localhost:8001/docs
```

### Ne göreceksin:

FastAPI otomatik dokümantasyonu:

```
┌─────────────────────────────────────────┐
│  Haystack Service API                   │
├─────────────────────────────────────────┤
│                                         │
│  GET  /                                 │
│  GET  /health                           │
│  POST /api/query                        │
│  POST /api/index                        │
│  GET  /api/documents                    │
│  DELETE /api/documents/{document_id}    │
│                                         │
└─────────────────────────────────────────┘
```

### Test Et:

1. **"GET /health"** → Try it out → Execute

**Response:**
```json
{
  "status": "healthy",
  "documents_count": 0
}
```

---

## 📍 8. ADIM: Terminal'den Test (Gelişmiş)

### Test Script Çalıştır:

```bash
cd /Users/dogandalkiran/Desktop/chatbot
chmod +x test-api.sh
./test-api.sh
```

**Göreceğin çıktı:**
```bash
🧪 API Test Scripti
==================

[1/4] API health check...
✅ API is healthy

[2/4] Haystack service health check...
✅ Haystack service is healthy

[3/4] Testing chat endpoint...
✅ Chat endpoint working
Response: {
  "sessionId": "...",
  "message": "Merhaba! ...",
  "source": "database"
}

[4/4] Testing document upload endpoint...
✅ Document upload working

✅ Tüm testler tamamlandı!
```

---

## 📍 9. ADIM: cURL ile Manuel Test

### Chat Testi:
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Merhaba"}'
```

### Doküman Listesi:
```bash
curl http://localhost:5000/api/documents
```

### Doküman Yükle:
```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -F "file=@/path/to/your/file.pdf"
```

---

## 📍 10. ADIM: Veritabanını Gör

### PostgreSQL'e Bağlan:

```bash
docker exec -it chatbot_postgres psql -U postgres chatbot_db
```

### SQL Sorguları Çalıştır:

```sql
-- Yüklenen dokümanları gör
SELECT id, original_filename, file_size, uploaded_at, indexed 
FROM documents;

-- Chat mesajlarını gör
SELECT message_type, message, source, confidence, created_at 
FROM chat_messages 
ORDER BY created_at DESC 
LIMIT 10;

-- Bilgi bankasını gör
SELECT question, answer, category 
FROM knowledge_base;

-- Çık
\q
```

**Örnek Çıktı:**
```
 id | original_filename | file_size |      uploaded_at        | indexed 
----+-------------------+-----------+------------------------+---------
  1 | document.pdf      |    245678 | 2025-10-22 10:35:00    | t
  2 | notes.txt         |      1234 | 2025-10-22 10:36:00    | t
```

---

## 📊 Sistem Mimarisi (Görsel)

```
┌──────────────┐
│   Kullanıcı  │
└──────┬───────┘
       │
       ├─→ Web Client (http://localhost:8080)
       │   └─→ HTML/CSS/JS
       │
       ├─→ API (http://localhost:5000)
       │   ├─→ C# ASP.NET Core
       │   ├─→ Chat Controller
       │   ├─→ Documents Controller
       │   └─→ Services
       │       ├─→ ChatService
       │       ├─→ DocumentService
       │       ├─→ HaystackService (HTTP Client)
       │       └─→ EmailService
       │
       ├─→ Haystack Service (http://localhost:8001)
       │   ├─→ Python FastAPI
       │   ├─→ Document Store
       │   └─→ BM25 Retriever
       │
       ├─→ PostgreSQL (localhost:5432)
       │   ├─→ documents
       │   ├─→ chat_messages
       │   ├─→ chat_sessions
       │   └─→ knowledge_base
       │
       └─→ Elasticsearch (localhost:9200)
           └─→ Document Search Index
```

---

## 🔄 Veri Akışı (Step by Step)

### Senaryo: "PDF hakkında soru sor"

```
1. Kullanıcı mesaj yazar: "PDF'de ne yazıyor?"
   │
   ▼
2. Web Client → POST /api/chat
   │
   ▼
3. ChatController → ChatService.ProcessMessageAsync()
   │
   ▼
4. ChatService → Knowledge Base'de ara
   │
   ├─→ Bulursa → Cevap döner ✅
   │
   └─→ Bulamazsa → HaystackService'e sor
       │
       ▼
5. HaystackService → POST http://localhost:8001/api/query
   │
   ▼
6. Haystack API → Document Store'da ara
   │
   ├─→ BM25 Retriever ile arama
   ├─→ En alakalı dokümanları bul
   └─→ Cevap oluştur
       │
       ▼
7. Response ← Kullanıcıya dön
   {
     "message": "PDF'de şu bilgiler var...",
     "source": "document",
     "confidence": 0.87
   }
```

---

## 🎯 Hızlı Kontrol Listesi

Her şeyin çalıştığını kontrol et:

```bash
# 1. Docker çalışıyor mu?
docker ps

# 2. Tüm servisler ayakta mı?
docker-compose ps

# 3. API çalışıyor mu?
curl http://localhost:5000/api/chat/health

# 4. Haystack çalışıyor mu?
curl http://localhost:8001/health

# 5. Database erişilebilir mi?
docker exec chatbot_postgres pg_isready

# 6. Logları kontrol et
docker-compose logs chatbot-api
docker-compose logs haystack-service
```

---

## 🌐 Tüm URL'ler Bir Arada

| Ne istiyorsun? | URL | Açıklama |
|----------------|-----|----------|
| 🎨 Güzel UI | `http://localhost:8080` | Web client |
| 🔌 API Test | `http://localhost:5000/swagger` | Swagger UI |
| 🔎 Haystack API | `http://localhost:8001/docs` | FastAPI docs |
| 🗄️ Health Check | `http://localhost:5000/api/chat/health` | API durumu |
| 📊 Elasticsearch | `http://localhost:9200` | Search engine |

---

## 💡 Demo Senaryoları

### Senaryo 1: Basit Chat
1. Web client aç
2. "Merhaba" yaz
3. "Teşekkürler" yaz
4. ✅ Knowledge base'den cevap alırsın

### Senaryo 2: PDF Upload & Query
1. "Doküman Yükle" sekmesi
2. PDF yükle
3. "Sohbet" sekmesine dön
4. "PDF'de hangi konular var?" diye sor
5. ✅ Haystack'ten cevap alırsın

### Senaryo 3: API ile Programatik
1. Swagger UI aç
2. POST /api/chat ile mesaj gönder
3. POST /api/documents/upload ile dosya yükle
4. GET /api/documents ile listele
5. ✅ Tüm API'yi test edersin

---

## 🎬 Sonuç

Artık chatbot'un **nasıl çalıştığını görsel olarak** anlayabilirsin:

✅ **Web UI** - Kullanıcı dostu arayüz
✅ **Swagger** - API test arayüzü
✅ **FastAPI Docs** - Haystack arayüzü
✅ **Terminal** - Gelişmiş testler
✅ **Database** - Veri görüntüleme

---

## 🚀 Başlamak İçin

```bash
# Docker Desktop'ı aç, sonra:
cd /Users/dogandalkiran/Desktop/chatbot
docker-compose up -d

# 30 saniye bekle, sonra:
cd web-client && python3 -m http.server 8080

# Tarayıcıda aç:
http://localhost:8080
```

**İyi eğlenceler! 🎉**

