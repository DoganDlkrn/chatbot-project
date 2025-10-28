# 🤖 Chatbot - Basit Kullanım Rehberi

## 🎯 BU SİSTEM NE YAPAR?

1. **Seninle Konuşur** - Basit sorulara cevap verir
2. **PDF Yüklersin** - PDF içeriğini okur
3. **PDF Hakkında Soru Sorarsın** - PDF'deki bilgilerden cevap verir

---

## 💾 DATABASE (VERİTABANI) NEDİR?

**PostgreSQL** - Senin için otomatik kuruldu, Docker'da çalışıyor.

**Ne işe yarar?**
- Yüklediğin PDF'leri kaydeder
- Sohbet geçmişini saklar
- Bilgi bankasını tutar

**Sen bir şey yapmana gerek yok!** Otomatik çalışıyor.

---

## 📁 KULLANILAN SİSTEMLER:

| İsim | Ne İşe Yarar? | Durum |
|------|---------------|-------|
| **PostgreSQL** | Veritabanı (PDF listesi, chat geçmişi) | ✅ Çalışıyor |
| **Haystack** | PDF'leri okur ve arama yapar | ✅ Çalışıyor |
| **C# API** | Backend (arka plan) servisi | ✅ Çalışıyor |
| **Web UI** | Tarayıcıda gördüğün arayüz | ✅ Çalışıyor |
| **Jenkins** | Otomatik deploy (GEREKLİ DEĞİL) | ❌ Kurulmadı |

---

## 🚀 NASIL KULLANILIR?

### 1. Sistemi Başlat:
```bash
# Terminal'de
cd /Users/dogandalkiran/Desktop/chatbot
docker-compose up -d
```

### 2. Web Arayüzünü Aç:
```bash
# Başka bir terminal'de
cd web-client
python3 -m http.server 8080
```

Tarayıcıda: **http://localhost:8080**

### 3. PDF Yükle:
- "Doküman Yükle" sekmesine git
- PDF'i sürükle
- 5-10 saniye bekle

### 4. Soru Sor:
- "Sohbet" sekmesine dön
- "Bu PDF'de neler var?" diye sor

---

## 🛑 DURDURMAK İÇİN:

```bash
# Docker'ı durdur
docker-compose down

# Web server'ı durdur (Terminal'de CTRL+C)
```

---

## ❓ SORUN ÇÖZME:

### PDF okuyamıyor:
```bash
# 1. Haystack kontrol
curl http://localhost:8001/health

# 2. Yeni PDF yükle (eski silindi)
```

### Chatbot cevap vermiyor:
```bash
# API kontrol
curl http://localhost:5001/api/chat/health
```

### Docker çalışmıyor:
```bash
# Docker Desktop'ı aç
docker ps
```

---

## 🎯 ÖNEMLİ NOTLAR:

### Jenkins Nedir?
**Otomatik deploy sistemi** - Git'e kod attığında otomatik çalıştırır.
**SENİN İÇİN GEREKLİ DEĞİL** - Proje zaten çalışıyor!

### Jenkins'i Kurmak İster misin?
**HAYIR** - Şu an gerekli değil
**EVET** - 30 dakika sürer, opsiyonel

---

## 📊 SİSTEM MİMARİSİ (BASİT):

```
TARAYICI (Web UI)
    ↓
C# API (Port 5001)
    ↓
PostgreSQL (Veritabanı)
    ↓
Haystack (PDF Okuyucu)
```

Hepsi **Docker'da otomatik** çalışıyor!

---

## ✅ ÇALIŞIYOR MU KONTROL:

```bash
# Tüm servisleri kontrol et
docker-compose ps

# API
curl http://localhost:5001/api/chat/health

# Haystack
curl http://localhost:8001/health

# Database
docker exec chatbot_postgres pg_isready
```

---

## 🎨 SADE ARAYÜZ İSTİYORSAN:

Şu an ki arayüz biraz renkli. Daha sade istersen:
- Gradient renkler → Tek renk
- Animasyonlar → Kaldır
- Basit tasarım → Minimal

**İster misin düzelteyim?** (5 dk)

---

## 💡 SONUÇ:

✅ **Sistem çalışıyor**
✅ **Database var (PostgreSQL)**
❌ **Jenkins yok (gerekli değil)**
⚠️ **PDF indexleme yavaş** (düzeltilecek)

**SORULAR?** Sor, sade cevaplarım!

