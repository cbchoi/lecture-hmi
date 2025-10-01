# 🚀 심화 실습

---

## 실습 3: SignalR 실시간 통신

<div style="margin: 2rem 0;">

### 📡 SignalR Hub 구현

```csharp
// SignalR Hub (서버 측)
public class EquipmentHub : Hub
{
    private readonly ILogger<EquipmentHub> _logger;
    private static readonly ConcurrentDictionary<string, HashSet<string>> _equipmentSubscribers
        = new ConcurrentDictionary<string, HashSet<string>>();

    public EquipmentHub(ILogger<EquipmentHub> logger)
    {
        _logger = logger;
    }

    // 특정 장비 구독
    public async Task SubscribeToEquipment(string equipmentId)
    {
        var connectionId = Context.ConnectionId;

        _equipmentSubscribers.AddOrUpdate(equipmentId,
            new HashSet<string> { connectionId },
            (key, existing) =>
            {
                existing.Add(connectionId);
                return existing;
            });

        await Groups.AddToGroupAsync(connectionId, $"Equipment_{equipmentId}");

        _logger.LogInformation($"클라이언트 {connectionId}가 {equipmentId} 구독 시작");

        await Clients.Caller.SendAsync("SubscriptionConfirmed", equipmentId);
    }

    // 장비 구독 해제
    public async Task UnsubscribeFromEquipment(string equipmentId)
    {
        var connectionId = Context.ConnectionId;

        if (_equipmentSubscribers.TryGetValue(equipmentId, out var subscribers))
        {
            subscribers.Remove(connectionId);
            if (subscribers.Count == 0)
            {
                _equipmentSubscribers.TryRemove(equipmentId, out _);
            }
        }

        await Groups.RemoveFromGroupAsync(connectionId, $"Equipment_{equipmentId}");

        _logger.LogInformation($"클라이언트 {connectionId}가 {equipmentId} 구독 해제");
    }

    // 모든 장비 구독
    public async Task SubscribeToAllEquipment()
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, "AllEquipment");
        _logger.LogInformation($"클라이언트 {Context.ConnectionId}가 모든 장비 구독 시작");
    }

    // 연결 해제 시 정리
    public override async Task OnDisconnectedAsync(Exception exception)
    {
        var connectionId = Context.ConnectionId;

        // 모든 구독에서 제거
        foreach (var kvp in _equipmentSubscribers)
        {
            kvp.Value.Remove(connectionId);
            if (kvp.Value.Count == 0)
            {
                _equipmentSubscribers.TryRemove(kvp.Key, out _);
            }
        }

        _logger.LogInformation($"클라이언트 {connectionId} 연결 해제");

        await base.OnDisconnectedAsync(exception);
    }

    // 특정 장비에 데이터 브로드캐스트
    public async Task BroadcastEquipmentData(string equipmentId, object data)
    {
        await Clients.Group($"Equipment_{equipmentId}").SendAsync("EquipmentDataUpdate", equipmentId, data);
        await Clients.Group("AllEquipment").SendAsync("EquipmentDataUpdate", equipmentId, data);
    }

    // 알람 브로드캐스트
    public async Task BroadcastAlarm(string equipmentId, string alarmType, string message)
    {
        var alarmData = new
        {
            EquipmentId = equipmentId,
            Type = alarmType,
            Message = message,
            Timestamp = DateTime.Now
        };

        await Clients.All.SendAsync("AlarmTriggered", alarmData);

        _logger.LogWarning($"알람 브로드캐스트: {equipmentId} - {alarmType}: {message}");
    }
}

// SignalR 백그라운드 서비스
public class EquipmentDataBroadcastService : BackgroundService
{
    private readonly IHubContext<EquipmentHub> _hubContext;
    private readonly ILogger<EquipmentDataBroadcastService> _logger;
    private readonly EquipmentDataCollector _dataCollector;

    public EquipmentDataBroadcastService(
        IHubContext<EquipmentHub> hubContext,
        ILogger<EquipmentDataBroadcastService> logger)
    {
        _hubContext = hubContext;
        _logger = logger;
        _dataCollector = new EquipmentDataCollector();
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("장비 데이터 브로드캐스트 서비스 시작");

        _dataCollector.DataReceived += async (sender, args) =>
        {
            try
            {
                await _hubContext.Clients.Group($"Equipment_{args.EquipmentId}")
                    .SendAsync("EquipmentDataUpdate", args.EquipmentId, args.Data, stoppingToken);

                await _hubContext.Clients.Group("AllEquipment")
                    .SendAsync("EquipmentDataUpdate", args.EquipmentId, args.Data, stoppingToken);

                // 알람 조건 확인
                await CheckAlarmConditions(args.EquipmentId, args.Data, stoppingToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"데이터 브로드캐스트 중 오류: {args.EquipmentId}");
            }
        };

        await _dataCollector.StartDataCollectionAsync();

        while (!stoppingToken.IsCancellationRequested)
        {
            await Task.Delay(1000, stoppingToken);
        }
    }

    private async Task CheckAlarmConditions(string equipmentId, EquipmentData data, CancellationToken cancellationToken)
    {
        // 온도 알람 확인
        if (data.Temperature > 300)
        {
            await _hubContext.Clients.All.SendAsync("AlarmTriggered", new
            {
                EquipmentId = equipmentId,
                Type = "CRITICAL",
                Message = $"온도 위험 수준: {data.Temperature:F1}°C",
                Timestamp = DateTime.Now
            }, cancellationToken);
        }
        else if (data.Temperature > 280)
        {
            await _hubContext.Clients.All.SendAsync("AlarmTriggered", new
            {
                EquipmentId = equipmentId,
                Type = "WARNING",
                Message = $"온도 경고 수준: {data.Temperature:F1}°C",
                Timestamp = DateTime.Now
            }, cancellationToken);
        }

        // 압력 알람 확인
        if (data.Pressure > 2.0)
        {
            await _hubContext.Clients.All.SendAsync("AlarmTriggered", new
            {
                EquipmentId = equipmentId,
                Type = "CRITICAL",
                Message = $"압력 위험 수준: {data.Pressure:F3} Torr",
                Timestamp = DateTime.Now
            }, cancellationToken);
        }
    }

    public override async Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("장비 데이터 브로드캐스트 서비스 중지");
        await _dataCollector.StopAsync();
        await base.StopAsync(cancellationToken);
    }
}
```

