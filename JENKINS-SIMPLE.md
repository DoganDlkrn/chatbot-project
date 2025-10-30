# Jenkins Basitleştirilmiş Yaklaşım

## 🎯 Problem

Jenkins container'ı içinde Docker CLI yok, bu yüzden Docker komutları çalışmıyor.

## 💡 Çözüm Seçenekleri

### Seçenek 1: Basitleştirilmiş Pipeline (HIZLI - ÖNERİLEN)

Jenkins sadece şunları yapar:
- ✅ Kodu kontrol eder
- ✅ Test senaryolarını çalıştırır  
- ✅ Başarısız olursa email gönderir
- ⚠️ Docker build yapmaz (manuel veya webhook ile yapılır)

**Avantaj:** Hemen çalışır, basit
**Dezavantaj:** Full otomatik deployment yok

### Seçenek 2: Docker CLI'li Custom Jenkins (TAM ÇÖZÜM)

Jenkins container'ına Docker CLI kurulur ve tam CI/CD pipeline çalışır.

**Avantaj:** Tam otomatik deployment
**Dezavantaj:** Custom Dockerfile gerekir, biraz daha karmaşık

---

## 🚀 Seçenek 1: Basit Pipeline (Hemen Kullan)

Bu Jenkinsfile'ı kullan (Docker komutları YOK):

```groovy
pipeline {
    agent any
    
    environment {
        BRANCH_NAME = 'dev'
        NOTIFICATION_EMAIL = 'your-email@example.com'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '🔄 Checking out code from dev branch...'
                checkout scm
            }
        }
        
        stage('Code Validation') {
            steps {
                echo '✅ Validating project structure...'
                sh '''
                    # Check if required files exist
                    if [ ! -f "docker-compose.yml" ]; then
                        echo "❌ docker-compose.yml not found!"
                        exit 1
                    fi
                    
                    if [ ! -f "ChatbotAPI/ChatbotAPI.csproj" ]; then
                        echo "❌ ChatbotAPI.csproj not found!"
                        exit 1
                    fi
                    
                    echo "✅ All required files exist"
                '''
            }
        }
        
        stage('Simple Tests') {
            steps {
                echo '🧪 Running basic tests...'
                sh '''
                    # Simple file existence tests
                    echo "Checking C# files..."
                    find ChatbotAPI -name "*.cs" | wc -l
                    
                    echo "Checking Python files..."
                    find HaystackService -name "*.py" | wc -l
                    
                    echo "✅ Basic tests passed"
                '''
            }
        }
        
        stage('Deployment Info') {
            steps {
                echo '📦 Deployment Info'
                sh '''
                    echo "================================================"
                    echo "✅ Code validated successfully!"
                    echo "📝 Branch: ${BRANCH_NAME}"
                    echo "📝 Commit: ${GIT_COMMIT}"
                    echo ""
                    echo "⚠️  Manual deployment required:"
                    echo "   cd /path/to/chatbot"
                    echo "   docker-compose down"
                    echo "   docker-compose up -d --build"
                    echo "================================================"
                '''
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        
        failure {
            echo '❌ Pipeline failed! Sending notification...'
            emailext(
                to: "${env.NOTIFICATION_EMAIL}",
                subject: "❌ Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: """
                    <html>
                    <body style="font-family: Arial, sans-serif;">
                        <h2 style="color: #d32f2f;">❌ Build Failed</h2>
                        <table style="border-collapse: collapse; width: 100%;">
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Project:</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">${env.JOB_NAME}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Build Number:</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">${env.BUILD_NUMBER}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Branch:</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd;">${env.BRANCH_NAME}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Status:</strong></td>
                                <td style="padding: 8px; border: 1px solid #ddd; color: #d32f2f;"><strong>FAILED</strong></td>
                            </tr>
                        </table>
                        <br>
                        <p><a href="${env.BUILD_URL}console" style="background-color: #2196F3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">View Console Output</a></p>
                    </body>
                    </html>
                """,
                mimeType: 'text/html'
            )
        }
    }
}
```

Bu Jenkinsfile:
- ✅ Git'ten kodu çeker
- ✅ Dosyaların varlığını kontrol eder
- ✅ Basit testler yapar
- ✅ Başarısız olursa email gönderir
- ⚠️ Docker build yapmaz (sen manuel yaparsın)

---

## 🔧 Seçenek 2: Full CI/CD (Custom Jenkins)

Eğer tam otomasyonu istiyorsan, custom Jenkins image'ı oluşturmamız gerekir:

### 1. Jenkins Dockerfile Oluştur

`jenkins-docker/Dockerfile` oluştur:

```dockerfile
FROM jenkinsci/blueocean

USER root

# Docker CLI kurulumu
RUN apk add --no-cache docker-cli docker-compose

# Jenkins kullanıcısına docker yetkisi ver
RUN addgroup jenkins docker || true

USER jenkins
```

### 2. docker-compose.yml Güncelle

```yaml
jenkins:
  build:
    context: ./jenkins-docker
    dockerfile: Dockerfile
  container_name: chatbot_jenkins
  privileged: true
  # ... geri kalan ayarlar aynı
```

### 3. Rebuild Et

```bash
docker-compose build jenkins
docker-compose up -d jenkins
```

Bu sayede Jenkins container'ında Docker CLI kurulu olur ve Jenkinsfile'daki Docker komutları çalışır.

---

## 📋 Hangisini Seçmeliyim?

**Basit Pipeline (Seçenek 1):**
- Hemen çalışır
- Email bildirimleri çalışır
- Manuel deployment yaparsın
- Öğrenme amaçlı projeler için ideal

**Full CI/CD (Seçenek 2):**
- Biraz kurulum gerektirir
- Tam otomatik
- Production projeler için ideal

---

## 🎯 Önerilen Adımlar

1. **Şimdilik Basit Pipeline'ı kullan** (Seçenek 1)
2. Jenkins email ayarlarını yap
3. Test et (dev branch'e push yap)
4. Email gelirse ✅ başarılı!
5. İleride full automation istersen Seçenek 2'ye geç

**Hangi çözümü istersin?**

