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

