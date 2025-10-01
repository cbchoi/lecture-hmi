# 📖 이론 강의 (45분)

---

## .NET 멀티스레딩 모델

<div style="margin: 2rem 0;">

### 🧵 스레딩 진화 과정

<div style="background: #e3f2fd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2196f3; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #0d47a1;">Thread (초기):</strong> 저수준 스레드 관리, 복잡한 동기화</li>
        <li><strong style="color: #0d47a1;">ThreadPool (.NET 2.0):</strong> 스레드 풀 관리, 효율성 향상</li>
        <li><strong style="color: #0d47a1;">Task (.NET 4.0):</strong> 고수준 추상화, 조합 가능성</li>
        <li><strong style="color: #0d47a1;">async/await (.NET 4.5):</strong> 비동기 패턴 단순화</li>
    </ul>
</div>

### ⚡ 비동기 vs 병렬 처리

<div style="background: #f3e5f5; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #9c27b0; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #4a148c;">비동기 (Asynchronous):</strong> I/O 대기 시간 활용, 단일 스레드</li>
        <li><strong style="color: #4a148c;">병렬 (Parallel):</strong> CPU 집약적 작업, 다중 스레드</li>
        <li><strong style="color: #4a148c;">동시성 (Concurrency):</strong> 논리적 동시 실행</li>
        <li><strong style="color: #4a148c;">병행성 (Parallelism):</strong> 물리적 동시 실행</li>
    </ul>
</div>

### 💡 반도체 환경에서의 선택 기준

<div style="background: #fff3cd; padding: 1.5rem; border-radius: 8px; border: 1px solid #f39c12; margin: 1.5rem 0;">
    <p style="margin: 0; color: #856404; font-weight: 500; font-size: 1.1em;">
        ⚠️ 반도체 장비는 실시간성이 중요하므로 응답성을 위한 비동기와 처리량을 위한 병렬 처리를 적절히 조합해야 합니다.
    </p>
</div>

</div>

---

## Task와 async/await 패턴

<div style="margin: 2rem 0;">

### 📋 Task 기본 개념

<div style="background: #e8f5e8; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #155724;">Task:</strong> 비동기 작업의 표현, 결과가 없는 작업</li>
        <li><strong style="color: #155724;">Task&lt;T&gt;:</strong> 결과값을 반환하는 비동기 작업</li>
        <li><strong style="color: #155724;">TaskCompletionSource:</strong> 수동으로 Task 상태 제어</li>
        <li><strong style="color: #155724;">CancellationToken:</strong> 작업 취소 메커니즘</li>
    </ul>
</div>

### 💻 기본 Task 활용

```csharp
// 반도체 장비 데이터 수집 서비스
public class EquipmentDataCollector
{
    private readonly CancellationTokenSource _cancellationTokenSource;
    private readonly List<Task> _runningTasks;

    public EquipmentDataCollector()
    {
        _cancellationTokenSource = new CancellationTokenSource();
        _runningTasks = new List<Task>();
    }

    // 기본 Task 생성
    public Task StartDataCollectionAsync()
    {
        return Task.Run(async () =>
        {
            while (!_cancellationTokenSource.Token.IsCancellationRequested)
            {
                await CollectSensorDataAsync();
                await Task.Delay(1000, _cancellationTokenSource.Token);
            }
        }, _cancellationTokenSource.Token);
    }

    // async/await 패턴
    public async Task<EquipmentData> CollectSensorDataAsync()
    {
        var equipmentData = new EquipmentData();

        // 여러 센서에서 병렬로 데이터 수집
        var temperatureTask = ReadTemperatureAsync();
        var pressureTask = ReadPressureAsync();
        var flowRateTask = ReadFlowRateAsync();

        // 모든 센서 데이터 수집 완료 대기
        await Task.WhenAll(temperatureTask, pressureTask, flowRateTask);

        equipmentData.Temperature = await temperatureTask;
        equipmentData.Pressure = await pressureTask;
        equipmentData.FlowRate = await flowRateTask;
        equipmentData.Timestamp = DateTime.Now;

        return equipmentData;
    }

    // 시뮬레이션된 센서 읽기 (실제로는 하드웨어 통신)
    private async Task<double> ReadTemperatureAsync()
    {
        // 네트워크 지연 시뮬레이션
        await Task.Delay(Random.Shared.Next(50, 200));
        return 200 + Random.Shared.NextDouble() * 50;
    }

    private async Task<double> ReadPressureAsync()
    {
        await Task.Delay(Random.Shared.Next(30, 150));
        return 0.5 + Random.Shared.NextDouble() * 1.0;
    }

    private async Task<double> ReadFlowRateAsync()
    {
        await Task.Delay(Random.Shared.Next(40, 180));
        return 100 + Random.Shared.NextDouble() * 50;
    }

    // 취소 및 정리
    public async Task StopAsync()
    {
        _cancellationTokenSource.Cancel();

        try
        {
            await Task.WhenAll(_runningTasks);
        }
        catch (OperationCanceledException)
        {
            // 예상된 취소 예외는 무시
        }
    }
}

public class EquipmentData
{
    public double Temperature { get; set; }
    public double Pressure { get; set; }
    public double FlowRate { get; set; }
    public DateTime Timestamp { get; set; }
}
```

