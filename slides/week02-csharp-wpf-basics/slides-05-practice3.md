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

