# 반도체 장비 HMI 개발 강의 실행 지침서

## 강의 진행 원칙

### 기본 원칙
- 이론과 실습의 균형적 구성 (이론 30%, 실습 70%)
- 단계별 점진적 난이도 증가
- 실무 적용 가능한 코드 품질 유지
- 반도체 장비 개발 맥락 일관성 유지

### 강의 구조
각 주차별 180분 구성:
- 이론 강의: 45분
- 기초 실습: 45분
- 심화 실습: 45분
- Hands-on 프로젝트: 45분

## 주차별 상세 지침

### 1주차: HCI/HMI 이론 기초
#### 강의 목표
- HCI와 HMI의 개념적 차이점 이해
- 반도체 장비 환경에서의 HMI 특수성 파악
- 사용자 중심 설계 원칙 습득

#### 진행 방식
1. **이론 (45분)**
   - HCI 발전 역사 및 현재 동향
   - 반도체 FAB 환경의 인간공학적 고려사항
   - 인지 부하 이론과 인터페이스 설계

2. **기초 실습 (45분)**
   - 기존 반도체 장비 HMI 사례 분석
   - 사용성 평가 체크리스트 작성
   - 페르소나 및 시나리오 작성 실습

3. **심화 실습 (45분)**
   - HMI 프로토타입 설계
   - 사용자 테스트 계획 수립
   - 접근성 가이드라인 적용

4. **Hands-on (45분)**
   - 반도체 장비 운영자 인터뷰 시뮬레이션
   - 요구사항 도출 및 정리
   - 초기 와이어프레임 스케치

### 2-5주차: C# WPF 강의 지침
#### 2주차: WPF 기초 및 MVVM 패턴
**이론 (45분)**
- .NET Framework/Core 아키텍처
- XAML 구조 및 바인딩 메커니즘
- MVVM 패턴의 개념과 장점

**기초 실습 (45분)**
```csharp
// Equipment 모델 클래스
public class Equipment : INotifyPropertyChanged
{
    private string status;
    private double temperature;

    public string Status
    {
        get => status;
        set
        {
            status = value;
            OnPropertyChanged();
        }
    }

    public double Temperature
    {
        get => temperature;
        set
        {
            temperature = value;
            OnPropertyChanged();
        }
    }
}
```

**심화 실습 (45분)**
- 커스텀 컨트롤 개발
- 데이터 템플릿 및 스타일링
- 의존성 주입 패턴 적용

**Hands-on (45분)**
- 반도체 장비 상태 모니터링 창 구현
- 실시간 데이터 바인딩 적용
- 기본 알람 시스템 구현

#### 3주차: 실시간 데이터 처리
**진행 방식**
- SignalR을 활용한 실시간 통신
- 멀티스레딩 및 동기화
- 성능 최적화 기법

#### 4주차: 고급 UI/UX 구현
**진행 방식**
- 사용자 정의 컨트롤 개발
- 애니메이션 및 트랜지션
- 접근성 향상 기법

#### 5주차: 통합 및 배포
**진행 방식**
- 장비 시뮬레이터 연동
- 단위 테스트 및 통합 테스트
- 배포 패키지 생성

### 6-9주차: Python PySide6 강의 지침
#### 6주차: PySide6 기초 및 Qt 아키텍처
**이론 (45분)**
- Qt 프레임워크 개요
- 시그널-슬롯 메커니즘
- MVC 패턴과 Qt의 Model-View 구조

**기초 실습 (45분)**
```python
# equipment_model.py
from PySide6.QtCore import QAbstractTableModel, Qt, Signal
from PySide6.QtWidgets import QApplication
import sys

class EquipmentModel(QAbstractTableModel):
    dataChanged = Signal()

    def __init__(self):
        super().__init__()
        self.equipment_data = []

    def rowCount(self, parent=None):
        return len(self.equipment_data)

    def columnCount(self, parent=None):
        return 4  # ID, Status, Temperature, Pressure

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            equipment = self.equipment_data[index.row()]
            return equipment[index.column()]
```

#### 7주차: 크로스 플랫폼 개발
**진행 방식**
- 플랫폼별 빌드 설정
- 리소스 관리 및 국제화
- 성능 프로파일링

#### 8주차: 데이터 시각화
**진행 방식**
- matplotlib 및 pyqtgraph 연동
- 실시간 차트 구현
- 대용량 데이터 처리

#### 9주차: 시스템 통합
**진행 방식**
- REST API 연동
- 데이터베이스 연결
- 로깅 및 모니터링

### 10-13주차: ImGUI C++ 강의 지침
#### 10주차: ImGUI 기초 및 즉시 모드 개념
**이론 (45분)**
- 즉시 모드 vs 유지 모드 GUI
- ImGUI 아키텍처 및 렌더링 파이프라인
- 메모리 관리 및 성능 고려사항

**기초 실습 (45분)**
```cpp
// equipment_monitor.h
#pragma once
#include "imgui.h"
#include <vector>
#include <string>

class EquipmentMonitor {
private:
    struct Equipment {
        std::string id;
        std::string status;
        float temperature;
        float pressure;
        bool is_alarm;
    };

    std::vector<Equipment> equipment_list;

public:
    void render();
    void update_data();
    void show_equipment_table();
    void show_status_chart();
};
```

#### 11주차: 고성능 렌더링
**진행 방식**
- OpenGL/DirectX 연동
- 멀티 스레드 렌더링
- GPU 가속 활용

#### 12주차: 실시간 시스템 최적화
**진행 방식**
- 메모리 풀링
- 프레임 레이트 최적화
- 지연 시간 최소화

#### 13주차: 완성 및 배포
**진행 방식**
- 최종 시스템 통합
- 성능 벤치마킹
- 배포 및 설치 가이드

## 실습 환경 구성

### 공통 요구사항
- 개발용 PC: Windows 10/11, 16GB RAM, SSD
- 네트워크: 실습용 로컬 네트워크 환경
- 시뮬레이터: 반도체 장비 시뮬레이터 소프트웨어

### C# WPF 환경
- Visual Studio 2022 Community
- .NET 6.0 SDK
- NuGet 패키지 관리

### Python PySide6 환경
- Python 3.11 이상
- PyCharm Community 또는 VS Code
- pip 패키지 관리

### ImGUI C++ 환경
- Visual Studio 2022 또는 CLion
- vcpkg 패키지 관리
- CMake 빌드 시스템

## 평가 방법

### 평가 구성
- 이론 이해도: 20%
- 기초 실습: 25%
- 심화 실습: 25%
- Hands-on 프로젝트: 30%

### 평가 기준
1. **코드 품질**: 가독성, 유지보수성, 성능
2. **요구사항 충족**: 명세서 대비 구현 완성도
3. **창의성**: 독창적 해결책 및 개선 아이디어
4. **실무 적용성**: 실제 현장 적용 가능성

## 강사 준비사항

### 사전 준비
- 반도체 장비 운영 경험 또는 관련 지식
- 각 기술 스택에 대한 깊이 있는 이해
- 실습용 코드 및 프로젝트 템플릿 준비

### 강의 중 주의사항
- 학습자 수준별 개별 지도
- 실습 시간 엄수 및 진도 관리
- 질의응답 시간 충분히 확보
- 실무 경험 사례 적극 공유

### 사후 관리
- 실습 코드 저장소 관리
- 학습자 피드백 수집 및 반영
- 최신 기술 동향 반영한 내용 업데이트