### 🖥️ SignalR 클라이언트 구현

```csharp
// SignalR 클라이언트 서비스
public class SignalRClientService : IDisposable
{
    private HubConnection _connection;
    private readonly ILogger<SignalRClientService> _logger;
    private bool _isConnected;

    public event EventHandler<EquipmentDataReceivedEventArgs> EquipmentDataReceived;
    public event EventHandler<AlarmEventArgs> AlarmReceived;
    public event EventHandler<bool> ConnectionStateChanged;

    public bool IsConnected => _isConnected;

    public SignalRClientService(ILogger<SignalRClientService> logger = null)
    {
        _logger = logger ?? NullLogger<SignalRClientService>.Instance;
    }

    public async Task ConnectAsync(string serverUrl)
    {
        try
        {
            _connection = new HubConnectionBuilder()
                .WithUrl(serverUrl)
                .WithAutomaticReconnect(new[] { TimeSpan.Zero, TimeSpan.FromSeconds(2), TimeSpan.FromSeconds(10), TimeSpan.FromSeconds(30) })
                .ConfigureLogging(logging =>
                {
                    logging.SetMinimumLevel(LogLevel.Information);
                })
                .Build();

            // 이벤트 핸들러 등록
            RegisterEventHandlers();

            // 연결 시작
            await _connection.StartAsync();

            _isConnected = true;
            ConnectionStateChanged?.Invoke(this, true);

            _logger.LogInformation($"SignalR 서버에 연결됨: {serverUrl}");

            // 모든 장비 데이터 구독
            await _connection.InvokeAsync("SubscribeToAllEquipment");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "SignalR 연결 실패");
            _isConnected = false;
            ConnectionStateChanged?.Invoke(this, false);
            throw;
        }
    }

    private void RegisterEventHandlers()
    {
        // 장비 데이터 수신
        _connection.On<string, EquipmentData>("EquipmentDataUpdate", (equipmentId, data) =>
        {
            EquipmentDataReceived?.Invoke(this, new EquipmentDataReceivedEventArgs(equipmentId, data));
        });

        // 알람 수신
        _connection.On<object>("AlarmTriggered", (alarmData) =>
        {
            try
            {
                var json = JsonSerializer.Serialize(alarmData);
                var alarm = JsonSerializer.Deserialize<AlarmData>(json);
                AlarmReceived?.Invoke(this, new AlarmEventArgs(alarm));
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "알람 데이터 파싱 오류");
            }
        });

        // 구독 확인
        _connection.On<string>("SubscriptionConfirmed", (equipmentId) =>
        {
            _logger.LogInformation($"장비 구독 확인: {equipmentId}");
        });

        // 연결 상태 변경 이벤트
        _connection.Closed += async (error) =>
        {
            _isConnected = false;
            ConnectionStateChanged?.Invoke(this, false);
            _logger.LogWarning($"SignalR 연결 종료: {error?.Message}");
        };

        _connection.Reconnecting += (error) =>
        {
            _isConnected = false;
            ConnectionStateChanged?.Invoke(this, false);
            _logger.LogInformation("SignalR 재연결 시도 중...");
            return Task.CompletedTask;
        };

        _connection.Reconnected += async (connectionId) =>
        {
            _isConnected = true;
            ConnectionStateChanged?.Invoke(this, true);
            _logger.LogInformation($"SignalR 재연결 성공: {connectionId}");

            // 재연결 후 구독 복원
            await _connection.InvokeAsync("SubscribeToAllEquipment");
        };
    }

    public async Task SubscribeToEquipmentAsync(string equipmentId)
    {
        if (_connection?.State == HubConnectionState.Connected)
        {
            await _connection.InvokeAsync("SubscribeToEquipment", equipmentId);
        }
    }

    public async Task UnsubscribeFromEquipmentAsync(string equipmentId)
    {
        if (_connection?.State == HubConnectionState.Connected)
        {
            await _connection.InvokeAsync("UnsubscribeFromEquipment", equipmentId);
        }
    }

    public async Task DisconnectAsync()
    {
        if (_connection != null)
        {
            await _connection.DisposeAsync();
            _isConnected = false;
            ConnectionStateChanged?.Invoke(this, false);
            _logger.LogInformation("SignalR 연결 해제됨");
        }
    }

    public void Dispose()
    {
        _connection?.DisposeAsync();
    }
}

public class AlarmData
{
    public string EquipmentId { get; set; }
    public string Type { get; set; }
    public string Message { get; set; }
    public DateTime Timestamp { get; set; }
}

public class AlarmEventArgs : EventArgs
{
    public AlarmData Alarm { get; }

    public AlarmEventArgs(AlarmData alarm)
    {
        Alarm = alarm;
    }
}
```