### 🔒 스레드 안전성과 동기화

```csharp
// 스레드 안전한 데이터 저장소
public class ThreadSafeDataStore
{
    private readonly object _lock = new object();
    private readonly Queue<EquipmentData> _dataQueue;
    private readonly SemaphoreSlim _semaphore;

    public ThreadSafeDataStore(int maxCapacity = 1000)
    {
        _dataQueue = new Queue<EquipmentData>();
        _semaphore = new SemaphoreSlim(1, 1);
    }

    // lock 사용한 동기화
    public void AddData(EquipmentData data)
    {
        lock (_lock)
        {
            _dataQueue.Enqueue(data);

            // 큐 크기 제한
            while (_dataQueue.Count > 1000)
            {
                _dataQueue.Dequeue();
            }
        }
    }

    // SemaphoreSlim을 사용한 비동기 동기화
    public async Task<List<EquipmentData>> GetLatestDataAsync(int count)
    {
        await _semaphore.WaitAsync();
        try
        {
            lock (_lock)
            {
                return _dataQueue.TakeLast(count).ToList();
            }
        }
        finally
        {
            _semaphore.Release();
        }
    }

    // ConcurrentCollection 활용
    private readonly ConcurrentQueue<EquipmentData> _concurrentQueue
        = new ConcurrentQueue<EquipmentData>();

    public void AddDataConcurrent(EquipmentData data)
    {
        _concurrentQueue.Enqueue(data);

        // 크기 제한 (근사치)
        while (_concurrentQueue.Count > 1000)
        {
            _concurrentQueue.TryDequeue(out _);
        }
    }

    public List<EquipmentData> GetLatestDataConcurrent(int count)
    {
        var result = new List<EquipmentData>();
        var items = _concurrentQueue.ToArray();

        return items.TakeLast(count).ToList();
    }
}
```

</div>

---

## 실시간 통신 프로토콜

<div style="margin: 2rem 0;">

### 🌐 TCP/IP 소켓 프로그래밍

<div style="background: #e3f2fd; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #2196f3; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #0d47a1;">신뢰성:</strong> 연결 기반, 데이터 순서 보장</li>
        <li><strong style="color: #0d47a1;">성능:</strong> 낮은 오버헤드, 고속 전송</li>
        <li><strong style="color: #0d47a1;">제어:</strong> 세밀한 네트워크 제어 가능</li>
        <li><strong style="color: #0d47a1;">복잡성:</strong> 연결 관리 및 프로토콜 설계 필요</li>
    </ul>
</div>

### 💻 TCP 서버/클라이언트 구현

