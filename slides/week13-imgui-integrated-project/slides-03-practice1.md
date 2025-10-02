
# ===== 빌드 스테이지 =====
FROM ubuntu:22.04 AS builder

# 빌드 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    pkg-config \
    libssl-dev \
    libcurl4-openssl-dev \
    libjsoncpp-dev \
    libmosquitto-dev \
    libicu-dev \
    libboost-all-dev \
    libopengl-dev \
    libglfw3-dev \
    libglew-dev \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /build

# ImGui 및 의존성 라이브러리 빌드
COPY third_party/ ./third_party/
RUN cd third_party && \
    # ImGui 빌드
    mkdir -p imgui/build && cd imgui/build && \
    cmake .. -GNinja -DCMAKE_BUILD_TYPE=Release && \
    ninja && \
    ninja install && \
    cd ../.. && \
    # GLM 설치
    cd glm && \
    cmake . -GNinja -DCMAKE_BUILD_TYPE=Release && \
    ninja install && \
    cd .. && \
    # Assimp 빌드
    cd assimp && \
    cmake . -GNinja -DCMAKE_BUILD_TYPE=Release -DASSIMP_BUILD_TESTS=OFF && \
    ninja && \
    ninja install

# 소스 코드 복사
COPY src/ ./src/
COPY CMakeLists.txt ./
COPY cmake/ ./cmake/

# 애플리케이션 빌드
RUN cmake . -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_STANDARD=20 \
    -DENABLE_OPTIMIZATION=ON \
    -DENABLE_SECURITY_HARDENING=ON \
    && ninja

# ===== 런타임 스테이지 =====
FROM ubuntu:22.04 AS runtime

# 런타임 의존성만 설치
RUN apt-get update && apt-get install -y \
    libssl3 \
    libcurl4 \
    libjsoncpp25 \
    libmosquitto1 \
    libicu70 \
    libboost-system1.74.0 \
    libboost-filesystem1.74.0 \
    libboost-thread1.74.0 \
    libopengl0 \
    libglfw3 \
    libglew2.2 \
    ca-certificates \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 비특권 사용자 생성
RUN groupadd -r hmiuser && useradd -r -g hmiuser hmiuser

# 애플리케이션 디렉토리 생성
RUN mkdir -p /app/{bin,config,logs,data,plugins,certs} && \
    chown -R hmiuser:hmiuser /app

