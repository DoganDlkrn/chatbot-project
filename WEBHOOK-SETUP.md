# GitHub Webhook Kurulumu - Push Anında Tetikleme

## Sorun
`git push origin dev` yaptığınızda pipeline otomatik olarak çalışmıyor. Sadece polling (her 1 dakikada kontrol) var, bu yüzden push anında tetiklenmiyor.

## Çözüm: GitHub Webhook

GitHub webhook ile push anında Jenkins pipeline'ı tetiklenir.

---

## 📋 Adım 1: Jenkins'te GitHub Plugin Kontrolü

1. **Jenkins'e gidin:** http://localhost:8082
2. **Manage Jenkins** → **Manage Plugins** → **Installed** sekmesi
3. Şu plugin'lerin kurulu olduğundan emin olun:
   - ✅ **GitHub plugin** (GitHub integration)
   - ✅ **GitHub Branch Source Plugin** (opsiyonel ama önerilir)

Eğer yoksa:
- **Available** sekmesine gidin
- "GitHub plugin" arayın ve yükleyin
- Jenkins'i yeniden başlatın

---

## 📋 Adım 2: Jenkins Job Yapılandırması

1. **Jenkins Dashboard** → **chatbot-pipeline** job'una tıklayın
2. **Configure** (veya "Konfigürasyonu Düzenle") tıklayın
3. **Build Triggers** bölümüne gidin
4. **✅ GitHub hook trigger for GITScm polling** checkbox'ını işaretleyin
5. **Poll SCM** checkbox'ını kaldırın (veya bırakın, webhook çalışmazsa polling devreye girer)
6. **Kaydet** (Save) butonuna tıklayın

---

## 📋 Adım 3: GitHub Webhook Ekleme

### Önemli Not: Local Jenkins için

Jenkins'iniz `localhost:8082`'de çalışıyor. GitHub'dan local Jenkins'e webhook göndermek için **internet üzerinden erişilebilir** olması gerekir.

### Seçenek 1: Ngrok (Önerilen - Test için)

1. **Ngrok kurun:**
   ```bash
   brew install ngrok
   # veya https://ngrok.com/download
   ```

2. **Ngrok tunnel başlatın:**
   ```bash
   ngrok http 8082
   ```

3. **Ngrok size bir URL verecek:**
   ```
   Forwarding: https://abc123.ngrok.io -> http://localhost:8082
   ```
   Bu URL'yi kopyalayın (örn: `https://abc123.ngrok.io`)

### Seçenek 2: Cloud Jenkins (Production için)

Jenkins'i AWS, DigitalOcean, vs. gibi bir cloud'da çalıştırın.

---

## 📋 Adım 4: GitHub Repository'de Webhook Ekleme

1. **GitHub'a gidin:** https://github.com/DoganDlkrn/chatbot-project
2. **Settings** → **Webhooks** → **Add webhook** tıklayın
3. **Webhook ayarları:**
   - **Payload URL:** 
     - Eğer ngrok kullanıyorsanız: `https://abc123.ngrok.io/github-webhook/`
     - Eğer cloud Jenkins ise: `http://your-jenkins-ip:8082/github-webhook/`
     - **ÖNEMLİ:** Sonuna `/github-webhook/` eklemeyi unutmayın!
   
   - **Content type:** `application/json`
   - **Secret:** Boş bırakabilirsiniz (veya güvenlik için bir secret ekleyin)
   - **Events:** "Just the push event" seçin
   - **Active:** ✅ İşaretli olsun

4. **Add webhook** butonuna tıklayın

---

## 📋 Adım 5: Test

1. **Test commit yapın:**
   ```bash
   git checkout dev
   echo "# test" >> test.txt
   git add test.txt
   git commit -m "test: webhook trigger"
   git push origin dev
   ```

2. **Jenkins'i kontrol edin:**
   - Jenkins Dashboard'da `chatbot-pipeline` job'una bakın
   - Push yaptıktan sonra **birkaç saniye içinde** yeni bir build başlamalı

3. **GitHub Webhook Logları:**
   - GitHub → Settings → Webhooks → Webhook'unuzun yanındaki **"Recent Deliveries"** tıklayın
   - Başarılı ise ✅ yeşil, başarısız ise ❌ kırmızı görünür
   - Hata varsa detayları görebilirsiniz

---

## 🔍 Sorun Giderme

### Webhook tetiklenmiyor:

1. **Ngrok URL'sinin doğru olduğundan emin olun:**
   ```bash
   curl https://abc123.ngrok.io/github-webhook/ -X POST
   ```

2. **Jenkins loglarını kontrol edin:**
   ```bash
   docker logs chatbot-jenkins-1 --tail 100
   ```

3. **GitHub webhook delivery loglarını kontrol edin:**
   - GitHub → Settings → Webhooks → Recent Deliveries
   - Hata mesajlarını okuyun

4. **Jenkins job config'i kontrol edin:**
   - "GitHub hook trigger for GITScm polling" işaretli mi?
   - Repository URL doğru mu?
   - Credentials doğru mu?

### "Connection refused" hatası:

- Ngrok çalışıyor mu kontrol edin: `ngrok http 8082`
- Ngrok URL'si değiştiyse GitHub webhook'u güncelleyin

### Webhook 200 OK dönüyor ama build başlamıyor:

- Jenkins job config'te "GitHub hook trigger" işaretli mi?
- Branch name doğru mu? (`dev` branch'i için)
- Jenkinsfile'da trigger yapılandırması doğru mu?

---

## ✅ Başarılı Kurulum Sonrası

Artık her `git push origin dev` yaptığınızda:
1. GitHub webhook'u Jenkins'e bildirim gönderir
2. Jenkins pipeline **birkaç saniye içinde** otomatik başlar
3. Build başarılı/başarısız email alırsınız

---

## 📝 Notlar

- **Poll SCM** hala `Jenkinsfile`'da var, bu webhook çalışmazsa yedek olarak devreye girer
- Ngrok URL'si her başlatmada değişir, production için sabit bir domain kullanın
- GitHub webhook'ları maksimum 10 saniye içinde yanıt bekler, Jenkins'in hızlı yanıt vermesi gerekir

