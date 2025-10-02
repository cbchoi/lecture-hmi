# 🎯 Hands-on 프로젝트

---

## 종합 실시간 모니터링 시스템

<div style="margin: 2rem 0;">

### 🏗️ 통합 애플리케이션 구조

```csharp
// MainWindow에서 통합 관리
public partial class MainWindow : Window
{
    private readonly RealTimeEquipmentViewModel _realTimeViewModel;
    private readonly RealTimeChartViewModel _chartViewModel;
    private readonly SignalRClientService _signalRClient;
    private readonly ILogger<MainWindow> _logger;

    public MainWindow()
    {
        InitializeComponent();

        // 로깅 설정
        var loggerFactory = LoggerFactory.Create(builder =>
            builder.AddConsole().SetMinimumLevel(LogLevel.Information));
        _logger = loggerFactory.CreateLogger<MainWindow>();

        // SignalR 클라이언트 초기화
        _signalRClient = new SignalRClientService(
            loggerFactory.CreateLogger<SignalRClientService>());

        // ViewModel 초기화
        _realTimeViewModel = new RealTimeEquipmentViewModel(_signalRClient);
        _chartViewModel = new RealTimeChartViewModel(_signalRClient);

        // DataContext 설정
        RealTimeMonitoringView.DataContext = _realTimeViewModel;
        ChartView.DataContext = _chartViewModel;

        // 이벤트 구독
        _signalRClient.ConnectionStateChanged += OnConnectionStateChanged;
        _signalRClient.AlarmReceived += OnAlarmReceived;

        // 초기화
        Loaded += OnWindowLoaded;
        Closing += OnWindowClosing;
    }

    private async void OnWindowLoaded(object sender, RoutedEventArgs e)
    {
        try
        {
            // SignalR 서버 연결
            await _signalRClient.ConnectAsync("https://localhost:5001/equipmentHub");
            _logger.LogInformation("애플리케이션 초기화 완료");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "애플리케이션 초기화 실패");
            MessageBox.Show($"서버 연결 실패: {ex.Message}", "연결 오류",
                MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    private void OnConnectionStateChanged(object sender, bool isConnected)
    {
        Dispatcher.InvokeAsync(() =>
        {
            StatusBorder.Background = isConnected ?
                new SolidColorBrush(Color.FromRgb(46, 204, 113)) :
                new SolidColorBrush(Color.FromRgb(231, 76, 60));

            StatusText.Text = isConnected ? "연결됨" : "연결 끊김";
        });
    }

    private void OnAlarmReceived(object sender, AlarmEventArgs e)
    {
        Dispatcher.InvokeAsync(() =>
        {
            // 알람 팝업 표시
            var alarmWindow = new AlarmNotificationWindow(e.Alarm);
            alarmWindow.Show();

            // 로그 기록
            _logger.LogWarning($"알람 수신: {e.Alarm.EquipmentId} - {e.Alarm.Type}: {e.Alarm.Message}");
        });
    }

    private async void OnWindowClosing(object sender, CancelEventArgs e)
    {
        try
        {
            await _signalRClient.DisconnectAsync();
            _realTimeViewModel?.Dispose();
            _chartViewModel?.Dispose();
            _signalRClient?.Dispose();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "애플리케이션 종료 중 오류");
        }
    }
}
```

### 🚨 알람 시스템 구현

```csharp
// 알람 노티피케이션 창
public partial class AlarmNotificationWindow : Window
{
    private readonly AlarmData _alarm;
    private readonly Timer _autoCloseTimer;

    public AlarmNotificationWindow(AlarmData alarm)
    {
        InitializeComponent();
        _alarm = alarm;

        // 알람 정보 표시
        EquipmentIdText.Text = alarm.EquipmentId;
        AlarmTypeText.Text = alarm.Type;
        AlarmMessageText.Text = alarm.Message;
        TimestampText.Text = alarm.Timestamp.ToString("yyyy-MM-dd HH:mm:ss");

        // 알람 타입에 따른 스타일 설정
        SetAlarmStyle(alarm.Type);

        // 5초 후 자동 닫기
        _autoCloseTimer = new Timer(AutoClose, null, TimeSpan.FromSeconds(5), Timeout.InfiniteTimeSpan);

        // 화면 우상단에 위치
        WindowStartupLocation = WindowStartupLocation.Manual;
        Left = SystemParameters.WorkArea.Width - Width - 20;
        Top = 20;
    }

    private void SetAlarmStyle(string alarmType)
    {
        switch (alarmType)
        {
            case "CRITICAL":
                AlarmBorder.Background = new SolidColorBrush(Color.FromRgb(231, 76, 60));
                AlarmIcon.Text = "🚨";
                break;
            case "WARNING":
                AlarmBorder.Background = new SolidColorBrush(Color.FromRgb(243, 156, 18));
                AlarmIcon.Text = "⚠";
                break;
            default:
                AlarmBorder.Background = new SolidColorBrush(Color.FromRgb(52, 152, 219));
                AlarmIcon.Text = "ℹ";
                break;
        }
    }

    private void AutoClose(object state)
    {
        Dispatcher.InvokeAsync(() =>
        {
            Close();
        });
    }

    private void AcknowledgeButton_Click(object sender, RoutedEventArgs e)
    {
        _autoCloseTimer?.Dispose();
        Close();
    }

    protected override void OnClosed(EventArgs e)
    {
        _autoCloseTimer?.Dispose();
        base.OnClosed(e);
    }
}
```

