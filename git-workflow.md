# Git Workflow Rehberi

## Branch Yapısı

Bu projede şu branch stratejisi kullanılır:

- **main** - Production branch (canlı ortam)
- **dev** - Development branch (test ortamı, Jenkins CI/CD aktif)
- **feature/** - Feature branch'leri (yeni özellikler için)
- **bugfix/** - Bug fix branch'leri (hata düzeltmeleri için)
- **hotfix/** - Hotfix branch'leri (acil production düzeltmeleri)

## İlk Kurulum

### 1. Repository'yi Klonlama

```bash
git clone <repository-url>
cd chatbot
```

### 2. Dev Branch'e Geçiş

```bash
git checkout dev
```

### 3. Local Branch Oluşturma

```bash
# Feature branch
git checkout -b feature/chatbot-improvements

# Bugfix branch
git checkout -b bugfix/fix-pdf-upload

# Hotfix branch
git checkout -b hotfix/critical-security-fix
```

## Günlük Workflow

### Yeni Özellik Geliştirme

```bash
# 1. Dev branch'den güncel kodu çek
git checkout dev
git pull origin dev

# 2. Feature branch oluştur
git checkout -b feature/new-feature

# 3. Kodunuzu yazın ve commit edin
git add .
git commit -m "feat: add new feature"

# 4. Dev branch'e merge et (local)
git checkout dev
git merge feature/new-feature

# 5. Dev branch'e push et (Jenkins tetiklenir!)
git push origin dev

# 6. Feature branch'i sil (opsiyonel)
git branch -d feature/new-feature
```

### Hızlı Değişiklik (Doğrudan dev'de)

```bash
# 1. Dev branch'e geç
git checkout dev
git pull origin dev

# 2. Değişiklik yap
# ... kodlama ...

# 3. Commit ve push
git add .
git commit -m "fix: minor bug fix"
git push origin dev  # Jenkins otomatik çalışır
```

## Commit Message Kuralları

Conventional Commits standardını kullanın:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types:

- **feat**: Yeni özellik
- **fix**: Hata düzeltme
- **docs**: Dokümantasyon değişikliği
- **style**: Kod formatı (logic değişikliği yok)
- **refactor**: Kod refactoring
- **test**: Test ekleme/düzeltme
- **chore**: Bakım işleri (dependency update, vb.)
- **ci**: CI/CD değişiklikleri

### Örnekler:

```bash
git commit -m "feat(chatbot): add PDF text extraction"
git commit -m "fix(api): resolve database connection timeout"
git commit -m "docs(readme): update installation instructions"
git commit -m "refactor(services): improve document indexing performance"
git commit -m "ci(jenkins): add email notification on failure"
```

## Jenkins Trigger

### Dev Branch'e Push = Otomatik Deploy

Dev branch'e her push işleminde Jenkins otomatik olarak:

1. ✅ Kodu checkout eder
2. ✅ Docker image'larını build eder
3. ✅ Unit testleri çalıştırır
4. ✅ Uygulamayı deploy eder
5. ✅ Health check yapar
6. ✅ Sonucu e-mail ile bildirir

### Jenkins'i Manuel Tetikleme

```bash
# Empty commit ile tetikle
git commit --allow-empty -m "ci: trigger jenkins build"
git push origin dev
```

### Jenkins Build'i İzleme

1. Jenkins UI'a gidin: `http://localhost:8080`
2. `chatbot-pipeline` job'ına tıklayın
3. Son build'i açın
4. **Console Output** ile logları görün

## Production'a Deploy (Main Branch)

```bash
# 1. Dev branch'in test edildiğinden emin olun
git checkout dev
git pull origin dev

# 2. Main branch'e geç
git checkout main
git pull origin main

# 3. Dev'i main'e merge et
git merge dev

# 4. Tag oluştur (versioning)
git tag -a v1.0.0 -m "Release version 1.0.0"

# 5. Push et
git push origin main
git push origin --tags
```

## Faydalı Git Komutları

### Branch İşlemleri

```bash
# Tüm branch'leri listele
git branch -a

# Branch sil
git branch -d feature/old-feature

# Remote branch'i sil
git push origin --delete feature/old-feature

# Branch'i yeniden adlandır
git branch -m old-name new-name
```

### Değişiklikleri Geri Alma

```bash
# Son commit'i geri al (değişiklikler workspace'de kalır)
git reset --soft HEAD~1

# Son commit'i tamamen geri al
git reset --hard HEAD~1

# Belirli bir dosyayı geri al
git checkout -- filename

# Commit'i geri al (yeni commit oluşturarak)
git revert <commit-hash>
```

### Log ve History

```bash
# Commit history
git log --oneline --graph --all

# Son 10 commit
git log -10 --oneline

# Belirli dosyanın history'si
git log --follow filename

# Branch arasındaki farklar
git diff dev..main
```

### Stash (Geçici Saklama)

```bash
# Değişiklikleri geçici sakla
git stash

# Saklananları listele
git stash list

# En son stash'i geri getir
git stash pop

# Belirli stash'i uygula
git stash apply stash@{0}
```

## Conflict Çözümü

Merge conflict olduğunda:

```bash
# 1. Conflict'leri göster
git status

# 2. Dosyaları düzenle (conflict marker'ları kaldır)
# <<<<<<< HEAD
# your changes
# =======
# their changes
# >>>>>>> branch-name

# 3. Düzeltmeleri stage'e al
git add .

# 4. Merge'i tamamla
git commit -m "merge: resolve conflicts"
```

## Pre-commit Hooks (Opsiyonel)

Code quality için pre-commit hook:

```bash
# .git/hooks/pre-commit oluştur
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Run linter before commit
echo "Running pre-commit checks..."

# Add your checks here
# dotnet format --verify-no-changes
# python -m flake8

exit 0
EOF

chmod +x .git/hooks/pre-commit
```

## Sorun Giderme

### Push reddedildi:

```bash
git pull --rebase origin dev
git push origin dev
```

### Yanlış branch'e commit yaptım:

```bash
# Commit'i başka branch'e taşı
git checkout correct-branch
git cherry-pick <commit-hash>
git checkout wrong-branch
git reset --hard HEAD~1
```

### Remote branch ile senkronize değil:

```bash
git fetch origin
git reset --hard origin/dev
```

## Best Practices

1. ✅ Her zaman dev branch'den başlayın
2. ✅ Küçük, anlamlı commit'ler yapın
3. ✅ Conventional Commits kullanın
4. ✅ Push'tan önce local test yapın
5. ✅ Conflict'lerden kaçının (sık pull yapın)
6. ✅ Sensitive data commit'lemeyin (.env, secrets)
7. ✅ Feature branch'leri merge'den sonra silin
8. ✅ Production'a sadece test edilmiş kod gönderin

## Jenkins Email Notifications

Push sonrası e-mail alacaksınız:

- ✅ **Success:** Yeşil, deployment başarılı
- ❌ **Failure:** Kırmızı, deployment başarısız (loglar ekte)

Failure durumunda:
1. Jenkins console output'u kontrol edin
2. Hataları düzeltin
3. Yeniden commit & push yapın

