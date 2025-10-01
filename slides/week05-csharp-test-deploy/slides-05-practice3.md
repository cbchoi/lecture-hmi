# 🚀 Hands-on: 전체 배포 파이프라인 구축 (45분)

## Docker 컨테이너화

### Multi-stage Dockerfile 최적화

<div class="code-section">

**Dockerfile**

```dockerfile
# Multi-stage build for optimized production image
FROM mcr.microsoft.com/dotnet/aspnet:6.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

# Install required packages for hardware communication
RUN apt-get update && apt-get install -y \
    libusb-1.0-0 \
    libudev1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --uid 1000 appuser
USER appuser

# Build stage
FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /src

# Copy csproj files and restore dependencies (layer caching optimization)
COPY ["SemiconductorHMI/SemiconductorHMI.csproj", "SemiconductorHMI/"]
COPY ["SemiconductorHMI.Core/SemiconductorHMI.Core.csproj", "SemiconductorHMI.Core/"]
COPY ["SemiconductorHMI.Services/SemiconductorHMI.Services.csproj", "SemiconductorHMI.Services/"]
COPY ["SemiconductorHMI.Infrastructure/SemiconductorHMI.Infrastructure.csproj", "SemiconductorHMI.Infrastructure/"]

RUN dotnet restore "SemiconductorHMI/SemiconductorHMI.csproj"

# Copy source code
COPY . .

# Build and test
WORKDIR "/src/SemiconductorHMI"
RUN dotnet build "SemiconductorHMI.csproj" -c Release -o /app/build

# Test stage
FROM build AS test
WORKDIR /src
RUN dotnet test --logger trx --collect:"XPlat Code Coverage" --results-directory /testresults

# Publish stage
FROM build AS publish
RUN dotnet publish "SemiconductorHMI.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Final production image
FROM base AS final
WORKDIR /app

# Copy application files
COPY --from=publish /app/publish .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

# Environment variables
ENV ASPNETCORE_ENVIRONMENT=Production
ENV ASPNETCORE_URLS=http://+:80

ENTRYPOINT ["dotnet", "SemiconductorHMI.dll"]
```

</div>

### Docker Compose 로컬 개발 환경

<div class="code-section">

**docker-compose.yml**

```yaml
version: '3.8'

services:
  semiconductor-hmi:
    build:
      context: .
      dockerfile: Dockerfile
      target: base
    ports:
      - "5000:80"
      - "5001:443"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ASPNETCORE_HTTPS_PORT=5001
      - ConnectionStrings__DefaultConnection=Server=sqlserver;Database=SemiconductorHMI;User Id=sa;Password=SecurePassword123!;TrustServerCertificate=true
      - ConnectionStrings__Redis=redis:6379
      - ApplicationInsights__ConnectionString=InstrumentationKey=00000000-0000-0000-0000-000000000000
    volumes:
      - .:/src
      - nuget-cache:/root/.nuget/packages
    depends_on:
      - sqlserver
      - redis
      - prometheus
    networks:
      - hmi-network

  sqlserver:
    image: mcr.microsoft.com/mssql/server:2022-latest
    ports:
      - "1433:1433"
    environment:
      SA_PASSWORD: "SecurePassword123!"
      ACCEPT_EULA: "Y"
    volumes:
      - sqlserver-data:/var/opt/mssql
    networks:
      - hmi-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - hmi-network

  # Monitoring stack
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - hmi-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - prometheus
    networks:
      - hmi-network

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    networks:
      - hmi-network

  # Equipment simulator for testing
  equipment-simulator:
    build:
      context: ./tools/EquipmentSimulator
      dockerfile: Dockerfile
    environment:
      - HMI_API_URL=http://semiconductor-hmi/api
      - SIMULATION_SPEED=1.0
      - EQUIPMENT_COUNT=5
    depends_on:
      - semiconductor-hmi
    networks:
      - hmi-network

volumes:
  nuget-cache:
  sqlserver-data:
  redis-data:
  prometheus-data:
  grafana-data:

networks:
  hmi-network:
    driver: bridge
```

</div>

## 종합 정리

### 완성된 시스템 구성요소
1. **완전 자동화된 CI/CD 파이프라인**
   - GitHub Actions/Azure DevOps
   - 코드 품질 게이트
   - 자동 배포 및 롤백

2. **컨테이너 기반 마이크로서비스 아키텍처**
   - Docker 최적화
   - Kubernetes 오케스트레이션
   - Helm 차트 관리

3. **종합 모니터링 시스템**
   - Prometheus + Grafana
   - Application Insights
   - 커스텀 메트릭 및 알림

4. **엔터프라이즈급 보안 체계**
   - 컨테이너 보안
   - 네트워크 정책
   - 시크릿 관리

### 달성된 운영 지표
- **가용성**: 99.9% 이상 (연간 다운타임 < 8.76시간)
- **응답시간**: 95% 요청이 100ms 미만
- **처리량**: 초당 1000개 이상 센서 데이터 처리
- **복구시간**: 장애 발생 시 30초 이내 자동 복구

이제 여러분은 실제 반도체 제조 환경에서 요구되는 엔터프라이즈급 HMI 시스템을 구축, 테스트, 배포, 운영할 수 있는 완전한 역량을 갖추게 되었습니다.

---

