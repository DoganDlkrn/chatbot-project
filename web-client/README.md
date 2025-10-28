# Web Client - Chatbot Arayüzü

## Açıklama

Bu basit bir HTML/CSS/JavaScript chatbot arayüzüdür. Herhangi bir framework gerektirmez ve doğrudan tarayıcıda çalışır.

## Kullanım

### 1. API'yi Çalıştırın

```bash
cd /Users/dogandalkiran/Desktop/chatbot
docker-compose up -d
```

### 2. Web Arayüzünü Açın

Tarayıcınızda şu dosyayı açın:
```
/Users/dogandalkiran/Desktop/chatbot/web-client/index.html
```

Veya basit bir HTTP server başlatın:

```bash
cd web-client
python3 -m http.server 8080
```

Sonra tarayıcıda: `http://localhost:8080`

### 3. Kullanmaya Başlayın

**Sohbet Sekmesi:**
- Chatbot ile mesajlaşın
- Yüklediğiniz dokümanlar hakkında sorular sorun

**Doküman Yükle Sekmesi:**
- PDF, TXT, DOC, DOCX dosyalarını yükleyin
- Yüklenen dokümanları görün
- Dokümanları silin

## Özellikler

✅ Modern ve responsive tasarım
✅ Gerçek zamanlı mesajlaşma
✅ Drag & drop dosya yükleme
✅ Doküman listesi
✅ Kaynak gösterimi (Database/Document)
✅ Session yönetimi
✅ Güzel animasyonlar

## CORS Ayarı

API zaten `AllowAll` CORS policy ile yapılandırılmıştır, bu yüzden ek ayar gerekmez.

## Özelleştirme

### Renkleri Değiştirme

`index.html` içindeki CSS'i düzenleyin:

```css
/* Ana gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* İstediğiniz renklere değiştirin */
background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
```

### API URL Değiştirme

```javascript
const API_URL = 'http://localhost:5000';
// Production için:
const API_URL = 'https://api.yourcompany.com';
```

## Production'a Alma

### Nginx Konfigürasyonu

```nginx
server {
    listen 80;
    server_name chatbot.company.com;

    root /var/www/chatbot-web;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Static Hosting

Bu tek sayfalık uygulama şu platformlarda host edilebilir:

- **Netlify**: Drag & drop deployment
- **Vercel**: GitHub integration
- **GitHub Pages**: Ücretsiz hosting
- **AWS S3 + CloudFront**: Scalable solution

## İleriye Yönelik Geliştirmeler

- [ ] TypeScript ile yeniden yazma
- [ ] React/Vue.js framework kullanma
- [ ] WebSocket ile real-time messaging
- [ ] File preview özelliği
- [ ] Dark mode
- [ ] Çoklu dil desteği
- [ ] Ses mesaj gönderme
- [ ] Emoji picker
- [ ] Markdown desteği
- [ ] Code highlighting

## Sorun Giderme

**CORS hatası alıyorum:**
- API'nin çalıştığından emin olun: `curl http://localhost:5000/api/chat/health`
- CORS ayarlarını kontrol edin

**Dosya yüklenmiyor:**
- Dosya boyutunu kontrol edin (max 10MB)
- Dosya uzantısını kontrol edin (.pdf, .txt, .doc, .docx)
- API loglarına bakın: `docker-compose logs chatbot-api`

**Mesaj gönderilmiyor:**
- Network tab'inde console'da hataları kontrol edin
- API'nin çalıştığından emin olun
- Session ID'nin doğru saklandığını kontrol edin

## Katkıda Bulunma

Bu basit bir örnek arayüzdür. İyileştirmeler için:

1. Fork edin
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request gönderin

