# Deployment Rehberi

## Local Development

### Hızlı Başlangıç

```bash
# 1. Repository'yi klonla
git clone <repository-url>
cd chatbot

# 2. Gerekli dosyaları düzenle
cp .env.example .env
# .env dosyasını düzenleyin

# 3. Setup scriptini çalıştır
chmod +x setup.sh
./setup.sh

# 4. Servislerin hazır olmasını bekle
docker-compose logs -f
```

### Manuel Kurulum

```bash
# Docker container'ları başlat
docker-compose up -d

# Logları izle
docker-compose logs -f chatbot-api
docker-compose logs -f haystack-service

# Servis durumunu kontrol et
docker-compose ps

# Health check
curl http://localhost:5000/api/chat/health
curl http://localhost:8001/health
```

### Development Modu (Hot Reload)

**C# API:**

```bash
cd ChatbotAPI
dotnet watch run
```

**Python Service:**

```bash
cd HaystackService
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8001
```

## Docker Deployment

### Production Build

```bash
# All services
docker-compose -f docker-compose.prod.yml up -d

# Sadece API
docker-compose up -d chatbot-api

# Sadece Haystack
docker-compose up -d haystack-service
```

### Custom Docker Images

```bash
# C# API build
cd ChatbotAPI
docker build -t myregistry/chatbot-api:v1.0.0 .
docker push myregistry/chatbot-api:v1.0.0

# Python Service build
cd HaystackService
docker build -t myregistry/haystack-service:v1.0.0 .
docker push myregistry/haystack-service:v1.0.0
```

## Jenkins CI/CD Deployment

### Prerequisites

1. Jenkins kurulumu (bkz: jenkins-setup.md)
2. Docker ve Docker Compose yüklü
3. Git repository bağlantısı
4. SMTP ayarları yapılmış

### Pipeline Kurulumu

```bash
# 1. Jenkins'e git repository'yi tanıt
# 2. Pipeline job oluştur
# 3. Jenkinsfile'ı tanımla
# 4. Build trigger ayarla (dev branch)
```

### Dev Branch Workflow

```bash
# Kod değişikliği yap
git checkout dev
git add .
git commit -m "feat: new feature"

# Push et (Jenkins otomatik deploy eder)
git push origin dev

# Jenkins'te build'i izle
# http://localhost:8080
```

### Production Deploy

```bash
# Dev'den main'e merge
git checkout main
git merge dev

# Tag oluştur
git tag -a v1.0.0 -m "Release v1.0.0"

# Push
git push origin main --tags

# Manuel production deploy (Jenkins veya manuel)
docker-compose -f docker-compose.prod.yml up -d
```

## Cloud Deployment

### AWS Deployment

**1. EC2 Instance Kurulumu:**

```bash
# SSH ile bağlan
ssh -i key.pem ubuntu@ec2-instance

# Docker kur
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Repository klonla
git clone <repo-url>
cd chatbot

# Deploy
docker-compose up -d
```

**2. RDS PostgreSQL:**

```bash
# .env güncellle
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/chatbot_db
```

**3. Load Balancer:**

- Application Load Balancer oluştur
- Target Group: EC2 instance
- Health check: /api/chat/health

### Azure Deployment

**Azure Container Instances:**

```bash
# Container Registry oluştur
az acr create --name chatbotregistry --resource-group chatbot-rg

# Image'ları push et
az acr login --name chatbotregistry
docker tag chatbot-api chatbotregistry.azurecr.io/chatbot-api:latest
docker push chatbotregistry.azurecr.io/chatbot-api:latest

# Container instance oluştur
az container create \
  --resource-group chatbot-rg \
  --name chatbot-api \
  --image chatbotregistry.azurecr.io/chatbot-api:latest \
  --ports 8080
```

### Google Cloud Platform

**Cloud Run:**

```bash
# Artifact Registry
gcloud artifacts repositories create chatbot-repo \
  --repository-format=docker \
  --location=us-central1

# Build & Deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/chatbot-api
gcloud run deploy chatbot-api \
  --image gcr.io/PROJECT-ID/chatbot-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Kubernetes Deployment

### K8s Manifests

**deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatbot-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chatbot-api
  template:
    metadata:
      labels:
        app: chatbot-api
    spec:
      containers:
      - name: chatbot-api
        image: chatbot-api:latest
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: database-url
```

