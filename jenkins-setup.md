# Jenkins Kurulum ve Yapılandırma Rehberi

## Jenkins Kurulumu

### 1. Jenkins'i Docker ile Çalıştırma

```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

### 2. İlk Kurulum

1. `http://localhost:8080` adresine gidin
2. İlk admin şifresini alın:
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```
3. Önerilen pluginleri yükleyin
4. Admin kullanıcı oluşturun

### 3. Gerekli Pluginler

Jenkins Dashboard'da **Manage Jenkins** → **Manage Plugins** → **Available** sekmesinden şu pluginleri yükleyin:

- **Git Plugin** - Git entegrasyonu için
- **Docker Pipeline Plugin** - Docker komutları için
- **Email Extension Plugin** - E-mail bildirimleri için
- **Pipeline** - Pipeline desteği için
- **Workspace Cleanup Plugin** - Otomatik temizleme için

## Pipeline Yapılandırması

### 1. Yeni Pipeline Job Oluşturma

1. **New Item** → **Pipeline** seçin
2. İsim verin: `chatbot-pipeline`
3. **OK** tıklayın

### 2. Pipeline Yapılandırması

**Pipeline** bölümünde:

- **Definition:** Pipeline script from SCM
- **SCM:** Git
- **Repository URL:** Git repository URL'nizi girin
- **Credentials:** GitHub credentials ekleyin (gerekirse)
- **Branch Specifier:** `*/dev` (dev branch için)
- **Script Path:** `Jenkinsfile`

### 3. Build Triggers

**Build Triggers** bölümünde:

- ✅ **Poll SCM** seçeneğini işaretleyin
- **Schedule:** `H/5 * * * *` (Her 5 dakikada bir kontrol)

Veya GitHub webhook kullanmak için:

- ✅ **GitHub hook trigger for GITScm polling**

### 4. E-mail Yapılandırması

**Manage Jenkins** → **Configure System** → **Extended E-mail Notification**:

```
SMTP Server: smtp.gmail.com
SMTP Port: 587
Use SMTP Authentication: ✅
Username: your-email@gmail.com
Password: your-app-password (Gmail App Password)
Use TLS: ✅
```

**E-mail Notification** bölümünde de aynı ayarları yapın.

### 5. Environment Variables

**Manage Jenkins** → **Configure System** → **Global properties** → **Environment variables**:

```
Name: NOTIFICATION_EMAIL
Value: admin@example.com
```

## Git Webhook Kurulumu (Opsiyonel)

### GitHub için:

1. Repository **Settings** → **Webhooks** → **Add webhook**
2. **Payload URL:** `http://your-jenkins-url:8080/github-webhook/`
3. **Content type:** `application/json`
4. **Events:** "Just the push event"
5. **Active:** ✅

## Dev Branch Workflow

### 1. Local'de çalışma:

```bash
# Dev branch'e geç
git checkout dev

# Değişikliklerinizi yapın
# ...

# Commit edin
git add .
git commit -m "feat: new feature"

# Push edin (Jenkins tetiklenir)
git push origin dev
```

### 2. Jenkins otomatik olarak:

1. ✅ Kodu checkout eder
2. ✅ Docker image'larını build eder
3. ✅ Testleri çalıştırır
4. ✅ Deploy eder
5. ✅ Health check yapar
6. ✅ Başarı/hata e-maili gönderir

## Manuel Test

Pipeline'ı manuel olarak test etmek için:

```bash
# Dev branch'e push yapın
git checkout dev
git commit --allow-empty -m "test: trigger jenkins"
git push origin dev
```

## Jenkins Docker Access

Jenkins container'ının Docker komutlarını çalıştırabilmesi için:

```bash
# Jenkins container'ına girin
docker exec -u root -it jenkins bash

# Docker'ı yükleyin
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Jenkins kullanıcısını docker grubuna ekleyin
usermod -aG docker jenkins

# Container'ı yeniden başlatın
exit
docker restart jenkins
```

## Sorun Giderme

### E-mail gönderilmiyor:
- Gmail için "App Password" kullanın
- SMTP ayarlarını kontrol edin
- Test e-mail gönderin: **Manage Jenkins** → **Configure System** → **Test configuration**

### Docker komutları çalışmıyor:
- Docker socket'in mount edildiğinden emin olun
- Jenkins kullanıcısının Docker grubunda olduğundan emin olun

### Pipeline başarısız oluyor:
- Console output'u kontrol edin
- Docker servislerinin çalıştığından emin olun
- Port çakışması olmadığını kontrol edin

## Güvenlik

Production için:

1. Jenkins'i reverse proxy (nginx) arkasında çalıştırın
2. SSL/TLS sertifikası kullanın
3. Güçlü şifreler kullanın
4. Secrets için Jenkins Credentials kullanın
5. RBAC (Role-Based Access Control) yapılandırın

## Monitoring

Jenkins build durumunu izlemek için:

- **Build History** - Son build'leri görün
- **Console Output** - Detaylı logları inceleyin
- **Blue Ocean** - Modern UI (plugin gerektirir)