### 📊 성능 대시보드

```csharp
// 성능 모니터링 ViewModel
public class PerformanceDashboardViewModel : BaseViewModel, IDisposable
{
    private readonly PerformanceMonitor _performanceMonitor;
    private readonly Timer _updateTimer;

    private float _cpuUsage;
    private float _memoryUsageMB;
    private double _dataProcessingRate;
    private long _totalProcessedData;
    private int _activeConnections;

    public float CpuUsage
    {
        get => _cpuUsage;
        set => SetProperty(ref _cpuUsage, value);
    }

    public float MemoryUsageMB
    {
        get => _memoryUsageMB;
        set => SetProperty(ref _memoryUsageMB, value);
    }

    public double DataProcessingRate
    {
        get => _dataProcessingRate;
        set => SetProperty(ref _dataProcessingRate, value);
    }

    public long TotalProcessedData
    {
        get => _totalProcessedData;
        set => SetProperty(ref _totalProcessedData, value);
    }

    public int ActiveConnections
    {
        get => _activeConnections;
        set => SetProperty(ref _activeConnections, value);
    }

    // 포맷된 속성들
    public string CpuUsageText => $"{CpuUsage:F1}%";
    public string MemoryUsageText => $"{MemoryUsageMB:F0} MB";
    public string DataProcessingRateText => $"{DataProcessingRate:F1} /초";
    public string TotalProcessedDataText => $"{TotalProcessedData:N0} 개";

    public PerformanceDashboardViewModel()
    {
        _performanceMonitor = new PerformanceMonitor();
        _performanceMonitor.MetricsUpdated += OnMetricsUpdated;

        // 1초마다 UI 업데이트
        _updateTimer = new Timer(UpdatePerformanceMetrics, null,
            TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1));
    }

    private void OnMetricsUpdated(object sender, PerformanceMetrics metrics)
    {
        Application.Current.Dispatcher.InvokeAsync(() =>
        {
            CpuUsage = metrics.CpuUsage;
            MemoryUsageMB = metrics.AvailableMemoryMB;
            DataProcessingRate = metrics.DataProcessingRate;
            TotalProcessedData = metrics.ProcessedDataCount;

            // 추가 계산된 속성들 업데이트
            OnPropertyChanged(nameof(CpuUsageText));
            OnPropertyChanged(nameof(MemoryUsageText));
            OnPropertyChanged(nameof(DataProcessingRateText));
            OnPropertyChanged(nameof(TotalProcessedDataText));
        });
    }

    private void UpdatePerformanceMetrics(object state)
    {
        // 성능 카운터 업데이트는 PerformanceMonitor에서 처리
        _performanceMonitor.IncrementProcessedData();
    }

    public void Dispose()
    {
        _updateTimer?.Dispose();
        _performanceMonitor?.Dispose();
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
        <li><strong style="color: #155724;">비동기 프로그래밍:</strong> Task와 async/await를 활용한 고성능 데이터 처리</li>
        <li><strong style="color: #155724;">실시간 통신:</strong> TCP/IP 소켓과 SignalR을 이용한 양방향 통신</li>
        <li><strong style="color: #155724;">데이터 시각화:</strong> LiveCharts를 활용한 실시간 차트 구현</li>
        <li><strong style="color: #155724;">성능 최적화:</strong> 객체 풀링과 메모리 관리 기법 적용</li>
        <li><strong style="color: #155724;">오류 처리:</strong> 견고한 예외 처리와 재시도 메커니즘</li>
    </ul>
</div>

### 🚀 다음 주차 예고: 고급 UI/UX 개발

<div style="background: #e3f2fd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2196f3; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #0d47a1;">사용자 정의 컨트롤:</strong> 반도체 장비용 특화 컨트롤 개발</li>
        <li><strong style="color: #0d47a1;">고급 레이아웃:</strong> 가상화 및 성능 최적화 기법</li>
        <li><strong style="color: #0d47a1;">애니메이션:</strong> 부드러운 전환과 피드백 시스템</li>
        <li><strong style="color: #0d47a1;">접근성:</strong> 산업용 환경을 위한 UX 개선</li>
    </ul>
</div>

### 📚 과제 및 복습

<div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #f39c12; margin: 1.5rem 0;">
    <p style="margin: 0; color: #856404; font-weight: 500; font-size: 1.1em;">
        💡 오늘 구현한 실시간 시스템에 데이터 히스토리 저장 기능을 추가해보세요. (SQLite 또는 CSV 파일 활용)
    </p>
</div>

</div>

---

## ❓ 질의응답

<div style="margin: 2rem 0;">

<div style="background: #f8f9fa; padding: 2rem; border-radius: 8px; text-align: center; border: 2px dashed #6c757d;">
    <h3 style="color: #495057; margin: 0 0 1rem 0;">💬 질문해 주세요!</h3>
    <p style="margin: 0; color: #6c757d; font-style: italic;">
        실시간 데이터 처리나 비동기 프로그래밍에 대해<br>
        궁금한 점이 있으시면 언제든지 질문해 주세요.
    </p>
</div>

