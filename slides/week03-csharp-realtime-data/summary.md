# C# 실시간 데이터 처리 및 통신

## 🎯 학습 목표
- 반도체 장비의 실시간 센서 데이터 수집 및 처리 기법 습득
- 멀티스레딩을 활용한 안전하고 효율적인 비동기 프로그래밍 능력 확보
- TCP/IP, SignalR 등 산업용 통신 프로토콜을 이용한 실시간 데이터 통신 구현
- 24/7 연속 운영 환경을 위한 메모리 관리 및 성능 최적화 기법 적용

## 📚 주요 내용
- .NET의 멀티스레딩 모델 (Thread, Task, async/await)
- 스레드 안전성과 동기화 메커니즘 (lock, Mutex, SemaphoreSlim)
- 실시간 데이터 수집을 위한 Timer 및 BackgroundService 활용
- TCP/IP 소켓 프로그래밍과 SignalR을 통한 실시간 통신
- 대용량 센서 데이터의 효율적 처리 및 필터링
- 데이터 시각화를 위한 실시간 차트 및 그래프 구현
- 알람 시스템과 이벤트 기반 아키텍처 설계

## ⏰ 예상 소요 시간
- **이론 강의**: 45분 (멀티스레딩, 통신 프로토콜, 성능 최적화)
- **기초 실습**: 45분 (비동기 데이터 수집 및 Timer 활용)
- **심화 실습**: 45분 (실시간 통신 및 데이터 시각화)
- **Hands-on**: 45분 (종합 모니터링 시스템 확장)
- **총합**: 180분

## 👥 대상 청중
- **수준**: 중급-고급 (C# 비동기 프로그래밍 기초 지식 필요)
- **사전 지식**: MVVM 패턴, 데이터 바인딩, 기본적인 네트워킹 개념
- **도구 경험**: Visual Studio 디버깅, 네트워크 도구 사용 경험 권장

## 💻 실습 환경
- **운영체제**: Windows 10/11 (64bit)
- **필수 소프트웨어**:
  - Visual Studio 2022 Community
  - .NET 6.0 SDK
  - Wireshark (네트워크 분석용)
- **선택 소프트웨어**:
  - Postman (API 테스트)
  - Performance Profiler (성능 분석)

## 📖 사전 준비
- [ ] 2주차 MVVM 패턴 복습 및 프로젝트 준비
- [ ] [Task-based Asynchronous Pattern (TAP)](https://docs.microsoft.com/en-us/dotnet/standard/asynchronous-programming-patterns/task-based-asynchronous-pattern-tap) 문서 숙지
- [ ] 기본적인 네트워크 개념 (TCP/IP, 포트, 소켓) 복습
- [ ] 멀티스레딩 기초 개념 학습

## 🔗 참고 자료
- [Asynchronous Programming with async and await](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/async/)
- [SignalR for .NET](https://docs.microsoft.com/en-us/aspnet/core/signalr/introduction)
- [System.Threading.Tasks Namespace](https://docs.microsoft.com/en-us/dotnet/api/system.threading.tasks)
- [Performance Best Practices](https://docs.microsoft.com/en-us/dotnet/framework/performance/performance-tips)

## 📋 체크리스트
- [ ] Task와 async/await 패턴 이해
- [ ] 스레드 안전성 고려사항 파악
- [ ] 실시간 데이터 수집 메커니즘 구현
- [ ] 통신 프로토콜 선택 및 적용
- [ ] 성능 모니터링 및 최적화 방법 습득