```csharp
// TCP 서버 (장비 데이터 송신)
public class EquipmentDataServer
{
    private TcpListener _listener;
    private readonly List<TcpClient> _clients;
    private readonly CancellationTokenSource _cancellationTokenSource;
    private bool _isRunning;

    public EquipmentDataServer(int port)
    {
        _listener = new TcpListener(IPAddress.Any, port);
        _clients = new List<TcpClient>();
        _cancellationTokenSource = new CancellationTokenSource();
    }

    public async Task StartAsync()
    {
        _listener.Start();
        _isRunning = true;

        Console.WriteLine($"장비 데이터 서버가 포트 {((IPEndPoint)_listener.LocalEndpoint).Port}에서 시작되었습니다.");

        // 클라이언트 연결 수락 태스크
        var acceptTask = AcceptClientsAsync(_cancellationTokenSource.Token);

        // 데이터 브로드캐스트 태스크
        var broadcastTask = BroadcastDataAsync(_cancellationTokenSource.Token);

        await Task.WhenAll(acceptTask, broadcastTask);
    }

    private async Task AcceptClientsAsync(CancellationToken cancellationToken)
    {
        while (!cancellationToken.IsCancellationRequested && _isRunning)
        {
            try
            {
                var tcpClient = await _listener.AcceptTcpClientAsync();

                lock (_clients)
                {
                    _clients.Add(tcpClient);
                }

                Console.WriteLine($"클라이언트 연결됨: {tcpClient.Client.RemoteEndPoint}");

                // 각 클라이언트를 별도 태스크에서 처리
                _ = Task.Run(() => HandleClientAsync(tcpClient, cancellationToken));
            }
            catch (ObjectDisposedException)
            {
                break;
            }
        }
    }

    private async Task HandleClientAsync(TcpClient client, CancellationToken cancellationToken)
    {
        var buffer = new byte[1024];
        var stream = client.GetStream();

        try
        {
            while (!cancellationToken.IsCancellationRequested && client.Connected)
            {
                var bytesRead = await stream.ReadAsync(buffer, 0, buffer.Length, cancellationToken);
                if (bytesRead == 0) break;

                // 클라이언트로부터 받은 메시지 처리
                var message = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                Console.WriteLine($"클라이언트 메시지: {message}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"클라이언트 처리 오류: {ex.Message}");
        }
        finally
        {
            lock (_clients)
            {
                _clients.Remove(client);
            }
            client.Close();
        }
    }

    private async Task BroadcastDataAsync(CancellationToken cancellationToken)
    {
        while (!cancellationToken.IsCancellationRequested && _isRunning)
        {
            // 장비 데이터 생성 (시뮬레이션)
            var data = new
            {
                EquipmentId = "CVD-001",
                Temperature = 250 + Random.Shared.NextDouble() * 10,
                Pressure = 0.8 + Random.Shared.NextDouble() * 0.2,
                Timestamp = DateTime.Now
            };

            var jsonData = JsonSerializer.Serialize(data);
            var dataBytes = Encoding.UTF8.GetBytes(jsonData + "\n");

            // 모든 연결된 클라이언트에게 브로드캐스트
            await BroadcastToAllClientsAsync(dataBytes);

            await Task.Delay(1000, cancellationToken);
        }
    }

    private async Task BroadcastToAllClientsAsync(byte[] data)
    {
        List<TcpClient> clientsCopy;

        lock (_clients)
        {
            clientsCopy = new List<TcpClient>(_clients);
        }

        var tasks = clientsCopy.Select(async client =>
        {
            try
            {
                if (client.Connected)
                {
                    await client.GetStream().WriteAsync(data, 0, data.Length);
                }
            }
            catch
            {
                // 연결 실패한 클라이언트는 목록에서 제거
                lock (_clients)
                {
                    _clients.Remove(client);
                }
            }
        });

        await Task.WhenAll(tasks);
    }

    public async Task StopAsync()
    {
        _isRunning = false;
        _cancellationTokenSource.Cancel();

        _listener?.Stop();

        lock (_clients)
        {
            foreach (var client in _clients)
            {
                client?.Close();
            }
            _clients.Clear();
        }
    }
}

// TCP 클라이언트 (HMI 애플리케이션)
public class EquipmentDataClient
{
    private TcpClient _client;
    private NetworkStream _stream;
    private readonly CancellationTokenSource _cancellationTokenSource;

    public event EventHandler<EquipmentDataReceivedEventArgs> DataReceived;

    public EquipmentDataClient()
    {
        _cancellationTokenSource = new CancellationTokenSource();
    }

    public async Task ConnectAsync(string serverAddress, int port)
    {
        _client = new TcpClient();
        await _client.ConnectAsync(serverAddress, port);
        _stream = _client.GetStream();

        Console.WriteLine($"서버에 연결됨: {serverAddress}:{port}");

        // 데이터 수신 태스크 시작
        _ = Task.Run(() => ReceiveDataAsync(_cancellationTokenSource.Token));
    }

    private async Task ReceiveDataAsync(CancellationToken cancellationToken)
    {
        var buffer = new byte[1024];
        var messageBuilder = new StringBuilder();

        try
        {
            while (!cancellationToken.IsCancellationRequested && _client.Connected)
            {
                var bytesRead = await _stream.ReadAsync(buffer, 0, buffer.Length, cancellationToken);
                if (bytesRead == 0) break;

                var data = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                messageBuilder.Append(data);

                // 개행 문자로 메시지 분리
                string[] messages = messageBuilder.ToString().Split('\n');

                for (int i = 0; i < messages.Length - 1; i++)
                {
                    if (!string.IsNullOrWhiteSpace(messages[i]))
                    {
                        ProcessReceivedMessage(messages[i]);
                    }
                }

                // 마지막 불완전한 메시지는 버퍼에 보관
                messageBuilder.Clear();
                if (!string.IsNullOrWhiteSpace(messages[messages.Length - 1]))
                {
                    messageBuilder.Append(messages[messages.Length - 1]);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"데이터 수신 오류: {ex.Message}");
        }
    }

    private void ProcessReceivedMessage(string jsonMessage)
    {
        try
        {
            var data = JsonSerializer.Deserialize<EquipmentDataMessage>(jsonMessage);
            DataReceived?.Invoke(this, new EquipmentDataReceivedEventArgs(data));
        }
        catch (Exception ex)
        {
            Console.WriteLine($"메시지 파싱 오류: {ex.Message}");
        }
    }

    public async Task DisconnectAsync()
    {
        _cancellationTokenSource.Cancel();
        _stream?.Close();
        _client?.Close();
    }
}

public class EquipmentDataMessage
{
    public string EquipmentId { get; set; }
    public double Temperature { get; set; }
    public double Pressure { get; set; }
    public DateTime Timestamp { get; set; }
}

public class EquipmentDataReceivedEventArgs : EventArgs
{
    public EquipmentDataMessage Data { get; }

    public EquipmentDataReceivedEventArgs(EquipmentDataMessage data)
    {
        Data = data;
    }
}
```

