# Week 2: C# WPF 아키텍처와 MVVM 패턴

## 학습 목표
- .NET 플랫폼 아키텍처와 CLR 메모리 관리 시스템 분석
- WPF 렌더링 엔진과 디펜던시 프로퍼티 시스템 심화 이해
- MVVM 패턴의 이론적 기반과 소프트웨어 아키텍처 원칙
- 실시간 HMI 시스템 성능 요구사항과 구현 방법론

---

# 📖 이론 강의 (45분)

---

## .NET 발전 역사

### 🔧 .NET 플랫폼 진화
- **.NET Framework (2002)**: Windows 전용, 완전한 기능셋
- **.NET Core (2016)**: 크로스 플랫폼, 고성능, 오픈소스
- **.NET 5+ (2020)**: 통합된 플랫폼, 단일 런타임
- **.NET 6 LTS (2021)**: 장기 지원, 성능 최적화

### 반도체 환경에서의 .NET 장점
> ⚠️ 24/7 연속 운영 환경에서 메모리 누수 방지와 안정성이 핵심입니다.

---

## CLR (Common Language Runtime)

### ⚙️ CLR 핵심 기능
- **JIT 컴파일**: 런타임 시 네이티브 코드로 변환
- **가비지 컬렉션**: 자동 메모리 관리
- **타입 안전성**: 메모리 보호 및 오류 방지
- **예외 처리**: 구조화된 오류 관리

### 산업용 HMI에서의 중요성
- **메모리 안정성**: 장시간 운영 시 메모리 누수 방지
- **성능 최적화**: JIT 컴파일로 네이티브 수준 성능
- **안전한 실행**: 타입 체크로 런타임 오류 최소화

---

## WPF 계층 구조

### 🏗️ WPF 아키텍처 스택

```
┌─────────────────────────────────────┐
│        Application Layer           │  ← 사용자 애플리케이션
├─────────────────────────────────────┤
│         Framework Layer             │  ← WPF 프레임워크
│  (Controls, Data Binding, Layout)   │
├─────────────────────────────────────┤
│           Core Layer                │  ← 핵심 시스템
│    (Visual System, Animation)       │
├─────────────────────────────────────┤
│         Base Layer                  │  ← 기본 서비스
│   (Threading, Input, Resources)     │
└─────────────────────────────────────┘
```

---

## 시각적 트리와 논리적 트리

### 🌳 두 가지 트리 구조
- **논리적 트리**: XAML에 정의된 요소들의 계층 구조
- **시각적 트리**: 실제 렌더링되는 모든 시각적 요소
- **성능 고려**: 시각적 트리 깊이가 렌더링 성능에 직접 영향

### 산업용 HMI 최적화 팁
- 복잡한 UserControl 중첩 최소화
- 불필요한 Container 제거
- 가상화(Virtualization) 활용

---

## WPF 렌더링 시스템

### 🎨 렌더링 특징
- **DirectX 기반**: 하드웨어 가속 렌더링
- **벡터 그래픽**: 해상도 독립적 UI
- **컴포지션**: 레이어 기반 렌더링
- **애니메이션**: GPU 가속 부드러운 전환

### 반도체 HMI 적용 이점
- **고해상도 지원**: 4K, 8K 모니터 대응
- **부드러운 UI**: 60fps 실시간 업데이트
- **확장성**: 멀티 모니터 환경 지원

---

## 디펜던시 프로퍼티 시스템

<div style="margin: 2rem 0;">

### 🔗 디펜던시 프로퍼티 개념

<div style="background: #f3e5f5; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #9c27b0; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #4a148c;">상속:</strong> 부모 요소에서 자식 요소로 값 전파</li>
        <li><strong style="color: #4a148c;">데이터 바인딩:</strong> 자동 값 동기화</li>
        <li><strong style="color: #4a148c;">애니메이션:</strong> 부드러운 값 변경</li>
        <li><strong style="color: #4a148c;">스타일링:</strong> 테마 및 스타일 적용</li>
    </ul>
</div>

### 💻 디펜던시 프로퍼티 구현 - Part 1

<div class="grid grid-cols-2 gap-8">
<div>

```csharp {1-25}
1  // 반도체 장비 상태를 나타내는 커스텀 컨트롤
2  public class EquipmentStatusControl : Control
3  {
4      // 디펜던시 프로퍼티 정의
5      public static readonly DependencyProperty StatusProperty =
6          DependencyProperty.Register(
7              "Status",
8              typeof(EquipmentStatus),
9              typeof(EquipmentStatusControl),
10             new PropertyMetadata(EquipmentStatus.Idle, OnStatusChanged));
11
12     // CLR 프로퍼티 래퍼
13     public EquipmentStatus Status
14     {
15         get { return (EquipmentStatus)GetValue(StatusProperty); }
16         set { SetValue(StatusProperty, value); }
17     }
18
19     // 프로퍼티 변경 콜백
20     private static void OnStatusChanged(DependencyObject d,
21         DependencyPropertyChangedEventArgs e)
22     {
23         var control = (EquipmentStatusControl)d;
24         control.UpdateVisualState((EquipmentStatus)e.NewValue);
25     }
```

</div>
<div>

**디펜던시 프로퍼티 기본 구조**
- **Line 1-2**: 반도체 장비 상태 표시용 커스텀 컨트롤 클래스
- **Line 5-10**: 디펜던시 프로퍼티 등록
  - **Line 7**: 프로퍼티 이름 "Status"
  - **Line 8**: 데이터 타입 EquipmentStatus enum
  - **Line 9**: 소유자 타입 지정
  - **Line 10**: 기본값과 변경 콜백 설정

- **Line 13-17**: CLR 프로퍼티 래퍼
  - **Line 15**: GetValue()로 디펜던시 프로퍼티 값 읽기
  - **Line 16**: SetValue()로 디펜던시 프로퍼티 값 설정

- **Line 20-25**: 프로퍼티 변경 콜백 메서드
  - 값 변경 시 자동으로 호출되어 UI 업데이트 수행

</div>
</div>

---

### 💻 디펜던시 프로퍼티 구현 - Part 2

<div class="grid grid-cols-2 gap-8">
<div>

```csharp {26-56}
26
27     private void UpdateVisualState(EquipmentStatus newStatus)
28     {
29         // 상태에 따른 시각적 업데이트
30         switch (newStatus)
31         {
32             case EquipmentStatus.Running:
33                 Background = Brushes.Green;
34                 break;
35             case EquipmentStatus.Warning:
36                 Background = Brushes.Orange;
37                 break;
38             case EquipmentStatus.Error:
39                 Background = Brushes.Red;
40                 break;
41             default:
42                 Background = Brushes.Gray;
43                 break;
44         }
45     }
46 }
47
48 public enum EquipmentStatus
49 {
50     Idle,      // 대기
51     Running,   // 운전 중
52     Warning,   // 경고
53     Error,     // 오류
54     Maintenance // 정비
55 }
56
```

</div>
<div>

**시각적 상태 업데이트 및 열거형 정의**
- **Line 27-45**: 상태 변경에 따른 시각적 업데이트 메서드
  - **Line 30**: switch문으로 상태별 분기 처리
  - **Line 32-33**: 운전 중 상태 - 녹색 배경
  - **Line 35-36**: 경고 상태 - 주황색 배경
  - **Line 38-39**: 오류 상태 - 빨간색 배경
  - **Line 41-42**: 기본 상태 - 회색 배경

- **Line 48-55**: 장비 상태 열거형 정의
  - **Line 50**: Idle - 대기 상태
  - **Line 51**: Running - 정상 운전 중
  - **Line 52**: Warning - 주의 필요 상태
  - **Line 53**: Error - 오류 발생 상태
  - **Line 54**: Maintenance - 정비 모드

**디펜던시 프로퍼티의 장점**: 데이터 바인딩, 애니메이션, 스타일링 자동 지원

</div>
</div>

</div>

---

## MVVM 패턴 이론

<div style="margin: 2rem 0;">

### 📐 MVVM 아키텍처

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #6c757d; margin: 1rem 0;">

```
┌─────────────┐    데이터 바인딩    ┌─────────────┐
│    View     │ ◄─────────────────► │ ViewModel   │
│   (XAML)    │      커맨드         │   (C#)      │
└─────────────┘                    └─────────────┘
                                           │
                                     비즈니스 로직
                                           │
                                           ▼
                                   ┌─────────────┐
                                   │    Model    │
                                   │  (데이터)    │
                                   └─────────────┘
```

</div>

### 🎯 각 계층의 역할

<div style="display: flex; flex-direction: column; gap: 1rem; margin: 1.5rem 0;">
    <div style="display: flex; align-items: center; background: #e8f5e8; padding: 1rem; border-radius: 8px;">
        <div style="background: #28a745; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">V</div>
        <span style="color: #155724;"><strong>View:</strong> XAML 기반 사용자 인터페이스, 사용자 입력 처리</span>
    </div>
    <div style="display: flex; align-items: center; background: #e3f2fd; padding: 1rem; border-radius: 8px;">
        <div style="background: #2196f3; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">VM</div>
        <span style="color: #0d47a1;"><strong>ViewModel:</strong> 프레젠테이션 로직, 데이터 변환, 커맨드 처리</span>
    </div>
    <div style="display: flex; align-items: center; background: #f3e5f5; padding: 1rem; border-radius: 8px;">
        <div style="background: #9c27b0; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">M</div>
        <span style="color: #4a148c;"><strong>Model:</strong> 비즈니스 로직, 데이터 액세스, 도메인 객체</span>
    </div>
</div>

### 💡 MVVM의 장점

<div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #f39c12; margin: 1.5rem 0;">
    <ul style="margin: 0; line-height: 1.8; color: #856404;">
        <li><strong>테스트 용이성:</strong> ViewModel 단위 테스트 가능</li>
        <li><strong>유지보수성:</strong> 관심사 분리로 코드 구조 명확</li>
        <li><strong>재사용성:</strong> ViewModel을 다른 View에서 재사용</li>
        <li><strong>디자이너 협업:</strong> XAML을 통한 UI/UX 협업</li>
    </ul>
</div>

</div>

---

## INotifyPropertyChanged 인터페이스

<div style="margin: 2rem 0;">

### 🔄 속성 변경 알림 메커니즘

<div style="background: #e8f5e8; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #155724;">자동 업데이트:</strong> 데이터 변경 시 UI 자동 갱신</li>
        <li><strong style="color: #155724;">성능 최적화:</strong> 변경된 속성만 선택적 업데이트</li>
        <li><strong style="color: #155724;">양방향 바인딩:</strong> UI ↔ 데이터 양방향 동기화</li>
    </ul>
</div>

### 💻 기본 ViewModel 구현 - Part 1

<div class="grid grid-cols-2 gap-8">
<div>

```csharp {1-25}
1  // 기본 ViewModel 베이스 클래스
2  public abstract class BaseViewModel : INotifyPropertyChanged
3  {
4      public event PropertyChangedEventHandler PropertyChanged;
5
6      // 속성 변경 알림
7      protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
8      {
9          PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
10     }
11
12     // 속성 값 설정 헬퍼 메서드
13     protected bool SetProperty<T>(ref T backingField, T value, [CallerMemberName] string propertyName = null)
14     {
15         if (EqualityComparer<T>.Default.Equals(backingField, value))
16             return false;
17
18         backingField = value;
19         OnPropertyChanged(propertyName);
20         return true;
21     }
22 }
23
24 // 반도체 장비 ViewModel 구현
25 public class EquipmentViewModel : BaseViewModel
```

</div>
<div>

**BaseViewModel 기본 구조**
- **Line 1-2**: INotifyPropertyChanged를 구현하는 추상 베이스 클래스
- **Line 4**: PropertyChanged 이벤트 선언
- **Line 7-10**: 속성 변경 알림 메서드
  - **[CallerMemberName]**: 호출한 속성 이름을 자동으로 가져옴
  - **Line 9**: null 조건부 연산자로 안전한 이벤트 호출

- **Line 13-21**: 제네릭 속성 설정 헬퍼 메서드
  - **Line 15-16**: 값이 동일하면 변경하지 않아 성능 최적화
  - **Line 18-20**: 백킹 필드 업데이트 후 알림 발생

- **Line 24-25**: 반도체 장비 전용 ViewModel 클래스 시작
  - BaseViewModel을 상속하여 기본 기능 확보

</div>
</div>

---

### 💻 기본 ViewModel 구현 - Part 2

<div class="grid grid-cols-2 gap-8">
<div>

```csharp {26-50}
26 {
27     private string _equipmentId;
28     private EquipmentStatus _status;
29     private double _temperature;
30     private double _pressure;
31     private DateTime _lastUpdate;
32
33     public string EquipmentId
34     {
35         get => _equipmentId;
36         set => SetProperty(ref _equipmentId, value);
37     }
38
39     public EquipmentStatus Status
40     {
41         get => _status;
42         set
43         {
44             if (SetProperty(ref _status, value))
45             {
46                 // 상태 변경 시 색상도 함께 업데이트
47                 OnPropertyChanged(nameof(StatusColor));
48                 OnPropertyChanged(nameof(StatusText));
49             }
50         }
```