</div>

---

## 실습 4: 실시간 차트 구현

<div style="margin: 2rem 0;">

### 📊 LiveCharts를 활용한 실시간 차트

```csharp
// 실시간 차트 ViewModel
public class RealTimeChartViewModel : BaseViewModel, IDisposable
{
    private readonly SignalRClientService _signalRClient;
    private readonly object _chartLock = new object();

    public SeriesCollection TemperatureSeriesCollection { get; set; }
    public SeriesCollection PressureSeriesCollection { get; set; }
    public string[] TimeLabels { get; set; }
    public Func<double, string> TemperatureFormatter { get; set; }
    public Func<double, string> PressureFormatter { get; set; }

    private readonly int _maxDataPoints = 50;
    private readonly Queue<string> _timeQueue;
    private readonly Dictionary<string, Queue<double>> _temperatureQueues;
    private readonly Dictionary<string, Queue<double>> _pressureQueues;

    public RealTimeChartViewModel(SignalRClientService signalRClient)
    {
        _signalRClient = signalRClient;
        _timeQueue = new Queue<string>();
        _temperatureQueues = new Dictionary<string, Queue<double>>();
        _pressureQueues = new Dictionary<string, Queue<double>>();

        InitializeCharts();
        InitializeFormatters();

        _signalRClient.EquipmentDataReceived += OnEquipmentDataReceived;
    }

    private void InitializeCharts()
    {
        var equipmentIds = new[] { "CVD-001", "PVD-002", "ETCH-003", "CMP-004" };
        var colors = new[] { "#E74C3C", "#3498DB", "#2ECC71", "#F39C12" };

        TemperatureSeriesCollection = new SeriesCollection();
        PressureSeriesCollection = new SeriesCollection();

        for (int i = 0; i < equipmentIds.Length; i++)
        {
            var equipmentId = equipmentIds[i];
            var color = colors[i];

            // 온도 차트 시리즈
            TemperatureSeriesCollection.Add(new LineSeries
            {
                Title = equipmentId,
                Values = new ChartValues<double>(),
                Stroke = (Brush)new BrushConverter().ConvertFrom(color),
                Fill = Brushes.Transparent,
                StrokeThickness = 2,
                PointGeometry = null // 포인트 숨기기 (성능 향상)
            });

            // 압력 차트 시리즈
            PressureSeriesCollection.Add(new LineSeries
            {
                Title = equipmentId,
                Values = new ChartValues<double>(),
                Stroke = (Brush)new BrushConverter().ConvertFrom(color),
                Fill = Brushes.Transparent,
                StrokeThickness = 2,
                PointGeometry = null
            });

            // 데이터 큐 초기화
            _temperatureQueues[equipmentId] = new Queue<double>();
            _pressureQueues[equipmentId] = new Queue<double>();
        }

        // 초기 시간 레이블
        TimeLabels = new string[_maxDataPoints];
        for (int i = 0; i < _maxDataPoints; i++)
        {
            TimeLabels[i] = "";
        }
    }

    private void InitializeFormatters()
    {
        TemperatureFormatter = value => $"{value:F1}°C";
        PressureFormatter = value => $"{value:F3} Torr";
    }

    private void OnEquipmentDataReceived(object sender, EquipmentDataReceivedEventArgs e)
    {
        Application.Current.Dispatcher.InvokeAsync(() =>
        {
            UpdateChartData(e.EquipmentId, e.Data);
        });
    }

    private void UpdateChartData(string equipmentId, EquipmentData data)
    {
        lock (_chartLock)
        {
            // 시간 레이블 업데이트
            var timeLabel = data.Timestamp.ToString("HH:mm:ss");
            _timeQueue.Enqueue(timeLabel);

            if (_timeQueue.Count > _maxDataPoints)
            {
                _timeQueue.Dequeue();
            }

            // 온도 데이터 업데이트
            if (_temperatureQueues.ContainsKey(equipmentId))
            {
                _temperatureQueues[equipmentId].Enqueue(data.Temperature);

                if (_temperatureQueues[equipmentId].Count > _maxDataPoints)
                {
                    _temperatureQueues[equipmentId].Dequeue();
                }
            }

            // 압력 데이터 업데이트
            if (_pressureQueues.ContainsKey(equipmentId))
            {
                _pressureQueues[equipmentId].Enqueue(data.Pressure);

                if (_pressureQueues[equipmentId].Count > _maxDataPoints)
                {
                    _pressureQueues[equipmentId].Dequeue();
                }
            }

            // 차트 업데이트
            UpdateChartSeries();
            UpdateTimeLabels();
        }
    }

    private void UpdateChartSeries()
    {
        var equipmentIds = new[] { "CVD-001", "PVD-002", "ETCH-003", "CMP-004" };

        for (int i = 0; i < equipmentIds.Length; i++)
        {
            var equipmentId = equipmentIds[i];

            // 온도 시리즈 업데이트
            if (i < TemperatureSeriesCollection.Count && _temperatureQueues.ContainsKey(equipmentId))
            {
                var temperatureSeries = TemperatureSeriesCollection[i];
                temperatureSeries.Values.Clear();

                foreach (var temp in _temperatureQueues[equipmentId])
                {
                    temperatureSeries.Values.Add(temp);
                }
            }

            // 압력 시리즈 업데이트
            if (i < PressureSeriesCollection.Count && _pressureQueues.ContainsKey(equipmentId))
            {
                var pressureSeries = PressureSeriesCollection[i];
                pressureSeries.Values.Clear();

                foreach (var pressure in _pressureQueues[equipmentId])
                {
                    pressureSeries.Values.Add(pressure);
                }
            }
        }
    }

    private void UpdateTimeLabels()
    {
        var labels = _timeQueue.ToArray();

        // 배열 크기를 _maxDataPoints로 맞춤
        TimeLabels = new string[_maxDataPoints];

        for (int i = 0; i < _maxDataPoints; i++)
        {
            if (i < labels.Length)
            {
                TimeLabels[i] = labels[i];
            }
            else
            {
                TimeLabels[i] = "";
            }
        }

        OnPropertyChanged(nameof(TimeLabels));
    }

    public void ClearChartData()
    {
        lock (_chartLock)
        {
            _timeQueue.Clear();

            foreach (var queue in _temperatureQueues.Values)
            {
                queue.Clear();
            }

            foreach (var queue in _pressureQueues.Values)
            {
                queue.Clear();
            }

            foreach (var series in TemperatureSeriesCollection)
            {
                series.Values.Clear();
            }

            foreach (var series in PressureSeriesCollection)
            {
                series.Values.Clear();
            }

            TimeLabels = new string[_maxDataPoints];
            OnPropertyChanged(nameof(TimeLabels));
        }
    }

    public void Dispose()
    {
        if (_signalRClient != null)
        {
            _signalRClient.EquipmentDataReceived -= OnEquipmentDataReceived;
        }
    }
}
```

