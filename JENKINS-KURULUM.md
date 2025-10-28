# Jenkins Kurulum ve Yapılandırma Rehberi

## 🚀 1. Jenkins'e İlk Giriş

### Jenkins'i Açın
- **URL:** http://localhost:8082
- **İlk Giriş Şifresi:** `f89c55af4a0045e5914a2e3d857df10e`

### Kurulum Adımları

1. **Unlock Jenkins Ekranı:**
   - Yukarıdaki şifreyi yapıştırın
   - "Continue" butonuna tıklayın

2. **Plugin Seçimi:**
   - "Install suggested plugins" seçeneğini seçin
   - Kurulum tamamlanana kadar bekleyin (2-3 dakika)

3. **Admin Kullanıcı Oluşturun:**
   ```
   Kullanıcı Adı: admin
   Şifre: [Güçlü bir şifre belirleyin]
   Email: [Email adresiniz]
   ```
   - "Save and Continue" tıklayın

4. **Jenkins URL Onayı:**
   - Varsayılan olarak `http://localhost:8082` gelecek
   - "Save and Finish" tıklayın

---

## 🔧 2. Email Bildirimleri Yapılandırma

### SMTP Ayarları

1. **Jenkins Ana Sayfada:**
   - Sol menüden "Manage Jenkins" → "System" (veya "Configure System")

2. **E-mail Notification Bölümü:**
   Sayfayı aşağı kaydırın ve "E-mail Notification" bölümünü bulun:

   ```
   SMTP Server: smtp.gmail.com
   Use SMTP Authentication: ✓ (işaretleyin)
   
   User Name: sizinemail@gmail.com
   Password: [Gmail App Password - aşağıda açıklandı]
   
   Use SSL: ✓ (işaretleyin)
   SMTP Port: 465
   
   Reply-To Address: sizenemail@gmail.com
   Charset: UTF-8
   ```

3. **Gmail App Password Oluşturma:**
   - Google hesabınıza gidin: https://myaccount.google.com/
   - "Security" → "2-Step Verification" (Açık olmalı)
   - "App passwords" → "Select app: Mail" → "Generate"
   - Oluşan 16 karakterlik şifreyi Jenkins'e yapıştırın

4. **Test Email Gönderin:**
   - "Test configuration by sending test e-mail" kutusunu işaretleyin
   - Test email adresinizi girin
   - "Test configuration" butonuna tıklayın
   - Email gelirse ayarlar doğru!

5. **Kaydet:**
   - "Save" butonuna tıklayın

---

## 🎯 3. Pipeline (Job) Oluşturma

### Yeni Pipeline Oluşturun

1. **Jenkins Ana Sayfa:**
   - "New Item" (Sol üst) tıklayın

2. **Pipeline Yapılandırması:**
   ```
   Item Name: chatbot-dev-pipeline
   Type: Pipeline (seçin)
   ```
   - "OK" butonuna tıklayın