</div>
<div>

**필드 및 기본 속성 정의**
- **Line 27-31**: private 백킹 필드 선언
  - **equipmentId**: 장비 고유 식별자
  - **status**: 현재 장비 상태
  - **temperature**: 온도 센서 값
  - **pressure**: 압력 센서 값
  - **lastUpdate**: 마지막 업데이트 시간

- **Line 33-37**: 장비 ID 속성
  - get/set 표현식 구문으로 간결한 구현
  - SetProperty 헬퍼 사용으로 자동 알림

- **Line 39-50**: 상태 속성 (복합 알림)
  - **Line 44**: SetProperty가 true 반환시 (값이 실제 변경됨)
  - **Line 47-48**: 관련 계산 속성들도 함께 알림
  - **nameof**: 컴파일 타임 문자열 안전성 확보

</div>
</div>

---

### 💻 기본 ViewModel 구현 - Part 3

<div class="grid grid-cols-2 gap-8">
<div>

```csharp {51-75}
51     }
52
53     public double Temperature
54     {
55         get => _temperature;
56         set => SetProperty(ref _temperature, value);
57     }
58
59     public double Pressure
60     {
61         get => _pressure;
62         set => SetProperty(ref _pressure, value);
63     }
64
65     public DateTime LastUpdate
66     {
67         get => _lastUpdate;
68         set => SetProperty(ref _lastUpdate, value);
69     }
70
71     // 계산된 속성들
72     public string StatusColor => Status switch
73     {
74         EquipmentStatus.Running => "#4CAF50",    // 녹색
75         EquipmentStatus.Warning => "#FF9800",    // 주황색
```

</div>
<div>

**센서 데이터 속성 및 계산 속성 시작**
- **Line 53-57**: 온도 속성
  - double 타입으로 정밀한 온도 값 관리
  - 센서에서 실시간으로 업데이트되는 값

- **Line 59-63**: 압력 속성
  - 반도체 공정에서 중요한 진공 압력 모니터링
  - Torr 단위로 측정되는 정밀 압력 값

- **Line 65-69**: 마지막 업데이트 시간
  - 데이터 신선도 확인용
  - 통신 상태 모니터링 지표

