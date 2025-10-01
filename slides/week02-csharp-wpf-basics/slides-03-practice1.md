# 💻 기초 실습

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

