# C# WPF 기초 및 MVVM 패턴
> 반도체 장비 HMI를 위한 Windows 기반 인터페이스 개발

---

## 📋 오늘의 학습 목표

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #007bff; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #1a365d;">.NET 아키텍처:</strong> WPF 프레임워크 구조와 렌더링 시스템 이해</li>
        <li><strong style="color: #1a365d;">XAML 마스터:</strong> 선언적 UI 개발과 데이터 바인딩 메커니즘</li>
        <li><strong style="color: #1a365d;">MVVM 패턴:</strong> 유지보수 가능한 HMI 애플리케이션 아키텍처</li>
        <li><strong style="color: #1a365d;">실무 적용:</strong> 반도체 장비 모니터링 시스템 기초 구현</li>
    </ul>
</div>

---

## 🗺️ 강의 진행 순서

<div style="display: flex; flex-direction: column; gap: 1rem; margin: 1.5rem 0;">
    <div style="display: flex; align-items: center; background: #e8f5e8; padding: 1rem; border-radius: 8px;">
        <div style="background: #28a745; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">1</div>
        <span style="color: #155724;"><strong>이론 (45분):</strong> .NET/WPF 아키텍처 및 MVVM 패턴</span>
    </div>
    <div style="display: flex; align-items: center; background: #e3f2fd; padding: 1rem; border-radius: 8px;">
        <div style="background: #2196f3; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">2</div>
        <span style="color: #0d47a1;"><strong>기초 실습 (45분):</strong> XAML 구조 및 데이터 바인딩</span>
    </div>
    <div style="display: flex; align-items: center; background: #f3e5f5; padding: 1rem; border-radius: 8px;">
        <div style="background: #9c27b0; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">3</div>
        <span style="color: #4a148c;"><strong>심화 실습 (45분):</strong> MVVM 패턴 구현</span>
    </div>
    <div style="display: flex; align-items: center; background: #fff3cd; padding: 1rem; border-radius: 8px;">
        <div style="background: #f39c12; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">4</div>
        <span style="color: #856404;"><strong>Hands-on (45분):</strong> 장비 모니터링 창 구현</span>
    </div>
</div>

---

# 📖 이론 강의 (45분)

---

## .NET 생태계 개요

<div style="margin: 2rem 0;">

### 🔧 .NET 발전 역사

<div style="background: #e3f2fd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2196f3; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #0d47a1;">.NET Framework (2002):</strong> Windows 전용, 완전한 기능셋</li>
        <li><strong style="color: #0d47a1;">.NET Core (2016):</strong> 크로스 플랫폼, 고성능, 오픈소스</li>
        <li><strong style="color: #0d47a1;">.NET 5+ (2020):</strong> 통합된 플랫폼, 단일 런타임</li>
        <li><strong style="color: #0d47a1;">.NET 6 LTS (2021):</strong> 장기 지원, 성능 최적화</li>
    </ul>
</div>

### ⚙️ CLR (Common Language Runtime)

<div style="background: #f3e5f5; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #9c27b0; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #4a148c;">JIT 컴파일:</strong> 런타임 시 네이티브 코드로 변환</li>
        <li><strong style="color: #4a148c;">가비지 컬렉션:</strong> 자동 메모리 관리</li>
        <li><strong style="color: #4a148c;">타입 안전성:</strong> 메모리 보호 및 오류 방지</li>
        <li><strong style="color: #4a148c;">예외 처리:</strong> 구조화된 오류 관리</li>
    </ul>
</div>

### 💡 반도체 환경에서의 .NET 장점

<div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #f39c12; margin: 1.5rem 0;">
    <p style="margin: 0; color: #856404; font-weight: 500; font-size: 1.1em;">
        ⚠️ 24/7 연속 운영 환경에서 메모리 누수 방지와 안정성이 핵심입니다.
    </p>
</div>

</div>

---

## WPF 아키텍처 심화

<div style="margin: 2rem 0;">

### 🏗️ WPF 계층 구조

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #6c757d; margin: 1rem 0;">

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

</div>

### 🌳 시각적 트리와 논리적 트리

<div style="background: #e8f5e8; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #155724;">논리적 트리:</strong> XAML에 정의된 요소들의 계층 구조</li>
        <li><strong style="color: #155724;">시각적 트리:</strong> 실제 렌더링되는 모든 시각적 요소</li>
        <li><strong style="color: #155724;">성능 고려:</strong> 시각적 트리 깊이가 렌더링 성능에 직접 영향</li>
    </ul>
