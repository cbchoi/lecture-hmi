# C# 테스트/배포 및 유지보수

## 🎯 학습 목표
- 반도체 장비 HMI의 체계적인 테스트 전략 및 자동화 테스트 구현 능력 습득
- CI/CD 파이프라인을 통한 안전하고 효율적인 배포 프로세스 구축
- 산업용 환경에서의 장기간 운영을 위한 모니터링 및 유지보수 체계 확립
- 성능 프로파일링과 최적화를 통한 안정적인 24/7 운영 체계 구현

## 📚 주요 내용
- Unit Test 및 Integration Test 설계 및 구현 (MSTest, xUnit, NUnit)
- UI 자동화 테스트 (TestStack.White, FlaUI)
- 성능 테스트 및 부하 테스트 (NBomber, PerfDotNet)
- CI/CD 파이프라인 구축 (Azure DevOps, GitHub Actions, Jenkins)
- Docker 컨테이너화 및 Kubernetes 배포
- 모니터링 및 로깅 시스템 (Serilog, Application Insights, Prometheus)
- 장애 대응 및 복구 전략
- 버전 관리 및 릴리스 관리

## ⏰ 예상 소요 시간
- **이론 강의**: 45분 (테스트 전략, CI/CD, 모니터링)
- **기초 실습**: 45분 (Unit Test 및 Integration Test)
- **심화 실습**: 45분 (UI 자동화 테스트 및 성능 테스트)
- **Hands-on**: 45분 (전체 배포 파이프라인 구축)
- **총합**: 180분

## 👥 대상 청중
- **수준**: 고급 (전체 개발 라이프사이클 경험 필수)
- **사전 지식**: 소프트웨어 테스팅 기초, DevOps 개념, 컨테이너 기술 이해
- **도구 경험**: Git, Azure/AWS 클라우드 서비스, Docker 사용 경험 권장

## 💻 실습 환경
- **운영체제**: Windows 10/11 (64bit) + Linux 컨테이너 지원
- **필수 소프트웨어**:
  - Visual Studio 2022 Community + Test Explorer
  - .NET 6.0 SDK + ASP.NET Core Runtime
  - Docker Desktop
  - Azure CLI 또는 AWS CLI
- **선택 소프트웨어**:
  - SonarQube (코드 품질 분석)
  - Grafana + Prometheus (모니터링)

## 📖 사전 준비
- [ ] 4주차 고급 UI/UX 프로젝트 완성 및 Git 저장소 준비
- [ ] [.NET Testing Best Practices](https://docs.microsoft.com/en-us/dotnet/core/testing/) 숙지
- [ ] Docker 및 컨테이너 기본 개념 학습
- [ ] CI/CD 파이프라인 기본 개념 복습

## 🔗 참고 자료
- [Testing in .NET](https://docs.microsoft.com/en-us/dotnet/core/testing/)
- [Azure DevOps Documentation](https://docs.microsoft.com/en-us/azure/devops/)
- [Docker for .NET](https://docs.microsoft.com/en-us/dotnet/architecture/containerized-lifecycle/)
- [Application Insights](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [Serilog Documentation](https://serilog.net/)

## 📋 체크리스트
- [ ] 체계적인 테스트 전략 수립 및 구현
- [ ] 자동화된 CI/CD 파이프라인 구축
- [ ] 컨테이너 기반 배포 환경 구성
- [ ] 실시간 모니터링 및 알림 시스템 구현
- [ ] 장애 대응 프로세스 및 복구 전략 수립