- **Line 72-75**: 상태별 색상 계산 속성
  - **switch 식**: C# 8.0의 간결한 패턴 매칭
  - **Line 74**: Running 상태 - 녹색 (#4CAF50)
  - **Line 75**: Warning 상태 - 주황색 (#FF9800)

</div>
</div>

---

### 💻 기본 ViewModel 구현 - Part 4

<div class="grid grid-cols-2 gap-8">
<div>

```csharp {76-95}
76         EquipmentStatus.Error => "#F44336",      // 빨간색
77         EquipmentStatus.Maintenance => "#2196F3", // 파란색
78         _ => "#9E9E9E"                           // 회색
79     };
80
81     public string StatusText => Status switch
82     {
83         EquipmentStatus.Idle => "대기",
84         EquipmentStatus.Running => "운전 중",
85         EquipmentStatus.Warning => "경고",
86         EquipmentStatus.Error => "오류",
87         EquipmentStatus.Maintenance => "정비 중",
88         _ => "알 수 없음"
89     };
90
91     public string TemperatureText => $"{Temperature:F1}°C";
92     public string PressureText => $"{Pressure:F3} Torr";
93     public string LastUpdateText => LastUpdate.ToString("yyyy-MM-dd HH:mm:ss");
94 }
95
```

</div>
<div>

**계산 속성 완성 및 포맷팅**
- **Line 76-79**: 상태 색상 매핑 완료
  - **Line 76**: Error 상태 - 빨간색 (#F44336)
  - **Line 77**: Maintenance 상태 - 파란색 (#2196F3)
  - **Line 78**: 기본값 - 회색 (#9E9E9E)

- **Line 81-89**: 상태 텍스트 한글 표시
  - 사용자 친화적 한글 메시지
  - 각 상태별 명확한 의미 전달

- **Line 91-93**: 데이터 포맷팅 속성
  - **Line 91**: 온도 - 소수점 1자리 + 단위
  - **Line 92**: 압력 - 소수점 3자리 정밀도 + Torr 단위
  - **Line 93**: 시간 - 표준 datetime 포맷

**MVVM 패턴의 핵심**: View에서 직접 사용 가능한 형태로 데이터 가공

</div>
</div>

</div>

---

## 커맨드 패턴과 RelayCommand

<div style="margin: 2rem 0;">

### ⚡ ICommand 인터페이스

<div style="background: #e3f2fd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2196f3; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #0d47a1;">Execute:</strong> 명령 실행 메서드</li>
        <li><strong style="color: #0d47a1;">CanExecute:</strong> 실행 가능 여부 확인</li>
        <li><strong style="color: #0d47a1;">CanExecuteChanged:</strong> 실행 가능 상태 변경 이벤트</li>
    </ul>
</div>

### 💻 RelayCommand 구현

```csharp
// 범용 RelayCommand 구현
public class RelayCommand : ICommand
{
    private readonly Action _execute;
    private readonly Func<bool> _canExecute;

    public RelayCommand(Action execute, Func<bool> canExecute = null)
    {
        _execute = execute ?? throw new ArgumentNullException(nameof(execute));
        _canExecute = canExecute;
    }

    public event EventHandler CanExecuteChanged
    {
        add { CommandManager.RequerySuggested += value; }
        remove { CommandManager.RequerySuggested -= value; }
    }

    public bool CanExecute(object parameter)
    {
        return _canExecute?.Invoke() ?? true;
    }

    public void Execute(object parameter)
    {
        _execute.Invoke();
    }

    // 강제로 CanExecute 재평가 요청
    public void RaiseCanExecuteChanged()
    {
        CommandManager.InvalidateRequerySuggested();
    }
}

// 제네릭 버전 (매개변수 포함)
public class RelayCommand<T> : ICommand
{
    private readonly Action<T> _execute;
    private readonly Predicate<T> _canExecute;

    public RelayCommand(Action<T> execute, Predicate<T> canExecute = null)
    {
        _execute = execute ?? throw new ArgumentNullException(nameof(execute));
        _canExecute = canExecute;
    }

    public event EventHandler CanExecuteChanged
    {
        add { CommandManager.RequerySuggested += value; }
        remove { CommandManager.RequerySuggested -= value; }
    }

    public bool CanExecute(object parameter)
    {
        return _canExecute?.Invoke((T)parameter) ?? true;
    }

    public void Execute(object parameter)
    {
        _execute.Invoke((T)parameter);
    }
}
```

</div>

---

# 💻 기초 실습 (45분)

---

## 실습 1: 기본 XAML 구조 생성

<div style="margin: 2rem 0;">

### 🏗️ 프로젝트 생성

<div style="background: #e8f5e8; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 1rem 0;">

**Visual Studio에서 새 프로젝트 생성:**
1. WPF Application (.NET 6.0) 선택
2. 프로젝트명: `SemiconductorHMI`
3. 솔루션명: `SemiconductorEquipmentMonitor`

</div>

### 📄 기본 MainWindow.xaml 구조

```xml
<Window x:Class="SemiconductorHMI.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="반도체 장비 모니터링 시스템"
        Height="800" Width="1200"
        WindowState="Maximized"
        Background="#F5F5F5">

    <!-- 메인 레이아웃 -->
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="80"/>      <!-- 헤더 -->
            <RowDefinition Height="*"/>       <!-- 메인 콘텐츠 -->
            <RowDefinition Height="30"/>      <!-- 상태바 -->
        </Grid.RowDefinitions>

        <!-- 헤더 영역 -->
        <Border Grid.Row="0" Background="#2C3E50" Padding="20,10">
            <Grid>
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="Auto"/>
                    <ColumnDefinition Width="Auto"/>
                </Grid.ColumnDefinitions>

                <!-- 시스템 제목 -->
                <StackPanel Grid.Column="0" VerticalAlignment="Center">
                    <TextBlock Text="반도체 장비 모니터링 시스템"
                               FontSize="24" FontWeight="Bold"
                               Foreground="White"/>
                    <TextBlock Text="Semiconductor Equipment Monitoring System"
                               FontSize="12"
                               Foreground="#BDC3C7"/>
                </StackPanel>

                <!-- 현재 시간 -->
                <TextBlock Grid.Column="1"
                           Text="{Binding CurrentTime}"
                           FontSize="16" FontWeight="Medium"
                           Foreground="White"
                           VerticalAlignment="Center"
                           Margin="20,0"/>

                <!-- 알람 요약 -->
                <Border Grid.Column="2"
                        Background="#E74C3C"
                        CornerRadius="15"
                        Padding="10,5"
                        VerticalAlignment="Center">
                    <StackPanel Orientation="Horizontal">
                        <TextBlock Text="🚨" FontSize="16" Margin="0,0,5,0"/>
                        <TextBlock Text="{Binding AlarmCount}"
                                   FontSize="14" FontWeight="Bold"
                                   Foreground="White"/>
                        <TextBlock Text="건"
                                   FontSize="14"
                                   Foreground="White" Margin="2,0,0,0"/>
                    </StackPanel>
                </Border>
            </Grid>
        </Border>

        <!-- 메인 콘텐츠 영역 -->
        <Grid Grid.Row="1" Margin="10">
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="250"/>    <!-- 사이드바 -->
                <ColumnDefinition Width="*"/>      <!-- 메인 영역 -->
            </Grid.ColumnDefinitions>

            <!-- 사이드바 -->
            <Border Grid.Column="0"
                    Background="White"
                    CornerRadius="5"
                    BorderBrush="#E0E0E0"
                    BorderThickness="1"
                    Margin="0,0,10,0">
                <StackPanel Margin="10">
                    <TextBlock Text="장비 목록"
                               FontSize="16" FontWeight="Bold"
                               Margin="0,0,0,10"/>

                    <!-- 장비 목록 리스트박스 -->
                    <ListBox x:Name="EquipmentListBox"
                             ItemsSource="{Binding EquipmentList}"
                             SelectedItem="{Binding SelectedEquipment}"
                             Background="Transparent"
                             BorderThickness="0">
                        <ListBox.ItemTemplate>
                            <DataTemplate>
                                <Border Background="{Binding StatusColor}"
                                        CornerRadius="3"
                                        Padding="8,5"
                                        Margin="0,2">
                                    <StackPanel>
                                        <TextBlock Text="{Binding EquipmentId}"
                                                   FontWeight="Bold"
                                                   Foreground="White"/>
                                        <TextBlock Text="{Binding StatusText}"
                                                   FontSize="12"
                                                   Foreground="White"/>
                                    </StackPanel>
                                </Border>
                            </DataTemplate>
                        </ListBox.ItemTemplate>
                    </ListBox>
                </StackPanel>
            </Border>

            <!-- 메인 모니터링 영역 -->
            <Border Grid.Column="1"
                    Background="White"
                    CornerRadius="5"
                    BorderBrush="#E0E0E0"
                    BorderThickness="1">
                <Grid Margin="20">
                    <Grid.RowDefinitions>
                        <RowDefinition Height="Auto"/>
                        <RowDefinition Height="*"/>
                    </Grid.RowDefinitions>

                    <!-- 선택된 장비 정보 헤더 -->
                    <StackPanel Grid.Row="0" Margin="0,0,0,20">
                        <TextBlock Text="{Binding SelectedEquipment.EquipmentId}"
                                   FontSize="24" FontWeight="Bold"/>
                        <TextBlock Text="{Binding SelectedEquipment.LastUpdateText}"
                                   FontSize="12"
                                   Foreground="#666666"/>
                    </StackPanel>

                    <!-- 상세 모니터링 정보 -->
                    <Grid Grid.Row="1">
                        <Grid.ColumnDefinitions>
                            <ColumnDefinition Width="*"/>
                            <ColumnDefinition Width="*"/>
                        </Grid.ColumnDefinitions>

                        <!-- 온도 정보 -->
                        <Border Grid.Column="0"
                                Background="#F8F9FA"
                                CornerRadius="8"
                                Padding="20"
                                Margin="0,0,10,0">
                            <StackPanel>
                                <TextBlock Text="챔버 온도"
                                           FontSize="16" FontWeight="Medium"
                                           Margin="0,0,0,10"/>
                                <TextBlock Text="{Binding SelectedEquipment.TemperatureText}"
                                           FontSize="36" FontWeight="Bold"
                                           Foreground="#E67E22"/>
                                <ProgressBar Value="{Binding SelectedEquipment.Temperature}"
                                           Minimum="0" Maximum="300"
                                           Height="10"
                                           Background="#E0E0E0"
                                           Foreground="#E67E22"
                                           Margin="0,10,0,0"/>
                            </StackPanel>
                        </Border>

                        <!-- 압력 정보 -->
                        <Border Grid.Column="1"
                                Background="#F8F9FA"
                                CornerRadius="8"
                                Padding="20"
                                Margin="10,0,0,0">
                            <StackPanel>
                                <TextBlock Text="챔버 압력"
                                           FontSize="16" FontWeight="Medium"
                                           Margin="0,0,0,10"/>
                                <TextBlock Text="{Binding SelectedEquipment.PressureText}"
                                           FontSize="36" FontWeight="Bold"
                                           Foreground="#3498DB"/>
                                <ProgressBar Value="{Binding SelectedEquipment.Pressure}"
                                           Minimum="0" Maximum="2"
                                           Height="10"
                                           Background="#E0E0E0"
                                           Foreground="#3498DB"
                                           Margin="0,10,0,0"/>
                            </StackPanel>
                        </Border>
                    </Grid>
                </Grid>
            </Border>
        </Grid>

        <!-- 상태바 -->
        <Border Grid.Row="2" Background="#34495E" Padding="10,5">
            <Grid>
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="Auto"/>
                </Grid.ColumnDefinitions>

                <TextBlock Grid.Column="0"
                           Text="{Binding StatusMessage}"
                           Foreground="White"
                           VerticalAlignment="Center"/>

                <TextBlock Grid.Column="1"
                           Text="시스템 정상"
                           Foreground="#2ECC71"
                           VerticalAlignment="Center"/>
            </Grid>
        </Border>
    </Grid>
</Window>
```

</div>

---

## 실습 2: 데이터 바인딩 설정

<div style="margin: 2rem 0;">

### 📊 MainWindow.xaml.cs 코드-비하인드

<div class="grid grid-cols-2 gap-8">
<div>

```csharp {1-17}
1  using System.Windows;
2
3  namespace SemiconductorHMI
4  {
5      public partial class MainWindow : Window
6      {
7          public MainWindow()
8          {
9              InitializeComponent();
10
11             // ViewModel 설정
12             DataContext = new MainWindowViewModel();
13         }
14     }
15 }
16
17
```

</div>
<div>

**코드-비하인드 기본 구조**
- **Line 1**: System.Windows 네임스페이스 사용
- **Line 3**: SemiconductorHMI 네임스페이스 정의
- **Line 5**: MainWindow가 Window 클래스 상속
- **Line 7-13**: 생성자 메서드
  - **Line 9**: InitializeComponent() - XAML 초기화
  - **Line 12**: DataContext 설정으로 MVVM 바인딩 활성화

**MVVM 패턴 핵심**:
- View(XAML)와 ViewModel 연결점
- 최소한의 코드-비하인드로 관심사 분리
- DataContext를 통한 자동 데이터 바인딩

</div>
</div>

---

### 🎯 MainWindowViewModel 구현 - Part 1

<div class="grid grid-cols-2 gap-8">
<div>

```csharp {18-42}
18 using System;
19 using System.Collections.ObjectModel;
20 using System.ComponentModel;
21 using System.Runtime.CompilerServices;
22 using System.Windows.Threading;
23
24 namespace SemiconductorHMI
25 {
26     public class MainWindowViewModel : BaseViewModel
27     {
28         private EquipmentViewModel _selectedEquipment;
29         private string _currentTime;
30         private int _alarmCount;
31         private string _statusMessage;
32         private DispatcherTimer _clockTimer;
33
34         public ObservableCollection<EquipmentViewModel> EquipmentList { get; }
35
36         public EquipmentViewModel SelectedEquipment
37         {
38             get => _selectedEquipment;
39             set => SetProperty(ref _selectedEquipment, value);
40         }
41
42         public string CurrentTime
```

</div>
<div>

**ViewModel 클래스 기본 구조**
- **Line 18-22**: 필요한 네임스페이스 import
  - ObservableCollection: 컬렉션 바인딩용
  - DispatcherTimer: UI 스레드 타이머
- **Line 26**: BaseViewModel 상속으로 INotifyPropertyChanged 구현

- **Line 28-32**: private 백킹 필드들
  - **selectedEquipment**: 현재 선택된 장비
  - **currentTime**: 실시간 시계 표시
  - **alarmCount**: 알람 발생 개수
  - **statusMessage**: 상태 메시지
  - **clockTimer**: 시계 업데이트용 타이머

- **Line 34**: ObservableCollection으로 UI 자동 업데이트
- **Line 36-40**: 선택된 장비 속성 (읽기전용 프로퍼티 사용)

</div>
</div>

---

### 🎯 MainWindowViewModel 구현 - Part 2

<div class="grid grid-cols-2 gap-8">
<div>

```csharp {43-67}
43         {
44             get => _currentTime;
45             set => SetProperty(ref _currentTime, value);
46         }
47
48         public int AlarmCount
49         {
50             get => _alarmCount;
51             set => SetProperty(ref _alarmCount, value);
52         }
53
54         public string StatusMessage
55         {
56             get => _statusMessage;
57             set => SetProperty(ref _statusMessage, value);
58         }
59
60         public MainWindowViewModel()
61         {
62             EquipmentList = new ObservableCollection<EquipmentViewModel>();
63             InitializeEquipmentData();
64             InitializeClock();
65
66             // 첫 번째 장비를 기본 선택
67             if (EquipmentList.Count > 0)
```

</div>
<div>

**속성 정의 및 생성자**
- **Line 43-46**: CurrentTime 속성
  - 실시간 시계 표시용
  - UI에서 바인딩하여 자동 업데이트

- **Line 48-52**: AlarmCount 속성
  - Warning/Error 상태 장비 개수
  - 헤더 영역 알람 표시용

- **Line 54-58**: StatusMessage 속성
  - 시스템 상태 메시지
  - 사용자에게 현재 상태 안내

- **Line 60-67**: 생성자 메서드 시작
  - **Line 62**: ObservableCollection 초기화
  - **Line 63**: 샘플 장비 데이터 생성
  - **Line 64**: 실시간 시계 초기화
  - **Line 67**: 첫 번째 장비를 기본 선택

</div>
</div>

---

### 🎯 MainWindowViewModel 구현 - Part 3

<div class="grid grid-cols-2 gap-8">
<div>

```csharp {68-92}
68                 SelectedEquipment = EquipmentList[0];
69
70             StatusMessage = "시스템 초기화 완료";
71         }
72
73         private void InitializeEquipmentData()
74         {
75             // 샘플 반도체 장비 데이터 생성
76             EquipmentList.Add(new EquipmentViewModel
77             {
78                 EquipmentId = "CVD-001",
79                 Status = EquipmentStatus.Running,
80                 Temperature = 250.5,
81                 Pressure = 0.850,
82                 LastUpdate = DateTime.Now
83             });
84
85             EquipmentList.Add(new EquipmentViewModel
86             {
87                 EquipmentId = "PVD-002",
88                 Status = EquipmentStatus.Warning,
89                 Temperature = 185.2,
90                 Pressure = 1.250,
91                 LastUpdate = DateTime.Now.AddMinutes(-2)
92             });
```

</div>
<div>

**샘플 데이터 초기화 - Part 1**
- **Line 68**: 첫 번째 장비를 기본 선택으로 설정
- **Line 70**: 초기화 완료 메시지 설정

- **Line 73-83**: CVD-001 장비 데이터
  - **CVD**: Chemical Vapor Deposition (화학기상증착)
  - **Line 79**: Running 상태 - 정상 운전 중
  - **Line 80**: 250.5°C - 일반적인 CVD 공정 온도
  - **Line 81**: 0.850 Torr - 공정 압력

- **Line 85-92**: PVD-002 장비 데이터
  - **PVD**: Physical Vapor Deposition (물리기상증착)
  - **Line 88**: Warning 상태 - 주의 필요
  - **Line 90**: 1.250 Torr - 경고 상태 압력
  - **Line 91**: 2분 전 업데이트 - 통신 지연 시뮬레이션

</div>
</div>

---

### 🎯 MainWindowViewModel 구현 - Part 4

<div class="grid grid-cols-2 gap-8">
<div>

```csharp {93-117}
93
94             EquipmentList.Add(new EquipmentViewModel
95             {
96                 EquipmentId = "ETCH-003",
97                 Status = EquipmentStatus.Idle,
98                 Temperature = 25.0,
99                 Pressure = 0.001,
100                LastUpdate = DateTime.Now.AddMinutes(-15)
101            });
102
103            EquipmentList.Add(new EquipmentViewModel
104            {
105                EquipmentId = "CMP-004",
106                Status = EquipmentStatus.Error,
107                Temperature = 95.8,
108                Pressure = 0.750,
109                LastUpdate = DateTime.Now.AddMinutes(-5)
110            });
111
112            // 알람 개수 계산
113            UpdateAlarmCount();
114        }
115
116        private void InitializeClock()
117        {
```

</div>
<div>

**샘플 데이터 초기화 - Part 2**
- **Line 94-101**: ETCH-003 장비 데이터
  - **ETCH**: 식각 공정 장비
  - **Line 97**: Idle 상태 - 대기 중
  - **Line 98**: 25.0°C - 상온 상태
  - **Line 99**: 0.001 Torr - 고진공 상태
  - **Line 100**: 15분 전 업데이트 - 오프라인 상태

- **Line 103-110**: CMP-004 장비 데이터
  - **CMP**: Chemical Mechanical Planarization (화학기계평탄화)
  - **Line 106**: Error 상태 - 오류 발생
  - **Line 107**: 95.8°C - 비정상 온도
  - **Line 109**: 5분 전 업데이트

- **Line 113**: 알람 개수 계산 메서드 호출
- **Line 116**: 실시간 시계 초기화 메서드 시작

</div>
</div>

---

### 🎯 MainWindowViewModel 구현 - Part 5

<div class="grid grid-cols-2 gap-8">
<div>

```csharp {118-142}
118            // 1초마다 시간 업데이트
119            _clockTimer = new DispatcherTimer
120            {
121                Interval = TimeSpan.FromSeconds(1)
122            };
123            _clockTimer.Tick += (s, e) => UpdateCurrentTime();
124            _clockTimer.Start();
125
126            UpdateCurrentTime();
127        }
128
129        private void UpdateCurrentTime()
130        {
131            CurrentTime = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
132        }
133
134        private void UpdateAlarmCount()
135        {
136            int count = 0;
137            foreach (var equipment in EquipmentList)
138            {
139                if (equipment.Status == EquipmentStatus.Warning ||
140                    equipment.Status == EquipmentStatus.Error)
141                {
142                    count++;
```

</div>
<div>

**타이머 및 업데이트 메서드**
- **Line 119-122**: DispatcherTimer 설정
  - **Line 121**: 1초 간격으로 설정
  - UI 스레드에서 안전한 타이머 사용

- **Line 123**: 람다식으로 이벤트 핸들러 등록
  - 간결한 문법으로 콜백 설정
- **Line 124**: 타이머 시작
- **Line 126**: 즉시 시간 업데이트

- **Line 129-132**: 현재 시간 업데이트 메서드
  - **Line 131**: 표준 날짜/시간 포맷 사용

- **Line 134-142**: 알람 개수 계산 메서드
  - **Line 137**: 전체 장비 리스트 순회
  - **Line 139-140**: Warning 또는 Error 상태 체크
  - **Line 142**: 카운터 증가

</div>
</div>

---

### 🎯 MainWindowViewModel 구현 - Part 6

<div class="grid grid-cols-2 gap-8">
<div>

```csharp {143-152}
143                }
144            }
145            AlarmCount = count;
146        }
147    }
148 }
149
150
151
152
```

</div>
<div>

**메서드 완료 및 클래스 종료**
- **Line 145**: 계산된 알람 개수를 속성에 설정
  - SetProperty 호출로 UI 자동 업데이트
- **Line 146-148**: 메서드 및 클래스 종료

**MainWindowViewModel의 핵심 기능**:
1. **실시간 데이터 바인딩**: ObservableCollection 사용
2. **자동 UI 업데이트**: INotifyPropertyChanged 구현
3. **타이머 기반 갱신**: DispatcherTimer로 시계 업데이트
4. **알람 모니터링**: 상태 기반 알람 개수 계산
5. **샘플 데이터**: 4가지 반도체 장비 시뮬레이션

**MVVM 패턴 완성**: View는 ViewModel과 바인딩만으로 동작

</div>
</div>

</div>

---

# 🚀 심화 실습 (45분)

---

## 실습 3: MVVM 패턴 완성

<div style="margin: 2rem 0;">

### ⚡ 커맨드 구현

```csharp
// MainWindowViewModel에 커맨드 추가
public class MainWindowViewModel : BaseViewModel
{
    // ... 기존 코드 ...

    public ICommand RefreshCommand { get; }
    public ICommand StartMaintenanceCommand { get; }
    public ICommand StopEquipmentCommand { get; }
    public ICommand ClearAlarmsCommand { get; }

    public MainWindowViewModel()
    {
        // ... 기존 초기화 코드 ...

        // 커맨드 초기화
        RefreshCommand = new RelayCommand(ExecuteRefresh);
        StartMaintenanceCommand = new RelayCommand(ExecuteStartMaintenance, CanStartMaintenance);
        StopEquipmentCommand = new RelayCommand(ExecuteStopEquipment, CanStopEquipment);
        ClearAlarmsCommand = new RelayCommand(ExecuteClearAlarms, CanClearAlarms);
    }

    // 새로고침 커맨드
    private void ExecuteRefresh()
    {
        StatusMessage = "데이터를 새로고침하는 중...";

        // 실제로는 서버에서 데이터를 가져오는 로직
        foreach (var equipment in EquipmentList)
        {
            equipment.LastUpdate = DateTime.Now;
            // 임의의 데이터 업데이트 시뮬레이션
            var random = new Random();
            equipment.Temperature += (random.NextDouble() - 0.5) * 2;
            equipment.Pressure += (random.NextDouble() - 0.5) * 0.1;
        }

        UpdateAlarmCount();
        StatusMessage = "새로고침 완료";
    }

    // 정비 시작 커맨드
    private void ExecuteStartMaintenance()
    {
        if (SelectedEquipment != null)
        {
            SelectedEquipment.Status = EquipmentStatus.Maintenance;
            StatusMessage = $"{SelectedEquipment.EquipmentId} 정비 모드로 전환";
            UpdateAlarmCount();
        }
    }

    private bool CanStartMaintenance()
    {
        return SelectedEquipment?.Status == EquipmentStatus.Idle ||
               SelectedEquipment?.Status == EquipmentStatus.Error;
    }

    // 장비 정지 커맨드
    private void ExecuteStopEquipment()
    {
        if (SelectedEquipment != null)
        {
            SelectedEquipment.Status = EquipmentStatus.Idle;
            StatusMessage = $"{SelectedEquipment.EquipmentId} 장비 정지";
            UpdateAlarmCount();
        }
    }

    private bool CanStopEquipment()
    {
        return SelectedEquipment?.Status == EquipmentStatus.Running ||
               SelectedEquipment?.Status == EquipmentStatus.Warning;
    }

    // 알람 초기화 커맨드
    private void ExecuteClearAlarms()
    {
        foreach (var equipment in EquipmentList)
        {
            if (equipment.Status == EquipmentStatus.Warning)
            {
                equipment.Status = EquipmentStatus.Running;
            }
        }
        UpdateAlarmCount();
        StatusMessage = "모든 경고 알람이 초기화되었습니다";
    }

    private bool CanClearAlarms()
    {
        return AlarmCount > 0;
    }
}
```

### 🎮 XAML에 커맨드 바인딩 추가

```xml
<!-- MainWindow.xaml의 메인 콘텐츠 영역에 버튼 추가 -->
<Grid Grid.Row="1">
    <!-- 기존 콘텐츠... -->

    <!-- 제어 버튼 패널 추가 -->
    <Grid Grid.Row="2" Margin="0,20,0,0">
        <Grid.ColumnDefinitions>
            <ColumnDefinition Width="*"/>
            <ColumnDefinition Width="*"/>
            <ColumnDefinition Width="*"/>
            <ColumnDefinition Width="*"/>
        </Grid.ColumnDefinitions>

        <!-- 새로고침 버튼 -->
        <Button Grid.Column="0"
                Command="{Binding RefreshCommand}"
                Background="#3498DB"
                Foreground="White"
                Padding="15,10"
                Margin="5"
                FontWeight="Medium"
                BorderThickness="0"
                CornerRadius="5">
            <StackPanel Orientation="Horizontal">
                <TextBlock Text="🔄" FontSize="16" Margin="0,0,5,0"/>
                <TextBlock Text="새로고침"/>
            </StackPanel>
        </Button>

        <!-- 정비 시작 버튼 -->
        <Button Grid.Column="1"
                Command="{Binding StartMaintenanceCommand}"
                Background="#9B59B6"
                Foreground="White"
                Padding="15,10"
                Margin="5"
                FontWeight="Medium"
                BorderThickness="0"
                CornerRadius="5">
            <StackPanel Orientation="Horizontal">
                <TextBlock Text="🔧" FontSize="16" Margin="0,0,5,0"/>
                <TextBlock Text="정비 시작"/>
            </StackPanel>
        </Button>

        <!-- 장비 정지 버튼 -->
        <Button Grid.Column="2"
                Command="{Binding StopEquipmentCommand}"
                Background="#E67E22"
                Foreground="White"
                Padding="15,10"
                Margin="5"
                FontWeight="Medium"
                BorderThickness="0"
                CornerRadius="5">
            <StackPanel Orientation="Horizontal">
                <TextBlock Text="⏹️" FontSize="16" Margin="0,0,5,0"/>
                <TextBlock Text="장비 정지"/>
            </StackPanel>
        </Button>

        <!-- 알람 초기화 버튼 -->
        <Button Grid.Column="3"
                Command="{Binding ClearAlarmsCommand}"
                Background="#E74C3C"
                Foreground="White"
                Padding="15,10"
                Margin="5"
                FontWeight="Medium"
                BorderThickness="0"
                CornerRadius="5">
            <StackPanel Orientation="Horizontal">
                <TextBlock Text="🚨" FontSize="16" Margin="0,0,5,0"/>
                <TextBlock Text="알람 초기화"/>
            </StackPanel>
        </Button>
    </Grid>
</Grid>
```

</div>

---

## 실습 4: 값 변환기 구현

<div style="margin: 2rem 0;">

### 🔄 상태별 색상 변환기

```csharp
// StatusToColorConverter.cs
using System;
using System.Globalization;
using System.Windows.Data;
using System.Windows.Media;

namespace SemiconductorHMI.Converters
{
    public class StatusToColorConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value is EquipmentStatus status)
            {
                return status switch
                {
                    EquipmentStatus.Running => new SolidColorBrush(Color.FromRgb(76, 175, 80)),     // 녹색
                    EquipmentStatus.Warning => new SolidColorBrush(Color.FromRgb(255, 152, 0)),     // 주황색
                    EquipmentStatus.Error => new SolidColorBrush(Color.FromRgb(244, 67, 54)),       // 빨간색
                    EquipmentStatus.Maintenance => new SolidColorBrush(Color.FromRgb(33, 150, 243)), // 파란색
                    _ => new SolidColorBrush(Color.FromRgb(158, 158, 158))                          // 회색
                };
            }
            return new SolidColorBrush(Colors.Gray);
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }

    // 온도 범위별 색상 변환기
    public class TemperatureToColorConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value is double temperature)
            {
                if (temperature < 50)
                    return new SolidColorBrush(Color.FromRgb(33, 150, 243));   // 파란색 (저온)
                else if (temperature < 150)
                    return new SolidColorBrush(Color.FromRgb(76, 175, 80));    // 녹색 (정상)
                else if (temperature < 250)
                    return new SolidColorBrush(Color.FromRgb(255, 193, 7));    // 노란색 (주의)
                else if (temperature < 300)
                    return new SolidColorBrush(Color.FromRgb(255, 152, 0));    // 주황색 (경고)
                else
                    return new SolidColorBrush(Color.FromRgb(244, 67, 54));    // 빨간색 (위험)
            }
            return new SolidColorBrush(Colors.Gray);
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }

    // 압력 단위 표시 변환기
    public class PressureToStringConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            if (value is double pressure)
            {
                if (pressure < 0.001)
                    return $"{pressure * 1000000:F1} mTorr";
                else if (pressure < 1.0)
                    return $"{pressure * 1000:F1} mTorr";
                else
                    return $"{pressure:F3} Torr";
            }
            return "0 Torr";
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }
}
```

### 📄 XAML에서 변환기 사용

```xml
<Window x:Class="SemiconductorHMI.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:converters="clr-namespace:SemiconductorHMI.Converters"
        Title="반도체 장비 모니터링 시스템">

    <Window.Resources>
        <!-- 변환기 리소스 등록 -->
        <converters:StatusToColorConverter x:Key="StatusToColorConverter"/>
        <converters:TemperatureToColorConverter x:Key="TemperatureToColorConverter"/>
        <converters:PressureToStringConverter x:Key="PressureToStringConverter"/>
    </Window.Resources>

    <!-- 기존 내용... -->

    <!-- 장비 목록에서 색상 변환기 사용 -->
    <ListBox.ItemTemplate>
        <DataTemplate>
            <Border Background="{Binding Status, Converter={StaticResource StatusToColorConverter}}"
                    CornerRadius="3"
                    Padding="8,5"
                    Margin="0,2">
                <!-- 내용... -->
            </Border>
        </DataTemplate>
    </ListBox.ItemTemplate>

    <!-- 온도 표시에 색상 변환기 적용 -->
    <TextBlock Text="{Binding SelectedEquipment.TemperatureText}"
               FontSize="36" FontWeight="Bold"
               Foreground="{Binding SelectedEquipment.Temperature,
                          Converter={StaticResource TemperatureToColorConverter}}"/>

    <!-- 압력 표시에 단위 변환기 적용 -->
    <TextBlock Text="{Binding SelectedEquipment.Pressure,
                     Converter={StaticResource PressureToStringConverter}}"
               FontSize="36" FontWeight="Bold"
               Foreground="#3498DB"/>
</Window>
```

</div>

---

# 🎯 Hands-on 프로젝트 (45분)

---

## 종합 프로젝트: 반도체 장비 모니터링 시스템

<div style="margin: 2rem 0;">

### 🏗️ 프로젝트 구조 완성

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #6c757d; margin: 1rem 0;">

```
SemiconductorHMI/
├── Models/
│   ├── Equipment.cs
│   └── EquipmentStatus.cs
├── ViewModels/
│   ├── BaseViewModel.cs
│   ├── EquipmentViewModel.cs
│   └── MainWindowViewModel.cs
├── Views/
│   ├── MainWindow.xaml
│   └── MainWindow.xaml.cs
├── Converters/
│   ├── StatusToColorConverter.cs
│   ├── TemperatureToColorConverter.cs
│   └── PressureToStringConverter.cs
├── Commands/
│   └── RelayCommand.cs
└── Services/
    └── EquipmentDataService.cs
```

</div>

### 💾 Equipment 모델 클래스

```csharp
// Models/Equipment.cs
using System;

namespace SemiconductorHMI.Models
{
    public class Equipment
    {
        public string EquipmentId { get; set; }
        public string EquipmentName { get; set; }
        public EquipmentType Type { get; set; }
        public EquipmentStatus Status { get; set; }
        public double Temperature { get; set; }
        public double Pressure { get; set; }
        public double FlowRate { get; set; }
        public double Power { get; set; }
        public DateTime LastUpdate { get; set; }
        public string ProcessRecipe { get; set; }
        public int WaferCount { get; set; }
        public TimeSpan ProcessTime { get; set; }

        // 임계값 설정
        public double TemperatureMin { get; set; } = 0;
        public double TemperatureMax { get; set; } = 300;
        public double PressureMin { get; set; } = 0.001;
        public double PressureMax { get; set; } = 2.0;

        // 상태 확인 메서드
        public bool IsInNormalRange()
        {
            return Temperature >= TemperatureMin && Temperature <= TemperatureMax &&
                   Pressure >= PressureMin && Pressure <= PressureMax;
        }

        public EquipmentStatus GetCalculatedStatus()
        {
            if (!IsInNormalRange())
                return EquipmentStatus.Warning;

            return Status;
        }
    }

    public enum EquipmentType
    {
        CVD,        // Chemical Vapor Deposition
        PVD,        // Physical Vapor Deposition
        Etch,       // 에칭
        CMP,        // Chemical Mechanical Polishing
        Lithography, // 리소그래피
        Diffusion,  // 확산
        IonImplant, // 이온주입
        Metrology   // 계측
    }

    public enum EquipmentStatus
    {
        Idle,           // 대기
        Running,        // 운전 중
        Warning,        // 경고
        Error,          // 오류
        Maintenance,    // 정비 중
        Setup,          // 셋업 중
        Cleaning       // 청소 중
    }
}
```

### 🔧 데이터 서비스 구현

```csharp
// Services/EquipmentDataService.cs
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Threading;
using SemiconductorHMI.Models;

namespace SemiconductorHMI.Services
{
    public class EquipmentDataService
    {
        private readonly Random _random = new Random();
        private readonly Timer _updateTimer;
        private readonly List<Equipment> _equipmentList;

        public event EventHandler<EquipmentDataUpdatedEventArgs> DataUpdated;

        public EquipmentDataService()
        {
            _equipmentList = InitializeEquipmentData();

            // 1초마다 데이터 업데이트
            _updateTimer = new Timer(UpdateEquipmentData, null,
                TimeSpan.Zero, TimeSpan.FromSeconds(1));
        }

        private List<Equipment> InitializeEquipmentData()
        {
            return new List<Equipment>
            {
                new Equipment
                {
                    EquipmentId = "CVD-001",
                    EquipmentName = "PECVD Silicon Nitride",
                    Type = EquipmentType.CVD,
                    Status = EquipmentStatus.Running,
                    Temperature = 250.0,
                    Pressure = 0.850,
                    FlowRate = 150.0,
                    Power = 2500.0,
                    ProcessRecipe = "SiN_Standard_v1.2",
                    WaferCount = 25,
                    TemperatureMax = 280.0,
                    PressureMax = 1.0
                },
                new Equipment
                {
                    EquipmentId = "PVD-002",
                    EquipmentName = "Magnetron Sputtering",
                    Type = EquipmentType.PVD,
                    Status = EquipmentStatus.Warning,
                    Temperature = 185.0,
                    Pressure = 0.005,
                    FlowRate = 50.0,
                    Power = 3000.0,
                    ProcessRecipe = "Al_Deposition_v2.1",
                    WaferCount = 18,
                    TemperatureMax = 200.0,
                    PressureMax = 0.01
                },
                new Equipment
                {
                    EquipmentId = "ETCH-003",
                    EquipmentName = "Reactive Ion Etching",
                    Type = EquipmentType.Etch,
                    Status = EquipmentStatus.Idle,
                    Temperature = 25.0,
                    Pressure = 0.001,
                    FlowRate = 0.0,
                    Power = 0.0,
                    ProcessRecipe = "",
                    WaferCount = 0,
                    TemperatureMax = 100.0,
                    PressureMax = 0.1
                },
                new Equipment
                {
                    EquipmentId = "CMP-004",
                    EquipmentName = "Chemical Mechanical Polish",
                    Type = EquipmentType.CMP,
                    Status = EquipmentStatus.Error,
                    Temperature = 45.0,
                    Pressure = 0.750,
                    FlowRate = 200.0,
                    Power = 1500.0,
                    ProcessRecipe = "W_CMP_v3.0",
                    WaferCount = 12,
                    TemperatureMax = 60.0,
                    PressureMax = 1.0
                }
            };
        }

        private void UpdateEquipmentData(object state)
        {
            foreach (var equipment in _equipmentList)
            {
                if (equipment.Status == EquipmentStatus.Running)
                {
                    // 실제 운전 중인 장비의 데이터 변동 시뮬레이션
                    equipment.Temperature += (_random.NextDouble() - 0.5) * 2.0;
                    equipment.Pressure += (_random.NextDouble() - 0.5) * 0.02;
                    equipment.FlowRate += (_random.NextDouble() - 0.5) * 5.0;
                    equipment.Power += (_random.NextDouble() - 0.5) * 100.0;

                    // 범위 제한
                    equipment.Temperature = Math.Max(0, Math.Min(equipment.TemperatureMax + 50, equipment.Temperature));
                    equipment.Pressure = Math.Max(0, Math.Min(equipment.PressureMax + 0.5, equipment.Pressure));
                    equipment.FlowRate = Math.Max(0, equipment.FlowRate);
                    equipment.Power = Math.Max(0, equipment.Power);

                    // 상태 업데이트
                    equipment.Status = equipment.GetCalculatedStatus();
                    equipment.LastUpdate = DateTime.Now;
                }
            }

            // 데이터 업데이트 이벤트 발생
            DataUpdated?.Invoke(this, new EquipmentDataUpdatedEventArgs(_equipmentList));
        }

        public async Task<List<Equipment>> GetEquipmentListAsync()
        {
            // 실제로는 네트워크나 데이터베이스에서 데이터 조회
            await Task.Delay(100); // 네트워크 지연 시뮬레이션
            return new List<Equipment>(_equipmentList);
        }

        public async Task<Equipment> GetEquipmentAsync(string equipmentId)
        {
            await Task.Delay(50);
            return _equipmentList.Find(e => e.EquipmentId == equipmentId);
        }

        public async Task<bool> StartMaintenanceAsync(string equipmentId)
        {
            await Task.Delay(100);
            var equipment = _equipmentList.Find(e => e.EquipmentId == equipmentId);
            if (equipment != null && (equipment.Status == EquipmentStatus.Idle ||
                                    equipment.Status == EquipmentStatus.Error))
            {
                equipment.Status = EquipmentStatus.Maintenance;
                equipment.LastUpdate = DateTime.Now;
                return true;
            }
            return false;
        }

        public void Dispose()
        {
            _updateTimer?.Dispose();
        }
    }

    public class EquipmentDataUpdatedEventArgs : EventArgs
    {
        public List<Equipment> EquipmentList { get; }

        public EquipmentDataUpdatedEventArgs(List<Equipment> equipmentList)
        {
            EquipmentList = equipmentList;
        }
    }
}
```

### 🎮 최종 ViewModel 통합

```csharp
// ViewModels/MainWindowViewModel.cs (최종 버전)
public class MainWindowViewModel : BaseViewModel, IDisposable
{
    private readonly EquipmentDataService _dataService;

    // ... 기존 속성들 ...

    public MainWindowViewModel()
    {
        EquipmentList = new ObservableCollection<EquipmentViewModel>();
        _dataService = new EquipmentDataService();

        // 데이터 서비스 이벤트 구독
        _dataService.DataUpdated += OnDataUpdated;

        InitializeAsync();
        InitializeClock();
        InitializeCommands();
    }

    private async void InitializeAsync()
    {
        StatusMessage = "장비 데이터를 로딩하는 중...";

        try
        {
            var equipmentData = await _dataService.GetEquipmentListAsync();

            EquipmentList.Clear();
            foreach (var equipment in equipmentData)
            {
                EquipmentList.Add(new EquipmentViewModel(equipment));
            }

            if (EquipmentList.Count > 0)
                SelectedEquipment = EquipmentList[0];

            UpdateAlarmCount();
            StatusMessage = "시스템 준비 완료";
        }
        catch (Exception ex)
        {
            StatusMessage = $"데이터 로딩 실패: {ex.Message}";
        }
    }

    private void OnDataUpdated(object sender, EquipmentDataUpdatedEventArgs e)
    {
        // UI 스레드에서 실행되도록 보장
        App.Current.Dispatcher.Invoke(() =>
        {
            for (int i = 0; i < Math.Min(EquipmentList.Count, e.EquipmentList.Count); i++)
            {
                EquipmentList[i].UpdateFromModel(e.EquipmentList[i]);
            }
            UpdateAlarmCount();
        });
    }

    public void Dispose()
    {
        _dataService?.Dispose();
        _clockTimer?.Stop();
    }
}
```

</div>

---

## 📝 학습 정리 및 다음 단계

<div style="margin: 2rem 0;">

### ✅ 오늘 완성한 주요 기능

<div style="background: #e8f5e8; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #155724;">MVVM 아키텍처:</strong> 완전한 3계층 분리 구조 구현</li>
        <li><strong style="color: #155724;">데이터 바인딩:</strong> 양방향 실시간 데이터 동기화</li>
        <li><strong style="color: #155724;">커맨드 패턴:</strong> 사용자 인터랙션의 체계적 관리</li>
        <li><strong style="color: #155724;">값 변환기:</strong> 데이터 표현의 유연한 변환</li>
        <li><strong style="color: #155724;">실시간 모니터링:</strong> 반도체 장비 상태 추적</li>
    </ul>
</div>

### 🚀 다음 주차 예고: 실시간 데이터 처리

<div style="background: #e3f2fd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2196f3; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #0d47a1;">멀티스레딩:</strong> BackgroundWorker와 Task 활용</li>
        <li><strong style="color: #0d47a1;">통신 프로토콜:</strong> TCP/IP, SignalR 실시간 통신</li>
        <li><strong style="color: #0d47a1;">데이터 시각화:</strong> 실시간 차트와 그래프</li>
        <li><strong style="color: #0d47a1;">성능 최적화:</strong> 대용량 데이터 처리 기법</li>
    </ul>
</div>

### 📚 과제 및 복습

<div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #f39c12; margin: 1.5rem 0;">
    <p style="margin: 0; color: #856404; font-weight: 500; font-size: 1.1em;">
        💡 오늘 구현한 HMI 시스템에 알람 히스토리 기능을 추가해보세요.
    </p>
</div>

</div>

---

---

## 실습 1: WPF 성능 프로파일링 및 최적화

### 실습 목표
- WPF 애플리케이션의 성능 병목지점 식별
- 메모리 사용량과 CPU 사용률 최적화
- 실시간 모니터링 시스템의 성능 튜닝
- Visual Studio Diagnostic Tools 활용

### 성능 측정 도구 설정

#### Visual Studio Performance Profiler
```csharp
using System.Diagnostics;
using System.Windows;
using System.Windows.Threading;

public partial class PerformanceMonitor : Window
{
    private DispatcherTimer _performanceTimer;
    private Process _currentProcess;
    private PerformanceCounter _cpuCounter;
    private PerformanceCounter _memoryCounter;

    public PerformanceMonitor()
    {
        InitializeComponent();
        InitializePerformanceMonitoring();
    }

    private void InitializePerformanceMonitoring()
    {
        _currentProcess = Process.GetCurrentProcess();

        // CPU 성능 카운터 설정
        _cpuCounter = new PerformanceCounter("Process", "% Processor Time",
                                           _currentProcess.ProcessName);

        // 메모리 성능 카운터 설정
        _memoryCounter = new PerformanceCounter("Process", "Working Set",
                                              _currentProcess.ProcessName);

        // 1초마다 성능 데이터 업데이트
        _performanceTimer = new DispatcherTimer
        {
            Interval = TimeSpan.FromSeconds(1)
        };
        _performanceTimer.Tick += UpdatePerformanceMetrics;
        _performanceTimer.Start();
    }

    private void UpdatePerformanceMetrics(object sender, EventArgs e)
    {
        try
        {
            // CPU 사용률 계산 (첫 번째 호출은 무시)
            _cpuCounter.NextValue();
            System.Threading.Thread.Sleep(10);
            float cpuUsage = _cpuCounter.NextValue();

            // 메모리 사용량 (바이트 -> MB 변환)
            float memoryUsage = _memoryCounter.NextValue() / (1024 * 1024);

            // GC 정보 수집
            int gen0Collections = GC.CollectionCount(0);
            int gen1Collections = GC.CollectionCount(1);
            int gen2Collections = GC.CollectionCount(2);
            long totalMemory = GC.GetTotalMemory(false) / (1024 * 1024);

            // UI 스레드에서 업데이트
            Dispatcher.Invoke(() =>
            {
                CpuUsageLabel.Content = $"CPU: {cpuUsage:F1}%";
                MemoryUsageLabel.Content = $"Memory: {memoryUsage:F1} MB";
                GcMemoryLabel.Content = $"GC Memory: {totalMemory} MB";
                GcCollectionsLabel.Content = $"GC: Gen0={gen0Collections}, Gen1={gen1Collections}, Gen2={gen2Collections}";

                // 성능 경고 표시
                if (cpuUsage > 80)
                {
                    CpuUsageLabel.Foreground = Brushes.Red;
                    ShowPerformanceWarning("High CPU Usage Detected!");
                }
                else
                {
                    CpuUsageLabel.Foreground = Brushes.Black;
                }

                if (memoryUsage > 500) // 500MB 초과 시 경고
                {
                    MemoryUsageLabel.Foreground = Brushes.Orange;
                    ShowPerformanceWarning("High Memory Usage Detected!");
                }
                else
                {
                    MemoryUsageLabel.Foreground = Brushes.Black;
                }
            });
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Performance monitoring error: {ex.Message}");
        }
    }

    private void ShowPerformanceWarning(string message)
    {
        WarningPanel.Visibility = Visibility.Visible;
        WarningText.Text = message;

        // 5초 후 경고 자동 숨김
        var hideTimer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(5) };
        hideTimer.Tick += (s, e) =>
        {
            WarningPanel.Visibility = Visibility.Collapsed;
            hideTimer.Stop();
        };
        hideTimer.Start();
    }

    protected override void OnClosed(EventArgs e)
    {
        _performanceTimer?.Stop();
        _cpuCounter?.Dispose();
        _memoryCounter?.Dispose();
        base.OnClosed(e);
    }
}
```

### 메모리 누수 탐지 및 해결

#### WeakEvent 패턴 구현
```csharp
using System;
using System.Runtime.CompilerServices;
using System.Windows;

// 메모리 누수를 방지하는 WeakEvent 구현
public static class WeakEventManager<T> where T : EventArgs
{
    private static readonly ConditionalWeakTable<object, List<WeakReference>> _eventHandlers
        = new ConditionalWeakTable<object, List<WeakReference>>();

    public static void AddHandler(object source, EventHandler<T> handler)
    {
        if (source == null || handler == null) return;

        var handlers = _eventHandlers.GetOrCreateValue(source);
        handlers.Add(new WeakReference(handler));
    }

    public static void RemoveHandler(object source, EventHandler<T> handler)
    {
        if (source == null || handler == null) return;

        if (_eventHandlers.TryGetValue(source, out var handlers))
        {
            for (int i = handlers.Count - 1; i >= 0; i--)
            {
                if (!handlers[i].IsAlive || handlers[i].Target.Equals(handler))
                {
                    handlers.RemoveAt(i);
                }
            }
        }
    }

    public static void RaiseEvent(object source, T eventArgs)
    {
        if (source == null) return;

        if (_eventHandlers.TryGetValue(source, out var handlers))
        {
            for (int i = handlers.Count - 1; i >= 0; i--)
            {
                if (handlers[i].IsAlive && handlers[i].Target is EventHandler<T> handler)
                {
                    try
                    {
                        handler(source, eventArgs);
                    }
                    catch (Exception ex)
                    {
                        // 이벤트 핸들러 오류 로깅
                        Debug.WriteLine($"Event handler error: {ex.Message}");
                    }
                }
                else
                {
                    // 죽은 참조 제거
                    handlers.RemoveAt(i);
                }
            }
        }
    }
}

// 사용 예제: 메모리 누수 방지 데이터 서비스
public class MemoryEfficientDataService : IDisposable
{
    public event EventHandler<DataChangedEventArgs> DataChanged;

    private readonly Timer _updateTimer;
    private readonly List<SensorData> _sensorData;
    private bool _disposed = false;

    public MemoryEfficientDataService()
    {
        _sensorData = new List<SensorData>();
        _updateTimer = new Timer(UpdateSensorData, null, TimeSpan.Zero, TimeSpan.FromSeconds(1));
    }

    private void UpdateSensorData(object state)
    {
        try
        {
            // 센서 데이터 업데이트 시뮬레이션
            var newData = new SensorData
            {
                Timestamp = DateTime.Now,
                Temperature = Random.Shared.NextDouble() * 100,
                Pressure = Random.Shared.NextDouble() * 10,
                FlowRate = Random.Shared.NextDouble() * 200
            };

            // 메모리 효율을 위해 최근 1000개 데이터만 유지
            if (_sensorData.Count >= 1000)
            {
                _sensorData.RemoveAt(0);
            }
            _sensorData.Add(newData);

            // WeakEvent를 사용한 안전한 이벤트 발생
            WeakEventManager<DataChangedEventArgs>.RaiseEvent(
                this, new DataChangedEventArgs(newData));
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Data update error: {ex.Message}");
        }
    }

    public void Dispose()
    {
        if (!_disposed)
        {
            _updateTimer?.Dispose();
            _sensorData?.Clear();
            _disposed = true;
        }
        GC.SuppressFinalize(this);
    }
}

public class DataChangedEventArgs : EventArgs
{
    public SensorData Data { get; }

    public DataChangedEventArgs(SensorData data)
    {
        Data = data;
    }
}
```

### UI 가상화 구현

#### 대용량 데이터를 위한 가상화 ListView
```xml
<!-- XAML: 가상화가 적용된 ListView -->
<ListView x:Name="SensorDataListView"
          ItemsSource="{Binding SensorDataCollection}"
          VirtualizingPanel.IsVirtualizing="True"
          VirtualizingPanel.VirtualizationMode="Recycling"
          VirtualizingPanel.ScrollUnit="Item"
          ScrollViewer.CanContentScroll="True"
          Height="300">
    <ListView.View>
        <GridView>
            <GridViewColumn Header="시간"
                          DisplayMemberBinding="{Binding Timestamp, StringFormat='{0:HH:mm:ss}'}"
                          Width="100"/>
            <GridViewColumn Header="온도 (°C)"
                          DisplayMemberBinding="{Binding Temperature, StringFormat='{0:F1}'}"
                          Width="100"/>
            <GridViewColumn Header="압력 (Torr)"
                          DisplayMemberBinding="{Binding Pressure, StringFormat='{0:F2}'}"
                          Width="100"/>
            <GridViewColumn Header="유량 (sccm)"
                          DisplayMemberBinding="{Binding FlowRate, StringFormat='{0:F0}'}"
                          Width="100"/>
        </GridView>
    </ListView.View>

    <!-- 커스텀 ItemContainer 스타일 -->
    <ListView.ItemContainerStyle>
        <Style TargetType="ListViewItem">
            <Setter Property="HorizontalContentAlignment" Value="Center"/>
            <Style.Triggers>
                <!-- 온도가 80도 이상이면 빨간색으로 표시 -->
                <DataTrigger Binding="{Binding Temperature, Converter={StaticResource HighTemperatureConverter}}"
                           Value="True">
                    <Setter Property="Foreground" Value="Red"/>
                    <Setter Property="FontWeight" Value="Bold"/>
                </DataTrigger>
            </Style.Triggers>
        </Style>
    </ListView.ItemContainerStyle>
</ListView>
```

```csharp
// ViewModel: 성능 최적화된 컬렉션 관리
public class OptimizedSensorViewModel : ViewModelBase
{
    private readonly ObservableCollection<SensorDataViewModel> _sensorDataCollection;
    private readonly MemoryEfficientDataService _dataService;

    public ObservableCollection<SensorDataViewModel> SensorDataCollection
    {
        get => _sensorDataCollection;
    }

    public OptimizedSensorViewModel()
    {
        _sensorDataCollection = new ObservableCollection<SensorDataViewModel>();
        _dataService = new MemoryEfficientDataService();

        // WeakEvent 패턴 사용
        WeakEventManager<DataChangedEventArgs>.AddHandler(
            _dataService, OnDataChanged);
    }

    private void OnDataChanged(object sender, DataChangedEventArgs e)
    {
        // UI 스레드에서 실행되도록 보장
        Application.Current.Dispatcher.BeginInvoke(new Action(() =>
        {
            var viewModel = new SensorDataViewModel(e.Data);

            // 성능을 위해 컬렉션 크기 제한
            if (_sensorDataCollection.Count >= 1000)
            {
                _sensorDataCollection.RemoveAt(0);
            }

            _sensorDataCollection.Add(viewModel);

            // 자동 스크롤 (최신 데이터로)
            if (_sensorDataCollection.Count > 0)
            {
                var listView = Application.Current.MainWindow
                    ?.FindName("SensorDataListView") as ListView;
                listView?.ScrollIntoView(_sensorDataCollection.Last());
            }
        }), DispatcherPriority.Background);
    }

    protected override void OnDispose()
    {
        WeakEventManager<DataChangedEventArgs>.RemoveHandler(
            _dataService, OnDataChanged);
        _dataService?.Dispose();
        base.OnDispose();
    }
}

public class SensorDataViewModel : ViewModelBase
{
    private readonly SensorData _model;

    public DateTime Timestamp => _model.Timestamp;
    public double Temperature => _model.Temperature;
    public double Pressure => _model.Pressure;
    public double FlowRate => _model.FlowRate;

    // 성능을 위해 계산 속성 캐싱
    private bool? _isHighTemperature;
    public bool IsHighTemperature
    {
        get
        {
            _isHighTemperature ??= Temperature > 80.0;
            return _isHighTemperature.Value;
        }
    }

    public SensorDataViewModel(SensorData model)
    {
        _model = model ?? throw new ArgumentNullException(nameof(model));
    }
}

// 고온 판별 컨버터
public class HighTemperatureConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        if (value is double temperature)
        {
            return temperature > 80.0;
        }
        return false;
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
    {
        throw new NotImplementedException();
    }
}
```

---

## 실습 2: 고급 데이터 바인딩 및 검증

### 실습 목표
- IDataErrorInfo와 INotifyDataErrorInfo 구현
- 비동기 검증 로직 구현
- 복합 검증 규칙과 종속성 검증
- 실시간 입력 값 검증 시스템

### 고급 입력 검증 시스템

#### 다계층 검증 아키텍처
```csharp
using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;

// 고급 검증을 위한 베이스 클래스
public abstract class ValidatableViewModelBase : ViewModelBase, INotifyDataErrorInfo
{
    private readonly Dictionary<string, List<string>> _validationErrors
        = new Dictionary<string, List<string>>();

    private readonly Dictionary<string, List<ValidationRule>> _validationRules
        = new Dictionary<string, List<ValidationRule>>();

    public bool HasErrors => _validationErrors.Count > 0;

    public event EventHandler<DataErrorsChangedEventArgs> ErrorsChanged;

    protected ValidatableViewModelBase()
    {
        InitializeValidationRules();
    }

    protected abstract void InitializeValidationRules();

    protected void AddValidationRule(string propertyName, ValidationRule rule)
    {
        if (!_validationRules.ContainsKey(propertyName))
        {
            _validationRules[propertyName] = new List<ValidationRule>();
        }
        _validationRules[propertyName].Add(rule);
    }

    protected override bool SetProperty<T>(ref T field, T value, [CallerMemberName] string propertyName = null)
    {
        if (base.SetProperty(ref field, value, propertyName))
        {
            // 속성 변경 시 즉시 검증 실행
            ValidateProperty(propertyName, value);
            return true;
        }
        return false;
    }

    protected async Task<bool> ValidatePropertyAsync<T>(T value, [CallerMemberName] string propertyName = null)
    {
        return await Task.Run(() => ValidateProperty(propertyName, value));
    }

    protected bool ValidateProperty<T>(string propertyName, T value)
    {
        if (_validationRules.ContainsKey(propertyName))
        {
            var errors = new List<string>();

            foreach (var rule in _validationRules[propertyName])
            {
                var result = rule.Validate(value);
                if (!result.IsValid)
                {
                    errors.Add(result.ErrorMessage);
                }
            }

            SetErrors(propertyName, errors);
            return errors.Count == 0;
        }

        return true;
    }

    protected void SetErrors(string propertyName, IEnumerable<string> errors)
    {
        var errorList = errors?.ToList() ?? new List<string>();

        if (errorList.Count == 0)
        {
            if (_validationErrors.Remove(propertyName))
            {
                OnErrorsChanged(propertyName);
            }
        }
        else
        {
            _validationErrors[propertyName] = errorList;
            OnErrorsChanged(propertyName);
        }
    }

    public IEnumerable GetErrors(string propertyName)
    {
        if (string.IsNullOrEmpty(propertyName))
        {
            return _validationErrors.Values.SelectMany(x => x);
        }

        return _validationErrors.ContainsKey(propertyName)
            ? _validationErrors[propertyName]
            : Enumerable.Empty<string>();
    }

    protected virtual void OnErrorsChanged([CallerMemberName] string propertyName = null)
    {
        ErrorsChanged?.Invoke(this, new DataErrorsChangedEventArgs(propertyName));
        OnPropertyChanged(nameof(HasErrors));
    }

    public async Task<bool> ValidateAllPropertiesAsync()
    {
        var isValid = true;
        var validationTasks = new List<Task<bool>>();

        foreach (var propertyName in _validationRules.Keys)
        {
            var property = GetType().GetProperty(propertyName);
            if (property != null)
            {
                var value = property.GetValue(this);
                validationTasks.Add(ValidatePropertyAsync(value, propertyName));
            }
        }

        var results = await Task.WhenAll(validationTasks);
        return results.All(x => x);
    }
}

// 검증 규칙 정의
public abstract class ValidationRule
{
    public abstract ValidationResult Validate(object value);
}

public class ValidationResult
{
    public bool IsValid { get; set; }
    public string ErrorMessage { get; set; }

    public static ValidationResult Success => new ValidationResult { IsValid = true };

    public static ValidationResult Error(string message) =>
        new ValidationResult { IsValid = false, ErrorMessage = message };
}

// 구체적인 검증 규칙들
public class RangeValidationRule : ValidationRule
{
    public double MinValue { get; set; }
    public double MaxValue { get; set; }
    public string Unit { get; set; }

    public RangeValidationRule(double min, double max, string unit = "")
    {
        MinValue = min;
        MaxValue = max;
        Unit = unit;
    }

    public override ValidationResult Validate(object value)
    {
        if (value == null || !double.TryParse(value.ToString(), out double numericValue))
        {
            return ValidationResult.Error("숫자 값이 필요합니다.");
        }

        if (numericValue < MinValue || numericValue > MaxValue)
        {
            return ValidationResult.Error(
                $"값은 {MinValue}-{MaxValue} {Unit} 범위 내에 있어야 합니다.");
        }

        return ValidationResult.Success;
    }
}

public class RequiredValidationRule : ValidationRule
{
    public override ValidationResult Validate(object value)
    {
        if (value == null || string.IsNullOrWhiteSpace(value.ToString()))
        {
            return ValidationResult.Error("필수 입력 항목입니다.");
        }

        return ValidationResult.Success;
    }
}

public class RegexValidationRule : ValidationRule
{
    private readonly Regex _regex;
    private readonly string _errorMessage;

    public RegexValidationRule(string pattern, string errorMessage)
    {
        _regex = new Regex(pattern);
        _errorMessage = errorMessage;
    }

    public override ValidationResult Validate(object value)
    {
        var stringValue = value?.ToString() ?? string.Empty;

        if (!_regex.IsMatch(stringValue))
        {
            return ValidationResult.Error(_errorMessage);
        }

        return ValidationResult.Success;
    }
}

// 비동기 검증 규칙
public class AsyncDatabaseValidationRule : ValidationRule
{
    private readonly Func<object, Task<bool>> _validateFunc;
    private readonly string _errorMessage;

    public AsyncDatabaseValidationRule(Func<object, Task<bool>> validateFunc, string errorMessage)
    {
        _validateFunc = validateFunc;
        _errorMessage = errorMessage;
    }

    public override ValidationResult Validate(object value)
    {
        // 동기적 호출을 위해 Task.Run 사용 (실제로는 비동기 검증 메서드 별도 구현 권장)
        var isValid = Task.Run(() => _validateFunc(value)).GetAwaiter().GetResult();

        return isValid ? ValidationResult.Success : ValidationResult.Error(_errorMessage);
    }
}
```

### 반도체 장비 설정 검증 예제

```csharp
// 반도체 공정 파라미터 검증 ViewModel
public class ProcessParameterViewModel : ValidatableViewModelBase
{
    private string _recipeName;
    private double _temperature;
    private double _pressure;
    private double _gasFlowRate;
    private int _processTime;
    private string _operatorId;

    // Recipe 이름
    public string RecipeName
    {
        get => _recipeName;
        set => SetProperty(ref _recipeName, value);
    }

    // 온도 (°C)
    public double Temperature
    {
        get => _temperature;
        set => SetProperty(ref _temperature, value);
    }

    // 압력 (Torr)
    public double Pressure
    {
        get => _pressure;
        set => SetProperty(ref _pressure, value);
    }

    // 가스 유량 (sccm)
    public double GasFlowRate
    {
        get => _gasFlowRate;
        set => SetProperty(ref _gasFlowRate, value);
    }

    // 공정 시간 (초)
    public int ProcessTime
    {
        get => _processTime;
        set => SetProperty(ref _processTime, value);
    }

    // 운영자 ID
    public string OperatorId
    {
        get => _operatorId;
        set => SetProperty(ref _operatorId, value);
    }

    protected override void InitializeValidationRules()
    {
        // Recipe 이름 검증
        AddValidationRule(nameof(RecipeName), new RequiredValidationRule());
        AddValidationRule(nameof(RecipeName), new RegexValidationRule(
            @"^[A-Z][A-Za-z0-9_]{2,19}$",
            "Recipe 이름은 대문자로 시작하고 3-20자의 영문, 숫자, 언더스코어만 사용 가능합니다."));

        // 온도 검증 (CVD 공정 기준)
        AddValidationRule(nameof(Temperature), new RangeValidationRule(200, 800, "°C"));

        // 압력 검증
        AddValidationRule(nameof(Pressure), new RangeValidationRule(0.1, 100, "Torr"));

        // 가스 유량 검증
        AddValidationRule(nameof(GasFlowRate), new RangeValidationRule(10, 500, "sccm"));

        // 공정 시간 검증
        AddValidationRule(nameof(ProcessTime), new RangeValidationRule(60, 7200, "초"));

        // 운영자 ID 검증 (비동기 데이터베이스 검증)
        AddValidationRule(nameof(OperatorId), new RequiredValidationRule());
        AddValidationRule(nameof(OperatorId), new AsyncDatabaseValidationRule(
            async operatorId => await ValidateOperatorInDatabaseAsync(operatorId.ToString()),
            "존재하지 않는 운영자 ID이거나 권한이 없습니다."));
    }

    private async Task<bool> ValidateOperatorInDatabaseAsync(string operatorId)
    {
        // 실제 환경에서는 데이터베이스 조회
        await Task.Delay(100); // 네트워크 지연 시뮬레이션

        // 시뮬레이션: 특정 ID들만 유효하다고 가정
        var validOperators = new[] { "OP001", "OP002", "OP003", "ADMIN" };
        return validOperators.Contains(operatorId);
    }

    // 종속성 검증: 온도와 압력의 조합 검증
    protected override void OnPropertyChanged([CallerMemberName] string propertyName = null)
    {
        base.OnPropertyChanged(propertyName);

        // 온도나 압력 변경 시 조합 검증 실행
        if (propertyName == nameof(Temperature) || propertyName == nameof(Pressure))
        {
            ValidateTemperaturePressureCombination();
        }
    }

    private void ValidateTemperaturePressureCombination()
    {
        var errors = new List<string>();

        // CVD 공정 특성: 고온에서는 저압 유지 필요
        if (Temperature > 600 && Pressure > 10)
        {
            errors.Add("고온 공정(>600°C)에서는 압력이 10 Torr 이하여야 합니다.");
        }

        // 저온에서는 충분한 압력 필요
        if (Temperature < 300 && Pressure < 1)
        {
            errors.Add("저온 공정(<300°C)에서는 압력이 1 Torr 이상이어야 합니다.");
        }

        SetErrors("TemperaturePressureCombination", errors);
    }

    // 전체 파라미터 유효성 검사
    public async Task<bool> IsValidForProcessStartAsync()
    {
        var isBasicValid = await ValidateAllPropertiesAsync();

        // 추가 비즈니스 로직 검증
        ValidateTemperaturePressureCombination();

        return isBasicValid && !HasErrors;
    }
}
```

### XAML UI 바인딩

```xml
<!-- 고급 검증이 적용된 입력 폼 -->
<Grid Margin="20">
    <Grid.RowDefinitions>
        <RowDefinition Height="Auto"/>
        <RowDefinition Height="Auto"/>
        <RowDefinition Height="Auto"/>
        <RowDefinition Height="Auto"/>
        <RowDefinition Height="Auto"/>
        <RowDefinition Height="Auto"/>
        <RowDefinition Height="Auto"/>
        <RowDefinition Height="*"/>
    </Grid.RowDefinitions>

    <Grid.ColumnDefinitions>
        <ColumnDefinition Width="150"/>
        <ColumnDefinition Width="200"/>
        <ColumnDefinition Width="*"/>
    </Grid.ColumnDefinitions>

    <!-- Recipe 이름 -->
    <Label Grid.Row="0" Grid.Column="0" Content="Recipe 이름:" VerticalAlignment="Center"/>
    <TextBox Grid.Row="0" Grid.Column="1"
             Text="{Binding RecipeName, UpdateSourceTrigger=PropertyChanged, ValidatesOnNotifyDataErrors=True}"
             Margin="5"/>
    <TextBlock Grid.Row="0" Grid.Column="2"
               Text="{Binding (Validation.Errors)[0].ErrorContent, RelativeSource={RelativeSource PreviousData}}"
               Foreground="Red" VerticalAlignment="Center" Margin="5"/>

    <!-- 온도 -->
    <Label Grid.Row="1" Grid.Column="0" Content="온도 (°C):" VerticalAlignment="Center"/>
    <TextBox Grid.Row="1" Grid.Column="1"
             Text="{Binding Temperature, UpdateSourceTrigger=PropertyChanged, ValidatesOnNotifyDataErrors=True}"
             Margin="5"/>
    <StackPanel Grid.Row="1" Grid.Column="2" Orientation="Vertical" Margin="5">
        <TextBlock Text="{Binding (Validation.Errors)[0].ErrorContent, RelativeSource={RelativeSource PreviousData}}"
                   Foreground="Red"/>
        <TextBlock Text="권장 범위: 200-800°C" FontSize="10" Foreground="Gray"/>
    </StackPanel>

    <!-- 압력 -->
    <Label Grid.Row="2" Grid.Column="0" Content="압력 (Torr):" VerticalAlignment="Center"/>
    <TextBox Grid.Row="2" Grid.Column="1"
             Text="{Binding Pressure, UpdateSourceTrigger=PropertyChanged, ValidatesOnNotifyDataErrors=True}"
             Margin="5"/>
    <StackPanel Grid.Row="2" Grid.Column="2" Orientation="Vertical" Margin="5">
        <TextBlock Text="{Binding (Validation.Errors)[0].ErrorContent, RelativeSource={RelativeSource PreviousData}}"
                   Foreground="Red"/>
        <TextBlock Text="권장 범위: 0.1-100 Torr" FontSize="10" Foreground="Gray"/>
    </StackPanel>

    <!-- 가스 유량 -->
    <Label Grid.Row="3" Grid.Column="0" Content="가스 유량 (sccm):" VerticalAlignment="Center"/>
    <TextBox Grid.Row="3" Grid.Column="1"
             Text="{Binding GasFlowRate, UpdateSourceTrigger=PropertyChanged, ValidatesOnNotifyDataErrors=True}"
             Margin="5"/>
    <TextBlock Grid.Row="3" Grid.Column="2"
               Text="{Binding (Validation.Errors)[0].ErrorContent, RelativeSource={RelativeSource PreviousData}}"
               Foreground="Red" VerticalAlignment="Center" Margin="5"/>

    <!-- 공정 시간 -->
    <Label Grid.Row="4" Grid.Column="0" Content="공정 시간 (초):" VerticalAlignment="Center"/>
    <TextBox Grid.Row="4" Grid.Column="1"
             Text="{Binding ProcessTime, UpdateSourceTrigger=PropertyChanged, ValidatesOnNotifyDataErrors=True}"
             Margin="5"/>
    <TextBlock Grid.Row="4" Grid.Column="2"
               Text="{Binding (Validation.Errors)[0].ErrorContent, RelativeSource={RelativeSource PreviousData}}"
               Foreground="Red" VerticalAlignment="Center" Margin="5"/>

    <!-- 운영자 ID -->
    <Label Grid.Row="5" Grid.Column="0" Content="운영자 ID:" VerticalAlignment="Center"/>
    <TextBox Grid.Row="5" Grid.Column="1"
             Text="{Binding OperatorId, UpdateSourceTrigger=PropertyChanged, ValidatesOnNotifyDataErrors=True}"
             Margin="5"/>
    <TextBlock Grid.Row="5" Grid.Column="2"
               Text="{Binding (Validation.Errors)[0].ErrorContent, RelativeSource={RelativeSource PreviousData}}"
               Foreground="Red" VerticalAlignment="Center" Margin="5"/>

    <!-- 조합 검증 오류 표시 -->
    <Border Grid.Row="6" Grid.ColumnSpan="3"
            Background="LightPink"
            Visibility="{Binding HasErrors, Converter={StaticResource BooleanToVisibilityConverter}}"
            Margin="5" Padding="10" CornerRadius="5">
        <StackPanel>
            <TextBlock Text="검증 오류:" FontWeight="Bold" Foreground="DarkRed"/>
            <ItemsControl ItemsSource="{Binding (Validation.Errors), RelativeSource={RelativeSource Self}}">
                <ItemsControl.ItemTemplate>
                    <DataTemplate>
                        <TextBlock Text="{Binding ErrorContent}" Foreground="DarkRed" Margin="0,2"/>
                    </DataTemplate>
                </ItemsControl.ItemTemplate>
            </ItemsControl>
        </StackPanel>
    </Border>

    <!-- 제어 버튼 -->
    <StackPanel Grid.Row="7" Grid.ColumnSpan="3" Orientation="Horizontal" HorizontalAlignment="Center" Margin="20">
        <Button Content="공정 시작"
                Command="{Binding StartProcessCommand}"
                IsEnabled="{Binding HasErrors, Converter={StaticResource InverseBooleanConverter}}"
                Padding="20,10" Margin="10"/>
        <Button Content="리셋"
                Command="{Binding ResetCommand}"
                Padding="20,10" Margin="10"/>
        <Button Content="저장"
                Command="{Binding SaveCommand}"
                Padding="20,10" Margin="10"/>
    </StackPanel>
</Grid>
```

---

## 실습 3: 멀티스레딩과 비동기 프로그래밍

### 실습 목표
- Task와 async/await 패턴 마스터
- ConfigureAwait(false) 올바른 사용법
- CancellationToken을 통한 작업 취소
- 스레드 안전 컬렉션 활용
- UI 스레드와 백그라운드 작업 분리

### 비동기 데이터 처리 시스템

```csharp
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Threading;

// 고성능 비동기 데이터 처리 서비스
public class AsyncDataProcessingService : IDisposable
{
    private readonly ConcurrentQueue<SensorReading> _dataQueue;
    private readonly ConcurrentBag<ProcessedData> _processedResults;
    private readonly SemaphoreSlim _processingLock;
    private readonly CancellationTokenSource _cancellationTokenSource;

    private Task _processingTask;
    private readonly DispatcherTimer _uiUpdateTimer;

    public event EventHandler<DataProcessedEventArgs> DataProcessed;
    public event EventHandler<ProcessingStatsEventArgs> StatsUpdated;

    private int _totalProcessed = 0;
    private int _errorCount = 0;
    private DateTime _lastProcessingTime = DateTime.Now;

    public AsyncDataProcessingService()
    {
        _dataQueue = new ConcurrentQueue<SensorReading>();
        _processedResults = new ConcurrentBag<ProcessedData>();
        _processingLock = new SemaphoreSlim(Environment.ProcessorCount); // CPU 코어 수만큼 동시 처리
        _cancellationTokenSource = new CancellationTokenSource();

        // UI 업데이트 타이머 (UI 스레드에서 실행)
        _uiUpdateTimer = new DispatcherTimer
        {
            Interval = TimeSpan.FromMilliseconds(100) // 100ms마다 UI 업데이트
        };
        _uiUpdateTimer.Tick += OnUiUpdateTimer;
        _uiUpdateTimer.Start();

        // 백그라운드 처리 태스크 시작
        _processingTask = StartProcessingAsync(_cancellationTokenSource.Token);
    }

    public async Task EnqueueDataAsync(SensorReading reading)
    {
        _dataQueue.Enqueue(reading);

        // 큐가 너무 커지면 백프레셔 적용
        if (_dataQueue.Count > 10000)
        {
            await Task.Delay(10, _cancellationTokenSource.Token).ConfigureAwait(false);
        }
    }

    private async Task StartProcessingAsync(CancellationToken cancellationToken)
    {
        var processingTasks = new List<Task>();

        // 여러 개의 처리 워커 시작
        for (int i = 0; i < Environment.ProcessorCount; i++)
        {
            processingTasks.Add(ProcessDataWorkerAsync(cancellationToken));
        }

        try
        {
            await Task.WhenAll(processingTasks).ConfigureAwait(false);
        }
        catch (OperationCanceledException)
        {
            // 정상 종료
        }
        catch (Exception ex)
        {
            // 오류 로깅
            System.Diagnostics.Debug.WriteLine($"Processing error: {ex.Message}");
        }
    }

    private async Task ProcessDataWorkerAsync(CancellationToken cancellationToken)
    {
        while (!cancellationToken.IsCancellationRequested)
        {
            try
            {
                if (_dataQueue.TryDequeue(out var reading))
                {
                    await _processingLock.WaitAsync(cancellationToken).ConfigureAwait(false);

                    try
                    {
                        var processedData = await ProcessSensorReadingAsync(reading, cancellationToken)
                            .ConfigureAwait(false);

                        _processedResults.Add(processedData);

                        Interlocked.Increment(ref _totalProcessed);
                        _lastProcessingTime = DateTime.Now;

                        // UI 스레드로 이벤트 발생 (ConfigureAwait(false) 주의)
                        await Application.Current.Dispatcher.BeginInvoke(new Action(() =>
                        {
                            DataProcessed?.Invoke(this, new DataProcessedEventArgs(processedData));
                        })).Task.ConfigureAwait(false);
                    }
                    finally
                    {
                        _processingLock.Release();
                    }
                }
                else
                {
                    // 큐가 비어있으면 잠시 대기
                    await Task.Delay(10, cancellationToken).ConfigureAwait(false);
                }
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch (Exception ex)
            {
                Interlocked.Increment(ref _errorCount);
                System.Diagnostics.Debug.WriteLine($"Data processing error: {ex.Message}");

                // 오류 발생 시 잠시 대기 후 계속
                await Task.Delay(100, cancellationToken).ConfigureAwait(false);
            }
        }
    }

    private async Task<ProcessedData> ProcessSensorReadingAsync(SensorReading reading,
                                                               CancellationToken cancellationToken)
    {
        // CPU 집약적 처리 시뮬레이션
        await Task.Run(() =>
        {
            // 복잡한 계산 시뮬레이션
            var random = new Random();
            for (int i = 0; i < 1000; i++)
            {
                cancellationToken.ThrowIfCancellationRequested();
                Math.Sin(random.NextDouble() * Math.PI);
            }
        }, cancellationToken).ConfigureAwait(false);

        // 실제 데이터 처리 로직
        var processedData = new ProcessedData
        {
            OriginalReading = reading,
            ProcessedTimestamp = DateTime.Now,
            ProcessedValue = ApplyFiltering(reading.RawValue),
            QualityScore = CalculateQualityScore(reading),
            Anomalies = await DetectAnomaliesAsync(reading, cancellationToken).ConfigureAwait(false)
        };

        return processedData;
    }

    private double ApplyFiltering(double rawValue)
    {
        // 간단한 노이즈 필터링 (이동 평균 등)
        return rawValue * 0.95 + (rawValue * 0.05 * new Random().NextDouble());
    }

    private double CalculateQualityScore(SensorReading reading)
    {
        // 데이터 품질 점수 계산 (0.0 ~ 1.0)
        var ageSeconds = (DateTime.Now - reading.Timestamp).TotalSeconds;
        var ageFactor = Math.Max(0, 1 - ageSeconds / 300); // 5분 후 0점

        var valueFactor = reading.RawValue > 0 ? 1.0 : 0.5;

        return ageFactor * valueFactor;
    }

    private async Task<List<string>> DetectAnomaliesAsync(SensorReading reading,
                                                         CancellationToken cancellationToken)
    {
        var anomalies = new List<string>();

        // 비동기 이상 감지 알고리즘
        await Task.Run(() =>
        {
            if (reading.RawValue > 1000)
            {
                anomalies.Add("High value detected");
            }

            if (reading.RawValue < -1000)
            {
                anomalies.Add("Low value detected");
            }

            // 추가 복잡한 패턴 분석...

        }, cancellationToken).ConfigureAwait(false);

        return anomalies;
    }

    private void OnUiUpdateTimer(object sender, EventArgs e)
    {
        // UI 스레드에서 통계 업데이트
        var stats = new ProcessingStatsEventArgs
        {
            TotalProcessed = _totalProcessed,
            ErrorCount = _errorCount,
            QueueLength = _dataQueue.Count,
            ProcessedResultsCount = _processedResults.Count,
            LastProcessingTime = _lastProcessingTime,
            ProcessingRate = CalculateProcessingRate()
        };

        StatsUpdated?.Invoke(this, stats);
    }

    private double CalculateProcessingRate()
    {
        // 초당 처리량 계산
        var elapsed = (DateTime.Now - _lastProcessingTime).TotalSeconds;
        return elapsed > 0 ? _totalProcessed / elapsed : 0;
    }

    public async Task<List<ProcessedData>> GetProcessedDataAsync(int maxCount = 1000)
    {
        return await Task.Run(() =>
        {
            var results = new List<ProcessedData>();
            var count = 0;

            while (_processedResults.TryTake(out var result) && count < maxCount)
            {
                results.Add(result);
                count++;
            }

            return results;
        }).ConfigureAwait(false);
    }

    public async Task StopAsync()
    {
        _uiUpdateTimer?.Stop();
        _cancellationTokenSource?.Cancel();

        if (_processingTask != null)
        {
            try
            {
                await _processingTask.ConfigureAwait(false);
            }
            catch (OperationCanceledException)
            {
                // 정상 종료
            }
        }
    }

    public void Dispose()
    {
        Task.Run(async () => await StopAsync()).Wait(5000); // 최대 5초 대기

        _cancellationTokenSource?.Dispose();
        _processingLock?.Dispose();
        _uiUpdateTimer?.Stop();
    }
}

// 데이터 모델들
public class SensorReading
{
    public string SensorId { get; set; }
    public DateTime Timestamp { get; set; }
    public double RawValue { get; set; }
    public string Unit { get; set; }
}

public class ProcessedData
{
    public SensorReading OriginalReading { get; set; }
    public DateTime ProcessedTimestamp { get; set; }
    public double ProcessedValue { get; set; }
    public double QualityScore { get; set; }
    public List<string> Anomalies { get; set; }
}

// 이벤트 인자들
public class DataProcessedEventArgs : EventArgs
{
    public ProcessedData ProcessedData { get; }

    public DataProcessedEventArgs(ProcessedData data)
    {
        ProcessedData = data;
    }
}

public class ProcessingStatsEventArgs : EventArgs
{
    public int TotalProcessed { get; set; }
    public int ErrorCount { get; set; }
    public int QueueLength { get; set; }
    public int ProcessedResultsCount { get; set; }
    public DateTime LastProcessingTime { get; set; }
    public double ProcessingRate { get; set; }
}
```

### 비동기 처리를 위한 ViewModel

```csharp
public class AsyncProcessingViewModel : ViewModelBase
{
    private readonly AsyncDataProcessingService _processingService;
    private readonly Timer _dataGenerationTimer;

    private int _totalProcessed;
    private int _errorCount;
    private int _queueLength;
    private double _processingRate;
    private bool _isProcessing;

    public int TotalProcessed
    {
        get => _totalProcessed;
        private set => SetProperty(ref _totalProcessed, value);
    }

    public int ErrorCount
    {
        get => _errorCount;
        private set => SetProperty(ref _errorCount, value);
    }

    public int QueueLength
    {
        get => _queueLength;
        private set => SetProperty(ref _queueLength, value);
    }

    public double ProcessingRate
    {
        get => _processingRate;
        private set => SetProperty(ref _processingRate, value);
    }

    public bool IsProcessing
    {
        get => _isProcessing;
        private set => SetProperty(ref _isProcessing, value);
    }

    public ObservableCollection<ProcessedDataViewModel> ProcessedDataList { get; }

    public ICommand StartProcessingCommand { get; }
    public ICommand StopProcessingCommand { get; }
    public ICommand ClearDataCommand { get; }

    public AsyncProcessingViewModel()
    {
        ProcessedDataList = new ObservableCollection<ProcessedDataViewModel>();

        _processingService = new AsyncDataProcessingService();
        _processingService.DataProcessed += OnDataProcessed;
        _processingService.StatsUpdated += OnStatsUpdated;

        StartProcessingCommand = new RelayCommand(async () => await StartProcessingAsync());
        StopProcessingCommand = new RelayCommand(async () => await StopProcessingAsync());
        ClearDataCommand = new RelayCommand(ClearData);

        // 테스트 데이터 생성 타이머
        _dataGenerationTimer = new Timer(GenerateTestData, null,
            TimeSpan.FromMilliseconds(100), TimeSpan.FromMilliseconds(100));
    }

    private async Task StartProcessingAsync()
    {
        IsProcessing = true;

        // UI 반응성을 위해 ConfigureAwait(false) 사용하지 않음 (UI 컨텍스트에서 호출되므로)
        await Task.Run(async () =>
        {
            // 백그라운드에서 처리 시작
            for (int i = 0; i < 1000; i++) // 1000개의 테스트 데이터 생성
            {
                var reading = new SensorReading
                {
                    SensorId = $"SENSOR_{i % 10:D2}",
                    Timestamp = DateTime.Now,
                    RawValue = new Random().NextDouble() * 2000 - 1000,
                    Unit = "°C"
                };

                await _processingService.EnqueueDataAsync(reading).ConfigureAwait(false);
                await Task.Delay(10).ConfigureAwait(false); // 10ms 간격
            }
        });
    }

    private async Task StopProcessingAsync()
    {
        IsProcessing = false;
        await _processingService.StopAsync();
    }

    private void ClearData()
    {
        ProcessedDataList.Clear();
        TotalProcessed = 0;
        ErrorCount = 0;
        QueueLength = 0;
        ProcessingRate = 0;
    }

    private void OnDataProcessed(object sender, DataProcessedEventArgs e)
    {
        // UI 스레드에서 실행됨 (Dispatcher.BeginInvoke로 호출됨)
        var viewModel = new ProcessedDataViewModel(e.ProcessedData);

        // 성능을 위해 최근 100개만 UI에 표시
        if (ProcessedDataList.Count >= 100)
        {
            ProcessedDataList.RemoveAt(0);
        }

        ProcessedDataList.Add(viewModel);
    }

    private void OnStatsUpdated(object sender, ProcessingStatsEventArgs e)
    {
        // UI 스레드에서 실행됨
        TotalProcessed = e.TotalProcessed;
        ErrorCount = e.ErrorCount;
        QueueLength = e.QueueLength;
        ProcessingRate = e.ProcessingRate;
    }

    private void GenerateTestData(object state)
    {
        if (!IsProcessing) return;

        // 테스트 데이터 생성
        Task.Run(async () =>
        {
            var reading = new SensorReading
            {
                SensorId = $"SENSOR_{new Random().Next(0, 10):D2}",
                Timestamp = DateTime.Now,
                RawValue = new Random().NextDouble() * 2000 - 1000,
                Unit = new Random().Next(0, 2) == 0 ? "°C" : "Torr"
            };

            await _processingService.EnqueueDataAsync(reading).ConfigureAwait(false);
        });
    }

    protected override void OnDispose()
    {
        _dataGenerationTimer?.Dispose();
        _processingService?.Dispose();
        base.OnDispose();
    }
}

public class ProcessedDataViewModel : ViewModelBase
{
    private readonly ProcessedData _model;

    public string SensorId => _model.OriginalReading.SensorId;
    public DateTime Timestamp => _model.ProcessedTimestamp;
    public double ProcessedValue => _model.ProcessedValue;
    public double QualityScore => _model.QualityScore;
    public string Anomalies => string.Join(", ", _model.Anomalies);
    public bool HasAnomalies => _model.Anomalies?.Count > 0;

    public ProcessedDataViewModel(ProcessedData model)
    {
        _model = model ?? throw new ArgumentNullException(nameof(model));
    }
}
```

---

## ❓ 질의응답

<div style="margin: 2rem 0;">

<div style="background: #f8f9fa; padding: 2rem; border-radius: 8px; text-align: center; border: 2px dashed #6c757d;">
    <h3 style="color: #495057; margin: 0 0 1rem 0;">💬 질문해 주세요!</h3>
    <p style="margin: 0; color: #6c757d; font-style: italic;">
        C# WPF의 성능 최적화, 고급 데이터 바인딩, 비동기 프로그래밍에 대해<br>
        궁금한 점이 있으시면 언제든지 질문해 주세요.
    </p>
</div>

</div>