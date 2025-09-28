# System Administration Guide

> **대상**: 시스템 관리자, 개발자, DevOps 엔지니어
> **목적**: 시스템 설치, 배포, 운영, 모니터링 가이드

## 📋 목차

1. [시스템 설치](#시스템-설치)
2. [개발 환경 설정](#개발-환경-설정)
3. [프로덕션 배포](#프로덕션-배포)
4. [시스템 운영](#시스템-운영)
5. [모니터링 및 로깅](#모니터링-및-로깅)
6. [보안 관리](#보안-관리)
7. [장애 대응](#장애-대응)
8. [성능 최적화](#성능-최적화)

## 🔧 시스템 설치

### 전제 조건

**필수 요구사항**:
- **OS**: Linux, macOS, Windows 10+
- **Node.js**: 18.0.0 이상
- **Python**: 3.9.0 이상
- **메모리**: 최소 2GB, 권장 4GB+
- **디스크**: 최소 1GB, 권장 5GB+ (PDF 생성용)

**브라우저 요구사항** (PDF 생성용):
- Chrome/Chromium 90+ (Puppeteer 사용)
- 헤드리스 모드 지원

### 자동 설치

**Linux/Mac 환경**:
```bash
# 1. 리포지토리 클론
git clone <repository-url>
cd reveal.js-presentation

# 2. 자동 설정 스크립트 실행
chmod +x scripts/setup-linux.sh
./scripts/setup-linux.sh

# 3. 설치 확인
npm run health-check
```

**Windows 환경**:
```cmd
REM 1. 리포지토리 클론
git clone <repository-url>
cd reveal.js-presentation

REM 2. 자동 설정 스크립트 실행
scripts\setup-windows.bat

REM 3. 설치 확인
npm run health-check
```

### 수동 설치

**1. Node.js 및 npm 설치 확인**:
```bash
# 버전 확인
node --version  # v18.0.0+
npm --version   # v8.0.0+

# 설치가 필요한 경우
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS (Homebrew)
brew install node

# Windows: https://nodejs.org/에서 다운로드
```

**2. Python 설치 확인**:
```bash
# 버전 확인
python3 --version  # v3.9.0+

# 설치가 필요한 경우
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# macOS (Homebrew)
brew install python

# Windows: https://python.org/에서 다운로드
```

**3. 프로젝트 의존성 설치**:
```bash
# NPM 패키지 설치
npm install

# Python 의존성 설치 (필요시)
pip3 install -r requirements.txt
```

**4. Chrome 의존성 설치 (Linux)**:
```bash
# Ubuntu/Debian
sudo apt install -y \
  libnss3 \
  libatk-bridge2.0-0 \
  libdrm2 \
  libxcomposite1 \
  libxdamage1 \
  libxrandr2 \
  libgbm1 \
  libxss1 \
  libasound2t64 \
  libgtk-3-0t64

# CentOS/RHEL
sudo yum install -y \
  nss \
  atk \
  at-spi2-atk \
  gtk3 \
  cups-libs \
  libdrm \
  libxcomposite \
  libxdamage \
  libxrandr \
  libgbm \
  libxss \
  alsa-lib
```

## 🚀 개발 환경 설정

### 개발 서버 관리

**서버 시작**:
```bash
# 스크립트 사용 (권장)
./scripts/start-dev.sh      # Linux/Mac
scripts\start-dev.bat       # Windows

# 또는 NPM 명령어 직접 사용
npm run dev

# 커스텀 포트 사용
PORT=8080 npm run dev
```

**서버 상태 확인**:
```bash
# 포트 확인
curl -s http://localhost:5173/health || echo "Server not running"

# 프로세스 확인 (Linux/Mac)
ps aux | grep vite

# 프로세스 확인 (Windows)
tasklist | findstr node
```

**서버 종료**:
```bash
# 스크립트 사용 (권장)
./scripts/stop-dev.sh       # Linux/Mac
scripts\stop-dev.bat        # Windows

# 수동 종료
pkill -f vite               # Linux/Mac
taskkill /f /im node.exe    # Windows (모든 Node.js 프로세스)
```

### 포트 관리

**기본 포트 설정**:
- **개발 서버**: 5173 (Vite 기본값)
- **프로덕션**: 3000 (Express 서버)

**포트 충돌 해결**:
```bash
# 사용 중인 포트 확인
lsof -ti:5173              # Linux/Mac
netstat -ano | findstr :5173  # Windows

# 프로세스 강제 종료
kill -9 $(lsof -ti:5173)   # Linux/Mac
for /f "tokens=5" %a in ('netstat -ano ^| findstr :5173') do taskkill /f /pid %a  # Windows

# 다른 포트 사용
VITE_PORT=5174 npm run dev
```

### 환경 변수 설정

**개발 환경 (.env.development)**:
```bash
# 개발 서버 설정
VITE_PORT=5173
VITE_HOST=localhost

# PDF 생성 설정
PDF_OUTPUT_DIR=pdf-exports
PDF_DEFAULT_WIDTH=1920
PDF_DEFAULT_HEIGHT=1080

# 디버그 모드
DEBUG=true
VERBOSE_LOGGING=true
```

**프로덕션 환경 (.env.production)**:
```bash
# 서버 설정
NODE_ENV=production
PORT=3000
HOST=0.0.0.0

# PDF 생성 설정
PDF_OUTPUT_DIR=/app/pdf-exports
PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

# 로깅 설정
LOG_LEVEL=info
LOG_FILE=/var/log/presentation-system.log
```

## 🏭 프로덕션 배포

### Docker 배포 (권장)

**Dockerfile**:
```dockerfile
FROM node:18-alpine

# 시스템 의존성 설치
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    freetype-dev \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    python3 \
    py3-pip

# Puppeteer 설정
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 설치
COPY package*.json ./
RUN npm ci --only=production

# 소스 코드 복사
COPY . .

# 빌드
RUN npm run build

# 포트 노출
EXPOSE 3000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# 실행
CMD ["npm", "run", "start"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  presentation-system:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - PDF_OUTPUT_DIR=/app/pdf-exports
    volumes:
      - pdf-exports:/app/pdf-exports
      - ./slides:/app/slides:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - presentation-system
    restart: unless-stopped

volumes:
  pdf-exports:
```

**배포 스크립트**:
```bash
#!/bin/bash
# scripts/deploy-production.sh

set -e

echo "🚀 Starting production deployment..."

# 1. 이미지 빌드
echo "📦 Building Docker image..."
docker-compose build

# 2. 서비스 중단
echo "⏹️ Stopping existing services..."
docker-compose down

# 3. 새 서비스 시작
echo "▶️ Starting new services..."
docker-compose up -d

# 4. 헬스 체크
echo "🏥 Waiting for health check..."
sleep 30

if curl -f http://localhost:3000/health; then
    echo "✅ Deployment successful!"
else
    echo "❌ Deployment failed!"
    docker-compose logs
    exit 1
fi

echo "🎉 Production deployment complete!"
```

### 전통적 배포

**PM2를 사용한 프로세스 관리**:
```bash
# 1. PM2 설치
npm install -g pm2

# 2. 애플리케이션 빌드
npm run build

# 3. PM2 설정 파일 생성 (ecosystem.config.js)
module.exports = {
  apps: [{
    name: 'presentation-system',
    script: 'tools/server.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'development',
      PORT: 3000
    },
    env_production: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    log_file: '/var/log/presentation-system.log',
    error_file: '/var/log/presentation-system-error.log',
    out_file: '/var/log/presentation-system-out.log',
    max_memory_restart: '1G'
  }]
};

# 4. 애플리케이션 시작
pm2 start ecosystem.config.js --env production

# 5. 서비스 등록 (시스템 재시작 시 자동 시작)
pm2 startup
pm2 save
```

### Nginx 설정

**nginx.conf**:
```nginx
upstream presentation_backend {
    server localhost:3000;
    keepalive 32;
}

server {
    listen 80;
    server_name your-domain.com;

    # HTTPS로 리다이렉트
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL 설정
    ssl_certificate /etc/nginx/ssl/certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;

    # 보안 헤더
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # 정적 파일 서빙
    location /assets/ {
        root /app/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # PDF 파일 다운로드
    location /pdf-exports/ {
        alias /app/pdf-exports/;
        expires 1d;
        add_header Content-Disposition "attachment";
    }

    # 애플리케이션 프록시
    location / {
        proxy_pass http://presentation_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # 헬스 체크
    location /health {
        access_log off;
        proxy_pass http://presentation_backend;
    }
}
```

## 📊 시스템 운영

### 서비스 관리

**서비스 상태 확인**:
```bash
# Docker 환경
docker-compose ps
docker-compose logs -f presentation-system

# PM2 환경
pm2 status
pm2 logs presentation-system

# 시스템 리소스 확인
htop
df -h
free -m
```

**서비스 재시작**:
```bash
# Docker 환경
docker-compose restart presentation-system

# PM2 환경
pm2 restart presentation-system

# 전체 시스템 재시작
sudo systemctl restart presentation-system
```

### 백업 및 복구

**백업 스크립트**:
```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/backup/presentation-system"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$DATE"

mkdir -p "$BACKUP_PATH"

# 1. 콘텐츠 백업
echo "📂 Backing up content..."
cp -r slides/ "$BACKUP_PATH/slides/"

# 2. 설정 파일 백업
echo "⚙️ Backing up configuration..."
cp -r .claude/ "$BACKUP_PATH/.claude/"
cp package.json "$BACKUP_PATH/"
cp -r config/ "$BACKUP_PATH/config/"

# 3. PDF 파일 백업
echo "📄 Backing up PDFs..."
cp -r pdf-exports/ "$BACKUP_PATH/pdf-exports/"

# 4. 로그 백업
echo "📝 Backing up logs..."
cp -r logs/ "$BACKUP_PATH/logs/" 2>/dev/null || true

# 5. 압축
echo "🗜️ Compressing backup..."
cd "$BACKUP_DIR"
tar -czf "${DATE}.tar.gz" "$DATE/"
rm -rf "$DATE/"

echo "✅ Backup completed: ${BACKUP_DIR}/${DATE}.tar.gz"

# 6. 오래된 백업 정리 (30일 이전)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "🧹 Old backups cleaned up"
```

**복구 스크립트**:
```bash
#!/bin/bash
# scripts/restore.sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup-file.tar.gz>"
    exit 1
fi

BACKUP_FILE="$1"
RESTORE_DIR="/tmp/restore_$(date +%s)"

# 1. 백업 파일 압축 해제
echo "📦 Extracting backup..."
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

# 2. 현재 데이터 백업
echo "💾 Creating safety backup..."
./scripts/backup.sh

# 3. 서비스 중단
echo "⏹️ Stopping services..."
docker-compose down || pm2 stop presentation-system

# 4. 데이터 복구
echo "🔄 Restoring data..."
BACKUP_CONTENT=$(ls "$RESTORE_DIR")
cp -r "$RESTORE_DIR/$BACKUP_CONTENT"/* ./

# 5. 서비스 재시작
echo "▶️ Starting services..."
docker-compose up -d || pm2 start presentation-system

echo "✅ Restore completed!"
```

### 로그 관리

**로그 로테이션 설정** (/etc/logrotate.d/presentation-system):
```
/var/log/presentation-system*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        pm2 reloadLogs
    endscript
}
```

**로그 분석 스크립트**:
```bash
#!/bin/bash
# scripts/analyze-logs.sh

LOG_FILE="/var/log/presentation-system.log"
DATE="${1:-$(date +%Y-%m-%d)}"

echo "📊 Log Analysis for $DATE"
echo "================================="

# 요청 수 분석
echo "📈 Request Count:"
grep "$DATE" "$LOG_FILE" | grep "GET\|POST" | wc -l

# 오류 분석
echo "❌ Error Count:"
grep "$DATE" "$LOG_FILE" | grep -i "error" | wc -l

# 가장 많이 요청된 페이지
echo "🔥 Top Requested Pages:"
grep "$DATE" "$LOG_FILE" | grep "GET" | awk '{print $7}' | sort | uniq -c | sort -nr | head -10

# PDF 생성 통계
echo "📄 PDF Generation Stats:"
grep "$DATE" "$LOG_FILE" | grep "PDF generated" | wc -l

# 응답 시간 분석
echo "⏱️ Average Response Time:"
grep "$DATE" "$LOG_FILE" | grep "response_time" | awk '{sum += $NF; count++} END {if(count) print sum/count "ms"}'
```

## 📈 모니터링 및 로깅

### 헬스 체크 설정

**헬스 체크 엔드포인트** (tools/health-check.js):
```javascript
const express = require('express');
const fs = require('fs').promises;
const path = require('path');

async function healthCheck(req, res) {
    const checks = {
        timestamp: new Date().toISOString(),
        status: 'healthy',
        checks: {}
    };

    try {
        // 1. 파일 시스템 접근 확인
        await fs.access(path.join(__dirname, '../slides'));
        checks.checks.filesystem = 'ok';

        // 2. 메모리 사용량 확인
        const memUsage = process.memoryUsage();
        checks.checks.memory = {
            status: memUsage.heapUsed < 500 * 1024 * 1024 ? 'ok' : 'warning',
            heapUsed: Math.round(memUsage.heapUsed / 1024 / 1024) + 'MB'
        };

        // 3. PDF 생성 기능 확인
        const puppeteer = require('puppeteer');
        checks.checks.pdf_capability = 'ok';

        // 4. 디스크 공간 확인
        const stats = await fs.stat('.');
        checks.checks.disk = 'ok';

    } catch (error) {
        checks.status = 'unhealthy';
        checks.error = error.message;
    }

    const statusCode = checks.status === 'healthy' ? 200 : 503;
    res.status(statusCode).json(checks);
}

module.exports = { healthCheck };
```

### 메트릭 수집

**Prometheus 메트릭 설정**:
```javascript
const promClient = require('prom-client');

// 기본 메트릭 수집
const collectDefaultMetrics = promClient.collectDefaultMetrics;
collectDefaultMetrics({ timeout: 5000 });

// 커스텀 메트릭 정의
const httpRequestDuration = new promClient.Histogram({
    name: 'http_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route', 'status']
});

const pdfGenerationCounter = new promClient.Counter({
    name: 'pdf_generation_total',
    help: 'Total number of PDF generations',
    labelNames: ['status']
});

const activeSlides = new promClient.Gauge({
    name: 'active_slides_count',
    help: 'Number of active slide sets'
});

// 메트릭 미들웨어
function metricsMiddleware(req, res, next) {
    const start = Date.now();

    res.on('finish', () => {
        const duration = (Date.now() - start) / 1000;
        httpRequestDuration
            .labels(req.method, req.route?.path || req.path, res.statusCode)
            .observe(duration);
    });

    next();
}

module.exports = {
    promClient,
    httpRequestDuration,
    pdfGenerationCounter,
    activeSlides,
    metricsMiddleware
};
```

### 알림 설정

**Slack 알림 스크립트**:
```bash
#!/bin/bash
# scripts/alert.sh

SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
SERVICE_NAME="Presentation System"

send_alert() {
    local severity="$1"
    local message="$2"
    local emoji="⚠️"

    case "$severity" in
        "critical") emoji="🚨" ;;
        "warning") emoji="⚠️" ;;
        "info") emoji="ℹ️" ;;
    esac

    curl -X POST -H 'Content-type: application/json' \
        --data "{
            \"text\": \"${emoji} ${SERVICE_NAME} Alert\",
            \"attachments\": [{
                \"color\": \"danger\",
                \"fields\": [{
                    \"title\": \"Severity\",
                    \"value\": \"${severity}\",
                    \"short\": true
                }, {
                    \"title\": \"Message\",
                    \"value\": \"${message}\",
                    \"short\": false
                }, {
                    \"title\": \"Timestamp\",
                    \"value\": \"$(date)\",
                    \"short\": true
                }]
            }]
        }" \
        "$SLACK_WEBHOOK_URL"
}

# 사용 예시
if ! curl -f http://localhost:3000/health; then
    send_alert "critical" "Health check failed - service may be down"
fi
```

## 🔒 보안 관리

### SSL/TLS 설정

**Let's Encrypt 인증서 설정**:
```bash
#!/bin/bash
# scripts/setup-ssl.sh

DOMAIN="your-domain.com"
EMAIL="admin@your-domain.com"

# 1. Certbot 설치
sudo apt update
sudo apt install certbot python3-certbot-nginx

# 2. 인증서 발급
sudo certbot --nginx -d "$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive

# 3. 자동 갱신 설정
sudo crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

echo "✅ SSL certificate configured for $DOMAIN"
```

### 방화벽 설정

**UFW 방화벽 설정** (Ubuntu):
```bash
#!/bin/bash
# scripts/setup-firewall.sh

# 1. UFW 리셋 및 기본 정책 설정
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 2. SSH 접근 허용 (22번 포트)
sudo ufw allow ssh

# 3. HTTP/HTTPS 접근 허용 (80, 443번 포트)
sudo ufw allow http
sudo ufw allow https

# 4. 개발 서버 접근 허용 (필요시, 개발 환경에서만)
# sudo ufw allow 5173

# 5. 특정 IP에서만 관리 포트 접근 허용
ADMIN_IP="192.168.1.100"
sudo ufw allow from "$ADMIN_IP" to any port 3000

# 6. 방화벽 활성화
sudo ufw --force enable

# 7. 상태 확인
sudo ufw status verbose

echo "✅ Firewall configured successfully"
```

### 보안 검사 스크립트

**보안 취약점 검사**:
```bash
#!/bin/bash
# scripts/security-check.sh

echo "🔒 Security Check Report"
echo "======================="

# 1. NPM 보안 감사
echo "📦 NPM Security Audit:"
npm audit --audit-level moderate

# 2. 파일 권한 검사
echo "📁 File Permissions Check:"
find . -type f -perm /o+w | grep -v node_modules | head -10

# 3. 환경 변수 검사
echo "🔐 Environment Variables Check:"
if [ -f .env ]; then
    echo "⚠️ .env file found - ensure it's not committed to Git"
    grep -E "(password|secret|key)" .env | wc -l
fi

# 4. SSL 인증서 만료 확인
echo "🔏 SSL Certificate Check:"
if command -v openssl &> /dev/null; then
    echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates
fi

# 5. 포트 스캔
echo "🌐 Open Ports Check:"
ss -tuln | grep LISTEN

echo "✅ Security check completed"
```

## 🚨 장애 대응

### 자동 복구 스크립트

**서비스 자동 복구**:
```bash
#!/bin/bash
# scripts/auto-recovery.sh

SERVICE_URL="http://localhost:3000/health"
MAX_RETRIES=3
RETRY_COUNT=0

check_service() {
    curl -f "$SERVICE_URL" > /dev/null 2>&1
    return $?
}

restart_service() {
    echo "🔄 Restarting service..."

    if command -v docker-compose &> /dev/null; then
        docker-compose restart presentation-system
    elif command -v pm2 &> /dev/null; then
        pm2 restart presentation-system
    else
        systemctl restart presentation-system
    fi

    sleep 30
}

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if check_service; then
        echo "✅ Service is healthy"
        exit 0
    else
        echo "❌ Service health check failed (attempt $((RETRY_COUNT + 1))/$MAX_RETRIES)"
        restart_service
        ((RETRY_COUNT++))
    fi
done

echo "🚨 Service recovery failed after $MAX_RETRIES attempts"
# 알림 전송
./scripts/alert.sh "critical" "Service auto-recovery failed"
exit 1
```

### 장애 조사 도구

**로그 분석 도구**:
```bash
#!/bin/bash
# scripts/debug-issue.sh

ISSUE_TIME="${1:-$(date -d '1 hour ago' '+%Y-%m-%d %H:%M')}"

echo "🔍 Debugging issue around: $ISSUE_TIME"
echo "=================================="

# 1. 시스템 로그 확인
echo "📋 System Logs:"
journalctl --since "$ISSUE_TIME" | grep -E "(error|fail|critical)" | tail -20

# 2. 애플리케이션 로그 확인
echo "📝 Application Logs:"
if [ -f /var/log/presentation-system.log ]; then
    grep -A5 -B5 "$(date -d "$ISSUE_TIME" '+%Y-%m-%d %H')" /var/log/presentation-system.log | tail -30
fi

# 3. 메모리 사용량 히스토리
echo "💾 Memory Usage:"
free -m

# 4. 디스크 사용량
echo "💿 Disk Usage:"
df -h

# 5. 프로세스 상태
echo "⚙️ Process Status:"
if command -v docker-compose &> /dev/null; then
    docker-compose ps
elif command -v pm2 &> /dev/null; then
    pm2 status
fi

# 6. 네트워크 연결 상태
echo "🌐 Network Status:"
ss -tuln | grep -E "(5173|3000)"

echo "✅ Debug report completed"
```

## ⚡ 성능 최적화

### 성능 모니터링

**성능 메트릭 수집**:
```bash
#!/bin/bash
# scripts/performance-monitor.sh

LOG_FILE="/var/log/performance-$(date +%Y%m%d).log"

monitor_performance() {
    while true; do
        TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

        # CPU 사용률
        CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

        # 메모리 사용률
        MEM_USAGE=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100.0}')

        # 디스크 I/O
        DISK_IO=$(iostat -d 1 1 | tail -n +4 | awk 'NR==2{print $4}')

        # 응답 시간
        RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}\n' http://localhost:3000/health)

        echo "$TIMESTAMP,CPU:$CPU_USAGE,MEM:$MEM_USAGE,DISK:$DISK_IO,RESPONSE:$RESPONSE_TIME" >> "$LOG_FILE"

        sleep 60
    done
}

# 백그라운드에서 실행
monitor_performance &
echo "📊 Performance monitoring started (PID: $!)"
```

### 캐싱 설정

**Redis 캐싱 설정**:
```javascript
// tools/cache.js
const redis = require('redis');
const client = redis.createClient({
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379
});

class CacheManager {
    constructor() {
        this.defaultTTL = 3600; // 1시간
    }

    async get(key) {
        try {
            const value = await client.get(key);
            return value ? JSON.parse(value) : null;
        } catch (error) {
            console.error('Cache get error:', error);
            return null;
        }
    }

    async set(key, value, ttl = this.defaultTTL) {
        try {
            await client.setex(key, ttl, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Cache set error:', error);
            return false;
        }
    }

    async del(key) {
        try {
            await client.del(key);
            return true;
        } catch (error) {
            console.error('Cache delete error:', error);
            return false;
        }
    }

    // 슬라이드 캐싱
    async getCachedSlide(topic) {
        return await this.get(`slide:${topic}`);
    }

    async cacheSlide(topic, content) {
        return await this.set(`slide:${topic}`, content, 7200); // 2시간
    }

    // PDF 캐싱
    async getCachedPDF(topic) {
        return await this.get(`pdf:${topic}`);
    }

    async cachePDF(topic, pdfBuffer) {
        return await this.set(`pdf:${topic}`, pdfBuffer.toString('base64'), 86400); // 24시간
    }
}

module.exports = new CacheManager();
```

### 데이터베이스 최적화

**SQLite 성능 튜닝** (메타데이터 저장용):
```sql
-- 성능 최적화 설정
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 1000000;
PRAGMA temp_store = memory;

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_slides_topic ON slides(topic);
CREATE INDEX IF NOT EXISTS idx_slides_created_at ON slides(created_at);
CREATE INDEX IF NOT EXISTS idx_pdf_cache_topic ON pdf_cache(topic);
```

이 시스템 관리 가이드는 시스템의 안정적인 운영을 위한 모든 필수 사항을 다룹니다. 추가 질문이나 특정 환경에 대한 맞춤 설정이 필요하시면 [specification.system.md](specification.system.md)를 참조하거나 지원팀에 문의해 주세요.