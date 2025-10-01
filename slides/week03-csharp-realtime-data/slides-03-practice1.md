# 💻 기초 실습 (45분)

---

## 실습 1: Timer 기반 실시간 데이터 수집

<div style="margin: 2rem 0;">

### 🔧 ViewModel 확장

```csharp
// RealTimeEquipmentViewModel.cs
public class RealTimeEquipmentViewModel : BaseViewModel, IDisposable
{
    private readonly Timer _dataUpdateTimer;
    private readonly EquipmentDataCollector _dataCollector;
    private readonly ThreadSafeDataStore _dataStore;
    private bool _isCollecting;

    private ObservableCollection<EquipmentViewModel> _equipmentList;
    private EquipmentViewModel _selectedEquipment;
    private double _dataCollectionRate;
    private int _totalDataPoints;
    private string _connectionStatus;

    public ObservableCollection<EquipmentViewModel> EquipmentList
    {
        get => _equipmentList;
        set => SetProperty(ref _equipmentList, value);
    }

    public EquipmentViewModel SelectedEquipment
    {
        get => _selectedEquipment;
        set => SetProperty(ref _selectedEquipment, value);
    }

    public double DataCollectionRate
    {
        get => _dataCollectionRate;
        set => SetProperty(ref _dataCollectionRate, value);
    }

    public int TotalDataPoints
    {
        get => _totalDataPoints;
        set => SetProperty(ref _totalDataPoints, value);
    }

    public string ConnectionStatus
    {
        get => _connectionStatus;
        set => SetProperty(ref _connectionStatus, value);
    }

    public bool IsCollecting
    {
        get => _isCollecting;
        set
        {
            if (SetProperty(ref _isCollecting, value))
            {
                OnPropertyChanged(nameof(CollectionStatusText));
                OnPropertyChanged(nameof(CollectionButtonText));
            }
        }
    }

    public string CollectionStatusText => IsCollecting ? "수집 중" : "정지됨";
    public string CollectionButtonText => IsCollecting ? "수집 중지" : "수집 시작";

    // 커맨드
    public ICommand StartCollectionCommand { get; }
    public ICommand StopCollectionCommand { get; }
    public ICommand ClearDataCommand { get; }

    public RealTimeEquipmentViewModel()
    {
        EquipmentList = new ObservableCollection<EquipmentViewModel>();
        _dataCollector = new EquipmentDataCollector();
        _dataStore = new ThreadSafeDataStore();

        // 1초마다 UI 업데이트
        _dataUpdateTimer = new Timer(UpdateUI, null,
            TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(1));

        InitializeCommands();
        InitializeEquipment();

        ConnectionStatus = "준비됨";
    }

    private void InitializeCommands()
    {
        StartCollectionCommand = new RelayCommand(StartCollection, () => !IsCollecting);
        StopCollectionCommand = new RelayCommand(StopCollection, () => IsCollecting);
        ClearDataCommand = new RelayCommand(ClearData);
    }

    private void InitializeEquipment()
    {
        var equipmentIds = new[] { "CVD-001", "PVD-002", "ETCH-003", "CMP-004" };

        foreach (var id in equipmentIds)
        {
            var equipment = new EquipmentViewModel
            {
                EquipmentId = id,
                Status = EquipmentStatus.Idle,
                Temperature = 0,
                Pressure = 0,
                LastUpdate = DateTime.Now
            };

            EquipmentList.Add(equipment);
        }

        if (EquipmentList.Count > 0)
            SelectedEquipment = EquipmentList[0];
    }

    private async void StartCollection()
    {
        IsCollecting = true;
        ConnectionStatus = "연결 중...";

        try
        {
            // 백그라운드에서 데이터 수집 시작
            _ = Task.Run(async () =>
            {
                var random = new Random();
                var dataPointCount = 0;
                var lastRateCalculation = DateTime.Now;

                while (IsCollecting)
                {
                    // 모든 장비에 대해 데이터 수집
                    foreach (var equipment in EquipmentList)
                    {
                        var data = new EquipmentData
                        {
                            Temperature = GetRandomTemperature(equipment.EquipmentId, random),
                            Pressure = GetRandomPressure(equipment.EquipmentId, random),
                            FlowRate = GetRandomFlowRate(equipment.EquipmentId, random),
                            Timestamp = DateTime.Now
                        };

                        // 스레드 안전한 저장
                        _dataStore.AddDataConcurrent(data);

                        // UI 스레드에서 업데이트
                        await Application.Current.Dispatcher.InvokeAsync(() =>
                        {
                            equipment.Temperature = data.Temperature;
                            equipment.Pressure = data.Pressure;
                            equipment.LastUpdate = data.Timestamp;

                            // 상태 업데이트
                            equipment.Status = DetermineStatus(data);
                        });

                        dataPointCount++;
                        TotalDataPoints = dataPointCount;
                    }

                    // 데이터 수집 속도 계산
                    var now = DateTime.Now;
                    var elapsed = now - lastRateCalculation;
                    if (elapsed.TotalSeconds >= 1)
                    {
                        DataCollectionRate = dataPointCount / elapsed.TotalSeconds;
                        dataPointCount = 0;
                        lastRateCalculation = now;
                    }

                    await Task.Delay(250); // 250ms 간격으로 수집
                }
            });

            ConnectionStatus = "데이터 수집 중";
        }
        catch (Exception ex)
        {
            ConnectionStatus = $"오류: {ex.Message}";
            IsCollecting = false;
        }
    }

    private void StopCollection()
    {
        IsCollecting = false;
        ConnectionStatus = "수집 중지됨";
    }

    private void ClearData()
    {
        TotalDataPoints = 0;
        DataCollectionRate = 0;

        foreach (var equipment in EquipmentList)
        {
            equipment.Status = EquipmentStatus.Idle;
            equipment.Temperature = 0;
            equipment.Pressure = 0;
            equipment.LastUpdate = DateTime.Now;
        }
    }

    private double GetRandomTemperature(string equipmentId, Random random)
    {
        return equipmentId switch
        {
            "CVD-001" => 250 + random.NextDouble() * 20 - 10,
            "PVD-002" => 180 + random.NextDouble() * 15 - 7.5,
            "ETCH-003" => 30 + random.NextDouble() * 10 - 5,
            "CMP-004" => 45 + random.NextDouble() * 8 - 4,
            _ => 25 + random.NextDouble() * 5
        };
    }

    private double GetRandomPressure(string equipmentId, Random random)
    {
        return equipmentId switch
        {
            "CVD-001" => 0.8 + random.NextDouble() * 0.4 - 0.2,
            "PVD-002" => 0.005 + random.NextDouble() * 0.01 - 0.005,
            "ETCH-003" => 0.001 + random.NextDouble() * 0.002 - 0.001,
            "CMP-004" => 0.75 + random.NextDouble() * 0.3 - 0.15,
            _ => 0.1 + random.NextDouble() * 0.1
        };
    }

    private double GetRandomFlowRate(string equipmentId, Random random)
    {
        return equipmentId switch
        {
            "CVD-001" => 150 + random.NextDouble() * 30 - 15,
            "PVD-002" => 50 + random.NextDouble() * 20 - 10,
            "ETCH-003" => 0,
            "CMP-004" => 200 + random.NextDouble() * 40 - 20,
            _ => 100 + random.NextDouble() * 20
        };
    }

    private EquipmentStatus DetermineStatus(EquipmentData data)
    {
        // 간단한 상태 결정 로직
        if (data.Temperature > 300 || data.Pressure > 2.0)
            return EquipmentStatus.Error;
        else if (data.Temperature > 280 || data.Pressure > 1.5)
            return EquipmentStatus.Warning;
        else if (data.Temperature > 50)
            return EquipmentStatus.Running;
        else
            return EquipmentStatus.Idle;
    }

    private void UpdateUI(object state)
    {
        if (!IsCollecting) return;

        // 성능 지표 업데이트를 UI 스레드에서 실행
        Application.Current.Dispatcher.InvokeAsync(() =>
        {
            OnPropertyChanged(nameof(DataCollectionRate));
            OnPropertyChanged(nameof(TotalDataPoints));
        });
    }

    public void Dispose()
    {
        IsCollecting = false;
        _dataUpdateTimer?.Dispose();
        _dataCollector?.StopAsync();
        _dataStore?.Dispose();
    }
}
```

