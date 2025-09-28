# Python PySide6 실시간 데이터 처리 및 멀티스레딩

## 🎯 학습 목표
- PySide6에서 QThread를 활용한 효율적인 멀티스레딩 구현 및 UI 블록킹 방지
- 실시간 데이터 수집, 처리, 시각화를 위한 고성능 아키텍처 설계
- 시리얼 통신 및 네트워크 프로토콜을 통한 반도체 장비 데이터 통신 구현
- SQLite 데이터베이스를 활용한 대용량 데이터 저장 및 이력 관리 시스템

## 📚 주요 내용
- QThread 기반 멀티스레딩 아키텍처 설계 및 구현
- Worker 패턴을 활용한 백그라운드 데이터 처리
- QTimer 고급 활용 및 정밀한 타이밍 제어
- 시리얼 통신 (QSerialPort) 및 네트워크 통신 (QTcpSocket)
- SQLite 데이터베이스 연동 및 ORM 패턴 구현
- 실시간 차트 및 대시보드 구현 (PyQtGraph)
- 성능 모니터링 및 메모리 최적화 기법

## ⏰ 예상 소요 시간
- **이론 강의**: 45분 (멀티스레딩 개념, 실시간 처리 아키텍처)
- **기초 실습**: 45분 (QThread 구현 및 데이터 수집)
- **심화 실습**: 45분 (데이터베이스 연동 및 통신 구현)
- **Hands-on**: 45분 (실시간 장비 모니터링 시스템 완성)
- **총합**: 180분

## 👥 대상 청중
- **수준**: 중급+ (Python PySide6 기초 필수, 6주차 과정 완료)
- **사전 지식**: 스레딩 개념, 데이터베이스 기초, 네트워크 통신 이해
- **도구 경험**: Python 중급 수준, SQLite 사용 경험 권장

## 💻 실습 환경
- **운영체제**: Windows/Linux/macOS (크로스 플랫폼)
- **필수 소프트웨어**:
  - Python 3.9+ 및 PySide6
  - SQLite3 (Python 내장)
  - PyQtGraph (실시간 차트)
  - pyserial (시리얼 통신)
- **선택 소프트웨어**:
  - Qt Designer
  - SQLite Browser (DB 관리)

## 📖 사전 준비
- [ ] 6주차 Python PySide6 기초 과정 완료
- [ ] [Qt Threading Documentation](https://doc.qt.io/qtforpython/overviews/thread-basics.html) 숙지
- [ ] Python 멀티스레딩 개념 복습
- [ ] SQLite 기본 SQL 문법 학습

## 🔗 참고 자료
- [PySide6 Threading Guide](https://doc.qt.io/qtforpython/overviews/thread-basics.html)
- [PyQtGraph Documentation](https://pyqtgraph.readthedocs.io/)
- [Python SQLite Tutorial](https://docs.python.org/3/library/sqlite3.html)
- [QSerialPort Documentation](https://doc.qt.io/qtforpython/PySide6/QtSerialPort/QSerialPort.html)

## 📋 체크리스트
- [ ] QThread 기반 멀티스레딩 구현 및 UI 응답성 확보
- [ ] 실시간 데이터 수집 및 처리 파이프라인 구축
- [ ] 시리얼/네트워크 통신을 통한 장비 연동
- [ ] SQLite 기반 데이터 저장 및 이력 관리 시스템
- [ ] 고성능 실시간 차트 및 모니터링 대시보드 완성