### 🎨 차트 XAML 구현

```xml
<!-- RealTimeChartView.xaml -->
<UserControl x:Class="SemiconductorHMI.Views.RealTimeChartView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:lvc="clr-namespace:LiveCharts.Wpf;assembly=LiveCharts.Wpf">

    <Grid Margin="10">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>
            <RowDefinition Height="*"/>
            <RowDefinition Height="*"/>
        </Grid.RowDefinitions>

        <!-- 차트 제어 패널 -->
        <Border Grid.Row="0" Background="#2C3E50" CornerRadius="5" Padding="15" Margin="0,0,0,10">
            <Grid>
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="Auto"/>
                </Grid.ColumnDefinitions>

                <StackPanel Grid.Column="0" Orientation="Horizontal" VerticalAlignment="Center">
                    <TextBlock Text="실시간 차트" FontSize="18" FontWeight="Bold" Foreground="White" Margin="0,0,20,0"/>
                    <TextBlock Text="• 50개 데이터 포인트 표시" FontSize="12" Foreground="#BDC3C7" VerticalAlignment="Center"/>
                </StackPanel>

                <Button Grid.Column="1"
                        Command="{Binding ClearChartCommand}"
                        Background="#E74C3C" Foreground="White"
                        Padding="12,6" BorderThickness="0" CornerRadius="3">
                    <StackPanel Orientation="Horizontal">
                        <TextBlock Text="🗑" FontSize="12" Margin="0,0,5,0"/>
                        <TextBlock Text="차트 초기화"/>
                    </StackPanel>
                </Button>
            </Grid>
        </Border>

        <!-- 온도 차트 -->
        <Border Grid.Row="1" Background="White" CornerRadius="5"
                BorderBrush="#E0E0E0" BorderThickness="1" Margin="0,0,0,5">
            <Grid Margin="15">
                <Grid.RowDefinitions>
                    <RowDefinition Height="Auto"/>
                    <RowDefinition Height="*"/>
                </Grid.RowDefinitions>

                <!-- 차트 제목 -->
                <TextBlock Grid.Row="0" Text="장비 온도 실시간 모니터링"
                           FontSize="16" FontWeight="Bold" Margin="0,0,0,10"/>

                <!-- 온도 차트 -->
                <lvc:CartesianChart Grid.Row="1"
                                    Series="{Binding TemperatureSeriesCollection}"
                                    LegendLocation="Bottom"
                                    AnimationsSpeed="0:0:0.5">
                    <lvc:CartesianChart.AxisX>
                        <lvc:Axis Title="시간"
                                  Labels="{Binding TimeLabels}"
                                  Foreground="#666666">
                            <lvc:Axis.Separator>
                                <lvc:Separator StrokeThickness="1" StrokeDashArray="2" Stroke="#E0E0E0"/>
                            </lvc:Axis.Separator>
                        </lvc:Axis>
                    </lvc:CartesianChart.AxisX>
                    <lvc:CartesianChart.AxisY>
                        <lvc:Axis Title="온도 (°C)"
                                  LabelFormatter="{Binding TemperatureFormatter}"
                                  Foreground="#666666">
                            <lvc:Axis.Separator>
                                <lvc:Separator StrokeThickness="1" StrokeDashArray="2" Stroke="#E0E0E0"/>
                            </lvc:Axis.Separator>
                        </lvc:Axis>
                    </lvc:CartesianChart.AxisY>
                </lvc:CartesianChart>
            </Grid>
        </Border>

        <!-- 압력 차트 -->
        <Border Grid.Row="2" Background="White" CornerRadius="5"
                BorderBrush="#E0E0E0" BorderThickness="1" Margin="0,5,0,0">
            <Grid Margin="15">
                <Grid.RowDefinitions>
                    <RowDefinition Height="Auto"/>
                    <RowDefinition Height="*"/>
                </Grid.RowDefinitions>

                <!-- 차트 제목 -->
                <TextBlock Grid.Row="0" Text="장비 압력 실시간 모니터링"
                           FontSize="16" FontWeight="Bold" Margin="0,0,0,10"/>

                <!-- 압력 차트 -->
                <lvc:CartesianChart Grid.Row="1"
                                    Series="{Binding PressureSeriesCollection}"
                                    LegendLocation="Bottom"
                                    AnimationsSpeed="0:0:0.5">
                    <lvc:CartesianChart.AxisX>
                        <lvc:Axis Title="시간"
                                  Labels="{Binding TimeLabels}"
                                  Foreground="#666666">
                            <lvc:Axis.Separator>
                                <lvc:Separator StrokeThickness="1" StrokeDashArray="2" Stroke="#E0E0E0"/>
                            </lvc:Axis.Separator>
                        </lvc:Axis>
                    </lvc:CartesianChart.AxisX>
                    <lvc:CartesianChart.AxisY>
                        <lvc:Axis Title="압력 (Torr)"
                                  LabelFormatter="{Binding PressureFormatter}"
                                  Foreground="#666666">
                            <lvc:Axis.Separator>
                                <lvc:Separator StrokeThickness="1" StrokeDashArray="2" Stroke="#E0E0E0"/>
                            </lvc:Axis.Separator>
                        </lvc:Axis>
                    </lvc:CartesianChart.AxisY>
                </lvc:CartesianChart>
            </Grid>
        </Border>
    </Grid>
</UserControl>
```

</div>

---

