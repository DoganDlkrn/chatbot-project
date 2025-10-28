# 👋 BURADAN BAŞLA!

## Hoş Geldin! 🎉

Bu chatbot projesini çalıştırmak için **sadece 3 adım** var:

---

## ⚡ Hızlı Başlangıç

### 1️⃣ Docker Desktop'ı Aç
Mac'te Applications → Docker.app

### 2️⃣ Terminal'de Çalıştır:
```bash
cd /Users/dogandalkiran/Desktop/chatbot

# Environment dosyası oluştur
cat > .env << 'EOF'
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
NOTIFICATION_EMAIL=
EOF

# Servisleri başlat
docker-compose up -d

# 30 saniye bekle...
sleep 30
```

### 3️⃣ Test Et:
```bash
# Web arayüzünü başlat
cd web-client
python3 -m http.server 8080
```

**Tarayıcıda aç:** http://localhost:8080

---

## 🎯 Ne Yapabilirsin?

### Web Arayüzünde (http://localhost:8080)
✅ Chatbot ile konuş
✅ PDF dosyası yükle
✅ PDF hakkında soru sor

### Swagger UI'da (http://localhost:5000/swagger)
✅ API'yi test et
✅ Endpoint'leri keşfet
✅ Canlı istekler gönder

### Haystack API'de (http://localhost:8001/docs)
✅ Document search test et
✅ Indexing işlemlerini gör

---

## 📚 Detaylı Rehberler

Daha fazla bilgi için:

1. **DEMO-GUIDE.md** ← 🎬 **Görsel demo, buraya bak!**
2. **QUICKSTART.md** ← Hızlı başlangıç
3. **API-EXAMPLES.md** ← API örnekleri
4. **jenkins-setup.md** ← CI/CD kurulumu
5. **git-workflow.md** ← Git kullanımı

---

## 🆘 Sorun mu Yaşıyorsun?

### Docker çalışmıyor:
```bash
# Docker Desktop'ın açık olduğundan emin ol
docker ps
```

### Portlar kullanımda:
```bash
# Çalışan uygulamaları kontrol et
lsof -i :5000
lsof -i :8001
```

### Servisleri yeniden başlat:
```bash
docker-compose down
docker-compose up -d
```

### Logları kontrol et:
```bash
docker-compose logs -f
```

---

## ✨ İlk Testi Yap

Terminalden hızlı test:

```bash
# API health check
curl http://localhost:5000/api/chat/health

# Chat mesajı gönder
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Merhaba"}'
```

Çalışıyorsa bu cevabı göreceksin:
```json
{
  "sessionId": "...",
  "message": "Merhaba! Ben bir yapay zeka asistanıyım...",
  "source": "database"
}
```

---

## 🎊 Başarılı! Şimdi Ne Yapmalısın?

1. ✅ Web arayüzünü aç ve chatbot ile konuş
2. ✅ Bir PDF yükle ve hakkında soru sor
3. ✅ Swagger'da API'yi keşfet
4. ✅ **DEMO-GUIDE.md** dosyasını oku (en detaylı rehber)

---

**Kolay gelsin! 🚀**

Sorun olursa **DEMO-GUIDE.md** dosyasına bak, orada her şey adım adım anlatılıyor!

