# C# 실시간 데이터 처리 및 통신
> 반도체 장비의 실시간 모니터링을 위한 고성능 데이터 처리 시스템

---

## 📋 오늘의 학습 목표

<div style="background: #f8f9fa; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #007bff; margin: 1rem 0;">
    <ul style="margin: 0; line-height: 1.8;">
        <li><strong style="color: #1a365d;">멀티스레딩:</strong> 안전하고 효율적인 비동기 프로그래밍 마스터</li>
        <li><strong style="color: #1a365d;">실시간 통신:</strong> TCP/IP, SignalR을 활용한 데이터 스트리밍</li>
        <li><strong style="color: #1a365d;">데이터 처리:</strong> 대용량 센서 데이터의 실시간 분석</li>
        <li><strong style="color: #1a365d;">성능 최적화:</strong> 24/7 연속 운영을 위한 메모리 관리</li>
    </ul>
</div>

---

## 🗺️ 강의 진행 순서

<div style="display: flex; flex-direction: column; gap: 1rem; margin: 1.5rem 0;">
    <div style="display: flex; align-items: center; background: #e8f5e8; padding: 1rem; border-radius: 8px;">
        <div style="background: #28a745; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">1</div>
        <span style="color: #155724;"><strong>이론 (45분):</strong> 멀티스레딩과 비동기 프로그래밍</span>
    </div>
    <div style="display: flex; align-items: center; background: #e3f2fd; padding: 1rem; border-radius: 8px;">
        <div style="background: #2196f3; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">2</div>
        <span style="color: #0d47a1;"><strong>기초 실습 (45분):</strong> Timer 기반 데이터 수집</span>
    </div>
    <div style="display: flex; align-items: center; background: #f3e5f5; padding: 1rem; border-radius: 8px;">
        <div style="background: #9c27b0; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">3</div>
        <span style="color: #4a148c;"><strong>심화 실습 (45분):</strong> 실시간 통신 및 차트</span>
    </div>
    <div style="display: flex; align-items: center; background: #fff3cd; padding: 1rem; border-radius: 8px;">
        <div style="background: #f39c12; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">4</div>
        <span style="color: #856404;"><strong>Hands-on (45분):</strong> 종합 실시간 모니터링 시스템</span>
    </div>
</div>

---

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

# 🚀 심화 실습 (45분)

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

# 🎯 Hands-on 프로젝트 (45분)

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

</div>