### 🎨 XAML UI 확장

```xml
<!-- RealTimeMonitoringView.xaml -->
<UserControl x:Class="SemiconductorHMI.Views.RealTimeMonitoringView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">

    <Grid Margin="10">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>  <!-- 제어 패널 -->
            <RowDefinition Height="Auto"/>  <!-- 성능 지표 -->
            <RowDefinition Height="*"/>     <!-- 장비 모니터링 -->
        </Grid.RowDefinitions>

        <!-- 제어 패널 -->
        <Border Grid.Row="0" Background="#34495E" CornerRadius="5" Padding="15" Margin="0,0,0,10">
            <Grid>
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="Auto"/>
                    <ColumnDefinition Width="Auto"/>
                    <ColumnDefinition Width="Auto"/>
                </Grid.ColumnDefinitions>

                <!-- 상태 정보 -->
                <StackPanel Grid.Column="0" Orientation="Horizontal" VerticalAlignment="Center">
                    <TextBlock Text="상태: " Foreground="White" FontWeight="Medium"/>
                    <TextBlock Text="{Binding ConnectionStatus}" Foreground="#2ECC71" FontWeight="Bold"/>
                    <TextBlock Text=" | " Foreground="White" Margin="10,0"/>
                    <TextBlock Text="{Binding CollectionStatusText}" Foreground="#E74C3C" FontWeight="Bold"/>
                </StackPanel>

                <!-- 제어 버튼 -->
                <Button Grid.Column="1"
                        Command="{Binding StartCollectionCommand}"
                        Background="#27AE60" Foreground="White"
                        Padding="15,8" Margin="5,0"
                        BorderThickness="0" CornerRadius="3">
                    <StackPanel Orientation="Horizontal">
                        <TextBlock Text="▶" FontSize="12" Margin="0,0,5,0"/>
                        <TextBlock Text="시작"/>
                    </StackPanel>
                </Button>

                <Button Grid.Column="2"
                        Command="{Binding StopCollectionCommand}"
                        Background="#E74C3C" Foreground="White"
                        Padding="15,8" Margin="5,0"
                        BorderThickness="0" CornerRadius="3">
                    <StackPanel Orientation="Horizontal">
                        <TextBlock Text="⏹" FontSize="12" Margin="0,0,5,0"/>
                        <TextBlock Text="정지"/>
                    </StackPanel>
                </Button>

                <Button Grid.Column="3"
                        Command="{Binding ClearDataCommand}"
                        Background="#95A5A6" Foreground="White"
                        Padding="15,8" Margin="5,0"
                        BorderThickness="0" CornerRadius="3">
                    <StackPanel Orientation="Horizontal">
                        <TextBlock Text="🗑" FontSize="12" Margin="0,0,5,0"/>
                        <TextBlock Text="초기화"/>
                    </StackPanel>
                </Button>
            </Grid>
        </Border>

        <!-- 성능 지표 -->
        <Border Grid.Row="1" Background="White" CornerRadius="5"
                BorderBrush="#E0E0E0" BorderThickness="1" Padding="15" Margin="0,0,0,10">
            <Grid>
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="*"/>
                </Grid.ColumnDefinitions>

                <!-- 데이터 수집 속도 -->
                <StackPanel Grid.Column="0">
                    <TextBlock Text="데이터 수집 속도" FontSize="12" Foreground="#7F8C8D" Margin="0,0,0,5"/>
                    <StackPanel Orientation="Horizontal">
                        <TextBlock Text="{Binding DataCollectionRate, StringFormat='{}{0:F1}'}"
                                   FontSize="24" FontWeight="Bold" Foreground="#3498DB"/>
                        <TextBlock Text=" 포인트/초" FontSize="14" Foreground="#7F8C8D" VerticalAlignment="Bottom" Margin="5,0,0,2"/>
                    </StackPanel>
                </StackPanel>

                <!-- 총 데이터 포인트 -->
                <StackPanel Grid.Column="1">
                    <TextBlock Text="총 데이터 포인트" FontSize="12" Foreground="#7F8C8D" Margin="0,0,0,5"/>
                    <StackPanel Orientation="Horizontal">
                        <TextBlock Text="{Binding TotalDataPoints, StringFormat='{}{0:N0}'}"
                                   FontSize="24" FontWeight="Bold" Foreground="#E67E22"/>
                        <TextBlock Text=" 개" FontSize="14" Foreground="#7F8C8D" VerticalAlignment="Bottom" Margin="5,0,0,2"/>
                    </StackPanel>
                </StackPanel>

                <!-- 활성 장비 수 -->
                <StackPanel Grid.Column="2">
                    <TextBlock Text="활성 장비" FontSize="12" Foreground="#7F8C8D" Margin="0,0,0,5"/>
                    <StackPanel Orientation="Horizontal">
                        <TextBlock Text="{Binding EquipmentList.Count}"
                                   FontSize="24" FontWeight="Bold" Foreground="#27AE60"/>
                        <TextBlock Text=" 대" FontSize="14" Foreground="#7F8C8D" VerticalAlignment="Bottom" Margin="5,0,0,2"/>
                    </StackPanel>
                </StackPanel>
            </Grid>
        </Border>

        <!-- 장비 모니터링 그리드 -->
        <Border Grid.Row="2" Background="White" CornerRadius="5"
                BorderBrush="#E0E0E0" BorderThickness="1">
            <Grid Margin="15">
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="2*"/>
                    <ColumnDefinition Width="2*"/>
                </Grid.ColumnDefinitions>
                <Grid.RowDefinitions>
                    <RowDefinition Height="*"/>
                    <RowDefinition Height="*"/>
                </Grid.RowDefinitions>

                <!-- 각 장비별 모니터링 카드 -->
                <Border Grid.Row="0" Grid.Column="0" Background="#F8F9FA" CornerRadius="8"
                        Padding="15" Margin="5">
                    <StackPanel>
                        <TextBlock Text="{Binding EquipmentList[0].EquipmentId}"
                                   FontSize="16" FontWeight="Bold" Margin="0,0,0,10"/>
                        <Grid>
                            <Grid.ColumnDefinitions>
                                <ColumnDefinition Width="*"/>
                                <ColumnDefinition Width="*"/>
                            </Grid.ColumnDefinitions>
                            <StackPanel Grid.Column="0">
                                <TextBlock Text="온도" FontSize="12" Foreground="#7F8C8D"/>
                                <TextBlock Text="{Binding EquipmentList[0].TemperatureText}"
                                           FontSize="20" FontWeight="Bold" Foreground="#E67E22"/>
                            </StackPanel>
                            <StackPanel Grid.Column="1">
                                <TextBlock Text="압력" FontSize="12" Foreground="#7F8C8D"/>
                                <TextBlock Text="{Binding EquipmentList[0].PressureText}"
                                           FontSize="20" FontWeight="Bold" Foreground="#3498DB"/>
                            </StackPanel>
                        </Grid>
                        <Border Background="{Binding EquipmentList[0].StatusColor}"
                                CornerRadius="15" Padding="8,4" Margin="0,10,0,0" HorizontalAlignment="Left">
                            <TextBlock Text="{Binding EquipmentList[0].StatusText}"
                                       Foreground="White" FontSize="12" FontWeight="Medium"/>
                        </Border>
                    </StackPanel>
                </Border>

                <!-- 나머지 장비들도 동일한 패턴으로 구성 -->
                <Border Grid.Row="0" Grid.Column="1" Background="#F8F9FA" CornerRadius="8"
                        Padding="15" Margin="5">
                    <!-- PVD-002 장비 정보 -->
                </Border>

                <Border Grid.Row="1" Grid.Column="0" Background="#F8F9FA" CornerRadius="8"
                        Padding="15" Margin="5">
                    <!-- ETCH-003 장비 정보 -->
                </Border>

                <Border Grid.Row="1" Grid.Column="1" Background="#F8F9FA" CornerRadius="8"
                        Padding="15" Margin="5">
                    <!-- CMP-004 장비 정보 -->
                </Border>
            </Grid>
        </Border>
    </Grid>
</UserControl>
```

