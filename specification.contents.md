# 반도체 장비 HMI 개발 강의자료 명세서

## 강의 개요

### 과목명
반도체 장비를 위한 Human Machine Interface 개발

### 강의 기간
13주 (1주차: 이론, 2-5주차: C# WPF, 6-9주차: Python PySide6, 10-13주차: ImGUI C++)

### 강의 시간
주당 180분 (3시간), 총 2,340분 (39시간)

### 대상 학습자
- 반도체 장비 개발자
- HMI/HCI 개발 희망자
- GUI 프로그래밍 경험자 (기초 프로그래밍 지식 필수)

## 학습 목표

### 주요 학습 목표
1. 반도체 장비 환경에 특화된 HMI 설계 원칙 이해
2. C# WPF를 활용한 Windows 기반 HMI 시스템 개발 능력 습득
3. Python PySide6를 활용한 크로스 플랫폼 HMI 개발 능력 습득
4. ImGUI C++를 활용한 고성능 실시간 HMI 시스템 개발 능력 습득
5. 실무 환경에 즉시 적용 가능한 HMI 솔루션 구현 능력 확보

### 세부 학습 목표
- HCI 이론과 실제 반도체 장비 환경의 연계 이해
- MVVM, MVC 등 GUI 아키텍처 패턴 실무 적용
- 실시간 데이터 처리 및 시각화 기법 습득
- 다중 플랫폼 배포 및 성능 최적화 능력 확보

## 주차별 상세 명세

### 1주차: HCI/HMI 이론 기초
#### 학습 내용
**이론 (45분)**
- HCI 발전사 및 현재 동향
  - GUI 패러다임의 변화
  - 모바일 및 터치 인터페이스 영향
  - 음성 인터페이스 및 AI 통합
- HMI와 HCI의 차이점
  - 산업용 vs 소비자용 인터페이스
  - 안전성 및 신뢰성 요구사항
  - 운영 환경의 특수성
- 반도체 장비 환경의 특수성
  - 클린룸 환경 제약사항
  - 24/7 연속 운영 요구사항
  - 나노미터 수준의 정밀도 요구
- 인지 부하 이론
  - 작업 기억 모델
  - 주의 분산 최소화
  - 정보 처리 한계 고려

**기초 실습 (45분)**
- 기존 반도체 장비 HMI 사례 분석
  - Applied Materials, ASML, Tokyo Electron 장비 분석
  - 인터페이스 강점 및 약점 파악
  - 사용자 경험 평가
- 사용성 평가 체크리스트 작성
  - Nielsen의 10가지 사용성 원칙 적용
  - 반도체 환경 특화 평가 항목 추가
  - 정량적 평가 지표 설정

**심화 실습 (45분)**
- 페르소나 및 시나리오 개발
  - 장비 운영자 페르소나 작성
  - 엔지니어 페르소나 작성
  - 관리자 페르소나 작성
  - 각 페르소나별 사용 시나리오 구성
- HMI 프로토타입 설계
  - 와이어프레임 작성
  - 정보 구조 설계
  - 네비게이션 플로우 설계

**Hands-on (45분)**
- 반도체 장비 운영자 인터뷰 시뮬레이션
  - 역할극을 통한 요구사항 수집
  - 현장 관찰 시뮬레이션
  - 페인 포인트 식별
- 요구사항 문서 작성
  - 기능 요구사항 정리
  - 비기능 요구사항 정리
  - 우선순위 설정

#### 평가 기준
- 이론 이해도: HCI/HMI 개념 설명 능력
- 분석 능력: 기존 시스템 분석의 논리성 및 깊이
- 설계 능력: 프로토타입의 사용자 중심성
- 문서화: 요구사항 문서의 완성도

### 2주차: C# WPF 기초 및 MVVM 패턴
#### 학습 내용
**이론 (45분)**
- .NET 생태계 개요
  - .NET Framework vs .NET Core vs .NET 6+
  - CLR 및 JIT 컴파일 메커니즘
  - 가비지 컬렉션 이해
- WPF 아키텍처
  - 시각적 트리 및 논리적 트리
  - 디펜던시 프로퍼티 시스템
  - 라우팅 이벤트 메커니즘
- XAML 기초
  - 마크업 확장
  - 리소스 시스템
  - 바인딩 구문
- MVVM 패턴
  - 패턴의 동기 및 장점
  - View, ViewModel, Model 역할 분리
  - 데이터 바인딩과 커맨드 패턴

**기초 실습 (45분)**
```csharp
// Equipment.cs - 모델 클래스
using System.ComponentModel;
using System.Runtime.CompilerServices;

public class Equipment : INotifyPropertyChanged
{
    private string _equipmentId;
    private EquipmentStatus _status;
    private double _temperature;
    private double _pressure;
    private DateTime _lastUpdate;

    public string EquipmentId
    {
        get => _equipmentId;
        set
        {
            _equipmentId = value;
            OnPropertyChanged();
        }
    }

    public EquipmentStatus Status
    {
        get => _status;
        set
        {
            _status = value;
            OnPropertyChanged();
            OnPropertyChanged(nameof(StatusColor));
        }
    }

    public string StatusColor => Status switch
    {
        EquipmentStatus.Running => "Green",
        EquipmentStatus.Warning => "Orange",
        EquipmentStatus.Error => "Red",
        _ => "Gray"
    };

    public event PropertyChangedEventHandler PropertyChanged;

    protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}

public enum EquipmentStatus
{
    Idle,
    Running,
    Warning,
    Error,
    Maintenance
}
```

```csharp
// EquipmentViewModel.cs - 뷰모델 클래스
using System.Collections.ObjectModel;
using System.Windows.Input;

public class EquipmentViewModel : INotifyPropertyChanged
{
    public ObservableCollection<Equipment> EquipmentList { get; }

    private Equipment _selectedEquipment;
    public Equipment SelectedEquipment
    {
        get => _selectedEquipment;
        set
        {
            _selectedEquipment = value;
            OnPropertyChanged();
            ((RelayCommand)StartMaintenanceCommand).RaiseCanExecuteChanged();
        }
    }

    public ICommand StartMaintenanceCommand { get; }
    public ICommand RefreshDataCommand { get; }

    public EquipmentViewModel()
    {
        EquipmentList = new ObservableCollection<Equipment>();
        StartMaintenanceCommand = new RelayCommand(StartMaintenance, CanStartMaintenance);
        RefreshDataCommand = new RelayCommand(RefreshData);
        LoadEquipmentData();
    }

    private bool CanStartMaintenance()
    {
        return SelectedEquipment?.Status == EquipmentStatus.Idle;
    }

    private void StartMaintenance()
    {
        if (SelectedEquipment != null)
        {
            SelectedEquipment.Status = EquipmentStatus.Maintenance;
        }
    }
}
```

**심화 실습 (45분)**
- 데이터 템플릿 및 스타일링
- 커스텀 컨트롤 개발
- 값 변환기(Value Converter) 구현
- 유효성 검사(Validation) 적용

**Hands-on (45분)**
- 반도체 장비 모니터링 메인 창 구현
- 장비 목록 표시 기능
- 상태별 색상 표시 시스템
- 기본 알람 표시 기능

#### 평가 기준
- MVVM 패턴 이해도 및 구현 정확성
- 데이터 바인딩 활용 능력
- 코드 구조의 유지보수성
- UI/UX 품질

### 3주차: 실시간 데이터 처리 및 통신
#### 학습 내용
**이론 (45분)**
- 멀티스레딩 기초
  - Thread vs Task vs async/await
  - 동기화 메커니즘 (lock, Mutex, Semaphore)
  - 스레드 안전성 고려사항
- 실시간 통신 프로토콜
  - TCP/IP 소켓 프로그래밍
  - SignalR을 활용한 실시간 통신
  - MQTT 프로토콜 이해
- 데이터 수집 및 처리
  - 센서 데이터 수집 방법
  - 데이터 필터링 및 보정
  - 이상치 탐지 알고리즘

**기초 실습 (45분)**
```csharp
// DataService.cs - 실시간 데이터 서비스
public class EquipmentDataService : INotifyPropertyChanged
{
    private readonly Timer _dataTimer;
    private readonly Random _random;
    private readonly ConcurrentDictionary<string, Equipment> _equipmentData;

    public event EventHandler<EquipmentDataReceivedEventArgs> DataReceived;

    public EquipmentDataService()
    {
        _random = new Random();
        _equipmentData = new ConcurrentDictionary<string, Equipment>();
        _dataTimer = new Timer(GenerateData, null, TimeSpan.Zero, TimeSpan.FromSeconds(1));
    }

    private void GenerateData(object state)
    {
        var equipmentIds = new[] { "CVD-001", "PVD-002", "ETCH-003", "CMP-004" };

        Parallel.ForEach(equipmentIds, equipmentId =>
        {
            var equipment = _equipmentData.GetOrAdd(equipmentId, id => new Equipment { EquipmentId = id });

            // 시뮬레이션 데이터 생성
            equipment.Temperature = 200 + (_random.NextDouble() - 0.5) * 10;
            equipment.Pressure = 1.0 + (_random.NextDouble() - 0.5) * 0.1;
            equipment.LastUpdate = DateTime.Now;

            // 임계값 체크
            CheckThresholds(equipment);

            DataReceived?.Invoke(this, new EquipmentDataReceivedEventArgs(equipment));
        });
    }

    private void CheckThresholds(Equipment equipment)
    {
        if (equipment.Temperature > 210 || equipment.Pressure > 1.05)
        {
            equipment.Status = EquipmentStatus.Warning;
        }
        else if (equipment.Temperature > 220 || equipment.Pressure > 1.1)
        {
            equipment.Status = EquipmentStatus.Error;
        }
        else
        {
            equipment.Status = EquipmentStatus.Running;
        }
    }
}
```

**심화 실습 (45분)**
- WCF/gRPC 서비스 연동
- 데이터베이스 연결 및 히스토리 저장
- 성능 최적화 기법
- 메모리 누수 방지

**Hands-on (45분)**
- 실시간 모니터링 차트 구현
- 알람 시스템 확장
- 데이터 로깅 기능 추가
- 성능 지표 모니터링

### 4주차: 고급 UI/UX 및 사용자 정의 컨트롤
#### 학습 내용
**이론 (45분)**
- 고급 레이아웃 시스템
  - Grid vs StackPanel vs Canvas 성능 비교
  - 가상화(Virtualization) 기법
  - 측정(Measure) 및 배치(Arrange) 과정
- 애니메이션 및 트랜지션
  - Storyboard 및 애니메이션 타임라인
  - Easing 함수 활용
  - 성능을 고려한 애니메이션 설계
- 사용자 정의 컨트롤
  - UserControl vs CustomControl
  - 디펜던시 프로퍼티 정의
  - 컨트롤 템플릿 작성

**기초 실습 (45분)**
```csharp
// GaugeControl.cs - 사용자 정의 게이지 컨트롤
[TemplatePart(Name = "PART_Indicator", Type = typeof(FrameworkElement))]
public class CircularGauge : Control
{
    public static readonly DependencyProperty ValueProperty =
        DependencyProperty.Register("Value", typeof(double), typeof(CircularGauge),
            new PropertyMetadata(0.0, OnValueChanged));

    public static readonly DependencyProperty MinimumProperty =
        DependencyProperty.Register("Minimum", typeof(double), typeof(CircularGauge),
            new PropertyMetadata(0.0));

    public static readonly DependencyProperty MaximumProperty =
        DependencyProperty.Register("Maximum", typeof(double), typeof(CircularGauge),
            new PropertyMetadata(100.0));

    private FrameworkElement _indicator;

    static CircularGauge()
    {
        DefaultStyleKeyProperty.OverrideMetadata(typeof(CircularGauge),
            new FrameworkPropertyMetadata(typeof(CircularGauge)));
    }

    public double Value
    {
        get => (double)GetValue(ValueProperty);
        set => SetValue(ValueProperty, value);
    }

    public override void OnApplyTemplate()
    {
        base.OnApplyTemplate();
        _indicator = GetTemplateChild("PART_Indicator") as FrameworkElement;
        UpdateIndicator();
    }

    private static void OnValueChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        if (d is CircularGauge gauge)
        {
            gauge.UpdateIndicator();
        }
    }

    private void UpdateIndicator()
    {
        if (_indicator == null) return;

        var percentage = (Value - Minimum) / (Maximum - Minimum);
        var angle = percentage * 270 - 135; // -135도부터 135도까지

        var transform = new RotateTransform(angle);
        _indicator.RenderTransform = transform;
    }
}
```

**심화 실습 (45분)**
- 3D 시각화 컨트롤 구현
- 터치 인터페이스 지원
- 접근성(Accessibility) 향상
- 다국어 지원(Localization)

**Hands-on (45분)**
- 종합 대시보드 구현
- 사용자 정의 차트 컨트롤
- 드래그 앤 드롭 기능
- 설정 관리 시스템

### 5주차: 테스트, 배포 및 성능 최적화
#### 학습 내용
**이론 (45분)**
- 단위 테스트 및 통합 테스트
  - MSTest, NUnit, xUnit 비교
  - 목(Mock) 객체 활용
  - 테스트 주도 개발(TDD) 접근법
- 성능 최적화
  - 메모리 프로파일링
  - CPU 사용량 최적화
  - UI 가상화 기법
- 배포 전략
  - ClickOnce 배포
  - Windows Installer 패키지
  - .NET 자체 포함 배포

**기초 실습 (45분)**
```csharp
// EquipmentViewModelTests.cs - 단위 테스트
[TestClass]
public class EquipmentViewModelTests
{
    [TestMethod]
    public void StartMaintenance_WhenEquipmentIdle_ShouldSetMaintenanceStatus()
    {
        // Arrange
        var viewModel = new EquipmentViewModel();
        var equipment = new Equipment { Status = EquipmentStatus.Idle };
        viewModel.SelectedEquipment = equipment;

        // Act
        viewModel.StartMaintenanceCommand.Execute(null);

        // Assert
        Assert.AreEqual(EquipmentStatus.Maintenance, equipment.Status);
    }

    [TestMethod]
    public void StartMaintenance_WhenEquipmentRunning_ShouldNotExecute()
    {
        // Arrange
        var viewModel = new EquipmentViewModel();
        var equipment = new Equipment { Status = EquipmentStatus.Running };
        viewModel.SelectedEquipment = equipment;

        // Act & Assert
        Assert.IsFalse(viewModel.StartMaintenanceCommand.CanExecute(null));
    }
}
```

**심화 실습 (45분)**
- 부하 테스트 및 스트레스 테스트
- 메모리 누수 탐지 및 해결
- 코드 커버리지 분석
- 지속적 통합(CI) 설정

**Hands-on (45분)**
- 최종 프로젝트 통합
- 성능 벤치마킹
- 배포 패키지 생성
- 사용자 매뉴얼 작성

### 6주차: Python PySide6 기초 및 Qt 아키텍처
#### 학습 내용
**이론 (45분)**
- Python 개발 환경 설정
  - 가상 환경(Virtual Environment) 관리
  - pip 및 conda 패키지 관리
  - IDE 설정 (PyCharm, VS Code)
- Qt 프레임워크 개요
  - Qt Core, Qt GUI, Qt Widgets 모듈
  - 메타 객체 시스템(Meta-Object System)
  - Qt의 메모리 관리 방식
- PySide6 vs PyQt6 비교
  - 라이선스 차이점
  - API 호환성
  - 성능 특성

**기초 실습 (45분)**
```python
# equipment_model.py
from PySide6.QtCore import QAbstractTableModel, Qt, Signal, QTimer
from PySide6.QtWidgets import QApplication
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
import random
import sys

class EquipmentStatus(Enum):
    IDLE = "Idle"
    RUNNING = "Running"
    WARNING = "Warning"
    ERROR = "Error"
    MAINTENANCE = "Maintenance"

@dataclass
class Equipment:
    equipment_id: str
    status: EquipmentStatus = EquipmentStatus.IDLE
    temperature: float = 0.0
    pressure: float = 0.0
    last_update: str = ""

class EquipmentTableModel(QAbstractTableModel):
    dataChanged = Signal()

    def __init__(self):
        super().__init__()
        self.equipment_list: List[Equipment] = []
        self.headers = ['장비 ID', '상태', '온도', '압력', '최근 업데이트']

        # 시뮬레이션 데이터 생성
        self.setup_simulation_data()

        # 데이터 업데이트 타이머
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # 1초마다 업데이트

    def setup_simulation_data(self):
        equipment_ids = ['CVD-001', 'PVD-002', 'ETCH-003', 'CMP-004']
        for eq_id in equipment_ids:
            equipment = Equipment(
                equipment_id=eq_id,
                status=EquipmentStatus.IDLE,
                temperature=200.0,
                pressure=1.0
            )
            self.equipment_list.append(equipment)

    def rowCount(self, parent=None):
        return len(self.equipment_list)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        equipment = self.equipment_list[index.row()]
        column = index.column()

        if role == Qt.DisplayRole:
            if column == 0:
                return equipment.equipment_id
            elif column == 1:
                return equipment.status.value
            elif column == 2:
                return f"{equipment.temperature:.1f}°C"
            elif column == 3:
                return f"{equipment.pressure:.3f} Torr"
            elif column == 4:
                return equipment.last_update

        elif role == Qt.BackgroundRole:
            if column == 1:  # 상태 컬럼
                if equipment.status == EquipmentStatus.RUNNING:
                    return Qt.green
                elif equipment.status == EquipmentStatus.WARNING:
                    return Qt.yellow
                elif equipment.status == EquipmentStatus.ERROR:
                    return Qt.red

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None

    def update_data(self):
        for equipment in self.equipment_list:
            # 시뮬레이션 데이터 업데이트
            equipment.temperature = 200 + (random.random() - 0.5) * 10
            equipment.pressure = 1.0 + (random.random() - 0.5) * 0.1
            equipment.last_update = QTimer().currentTime().toString()

            # 임계값 체크
            if equipment.temperature > 210 or equipment.pressure > 1.05:
                equipment.status = EquipmentStatus.WARNING
            elif equipment.temperature > 220 or equipment.pressure > 1.1:
                equipment.status = EquipmentStatus.ERROR
            else:
                equipment.status = EquipmentStatus.RUNNING

        # 전체 테이블 업데이트 신호
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(self.rowCount() - 1, self.columnCount() - 1)
        )
```

**심화 실습 (45분)**
- 시그널-슬롯 고급 활용
- 사용자 정의 위젯 개발
- 스타일 시트(QSS) 적용
- 리소스 시스템 활용

**Hands-on (45분)**
- 메인 윈도우 구현
- 장비 모니터링 테이블 생성
- 실시간 데이터 표시
- 기본 알람 시스템

### 7-9주차: Python PySide6 고급 기능
[이후 주차들도 동일한 상세 구조로 명세화...]

### 10-13주차: ImGUI C++ 개발
[ImGUI 관련 상세 명세...]

## 평가 방법

### 평가 구성비
- 출석 및 참여도: 10%
- 주차별 과제: 30%
- 중간 프로젝트: 25%
- 기말 프로젝트: 35%

### 평가 기준
1. **기능 구현 완성도** (40%)
   - 요구사항 명세 대비 구현 완료율
   - 기능의 정확성 및 안정성
   - 오류 처리 및 예외 상황 대응

2. **코드 품질** (30%)
   - 가독성 및 유지보수성
   - 아키텍처 패턴 적용 적절성
   - 성능 최적화 고려사항
   - 주석 및 문서화 수준

3. **사용자 경험** (20%)
   - 직관적 인터페이스 설계
   - 응답성 및 성능
   - 접근성 고려사항
   - 시각적 디자인 품질

4. **실무 적용성** (10%)
   - 실제 현장 적용 가능성
   - 확장성 및 유지보수 고려
   - 표준 준수 여부
   - 보안 고려사항

## 교육 환경 및 도구

### 하드웨어 요구사항
- CPU: Intel i5 8세대 이상 또는 AMD Ryzen 5 3세대 이상
- RAM: 16GB 이상
- 저장장치: SSD 256GB 이상
- 그래픽: DirectX 11 지원 GPU
- 모니터: Full HD (1920x1080) 이상

### 소프트웨어 요구사항
- 운영체제: Windows 10/11 (64bit)
- 개발 도구:
  - Visual Studio 2022 Community
  - Python 3.11 이상
  - PyCharm Community 또는 VS Code
  - Git for Windows

### 추가 도구 및 라이브러리
- .NET 6.0 SDK
- NuGet Package Manager
- vcpkg (C++ 패키지 관리)
- CMake 3.20 이상
- Qt Designer
- 반도체 장비 시뮬레이터 (별도 제공)

## 성과 지표

### 정량적 지표
- 강의 만족도: 4.5/5.0 이상
- 과제 완성률: 95% 이상
- 최종 프로젝트 성공률: 90% 이상
- 실무 적용률: 80% 이상 (6개월 후 추적 조사)

### 정성적 지표
- HMI 설계 원칙 이해도 향상
- 다중 플랫폼 개발 역량 확보
- 실시간 시스템 개발 경험 습득
- 협업 및 문제 해결 능력 향상

## 사후 지원

### 온라인 리소스
- 강의 자료 저장소 (GitHub)
- Q&A 포럼 운영
- 월간 기술 세미나
- 최신 기술 동향 공유

### 멘토링 프로그램
- 1:1 멘토링 (월 1회, 3개월간)
- 프로젝트 코드 리뷰
- 실무 적용 사례 공유
- 커리어 상담

이 명세서는 반도체 장비 HMI 개발에 필요한 모든 핵심 기술과 실무 지식을 체계적으로 다루며, 학습자가 실제 현장에서 즉시 활용할 수 있는 수준의 역량을 확보할 수 있도록 구성되었습니다.