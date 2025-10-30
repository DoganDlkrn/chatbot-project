FROM jenkinsci/blueocean:latest

USER root

# Docker CLI ve Docker Compose kurulumu
RUN apk add --no-cache \
    docker-cli \
    docker-compose \
    curl \
    bash

# Jenkins kullanıcısını docker grubuna ekle
RUN addgroup -S docker 2>/dev/null || true && \
    addgroup jenkins docker 2>/dev/null || true

USER jenkins