**service.yaml:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: chatbot-api-service
spec:
  selector:
    app: chatbot-api
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

### Deploy to K8s

```bash
# Apply manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods
kubectl get services

# Logs
kubectl logs -f deployment/chatbot-api
```

## Environment Variables

### Production .env

```bash
# Database
DATABASE_URL=postgresql://prod_user:strong_pass@db-host:5432/chatbot_prod

# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notifications@company.com
SMTP_PASSWORD=app_specific_password
NOTIFICATION_EMAIL=devops@company.com

# Security
JWT_SECRET=random_strong_secret
ALLOWED_ORIGINS=https://chatbot.company.com

# Monitoring
SENTRY_DSN=https://sentry.io/...
LOG_LEVEL=INFO
```

## SSL/TLS Setup

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name chatbot.company.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name chatbot.company.com;

    ssl_certificate /etc/letsencrypt/live/chatbot.company.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/chatbot.company.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Let's Encrypt SSL

```bash
# Certbot kur
sudo apt-get install certbot python3-certbot-nginx

# SSL sertifikası al
sudo certbot --nginx -d chatbot.company.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Monitoring & Logging

### Prometheus + Grafana

```bash
# Prometheus
docker run -d -p 9090:9090 prom/prometheus

# Grafana
docker run -d -p 3000:3000 grafana/grafana
```

### Centralized Logging (ELK Stack)

```bash
# Elasticsearch
docker run -d -p 9200:9200 elasticsearch:8.11.0

# Logstash
docker run -d -p 5000:5000 logstash:8.11.0

# Kibana
docker run -d -p 5601:5601 kibana:8.11.0
```

## Backup & Recovery

### Database Backup

```bash
# PostgreSQL backup
docker exec chatbot_postgres pg_dump -U postgres chatbot_db > backup.sql

# Restore
docker exec -i chatbot_postgres psql -U postgres chatbot_db < backup.sql
```

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Database
docker exec chatbot_postgres pg_dump -U postgres chatbot_db > \
  $BACKUP_DIR/db_$DATE.sql

# Uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz uploads/

# Keep only last 7 days
find $BACKUP_DIR -mtime +7 -delete
```

### Cron Job

```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh
```

## Scaling

### Horizontal Scaling

```bash
# API'yi scale et
docker-compose up -d --scale chatbot-api=3

# Kubernetes
kubectl scale deployment chatbot-api --replicas=5
```

### Load Balancing

**Nginx:**

```nginx
upstream chatbot_backend {
    server localhost:5001;
    server localhost:5002;
    server localhost:5003;
}

server {
    location / {
        proxy_pass http://chatbot_backend;
    }
}
```

## Health Checks

### Monitoring Endpoints

```bash
# API Health
curl http://localhost:5000/api/chat/health

# Haystack Health
curl http://localhost:8001/health

# Database Health
docker exec chatbot_postgres pg_isready

# Elasticsearch Health
curl http://localhost:9200/_cluster/health
```

### Automated Health Check Script

```bash
#!/bin/bash
# healthcheck.sh

if ! curl -f http://localhost:5000/api/chat/health; then
    echo "API is down! Restarting..."
    docker-compose restart chatbot-api
    # Send alert email
fi
```

## Troubleshooting

### Container Issues

```bash
# Logs
docker-compose logs -f chatbot-api

# Restart
docker-compose restart chatbot-api

# Rebuild
docker-compose up -d --build chatbot-api

# Shell access
docker exec -it chatbot_api bash
```

### Network Issues

```bash
# Check network
docker network ls
docker network inspect chatbot_chatbot_network

# DNS resolution
docker exec chatbot_api ping postgres
```

### Performance Issues

```bash
# Resource usage
docker stats

# Database connections
docker exec chatbot_postgres psql -U postgres -c \
  "SELECT * FROM pg_stat_activity;"
```

## Security Checklist

- [ ] HTTPS enabled
- [ ] Strong database passwords
- [ ] Environment variables secured
- [ ] CORS configured properly
- [ ] Rate limiting implemented
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] File upload restrictions
- [ ] Regular security updates
- [ ] Secrets not in git

## Production Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Monitoring setup
- [ ] Logging configured
- [ ] Backup automation
- [ ] Health checks working
- [ ] Load balancer configured
- [ ] DNS configured
- [ ] Email notifications working
- [ ] Documentation updated
- [ ] Disaster recovery plan