### 📡 SignalR 실시간 통신

<div style="background: #f3e5f5; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #9c27b0; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #4a148c;">추상화:</strong> 고수준 실시간 통신 라이브러리</li>
        <li><strong style="color: #4a148c;">자동 관리:</strong> 연결 관리, 재연결, 그룹 관리</li>
        <li><strong style="color: #4a148c;">스케일링:</strong> Redis 백플레인 지원</li>
        <li><strong style="color: #4a148c;">타입 안전성:</strong> 강타입 허브 지원</li>
    </ul>
</div>

</div>

---

## 성능 최적화 기법

<div style="margin: 2rem 0;">

### 🚀 메모리 관리 전략

<div style="background: #e8f5e8; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #28a745; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #155724;">객체 풀링:</strong> 반복 생성되는 객체의 재사용</li>
        <li><strong style="color: #155724;">메모리 스트림:</strong> 대용량 데이터의 효율적 처리</li>
        <li><strong style="color: #155724;">가비지 컬렉션 튜닝:</strong> GC 압박 최소화</li>
        <li><strong style="color: #155724;">스팬(Span) 활용:</strong> 제로 할당 데이터 처리</li>
    </ul>
</div>

### 💻 고성능 데이터 처리

```csharp
// 객체 풀을 활용한 고성능 데이터 처리
public class HighPerformanceDataProcessor
{
    private readonly ObjectPool<EquipmentData> _dataPool;
    private readonly ObjectPool<StringBuilder> _stringBuilderPool;
    private readonly Channel<EquipmentData> _dataChannel;

    public HighPerformanceDataProcessor()
    {
        // 객체 풀 설정
        var dataPoolPolicy = new DefaultPooledObjectPolicy<EquipmentData>();
        _dataPool = new DefaultObjectPool<EquipmentData>(dataPoolPolicy, 100);

        var stringBuilderPolicy = new StringBuilderPooledObjectPolicy();
        _stringBuilderPool = new DefaultObjectPool<StringBuilder>(stringBuilderPolicy, 50);

        // 채널 설정 (Producer-Consumer 패턴)
        var options = new BoundedChannelOptions(1000)
        {
            FullMode = BoundedChannelFullMode.Wait,
            SingleReader = false,
            SingleWriter = false
        };
        _dataChannel = Channel.CreateBounded<EquipmentData>(options);
    }

    // 제로 할당을 위한 Span 활용
    public ReadOnlySpan<byte> SerializeDataToSpan(EquipmentData data)
    {
        Span<byte> buffer = stackalloc byte[256];

        var written = 0;
        written += WriteDouble(buffer.Slice(written), data.Temperature);
        written += WriteDouble(buffer.Slice(written), data.Pressure);
        written += WriteDouble(buffer.Slice(written), data.FlowRate);
        written += WriteLong(buffer.Slice(written), data.Timestamp.Ticks);

        return buffer.Slice(0, written);
    }

    private int WriteDouble(Span<byte> buffer, double value)
    {
        return BitConverter.TryWriteBytes(buffer, value) ? sizeof(double) : 0;
    }

    private int WriteLong(Span<byte> buffer, long value)
    {
        return BitConverter.TryWriteBytes(buffer, value) ? sizeof(long) : 0;
    }

    // 채널을 활용한 Producer-Consumer 패턴
    public async Task ProduceDataAsync(CancellationToken cancellationToken)
    {
        var writer = _dataChannel.Writer;

        try
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                var data = _dataPool.Get();
                try
                {
                    // 데이터 수집 (시뮬레이션)
                    data.Temperature = 250 + Random.Shared.NextDouble() * 10;
                    data.Pressure = 0.8 + Random.Shared.NextDouble() * 0.2;
                    data.FlowRate = 100 + Random.Shared.NextDouble() * 20;
                    data.Timestamp = DateTime.Now;

                    await writer.WriteAsync(data, cancellationToken);
                }
                catch
                {
                    // 오류 발생 시 객체를 풀에 반환
                    _dataPool.Return(data);
                    throw;
                }

                await Task.Delay(100, cancellationToken);
            }
        }
        finally
        {
            writer.Complete();
        }
    }

    public async Task ConsumeDataAsync(CancellationToken cancellationToken)
    {
        var reader = _dataChannel.Reader;

        await foreach (var data in reader.ReadAllAsync(cancellationToken))
        {
            try
            {
                // 데이터 처리
                await ProcessDataAsync(data);
            }
            finally
            {
                // 처리 완료 후 객체를 풀에 반환
                _dataPool.Return(data);
            }
        }
    }

    private async Task ProcessDataAsync(EquipmentData data)
    {
        // StringBuilder 풀 활용
        var sb = _stringBuilderPool.Get();
        try
        {
            sb.Clear();
            sb.AppendLine($"Equipment Data Processing:");
            sb.AppendLine($"Temperature: {data.Temperature:F2}°C");
            sb.AppendLine($"Pressure: {data.Pressure:F3} Torr");
            sb.AppendLine($"Flow Rate: {data.FlowRate:F1} sccm");
            sb.AppendLine($"Timestamp: {data.Timestamp:yyyy-MM-dd HH:mm:ss.fff}");

            // 로깅 또는 다른 처리
            Console.WriteLine(sb.ToString());

            // 비동기 I/O 시뮬레이션
            await Task.Delay(1);
        }
        finally
        {
            _stringBuilderPool.Return(sb);
        }
    }
}

// 커스텀 풀 정책
public class DefaultPooledObjectPolicy<T> : IPooledObjectPolicy<T> where T : new()
{
    public T Create() => new T();

    public bool Return(T obj)
    {
        // 객체 상태 초기화
        if (obj is EquipmentData data)
        {
            data.Temperature = 0;
            data.Pressure = 0;
            data.FlowRate = 0;
            data.Timestamp = default;
        }
        return true;
    }
}
```