# 빌드된 애플리케이션 복사
COPY --from=builder /build/SemiconductorHMI /app/bin/
COPY --from=builder /build/plugins/*.so /app/plugins/
COPY config/ /app/config/
COPY certs/ /app/certs/

# 실행 권한 설정
RUN chmod +x /app/bin/SemiconductorHMI && \
    chown -R hmiuser:hmiuser /app

# 헬스체크 스크립트
COPY scripts/healthcheck.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/healthcheck.sh

# 사용자 전환
USER hmiuser
WORKDIR /app

# 포트 노출
EXPOSE 8080 8443 1883

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# 환경 변수 설정
ENV HMI_CONFIG_PATH=/app/config \
    HMI_LOG_LEVEL=INFO \
    HMI_ENABLE_METRICS=true

# 엔트리포인트
ENTRYPOINT ["/app/bin/SemiconductorHMI"]
CMD ["--config", "/app/config/production.json"]
```

#### 1.2 Docker Compose 설정

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 메인 HMI 애플리케이션
  hmi-app:
    build:
      context: .
      dockerfile: Dockerfile.production
      target: runtime
    container_name: semiconductor-hmi
    restart: unless-stopped
    ports:
      - "8080:8080"   # HTTP
      - "8443:8443"   # HTTPS
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config:ro
      - ./certs:/app/certs:ro
    environment:
      - HMI_DB_HOST=postgres
      - HMI_MQTT_BROKER=mqtt-broker:1883
      - HMI_REDIS_HOST=redis:6379
      - HMI_LOG_LEVEL=INFO
    depends_on:
      - postgres
      - redis
      - mqtt-broker
    networks:
      - hmi-network
    healthcheck:
      test: ["CMD", "/usr/local/bin/healthcheck.sh"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # PostgreSQL 데이터베이스
  postgres:
    image: postgres:15-alpine
    container_name: hmi-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: hmi_database
      POSTGRES_USER: hmi_user
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d:ro
    ports:
      - "5432:5432"
    secrets:
      - postgres_password
    networks:
      - hmi-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hmi_user -d hmi_database"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Redis 캐시
  redis:
    image: redis:7-alpine
    container_name: hmi-redis
    restart: unless-stopped
    command: redis-server /usr/local/etc/redis/redis.conf
    volumes:
      - redis_data:/data
      - ./redis/redis.conf:/usr/local/etc/redis/redis.conf:ro
    ports:
      - "6379:6379"
    networks:
      - hmi-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # MQTT 브로커
  mqtt-broker:
    image: eclipse-mosquitto:2.0
    container_name: hmi-mqtt
    restart: unless-stopped
    volumes:
      - ./mqtt/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro
      - ./mqtt/passwd:/mosquitto/config/passwd:ro
      - mqtt_data:/mosquitto/data
      - mqtt_logs:/mosquitto/log
    ports:
      - "1883:1883"
      - "8883:8883"
    networks:
      - hmi-network

  # Prometheus 모니터링
  prometheus:
    image: prom/prometheus:latest
    container_name: hmi-prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - hmi-network

  # Grafana 대시보드
  grafana:
    image: grafana/grafana:latest
    container_name: hmi-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD_FILE=/run/secrets/grafana_password
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    ports:
      - "3000:3000"
    secrets:
      - grafana_password
    networks:
      - hmi-network
    depends_on:
      - prometheus

  # Nginx 리버스 프록시
  nginx:
    image: nginx:alpine
    container_name: hmi-nginx
    restart: unless-stopped
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    networks:
      - hmi-network
    depends_on:
      - hmi-app

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  mqtt_data:
    driver: local
  mqtt_logs:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local

networks:
  hmi-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

secrets:
  postgres_password:
    file: ./secrets/postgres_password.txt
  grafana_password:
    file: ./secrets/grafana_password.txt
```

### 2. Kubernetes 배포

#### 2.1 Kubernetes 매니페스트

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: semiconductor-hmi
  labels:
    name: semiconductor-hmi
    environment: production

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: hmi-config
  namespace: semiconductor-hmi
data:
  production.json: |
    {
      "system": {
        "name": "SemiconductorHMI_Enterprise",
        "version": "1.0.0",
        "environment": "production"
      },
      "database": {
        "host": "postgres-service",
        "port": 5432,
        "name": "hmi_database",
        "username": "hmi_user"
      },
      "mqtt": {
        "broker": "mqtt-service:1883",
        "client_id": "hmi_k8s_cluster"
      },
      "redis": {
        "host": "redis-service",
        "port": 6379
      },
      "security": {
        "enable_encryption": true,
        "session_timeout_minutes": 30,
        "max_failed_attempts": 3
      },
      "monitoring": {
        "enable_metrics": true,
        "metrics_port": 8080,
        "health_check_interval_ms": 5000
      }
    }

---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: hmi-secrets
  namespace: semiconductor-hmi
type: Opaque
data:
  # Base64 인코딩된 값들
  postgres-password: aG1pX3Bhc3N3b3JkXzEyMw==
  jwt-secret: c3VwZXJfc2VjcmV0X2p3dF9rZXk=
  encryption-key: YWVzXzI1Nl9lbmNyeXB0aW9uX2tleQ==

---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hmi-app
  namespace: semiconductor-hmi
  labels:
    app: hmi-app
    version: v1.0.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: hmi-app
  template:
    metadata:
      labels:
        app: hmi-app
        version: v1.0.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: hmi-service-account
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
      - name: hmi-app
        image: semiconductor-hmi:1.0.0
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
          name: http
          protocol: TCP
        - containerPort: 8443
          name: https
          protocol: TCP
        env:
        - name: HMI_CONFIG_PATH
          value: "/app/config"
        - name: HMI_LOG_LEVEL
          value: "INFO"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: hmi-secrets
              key: postgres-password
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: hmi-secrets
              key: jwt-secret
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /startup
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 30
      volumes:
      - name: config
        configMap:
          name: hmi-config
      - name: data
        persistentVolumeClaim:
          claimName: hmi-data-pvc
      - name: logs
        emptyDir: {}
      nodeSelector:
        node-type: application
      tolerations:
      - key: "application"
        operator: "Equal"
        value: "hmi"
        effect: "NoSchedule"

---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: hmi-service
  namespace: semiconductor-hmi
  labels:
    app: hmi-app
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
    name: http
  - port: 443
    targetPort: 8443
    protocol: TCP
    name: https
  selector:
    app: hmi-app

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hmi-ingress
  namespace: semiconductor-hmi
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTP"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - hmi.semiconductor.company.com
    secretName: hmi-tls-secret
  rules:
  - host: hmi.semiconductor.company.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: hmi-service
            port:
              number: 80

---
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: hmi-hpa
  namespace: semiconductor-hmi
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hmi-app
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

### 3. CI/CD 파이프라인

#### 3.1 Jenkins 파이프라인

```groovy
// Jenkinsfile
pipeline {
    agent {
        kubernetes {
            yaml '''
                apiVersion: v1
                kind: Pod
                spec:
                  containers:
                  - name: docker
                    image: docker:20.10-dind
                    securityContext:
                      privileged: true
                    volumeMounts:
                    - name: docker-sock
                      mountPath: /var/run/docker.sock
                  - name: kubectl
                    image: bitnami/kubectl:latest
                    command:
                    - cat
                    tty: true
                  - name: helm
                    image: alpine/helm:latest
                    command:
                    - cat
                    tty: true
                  volumes:
                  - name: docker-sock
                    hostPath:
                      path: /var/run/docker.sock
            '''
        }
    }

    environment {
        DOCKER_REGISTRY = 'your-registry.com'
        IMAGE_NAME = 'semiconductor-hmi'
        KUBECONFIG = credentials('k8s-config')
        DOCKER_CREDENTIALS = credentials('docker-registry-creds')
        SONAR_TOKEN = credentials('sonar-token')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                    env.BUILD_VERSION = "${env.BUILD_NUMBER}-${env.GIT_COMMIT_SHORT}"
                }
            }
        }

        stage('Code Quality Analysis') {
            parallel {
                stage('Static Analysis') {
                    steps {
                        container('docker') {
                            sh '''
                                # SonarQube 분석
                                docker run --rm \
                                    -v ${WORKSPACE}:/usr/src \
                                    -e SONAR_HOST_URL=${SONAR_HOST_URL} \
                                    -e SONAR_LOGIN=${SONAR_TOKEN} \
                                    sonarsource/sonar-scanner-cli \
                                    -Dsonar.projectKey=semiconductor-hmi \
                                    -Dsonar.sources=src \
                                    -Dsonar.cfamily.build-wrapper-output=bw-output
                            '''
                        }
                    }
                }

                stage('Security Scan') {
                    steps {
                        container('docker') {
                            sh '''
                                # Trivy 보안 스캔
                                docker run --rm \
                                    -v ${WORKSPACE}:/workspace \
                                    aquasec/trivy fs \
                                    --security-checks vuln,secret,config \
                                    --format sarif \
                                    --output /workspace/trivy-report.sarif \
                                    /workspace
                            '''
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'trivy-report.sarif', fingerprint: true
                        }
                    }
                }
            }
        }

        stage('Build and Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        container('docker') {
                            sh '''
                                # 테스트용 Docker 이미지 빌드
                                docker build -f Dockerfile.test -t ${IMAGE_NAME}:test .

                                # 단위 테스트 실행
                                docker run --rm \