3. **Pipeline Ayarları:**

   **General Sekmesi:**
   - Description: "Chatbot Dev Branch CI/CD Pipeline"
   - ✓ GitHub project (işaretleyin)
     - Project url: [GitHub repo URL'niz]

   **Build Triggers:**
   - ✓ Poll SCM (işaretleyin)
     - Schedule: `H/5 * * * *` (Her 5 dakikada bir kontrol et)
     - Bu, Git'te değişiklik varsa otomatik build tetikler

   **Pipeline Sekmesi:**
   - Definition: "Pipeline script from SCM" seçin
   - SCM: "Git" seçin
   - Repository URL: [GitHub repo URL'niz]
   - Credentials: "Add" → "Jenkins"
     ```
     Kind: Username with password
     Username: [GitHub kullanıcı adınız]
     Password: [GitHub Personal Access Token]
     ID: github-credentials
     ```
   - Branch Specifier: `*/dev` (dev branch'i izleyecek)
   - Script Path: `Jenkinsfile`

4. **Kaydet:**
   - "Save" butonuna tıklayın

---

## 🔑 4. GitHub Personal Access Token Oluşturma

1. **GitHub'a gidin:**
   - https://github.com/settings/tokens

2. **Yeni Token Oluşturun:**
   - "Generate new token" → "Classic"
   - Note: "Jenkins CI/CD"
   - Expiration: 90 days (veya No expiration)
   - Seçilecek Yetkiler:
     - ✓ repo (tüm alt seçenekler)
     - ✓ admin:repo_hook

3. **Token'ı Kopyalayın:**
   - Oluşan token'ı kopyalayın (bir daha gösterilmez!)
   - Jenkins'de "Password" alanına yapıştırın

---

## 🔄 5. Git Workflow - Jenkins Tetikleme

### Projeyi Git'e Ekleyin

```bash
# Terminal'de proje dizinine gidin
cd /Users/dogandalkiran/Desktop/chatbot

# Git initialize edin (henüz yapmadıysanız)
git init

# .gitignore'u kontrol edin
cat .gitignore

# Dosyaları ekleyin
git add .

# İlk commit
git commit -m "Initial commit: Chatbot project with Jenkins CI/CD"

# Dev branch oluşturun
git checkout -b dev

# GitHub'a bağlayın (GitHub'da repo oluşturduktan sonra)
git remote add origin https://github.com/KULLANICI_ADI/REPO_ADI.git

# Dev branch'i push edin
git push -u origin dev
```

### Değişiklik Yaptığınızda

```bash
# Değişiklik yaptınız...

# Değişiklikleri görmek için
git status

# Dosyaları stage'e ekleyin
git add .

# Commit edin
git commit -m "Feature: Yeni özellik eklendi"

# Dev branch'e push edin
git push origin dev

# Jenkins otomatik olarak değişikliği algılayacak ve build başlatacak!
```

---

## 📧 6. Email Bildirimi Test Etme

### Pipeline'ı Manuel Çalıştırma

1. **Jenkins Ana Sayfa:**
   - "chatbot-dev-pipeline" üzerine tıklayın

2. **Build Başlatın:**
   - Sol menüden "Build Now" tıklayın

3. **Build Durumunu İzleyin:**
   - Altta "Build History" bölümünde build göreceksiniz
   - Build numarasına tıklayın
   - "Console Output" ile logları görebilirsiniz

4. **Email Kontrolü:**
   - Build başarısız olursa email almalısınız
   - Jenkinsfile'da email bildirimi yapılandırılmış durumda

---

## 🧪 7. Hata Testi (Email Bildirimi)

Email bildiriminin çalıştığından emin olmak için:

1. **Jenkinsfile'da bir hata oluşturun:**
   ```groovy
   stage('Test Email') {
       steps {
           sh 'exit 1'  // Bu build'i başarısız kılacak
       }
   }
   ```

2. **Commit ve Push edin:**
   ```bash
   git add Jenkinsfile
   git commit -m "Test: Email notification test"
   git push origin dev
   ```

3. **Email gelmeli:**
   - Konu: "Build Failed: chatbot-dev-pipeline"
   - İçerik: Hata detayları ve branch bilgisi

---

## 🎨 8. Jenkins Dashboard Özellikleri

### Build Durumları

- ☀️ **Mavi:** Build başarılı
- ☁️ **Sarı:** Build unstable
- ⛈️ **Kırmızı:** Build başarısız
- ⚪ **Gri:** Build henüz çalıştırılmadı

### Build History

- Her build'in loglarını görebilirsiniz
- "Console Output" ile detaylı hata mesajları
- "Changes" ile hangi commit'in build'i tetiklediğini görürsünüz

---

## ❓ Sık Karşılaşılan Sorunlar

### 1. Email Gönderilmiyor

**Çözüm:**
- Gmail App Password kullandığınızdan emin olun (normal şifre değil)
- 2-Step Verification açık olmalı
- SMTP Port: 465, SSL: Aktif

### 2. Git Credential Hatası

**Çözüm:**
- GitHub Personal Access Token kullandığınızdan emin olun
- Token'ın `repo` yetkisi olmalı

### 3. Pipeline Tetiklenmiyor

**Çözüm:**
- Poll SCM ayarını kontrol edin: `H/5 * * * *`
- Jenkins GitHub'a erişebiliyor mu kontrol edin
- "Build Now" ile manuel test edin

### 4. Docker Build Hatası

**Çözüm:**
- Jenkins container'ın Docker socket'e erişimi var mı kontrol edin
- `docker-compose.yml`'de `/var/run/docker.sock` mount edilmiş olmalı

---

## 🎯 Özet: Tam İş Akışı

```
1. Kod Değişikliği Yaptınız
   ↓
2. Git Commit & Push (dev branch)
   ↓
3. Jenkins Her 5 Dakikada Git'i Kontrol Eder
   ↓
4. Değişiklik Tespit Edilirse Build Başlar
   ↓
5. Jenkinsfile Çalıştırılır:
   - Docker imajlar build edilir
   - Testler çalıştırılır
   - Deploy edilir
   ↓
6. Build Başarılı: ✓ Hiçbir şey olmaz
7. Build Başarısız: ✗ Email gönderilir!
```

---

## 📝 Notlar

- Jenkins şifresi: İlk kurulumda belirlediğiniz şifre
- Jenkins portu: 8082 (8080 web-client tarafından kullanılıyor)
- Pipeline her dev branch push'unda otomatik çalışır
- Email sadece başarısız build'lerde gönderilir

---

## 🔗 Faydalı Linkler

- Jenkins Dokümantasyonu: https://www.jenkins.io/doc/
- Pipeline Syntax: https://www.jenkins.io/doc/book/pipeline/syntax/
- Email Extension Plugin: https://plugins.jenkins.io/email-ext/

---

**Hazır! Jenkins kurulumunuz tamamlandı. Artık Git ile kod gönderdiğinizde Jenkins otomatik olarak build başlatacak ve hata olursa email gönderecek! 🎉**