### 📊 성능 모니터링

```csharp
// 성능 카운터를 활용한 모니터링
public class PerformanceMonitor
{
    private readonly PerformanceCounter _cpuCounter;
    private readonly PerformanceCounter _memoryCounter;
    private readonly Timer _monitoringTimer;
    private long _processedDataCount;
    private DateTime _lastResetTime;

    public event EventHandler<PerformanceMetrics> MetricsUpdated;

    public PerformanceMonitor()
    {
        _cpuCounter = new PerformanceCounter("Processor", "% Processor Time", "_Total");
        _memoryCounter = new PerformanceCounter("Memory", "Available MBytes");

        _lastResetTime = DateTime.Now;

        // 5초마다 성능 지표 수집
        _monitoringTimer = new Timer(CollectMetrics, null,
            TimeSpan.FromSeconds(5), TimeSpan.FromSeconds(5));
    }

    public void IncrementProcessedData()
    {
        Interlocked.Increment(ref _processedDataCount);
    }

    private void CollectMetrics(object state)
    {
        var now = DateTime.Now;
        var elapsed = now - _lastResetTime;
        var currentCount = Interlocked.Read(ref _processedDataCount);

        var metrics = new PerformanceMetrics
        {
            CpuUsage = _cpuCounter.NextValue(),
            AvailableMemoryMB = _memoryCounter.NextValue(),
            DataProcessingRate = currentCount / elapsed.TotalSeconds,
            ProcessedDataCount = currentCount,
            Timestamp = now
        };

        MetricsUpdated?.Invoke(this, metrics);

        // 카운터 리셋
        Interlocked.Exchange(ref _processedDataCount, 0);
        _lastResetTime = now;
    }

    public void Dispose()
    {
        _monitoringTimer?.Dispose();
        _cpuCounter?.Dispose();
        _memoryCounter?.Dispose();
    }
}

public class PerformanceMetrics
{
    public float CpuUsage { get; set; }
    public float AvailableMemoryMB { get; set; }
    public double DataProcessingRate { get; set; }
    public long ProcessedDataCount { get; set; }
    public DateTime Timestamp { get; set; }
}
```

</div>

---