</div>

---

## 실습 2: 비동기 오류 처리

<div style="margin: 2rem 0;">

### 🛡️ 견고한 예외 처리

```csharp
// 포괄적인 오류 처리가 포함된 데이터 수집기
public class RobustDataCollector : IDisposable
{
    private readonly ILogger<RobustDataCollector> _logger;
    private readonly SemaphoreSlim _semaphore;
    private readonly CancellationTokenSource _cancellationTokenSource;
    private readonly List<Task> _runningTasks;
    private volatile bool _isDisposed;

    public event EventHandler<DataCollectionErrorEventArgs> ErrorOccurred;
    public event EventHandler<EquipmentDataReceivedEventArgs> DataReceived;

    public RobustDataCollector(ILogger<RobustDataCollector> logger = null)
    {
        _logger = logger ?? NullLogger<RobustDataCollector>.Instance;
        _semaphore = new SemaphoreSlim(1, 1);
        _cancellationTokenSource = new CancellationTokenSource();
        _runningTasks = new List<Task>();
    }

    public async Task StartCollectionAsync()
    {
        if (_isDisposed)
            throw new ObjectDisposedException(nameof(RobustDataCollector));

        await _semaphore.WaitAsync();
        try
        {
            _logger.LogInformation("데이터 수집 시작");

            // 각 장비별로 별도 태스크에서 데이터 수집
            var equipmentIds = new[] { "CVD-001", "PVD-002", "ETCH-003", "CMP-004" };

            foreach (var equipmentId in equipmentIds)
            {
                var task = CollectEquipmentDataAsync(equipmentId, _cancellationTokenSource.Token);
                _runningTasks.Add(task);
            }

            _logger.LogInformation($"{equipmentIds.Length}개 장비의 데이터 수집 태스크 시작됨");
        }
        finally
        {
            _semaphore.Release();
        }
    }

    private async Task CollectEquipmentDataAsync(string equipmentId, CancellationToken cancellationToken)
    {
        var retryCount = 0;
        const int maxRetries = 3;
        const int baseDelayMs = 1000;

        while (!cancellationToken.IsCancellationRequested)
        {
            try
            {
                var data = await CollectSingleDataPointAsync(equipmentId, cancellationToken);

                DataReceived?.Invoke(this, new EquipmentDataReceivedEventArgs(equipmentId, data));

                retryCount = 0; // 성공 시 재시도 카운터 리셋

                await Task.Delay(1000, cancellationToken); // 1초 간격
            }
            catch (OperationCanceledException)
            {
                _logger.LogInformation($"{equipmentId} 데이터 수집이 취소됨");
                break;
            }
            catch (TimeoutException ex)
            {
                _logger.LogWarning($"{equipmentId} 데이터 수집 타임아웃: {ex.Message}");
                await HandleRetryAsync(equipmentId, ex, ref retryCount, maxRetries, baseDelayMs, cancellationToken);
            }
            catch (HttpRequestException ex)
            {
                _logger.LogWarning($"{equipmentId} 네트워크 오류: {ex.Message}");
                await HandleRetryAsync(equipmentId, ex, ref retryCount, maxRetries, baseDelayMs, cancellationToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"{equipmentId} 데이터 수집 중 예상치 못한 오류");

                ErrorOccurred?.Invoke(this, new DataCollectionErrorEventArgs(equipmentId, ex));

                // 치명적 오류가 아닌 경우 재시도
                if (!(ex is OutOfMemoryException || ex is StackOverflowException))
                {
                    await HandleRetryAsync(equipmentId, ex, ref retryCount, maxRetries, baseDelayMs, cancellationToken);
                }
                else
                {
                    _logger.LogCritical($"{equipmentId} 치명적 오류로 인한 수집 중단");
                    break;
                }
            }
        }
    }

    private async Task<EquipmentData> CollectSingleDataPointAsync(string equipmentId, CancellationToken cancellationToken)
    {
        using var timeoutCts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        timeoutCts.CancelAfter(TimeSpan.FromSeconds(5)); // 5초 타임아웃

        try
        {
            // 실제 하드웨어와의 통신 시뮬레이션
            await Task.Delay(Random.Shared.Next(100, 500), timeoutCts.Token);

            // 간헐적으로 오류 발생 시뮬레이션
            if (Random.Shared.NextDouble() < 0.05) // 5% 확률로 타임아웃
            {
                throw new TimeoutException($"{equipmentId} 센서 응답 시간 초과");
            }

            if (Random.Shared.NextDouble() < 0.02) // 2% 확률로 네트워크 오류
            {
                throw new HttpRequestException($"{equipmentId} 네트워크 연결 실패");
            }

            return new EquipmentData
            {
                EquipmentId = equipmentId,
                Temperature = GetSimulatedTemperature(equipmentId),
                Pressure = GetSimulatedPressure(equipmentId),
                FlowRate = GetSimulatedFlowRate(equipmentId),
                Timestamp = DateTime.Now
            };
        }
        catch (OperationCanceledException) when (timeoutCts.Token.IsCancellationRequested && !cancellationToken.IsCancellationRequested)
        {
            throw new TimeoutException($"{equipmentId} 데이터 수집 타임아웃");
        }
    }

    private async Task HandleRetryAsync(string equipmentId, Exception ex, ref int retryCount,
        int maxRetries, int baseDelayMs, CancellationToken cancellationToken)
    {
        retryCount++;

        if (retryCount >= maxRetries)
        {
            _logger.LogError($"{equipmentId} 최대 재시도 횟수 초과. 데이터 수집 중단");
            ErrorOccurred?.Invoke(this, new DataCollectionErrorEventArgs(equipmentId, ex));
            return;
        }

        // 지수 백오프 지연
        var delayMs = baseDelayMs * (int)Math.Pow(2, retryCount - 1);
        _logger.LogInformation($"{equipmentId} {delayMs}ms 후 재시도 ({retryCount}/{maxRetries})");

        try
        {
            await Task.Delay(delayMs, cancellationToken);
        }
        catch (OperationCanceledException)
        {
            _logger.LogInformation($"{equipmentId} 재시도 중 취소됨");
        }
    }

    private double GetSimulatedTemperature(string equipmentId) =>
        equipmentId switch
        {
            "CVD-001" => 250 + (Random.Shared.NextDouble() - 0.5) * 20,
            "PVD-002" => 180 + (Random.Shared.NextDouble() - 0.5) * 15,
            "ETCH-003" => 30 + (Random.Shared.NextDouble() - 0.5) * 10,
            "CMP-004" => 45 + (Random.Shared.NextDouble() - 0.5) * 8,
            _ => 25
        };

    private double GetSimulatedPressure(string equipmentId) =>
        equipmentId switch
        {
            "CVD-001" => 0.8 + (Random.Shared.NextDouble() - 0.5) * 0.4,
            "PVD-002" => 0.005 + (Random.Shared.NextDouble() - 0.5) * 0.01,
            "ETCH-003" => 0.001 + (Random.Shared.NextDouble() - 0.5) * 0.002,
            "CMP-004" => 0.75 + (Random.Shared.NextDouble() - 0.5) * 0.3,
            _ => 0.1
        };

    private double GetSimulatedFlowRate(string equipmentId) =>
        equipmentId switch
        {
            "CVD-001" => 150 + (Random.Shared.NextDouble() - 0.5) * 30,
            "PVD-002" => 50 + (Random.Shared.NextDouble() - 0.5) * 20,
            "ETCH-003" => 0,
            "CMP-004" => 200 + (Random.Shared.NextDouble() - 0.5) * 40,
            _ => 100
        };

    public async Task StopAsync()
    {
        _logger.LogInformation("데이터 수집 중지 요청");

        _cancellationTokenSource.Cancel();

        try
        {
            await Task.WhenAll(_runningTasks);
            _logger.LogInformation("모든 데이터 수집 태스크가 정상 종료됨");
        }
        catch (OperationCanceledException)
        {
            _logger.LogInformation("데이터 수집 태스크들이 취소됨");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "데이터 수집 종료 중 오류 발생");
        }
    }

    public void Dispose()
    {
        if (_isDisposed) return;

        _isDisposed = true;

        _cancellationTokenSource?.Cancel();
        _cancellationTokenSource?.Dispose();
        _semaphore?.Dispose();

        _logger.LogInformation("RobustDataCollector 리소스가 해제됨");
    }
}

public class DataCollectionErrorEventArgs : EventArgs
{
    public string EquipmentId { get; }
    public Exception Exception { get; }
    public DateTime Timestamp { get; }

    public DataCollectionErrorEventArgs(string equipmentId, Exception exception)
    {
        EquipmentId = equipmentId;
        Exception = exception;
        Timestamp = DateTime.Now;
    }
}
```

</div>

---