</div>

### 🎨 렌더링 시스템

<div style="background: #e3f2fd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2196f3; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #0d47a1;">DirectX 기반:</strong> 하드웨어 가속 렌더링</li>
        <li><strong style="color: #0d47a1;">벡터 그래픽:</strong> 해상도 독립적 UI</li>
        <li><strong style="color: #0d47a1;">컴포지션:</strong> 레이어 기반 렌더링</li>
        <li><strong style="color: #0d47a1;">애니메이션:</strong> GPU 가속 부드러운 전환</li>
    </ul>
</div>

</div>

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

### 💻 디펜던시 프로퍼티 구현

```csharp
// 반도체 장비 상태를 나타내는 커스텀 컨트롤
public class EquipmentStatusControl : Control
{
    // 디펜던시 프로퍼티 정의
    public static readonly DependencyProperty StatusProperty =
        DependencyProperty.Register(
            "Status",
            typeof(EquipmentStatus),
            typeof(EquipmentStatusControl),
            new PropertyMetadata(EquipmentStatus.Idle, OnStatusChanged));

    // CLR 프로퍼티 래퍼
    public EquipmentStatus Status
    {
        get { return (EquipmentStatus)GetValue(StatusProperty); }
        set { SetValue(StatusProperty, value); }
    }

    // 프로퍼티 변경 콜백
    private static void OnStatusChanged(DependencyObject d,
        DependencyPropertyChangedEventArgs e)
    {
        var control = (EquipmentStatusControl)d;
        control.UpdateVisualState((EquipmentStatus)e.NewValue);
    }

    private void UpdateVisualState(EquipmentStatus newStatus)
    {
        // 상태에 따른 시각적 업데이트
        switch (newStatus)
        {
            case EquipmentStatus.Running:
                Background = Brushes.Green;
                break;
            case EquipmentStatus.Warning:
                Background = Brushes.Orange;
                break;
            case EquipmentStatus.Error:
                Background = Brushes.Red;
                break;
            default:
                Background = Brushes.Gray;
                break;
        }
    }
}

public enum EquipmentStatus
{
    Idle,      // 대기
    Running,   // 운전 중
    Warning,   // 경고
    Error,     // 오류
    Maintenance // 정비
}
```

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

### 💻 기본 ViewModel 구현

```csharp
// 기본 ViewModel 베이스 클래스
public abstract class BaseViewModel : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler PropertyChanged;

    // 속성 변경 알림
    protected virtual void OnPropertyChanged([CallerMemberName] string propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }

    // 속성 값 설정 헬퍼 메서드
    protected bool SetProperty<T>(ref T backingField, T value, [CallerMemberName] string propertyName = null)
    {
        if (EqualityComparer<T>.Default.Equals(backingField, value))
            return false;

        backingField = value;
        OnPropertyChanged(propertyName);
        return true;
    }
}

// 반도체 장비 ViewModel 구현
public class EquipmentViewModel : BaseViewModel
{
    private string _equipmentId;
    private EquipmentStatus _status;
    private double _temperature;
    private double _pressure;
    private DateTime _lastUpdate;

    public string EquipmentId
    {
        get => _equipmentId;
        set => SetProperty(ref _equipmentId, value);
    }

    public EquipmentStatus Status
    {
        get => _status;
        set
        {
            if (SetProperty(ref _status, value))
            {
                // 상태 변경 시 색상도 함께 업데이트
                OnPropertyChanged(nameof(StatusColor));
                OnPropertyChanged(nameof(StatusText));
            }
        }
    }

    public double Temperature
    {
        get => _temperature;
        set => SetProperty(ref _temperature, value);
    }

    public double Pressure
    {
        get => _pressure;
        set => SetProperty(ref _pressure, value);
    }

    public DateTime LastUpdate
    {
        get => _lastUpdate;
        set => SetProperty(ref _lastUpdate, value);
    }

    // 계산된 속성들
    public string StatusColor => Status switch
    {
        EquipmentStatus.Running => "#4CAF50",    // 녹색
        EquipmentStatus.Warning => "#FF9800",    // 주황색
        EquipmentStatus.Error => "#F44336",      // 빨간색
        EquipmentStatus.Maintenance => "#2196F3", // 파란색
        _ => "#9E9E9E"                           // 회색
    };

    public string StatusText => Status switch
    {
        EquipmentStatus.Idle => "대기",
        EquipmentStatus.Running => "운전 중",
        EquipmentStatus.Warning => "경고",
        EquipmentStatus.Error => "오류",
        EquipmentStatus.Maintenance => "정비 중",
        _ => "알 수 없음"
    };

    public string TemperatureText => $"{Temperature:F1}°C";
    public string PressureText => $"{Pressure:F3} Torr";
    public string LastUpdateText => LastUpdate.ToString("yyyy-MM-dd HH:mm:ss");
}
```

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

```csharp
using System.Windows;

namespace SemiconductorHMI
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();

            // ViewModel 설정
            DataContext = new MainWindowViewModel();
        }
    }
}
```

### 🎯 MainWindowViewModel 구현

```csharp
using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Windows.Threading;

namespace SemiconductorHMI
{
    public class MainWindowViewModel : BaseViewModel
    {
        private EquipmentViewModel _selectedEquipment;
        private string _currentTime;
        private int _alarmCount;
        private string _statusMessage;
        private DispatcherTimer _clockTimer;

        public ObservableCollection<EquipmentViewModel> EquipmentList { get; }

        public EquipmentViewModel SelectedEquipment
        {
            get => _selectedEquipment;
            set => SetProperty(ref _selectedEquipment, value);
        }

        public string CurrentTime
        {
            get => _currentTime;
            set => SetProperty(ref _currentTime, value);
        }

        public int AlarmCount
        {
            get => _alarmCount;
            set => SetProperty(ref _alarmCount, value);
        }

        public string StatusMessage
        {
            get => _statusMessage;
            set => SetProperty(ref _statusMessage, value);
        }

        public MainWindowViewModel()
        {
            EquipmentList = new ObservableCollection<EquipmentViewModel>();
            InitializeEquipmentData();
            InitializeClock();

            // 첫 번째 장비를 기본 선택
            if (EquipmentList.Count > 0)
                SelectedEquipment = EquipmentList[0];

            StatusMessage = "시스템 초기화 완료";
        }

        private void InitializeEquipmentData()
        {
            // 샘플 반도체 장비 데이터 생성
            EquipmentList.Add(new EquipmentViewModel
            {
                EquipmentId = "CVD-001",
                Status = EquipmentStatus.Running,
                Temperature = 250.5,
                Pressure = 0.850,
                LastUpdate = DateTime.Now
            });

            EquipmentList.Add(new EquipmentViewModel
            {
                EquipmentId = "PVD-002",
                Status = EquipmentStatus.Warning,
                Temperature = 185.2,
                Pressure = 1.250,
                LastUpdate = DateTime.Now.AddMinutes(-2)
            });

            EquipmentList.Add(new EquipmentViewModel
            {
                EquipmentId = "ETCH-003",
                Status = EquipmentStatus.Idle,
                Temperature = 25.0,
                Pressure = 0.001,
                LastUpdate = DateTime.Now.AddMinutes(-15)
            });

            EquipmentList.Add(new EquipmentViewModel
            {
                EquipmentId = "CMP-004",
                Status = EquipmentStatus.Error,
                Temperature = 95.8,
                Pressure = 0.750,
                LastUpdate = DateTime.Now.AddMinutes(-5)
            });

            // 알람 개수 계산
            UpdateAlarmCount();
        }

        private void InitializeClock()
        {
            // 1초마다 시간 업데이트
            _clockTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(1)
            };
            _clockTimer.Tick += (s, e) => UpdateCurrentTime();
            _clockTimer.Start();

            UpdateCurrentTime();
        }

        private void UpdateCurrentTime()
        {
            CurrentTime = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        }

        private void UpdateAlarmCount()
        {
            int count = 0;
            foreach (var equipment in EquipmentList)
            {
                if (equipment.Status == EquipmentStatus.Warning ||
                    equipment.Status == EquipmentStatus.Error)
                {
                    count++;
                }
            }
            AlarmCount = count;
        }
    }
}
```

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

## ❓ 질의응답

<div style="margin: 2rem 0;">

<div style="background: #f8f9fa; padding: 2rem; border-radius: 8px; text-align: center; border: 2px dashed #6c757d;">
    <h3 style="color: #495057; margin: 0 0 1rem 0;">💬 질문해 주세요!</h3>
    <p style="margin: 0; color: #6c757d; font-style: italic;">
        WPF MVVM 패턴이나 데이터 바인딩에 대해<br>
        궁금한 점이 있으시면 언제든지 질문해 주세요.
    </p>
</div>

</div>