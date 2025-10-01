# 🔧 이론 강의: 테스트 전략 및 CI/CD

---

## 소프트웨어 테스팅 원칙

### 📊 Test Pyramid (테스트 피라미드)

**테스트 전략의 기본 원칙**

<div class="grid grid-cols-2 gap-8">
<div>

```
      /\
     /  \  E2E Tests
    /____\  (UI Tests)
   /      \
  / Integration \
 /    Tests      \
/___________________\
/                   \
/   Unit Tests      \
/_____________________\
```

**각 계층의 특징**:

```csharp
// Unit Test (70-80%)
[TestMethod]
public void CalculateDiscount_WithValidInput_ReturnsCorrectValue()
{
    // Arrange
    var calculator = new PriceCalculator();

    // Act
    var result = calculator.CalculateDiscount(100, 0.1);

    // Assert
    Assert.AreEqual(10.0, result);
}

// Integration Test (15-20%)
[TestMethod]
public async Task SaveEquipmentData_WithDatabase_PersistsCorrectly()
{
    // Arrange
    var repository = new EquipmentRepository(_dbContext);
    var equipment = new Equipment { Id = "E001", Name = "Etcher" };

    // Act
    await repository.SaveAsync(equipment);

    // Assert
    var saved = await repository.GetByIdAsync("E001");
    Assert.IsNotNull(saved);
    Assert.AreEqual("Etcher", saved.Name);
}

// E2E Test (5-10%)
[TestMethod]
public async Task UserCanStartEquipment_ThroughUI()
{
    // Selenium WebDriver로 UI 테스트
    await _driver.Navigate().GoToUrl("/equipment");
    await _driver.FindElement(By.Id("startButton")).Click();

    var status = await _driver.FindElement(By.Id("status")).Text;
    Assert.AreEqual("Running", status);
}
```

</div>
<div>

**Test Pyramid 원칙**:

**Unit Tests (기반)**:
- 가장 많은 수 (70-80%)
- 빠른 실행 (밀리초 단위)
- 격리된 테스트
- 낮은 유지보수 비용
- 높은 안정성

**Integration Tests (중간)**:
- 중간 규모 (15-20%)
- 여러 컴포넌트 통합
- DB, 파일, 네트워크 등 실제 리소스 사용
- 적당한 실행 시간 (초 단위)
- 중간 유지보수 비용

**E2E Tests (정점)**:
- 소수 (5-10%)
- 전체 시스템 검증
- 사용자 시나리오 테스트
- 느린 실행 (분 단위)
- 높은 유지보수 비용
- 불안정할 수 있음 (flaky tests)

**Anti-Pattern (Ice Cream Cone)**:
```
  __________
 /          \
|  Unit Tests |  ← 소수
|____________|
 \          /
  \ E2E    /    ← 다수 (문제!)
   \______/
```
- E2E에 의존하면 느리고 불안정
- 단위 테스트 부족으로 디버깅 어려움

**반도체 HMI에서의 적용**:
- Unit: 비즈니스 로직, 계산, 변환
- Integration: DB 저장, 센서 통신
- E2E: 전체 워크플로우 (장비 시작→데이터 수집→알람)

</div>
</div>

---

### 🔄 Test-Driven Development (TDD)

**Red-Green-Refactor 사이클**

<div class="grid grid-cols-2 gap-8">
<div>

**TDD 워크플로우**:

```
1. RED    →  2. GREEN  →  3. REFACTOR
(실패하는    (테스트를      (코드 개선)
 테스트 작성)  통과시킴)         ↓
    ↑                           |
    ←←←←←←←←←←←←←←←←←←←←←←←←←←←←
```

**Step 1: RED - 실패하는 테스트 작성**

```csharp
[TestClass]
public class TemperatureConverterTests
{
    [TestMethod]
    public void CelsiusToFahrenheit_WithZero_Returns32()
    {
        // Arrange
        var converter = new TemperatureConverter();

        // Act
        var result = converter.CelsiusToFahrenheit(0);

        // Assert
        Assert.AreEqual(32.0, result);
    }

    [TestMethod]
    public void CelsiusToFahrenheit_With100_Returns212()
    {
        var converter = new TemperatureConverter();
        var result = converter.CelsiusToFahrenheit(100);
        Assert.AreEqual(212.0, result);
    }
}

// 이 시점에서 TemperatureConverter 클래스가 없으므로
// 컴파일 에러 또는 테스트 실패
```

**Step 2: GREEN - 최소한의 코드로 통과**

```csharp
public class TemperatureConverter
{
    public double CelsiusToFahrenheit(double celsius)
    {
        // 가장 간단한 구현으로 테스트 통과
        return celsius * 9.0 / 5.0 + 32.0;
    }
}

// 테스트 통과! ✅
```

</div>
<div>

**TDD의 핵심 원칙**:

**1. 실패하는 테스트 먼저**:
- 구현 전에 테스트 작성
- 요구사항을 테스트 코드로 명세
- 컴파일 에러도 "실패"로 간주

**2. 최소한의 코드**:
- 테스트를 통과시키는 최소 코드
- Over-engineering 방지
- YAGNI (You Aren't Gonna Need It)

**3. Refactor (리팩터링)**:
- 테스트가 통과한 후 개선
- 중복 제거, 명확성 향상
- 테스트가 안전망 역할

**Step 3: REFACTOR - 코드 개선**

```csharp
public class TemperatureConverter
{
    private const double CelsiusToFahrenheitFactor = 9.0 / 5.0;
    private const double FahrenheitOffset = 32.0;

    public double CelsiusToFahrenheit(double celsius)
    {
        if (double.IsNaN(celsius) || double.IsInfinity(celsius))
        {
            throw new ArgumentException(
                "Invalid temperature value", nameof(celsius));
        }

        return celsius * CelsiusToFahrenheitFactor
            + FahrenheitOffset;
    }

    public double FahrenheitToCelsius(double fahrenheit)
    {
        if (double.IsNaN(fahrenheit) || double.IsInfinity(fahrenheit))
        {
            throw new ArgumentException(
                "Invalid temperature value", nameof(fahrenheit));
        }

        return (fahrenheit - FahrenheitOffset)
            / CelsiusToFahrenheitFactor;
    }
}

// 테스트 여전히 통과! ✅
// 더 명확하고 확장 가능한 코드
```

**TDD의 장점**:
- 설계 개선 (테스트 가능한 코드 = 좋은 설계)
- 높은 코드 커버리지 (자동)
- 리그레션 방지
- 문서화 (테스트가 사용 예시)
- 자신감 있는 리팩터링

**반도체 HMI에서의 TDD**:
```csharp
// 1. RED: 알람 로직 테스트 작성
[TestMethod]
public void CheckTemperature_AboveThreshold_TriggersAlarm()
{
    var alarmSystem = new AlarmSystem();
    var triggered = alarmSystem.CheckTemperature(250.0, 200.0);
    Assert.IsTrue(triggered);
}

// 2. GREEN: 최소 구현
public bool CheckTemperature(double current, double threshold)
{
    return current > threshold;
}

// 3. REFACTOR: 히스테리시스 추가
public bool CheckTemperature(double current, double threshold)
{
    const double Hysteresis = 5.0;
    if (current > threshold)
    {
        _alarmTriggered = true;
    }
    else if (current < threshold - Hysteresis)
    {
        _alarmTriggered = false;
    }
    return _alarmTriggered;
}
```

</div>
</div>

---

### 🎭 Behavior-Driven Development (BDD)

**Given-When-Then 패턴**

<div class="grid grid-cols-2 gap-8">
<div>

**BDD 핵심 개념**:
- 비즈니스 가치 중심 테스트
- 자연어로 시나리오 작성
- 개발자-QA-비즈니스 팀 협업

**SpecFlow를 활용한 BDD**:

```gherkin
# EquipmentControl.feature
Feature: Equipment Control
  As a fab operator
  I want to control equipment through HMI
  So that I can manage production processes

Scenario: Starting idle equipment
  Given the equipment is in "Idle" state
  And the equipment has no alarms
  When the operator presses the "Start" button
  Then the equipment state should be "Running"
  And the start time should be recorded
  And a notification should be sent to supervisors

Scenario: Cannot start equipment with active alarm
  Given the equipment is in "Idle" state
  And the equipment has a "High Temperature" alarm
  When the operator presses the "Start" button
  Then the equipment state should remain "Idle"
  And an error message "Cannot start with active alarms" should be displayed
  And no notification should be sent

Scenario: Emergency stop during operation
  Given the equipment is in "Running" state
  And the process has been running for "5" minutes
  When the operator presses the "Emergency Stop" button
  Then the equipment state should be "Emergency Stopped"
  And all recipes should be aborted
  And an emergency alert should be sent immediately
  And the equipment should be locked for "30" minutes
```

</div>
<div>

**Step Definitions (C# 구현)**:

```csharp
[Binding]
public class EquipmentControlSteps
{
    private Equipment _equipment;
    private EquipmentController _controller;
    private string _lastErrorMessage;
    private bool _notificationSent;

    [Given(@"the equipment is in ""(.*)"" state")]
    public void GivenTheEquipmentIsInState(string state)
    {
        _equipment = new Equipment
        {
            Id = "TEST001",
            State = Enum.Parse<EquipmentState>(state)
        };
        _controller = new EquipmentController(_equipment);
    }

    [Given(@"the equipment has no alarms")]
    public void GivenTheEquipmentHasNoAlarms()
    {
        _equipment.Alarms.Clear();
    }

    [Given(@"the equipment has a ""(.*)"" alarm")]
    public void GivenTheEquipmentHasAlarm(string alarmType)
    {
        _equipment.Alarms.Add(new Alarm
        {
            Type = Enum.Parse<AlarmType>(alarmType.Replace(" ", "")),
            Timestamp = DateTime.UtcNow
        });
    }

    [When(@"the operator presses the ""(.*)"" button")]
    public async Task WhenTheOperatorPressesButton(string buttonName)
    {
        try
        {
            switch (buttonName)
            {
                case "Start":
                    await _controller.StartAsync();
                    break;
                case "Emergency Stop":
                    await _controller.EmergencyStopAsync();
                    break;
            }
        }
        catch (Exception ex)
        {
            _lastErrorMessage = ex.Message;
        }
    }

    [Then(@"the equipment state should be ""(.*)""")]
    public void ThenTheEquipmentStateShouldBe(string expectedState)
    {
        var expected = Enum.Parse<EquipmentState>(expectedState);
        Assert.AreEqual(expected, _equipment.State);
    }

    [Then(@"the equipment state should remain ""(.*)""")]
    public void ThenTheEquipmentStateShouldRemain(string expectedState)
    {
        ThenTheEquipmentStateShouldBe(expectedState);
    }

    [Then(@"an error message ""(.*)"" should be displayed")]
    public void ThenAnErrorMessageShouldBeDisplayed(string expectedMessage)
    {
        Assert.IsNotNull(_lastErrorMessage);
        Assert.IsTrue(_lastErrorMessage.Contains(expectedMessage));
    }

    [Then(@"the start time should be recorded")]
    public void ThenTheStartTimeShouldBeRecorded()
    {
        Assert.IsNotNull(_equipment.LastStartTime);
        Assert.IsTrue(
            DateTime.UtcNow - _equipment.LastStartTime < TimeSpan.FromSeconds(5));
    }
}
```

**BDD의 장점**:
- 비즈니스 요구사항을 직접 테스트
- 실행 가능한 명세 (Living Documentation)
- 팀 간 의사소통 도구
- 인수 테스트 자동화

**테스트 리포트 예시**:
```
Feature: Equipment Control
  ✅ Starting idle equipment (2.3s)
  ✅ Cannot start equipment with active alarm (1.1s)
  ✅ Emergency stop during operation (3.5s)

3 scenarios (3 passed)
12 steps (12 passed)
Total: 6.9s
```

</div>
</div>

---

### 🎯 Test Doubles (테스트 대역)

**Mock, Stub, Fake, Spy 비교**

<div class="grid grid-cols-2 gap-8">
<div>

**1. Dummy (더미)**:
```csharp
// 전달만 되고 실제로 사용되지 않음
public class DummyLogger : ILogger
{
    public void Log(string message) { }
    public void LogError(Exception ex) { }
}

// 사용
var service = new EquipmentService(
    repository,
    new DummyLogger()); // 로거가 필요하지만 테스트에서 미사용
```

**2. Stub (스텁)**:
```csharp
// 미리 정의된 응답 반환
public class StubTemperatureSensor : ITemperatureSensor
{
    private readonly Queue<double> _temperatures;

    public StubTemperatureSensor(params double[] temps)
    {
        _temperatures = new Queue<double>(temps);
    }

    public Task<double> ReadTemperatureAsync()
    {
        if (_temperatures.Count > 0)
        {
            return Task.FromResult(_temperatures.Dequeue());
        }
        return Task.FromResult(25.0); // 기본값
    }
}

// 테스트
[TestMethod]
public async Task ProcessData_WithSpecificTemperatures_CalculatesAverage()
{
    // Arrange: 예측 가능한 온도 시퀀스
    var sensor = new StubTemperatureSensor(20.0, 25.0, 30.0);
    var processor = new DataProcessor(sensor);

    // Act
    var average = await processor.CalculateAverageTemperature(3);

    // Assert
    Assert.AreEqual(25.0, average);
}
```

**3. Fake (가짜)**:
```csharp
// 실제 동작하는 간단한 구현
public class FakeEquipmentRepository : IEquipmentRepository
{
    private readonly Dictionary<string, Equipment> _storage
        = new Dictionary<string, Equipment>();

    public Task<Equipment> GetByIdAsync(string id)
    {
        _storage.TryGetValue(id, out var equipment);
        return Task.FromResult(equipment);
    }

    public Task SaveAsync(Equipment equipment)
    {
        _storage[equipment.Id] = equipment;
        return Task.CompletedTask;
    }

    public Task<List<Equipment>> GetAllAsync()
    {
        return Task.FromResult(_storage.Values.ToList());
    }

    public Task DeleteAsync(string id)
    {
        _storage.Remove(id);
        return Task.CompletedTask;
    }
}

// 실제 DB 없이 동작하지만, 메모리에서 CRUD 동작 구현
```

</div>
<div>

**4. Mock (목)**:
```csharp
// 호출 검증 + 행동 정의
[TestMethod]
public async Task StartEquipment_WhenSuccessful_SendsNotification()
{
    // Arrange
    var mockNotificationService = new Mock<INotificationService>();
    var controller = new EquipmentController(
        _equipment,
        mockNotificationService.Object);

    // Act
    await controller.StartAsync();

    // Assert: 정확히 1번 호출되었는지 검증
    mockNotificationService.Verify(
        x => x.SendAsync(
            It.Is<Notification>(n =>
                n.Type == NotificationType.EquipmentStarted &&
                n.EquipmentId == "E001")),
        Times.Once);
}

[TestMethod]
public async Task ProcessAlarm_WithCriticalAlarm_CallsEmergencyProtocol()
{
    // Arrange
    var mockEmergencySystem = new Mock<IEmergencySystem>();
    mockEmergencySystem
        .Setup(x => x.TriggerProtocolAsync(It.IsAny<Alarm>()))
        .ReturnsAsync(true);

    var alarmHandler = new AlarmHandler(mockEmergencySystem.Object);
    var criticalAlarm = new Alarm
    {
        Severity = AlarmSeverity.Critical,
        Type = AlarmType.SafetyInterlock
    };

    // Act
    await alarmHandler.HandleAsync(criticalAlarm);

    // Assert
    mockEmergencySystem.Verify(
        x => x.TriggerProtocolAsync(criticalAlarm),
        Times.Once);
    mockEmergencySystem.Verify(
        x => x.NotifyOpsTeamAsync(It.IsAny<string>()),
        Times.Once);
}
```

**5. Spy (스파이)**:
```csharp
// 호출 기록 + 실제 동작
public class SpyLogger : ILogger
{
    private readonly List<LogEntry> _logEntries
        = new List<LogEntry>();

    public IReadOnlyList<LogEntry> LogEntries => _logEntries;

    public void Log(string message)
    {
        var entry = new LogEntry
        {
            Level = LogLevel.Info,
            Message = message,
            Timestamp = DateTime.UtcNow
        };
        _logEntries.Add(entry);

        // 실제 로깅도 수행
        Console.WriteLine($"[{entry.Timestamp}] {message}");
    }

    public void LogError(Exception ex)
    {
        var entry = new LogEntry
        {
            Level = LogLevel.Error,
            Message = ex.Message,
            Exception = ex,
            Timestamp = DateTime.UtcNow
        };
        _logEntries.Add(entry);
        Console.Error.WriteLine($"[ERROR] {ex.Message}");
    }
}

// 테스트
[TestMethod]
public async Task ProcessEquipment_LogsAllSteps()
{
    // Arrange
    var spyLogger = new SpyLogger();
    var processor = new EquipmentProcessor(spyLogger);

    // Act
    await processor.ProcessAsync(equipment);

    // Assert: 로깅 검증
    Assert.AreEqual(4, spyLogger.LogEntries.Count);
    Assert.IsTrue(spyLogger.LogEntries[0].Message.Contains("Starting"));
    Assert.IsTrue(spyLogger.LogEntries[3].Message.Contains("Completed"));
}
```

**선택 가이드**:
- **Dummy**: 필수 파라미터이지만 사용되지 않음
- **Stub**: 간접 입력 (indirect input) 제어
- **Fake**: 실제 동작하는 경량 구현
- **Mock**: 간접 출력 (indirect output) 검증
- **Spy**: 실제 동작 + 호출 기록

</div>
</div>

---

### 🏗️ AAA 패턴 (Arrange-Act-Assert)

**테스트 구조화**

<div class="grid grid-cols-2 gap-8">
<div>

**AAA 패턴 구조**:

```csharp
[TestMethod]
public async Task StartEquipment_WithValidConditions_StartsSuccessfully()
{
    // ============= ARRANGE =============
    // 테스트 준비: 객체 생성, 상태 설정, 의존성 주입

    var equipment = new Equipment
    {
        Id = "E001",
        Name = "Etcher",
        State = EquipmentState.Idle,
        Temperature = 25.0
    };

    var mockRepository = new Mock<IEquipmentRepository>();
    mockRepository
        .Setup(r => r.GetByIdAsync("E001"))
        .ReturnsAsync(equipment);

    var mockNotificationService = new Mock<INotificationService>();

    var controller = new EquipmentController(
        mockRepository.Object,
        mockNotificationService.Object);

    // ============= ACT =============
    // 테스트 대상 메서드 실행

    var result = await controller.StartEquipmentAsync("E001");

    // ============= ASSERT =============
    // 결과 검증

    Assert.IsTrue(result.IsSuccess);
    Assert.AreEqual(EquipmentState.Running, equipment.State);
    Assert.IsNotNull(equipment.LastStartTime);

    mockNotificationService.Verify(
        n => n.SendAsync(It.IsAny<Notification>()),
        Times.Once);
}
```

**복잡한 Arrange 리팩터링**:

```csharp
public class EquipmentTestBuilder
{
    private Equipment _equipment = new Equipment();
    private List<Alarm> _alarms = new List<Alarm>();

    public EquipmentTestBuilder WithId(string id)
    {
        _equipment.Id = id;
        return this;
    }

    public EquipmentTestBuilder WithState(EquipmentState state)
    {
        _equipment.State = state;
        return this;
    }

    public EquipmentTestBuilder WithTemperature(double temp)
    {
        _equipment.Temperature = temp;
        return this;
    }

    public EquipmentTestBuilder WithAlarm(AlarmType type, AlarmSeverity severity)
    {
        _alarms.Add(new Alarm { Type = type, Severity = severity });
        return this;
    }

    public Equipment Build()
    {
        _equipment.Alarms = _alarms;
        return _equipment;
    }
}

// 사용: Fluent API로 깔끔한 테스트
[TestMethod]
public async Task Test_WithBuilder()
{
    // Arrange - 훨씬 읽기 쉬움
    var equipment = new EquipmentTestBuilder()
        .WithId("E001")
        .WithState(EquipmentState.Idle)
        .WithTemperature(150.0)
        .WithAlarm(AlarmType.HighTemperature, AlarmSeverity.Warning)
        .Build();

    // Act
    var canStart = _controller.CanStart(equipment);

    // Assert
    Assert.IsFalse(canStart);
}
```

</div>
<div>

**AAA 패턴의 장점**:
- 테스트 가독성 향상
- 일관된 구조
- 명확한 의도 전달

**Common Patterns**:

**1. Setup 메서드 활용**:
```csharp
[TestClass]
public class EquipmentControllerTests
{
    private EquipmentController _controller;
    private Mock<IEquipmentRepository> _mockRepository;

    [TestInitialize]
    public void Setup()
    {
        // 모든 테스트에서 공통으로 사용할 Arrange
        _mockRepository = new Mock<IEquipmentRepository>();
        _controller = new EquipmentController(_mockRepository.Object);
    }

    [TestMethod]
    public async Task Test1()
    {
        // Arrange: 이 테스트만의 특수 설정
        var equipment = CreateTestEquipment();

        // Act
        await _controller.StartAsync(equipment);

        // Assert
        Assert.AreEqual(EquipmentState.Running, equipment.State);
    }
}
```

**2. Theory 테스트 (데이터 주도)**:
```csharp
[TestClass]
public class TemperatureValidationTests
{
    [DataTestMethod]
    [DataRow(-50, true,  "최소 온도")]
    [DataRow(0,   true,  "경계값 하한")]
    [DataRow(150, true,  "정상 범위")]
    [DataRow(300, true,  "경계값 상한")]
    [DataRow(301, false, "최대 초과")]
    [DataRow(double.NaN, false, "유효하지 않은 값")]
    public void ValidateTemperature_WithVariousInputs_ReturnsExpected(
        double temperature,
        bool expectedValid,
        string scenario)
    {
        // Arrange
        var validator = new TemperatureValidator(-50, 300);

        // Act
        var isValid = validator.IsValid(temperature);

        // Assert
        Assert.AreEqual(expectedValid, isValid, $"Failed for: {scenario}");
    }
}
```

**3. Helper Methods**:
```csharp
[TestClass]
public class AlarmTests
{
    [TestMethod]
    public async Task HighPriorityAlarm_TriggersImmediateNotification()
    {
        // Arrange
        var alarm = CreateCriticalAlarm();
        var handler = CreateAlarmHandler();

        // Act
        await handler.HandleAsync(alarm);

        // Assert
        AssertNotificationSent();
        AssertAlarmLogged(alarm);
    }

    private Alarm CreateCriticalAlarm()
    {
        return new Alarm
        {
            Type = AlarmType.SafetyInterlock,
            Severity = AlarmSeverity.Critical,
            EquipmentId = "E001",
            Message = "Safety door opened during operation",
            Timestamp = DateTime.UtcNow
        };
    }

    private AlarmHandler CreateAlarmHandler()
    {
        var mockNotification = new Mock<INotificationService>();
        var mockLogger = new Mock<ILogger>();
        return new AlarmHandler(
            mockNotification.Object,
            mockLogger.Object);
    }

    private void AssertNotificationSent()
    {
        // 검증 로직
    }
}
```

**Anti-Patterns (피해야 할 패턴)**:
- ❌ Multiple Act: 하나의 테스트에서 여러 동작
- ❌ No Assert: 검증 없는 테스트
- ❌ Conditional Logic: if/for 문 사용
- ❌ Test Interdependence: 테스트 간 의존성

</div>
</div>

---

## .NET 테스트 프레임워크 비교

### MSTest (Microsoft Test Framework)
**장점**:
- Visual Studio 완전 통합
- Azure DevOps 네이티브 지원
- Enterprise 기능 (Live Unit Testing)

**단점**:
- 상대적으로 느린 실행 속도
- 제한적인 확장성

**적용 분야**: 기업 환경, Azure 생태계

### xUnit.net
**장점**:
- 빠른 실행 속도
- 병렬 테스트 실행
- 현대적인 API 설계

**단점**:
- Setup/Teardown 개념 부재
- 러닝 커브 존재

**적용 분야**: 신규 프로젝트, 성능 중시

### NUnit
**장점**:
- 풍부한 Assert 메서드
- 유연한 테스트 구성
- 강력한 파라미터화 테스트

**단점**:
- 복잡한 설정
- 버전 호환성 이슈

**적용 분야**: 복잡한 테스트 시나리오

## 반도체 HMI 테스트 아키텍처

### Test Doubles 패턴

<div class="code-section">

**테스트용 Mock 객체 구현**

```csharp
// 1. 센서 인터페이스 정의
public interface ITemperatureSensor
{
    Task<double> ReadTemperatureAsync();
    Task<bool> CalibrateAsync(double referenceValue);
    event EventHandler<TemperatureChangedEventArgs> TemperatureChanged;
}

// 2. Mock 센서 구현
public class MockTemperatureSensor : ITemperatureSensor
{
    private double currentTemperature = 25.0;
    private readonly Random random = new Random();

    public event EventHandler<TemperatureChangedEventArgs> TemperatureChanged;

    public async Task<double> ReadTemperatureAsync()
    {
        // 실제 센서 응답 시간 시뮬레이션
        await Task.Delay(50);

        // 노이즈가 포함된 온도값 생성
        var noise = (random.NextDouble() - 0.5) * 0.1;
        currentTemperature += noise;

        return Math.Round(currentTemperature, 2);
    }

    public async Task<bool> CalibrateAsync(double referenceValue)
    {
        await Task.Delay(1000); // 보정 시간 시뮬레이션
        currentTemperature = referenceValue;
        return true;
    }

    // 테스트용 온도 설정 메서드
    public void SetTemperature(double temperature)
    {
        currentTemperature = temperature;
        TemperatureChanged?.Invoke(this, new TemperatureChangedEventArgs(temperature));
    }
}

// 3. Stub을 활용한 예측 가능한 테스트
public class StubTemperatureSensor : ITemperatureSensor
{
    private readonly Queue<double> temperatureValues;
    private bool calibrationResult = true;

    public event EventHandler<TemperatureChangedEventArgs> TemperatureChanged;

    public StubTemperatureSensor(params double[] temperatures)
    {
        temperatureValues = new Queue<double>(temperatures);
    }

    public Task<double> ReadTemperatureAsync()
    {
        if (temperatureValues.Count > 0)
            return Task.FromResult(temperatureValues.Dequeue());

        throw new InvalidOperationException("No more temperature values available");
    }

    public Task<bool> CalibrateAsync(double referenceValue)
    {
        return Task.FromResult(calibrationResult);
    }

    public void SetCalibrationResult(bool result) => calibrationResult = result;
}
```

</div>

### 의존성 주입을 통한 테스트 용이성

<div class="code-section">

**DI 컨테이너 기반 테스트 설정**

```csharp
public class EquipmentControllerTests
{
    private ServiceProvider serviceProvider;
    private IEquipmentController equipmentController;

    [TestInitialize]
    public void Setup()
    {
        var services = new ServiceCollection();

        // 프로덕션 의존성을 테스트용으로 교체
        services.AddSingleton<ITemperatureSensor, MockTemperatureSensor>();
        services.AddSingleton<IPressureSensor, MockPressureSensor>();
        services.AddSingleton<IDataLogger, InMemoryDataLogger>();
        services.AddSingleton<IAlarmSystem, MockAlarmSystem>();

        // 실제 비즈니스 로직은 그대로 사용
        services.AddSingleton<IEquipmentController, EquipmentController>();
        services.AddSingleton<IProcessController, ProcessController>();

        serviceProvider = services.BuildServiceProvider();
        equipmentController = serviceProvider.GetRequiredService<IEquipmentController>();
    }

    [TestMethod]
    public async Task StartProcess_WhenTemperatureInRange_ShouldSucceed()
    {
        // Arrange
        var mockSensor = serviceProvider.GetRequiredService<ITemperatureSensor>()
                        as MockTemperatureSensor;
        mockSensor.SetTemperature(150.0); // 정상 운영 온도

        var processParameters = new ProcessParameters
        {
            TargetTemperature = 150.0,
            PressureSetpoint = 1.5,
            Duration = TimeSpan.FromMinutes(30)
        };

        // Act
        var result = await equipmentController.StartProcessAsync(processParameters);

        // Assert
        Assert.IsTrue(result.IsSuccess);
        Assert.AreEqual(ProcessStatus.Running, result.Status);
    }

    [TestCleanup]
    public void Cleanup()
    {
        serviceProvider?.Dispose();
    }
}
```

</div>

## CI/CD 파이프라인 설계

### Azure DevOps 파이프라인

<div class="code-section">

**azure-pipelines.yml - 완전한 CI/CD 파이프라인**

```yaml
# Azure DevOps 파이프라인 정의
trigger:
  branches:
    include:
    - main
    - develop
    - release/*

variables:
  buildConfiguration: 'Release'
  dotNetFramework: 'net6.0'
  vmImageName: 'windows-2022'

stages:
- stage: Build
  displayName: 'Build and Test'
  jobs:
  - job: Build
    displayName: 'Build job'
    pool:
      vmImage: $(vmImageName)

    steps:
    # .NET SDK 설치
    - task: UseDotNet@2
      displayName: 'Use .NET 6 SDK'
      inputs:
        packageType: 'sdk'
        version: '6.0.x'

    # NuGet 패키지 복원
    - task: DotNetCoreCLI@2
      displayName: 'Restore packages'
      inputs:
        command: 'restore'
        projects: '**/*.csproj'

    # 코드 빌드
    - task: DotNetCoreCLI@2
      displayName: 'Build'
      inputs:
        command: 'build'
        projects: '**/*.csproj'
        arguments: '--configuration $(buildConfiguration) --no-restore'

    # 단위 테스트 실행
    - task: DotNetCoreCLI@2
      displayName: 'Run Unit Tests'
      inputs:
        command: 'test'
        projects: '**/*UnitTests.csproj'
        arguments: '--configuration $(buildConfiguration) --collect:"XPlat Code Coverage" --logger trx --no-build'
        publishTestResults: true

    # 통합 테스트 실행
    - task: DotNetCoreCLI@2
      displayName: 'Run Integration Tests'
      inputs:
        command: 'test'
        projects: '**/*IntegrationTests.csproj'
        arguments: '--configuration $(buildConfiguration) --collect:"XPlat Code Coverage" --logger trx --no-build'
        publishTestResults: true

    # 코드 커버리지 발행
    - task: PublishCodeCoverageResults@1
      displayName: 'Publish Code Coverage'
      inputs:
        codeCoverageTool: 'Cobertura'
        summaryFileLocation: '$(Agent.TempDirectory)/**/coverage.cobertura.xml'

    # SonarQube 코드 품질 분석
    - task: SonarQubePrepare@4
      displayName: 'Prepare SonarQube analysis'
      inputs:
        SonarQube: 'SonarQube-Server'
        scannerMode: 'MSBuild'
        projectKey: 'semiconductor-hmi'
        projectName: 'Semiconductor HMI'

    - task: SonarQubeAnalyze@4
      displayName: 'Run SonarQube analysis'

    - task: SonarQubePublish@4
      displayName: 'Publish SonarQube results'

    # Docker 이미지 빌드
    - task: Docker@2
      displayName: 'Build Docker image'
      inputs:
        containerRegistry: 'ACR-Connection'
        repository: 'semiconductor-hmi'
        command: 'build'
        Dockerfile: '**/Dockerfile'
        tags: |
          $(Build.BuildId)
          latest

- stage: Deploy_Test
  displayName: 'Deploy to Test Environment'
  dependsOn: Build
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/develop'))
  jobs:
  - deployment: DeployToTest
    displayName: 'Deploy to Test'
    pool:
      vmImage: $(vmImageName)
    environment: 'test'
    strategy:
      runOnce:
        deploy:
          steps:
          # Kubernetes 배포
          - task: KubernetesManifest@0
            displayName: 'Deploy to Kubernetes'
            inputs:
              action: 'deploy'
              kubernetesServiceConnection: 'k8s-test-cluster'
              namespace: 'test-environment'
              manifests: |
                k8s/deployment.yaml
                k8s/service.yaml
                k8s/configmap.yaml

          # 배포 후 헬스체크
          - task: PowerShell@2
            displayName: 'Health Check'
            inputs:
              targetType: 'inline'
              script: |
                $healthCheckUrl = "http://test-hmi.company.com/health"
                $maxAttempts = 30
                $attempt = 0

                do {
                    $attempt++
                    try {
                        $response = Invoke-RestMethod -Uri $healthCheckUrl -TimeoutSec 10
                        if ($response.status -eq "healthy") {
                            Write-Host "Health check passed on attempt $attempt"
                            exit 0
                        }
                    }
                    catch {
                        Write-Host "Health check failed on attempt $attempt: $($_.Exception.Message)"
                    }
                    Start-Sleep -Seconds 10
                } while ($attempt -lt $maxAttempts)

                Write-Error "Health check failed after $maxAttempts attempts"
                exit 1

- stage: Deploy_Production
  displayName: 'Deploy to Production'
  dependsOn: Deploy_Test
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployToProduction
    displayName: 'Deploy to Production'
    pool:
      vmImage: $(vmImageName)
    environment: 'production'
    strategy:
      canary:
        increments: [1, 10, 100]
        deploy:
          steps:
          # Blue-Green 배포 전략
          - task: KubernetesManifest@0
            displayName: 'Deploy to Green Environment'
            inputs:
              action: 'deploy'
              kubernetesServiceConnection: 'k8s-prod-cluster'
              namespace: 'production'
              manifests: |
                k8s/deployment-green.yaml

          # 트래픽 전환 대기 (수동 승인)
          - task: ManualValidation@0
            displayName: 'Manual Validation'
            inputs:
              notifyUsers: 'ops-team@company.com'
              instructions: 'Please validate the green deployment and approve traffic switch'

          # 트래픽 전환
          - task: KubernetesManifest@0
            displayName: 'Switch Traffic to Green'
            inputs:
              action: 'deploy'
              kubernetesServiceConnection: 'k8s-prod-cluster'
              namespace: 'production'
              manifests: 'k8s/service-green.yaml'
```

</div>

### GitHub Actions 워크플로우

<div class="code-section">

**.github/workflows/ci-cd.yml**

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  DOTNET_VERSION: '6.0.x'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: windows-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup .NET
      uses: actions/setup-dotnet@v3
      with:
        dotnet-version: ${{ env.DOTNET_VERSION }}

    - name: Restore dependencies
      run: dotnet restore

    - name: Build
      run: dotnet build --no-restore --configuration Release

    - name: Test
      run: |
        dotnet test --no-build --configuration Release --collect:"XPlat Code Coverage" `
          --logger trx --results-directory TestResults

    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: TestResults

    - name: Upload coverage reports to Codecov
      uses: codecov/codecov-action@v3
      with:
        directory: TestResults
        fail_ci_if_error: true

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/dotnet@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  build-and-push:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-

    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
```

</div>

## 모니터링 및 로깅 전략

### Application Insights 통합

<div class="code-section">

**Program.cs - 모니터링 설정**

```csharp
using Microsoft.ApplicationInsights;
using Microsoft.ApplicationInsights.Extensibility;
using Serilog;
using Serilog.Events;

var builder = WebApplication.CreateBuilder(args);

// Application Insights 설정
builder.Services.AddApplicationInsightsTelemetry(options =>
{
    options.ConnectionString = builder.Configuration.GetConnectionString("ApplicationInsights");
    options.EnableAdaptiveSampling = true;
    options.EnableQuickPulseMetricStream = true;
});

// Serilog 구성
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
    .MinimumLevel.Override("System", LogEventLevel.Warning)
    .Enrich.FromLogContext()
    .Enrich.WithProperty("Application", "SemiconductorHMI")
    .Enrich.WithProperty("Environment", builder.Environment.EnvironmentName)
    .WriteTo.Console()
    .WriteTo.File("logs/app-.log",
        rollingInterval: RollingInterval.Day,
        retainedFileCountLimit: 30,
        outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {Message:lj}{NewLine}{Exception}")
    .WriteTo.ApplicationInsights(
        builder.Configuration.GetConnectionString("ApplicationInsights"),
        TelemetryConverter.Traces)
    .CreateLogger();

builder.Host.UseSerilog();

// 커스텀 미들웨어 등록
builder.Services.AddSingleton<ITelemetryInitializer, CustomTelemetryInitializer>();
builder.Services.AddSingleton<IMetricsCollector, EquipmentMetricsCollector>();

var app = builder.Build();

// 커스텀 미들웨어 추가
app.UseMiddleware<PerformanceLoggingMiddleware>();
app.UseMiddleware<ErrorHandlingMiddleware>();

app.Run();
```

</div>

### 커스텀 메트릭 수집

<div class="code-section">

**메트릭 수집 및 알림 시스템**

```csharp
public class EquipmentMetricsCollector : IMetricsCollector, IDisposable
{
    private readonly TelemetryClient telemetryClient;
    private readonly ILogger<EquipmentMetricsCollector> logger;
    private readonly Timer metricsTimer;
    private readonly IEquipmentDataService equipmentDataService;

    public EquipmentMetricsCollector(
        TelemetryClient telemetryClient,
        ILogger<EquipmentMetricsCollector> logger,
        IEquipmentDataService equipmentDataService)
    {
        this.telemetryClient = telemetryClient;
        this.logger = logger;
        this.equipmentDataService = equipmentDataService;

        // 1분마다 메트릭 수집
        metricsTimer = new Timer(CollectMetrics, null, TimeSpan.Zero, TimeSpan.FromMinutes(1));
    }

    private async void CollectMetrics(object state)
    {
        try
        {
            var equipmentList = await equipmentDataService.GetAllEquipmentAsync();

            foreach (var equipment in equipmentList)
            {
                await CollectEquipmentMetrics(equipment);
            }

            // 시스템 전체 메트릭
            await CollectSystemMetrics();
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Failed to collect metrics");
        }
    }

    private async Task CollectEquipmentMetrics(Equipment equipment)
    {
        var metrics = await equipmentDataService.GetCurrentMetricsAsync(equipment.Id);

        // 온도 메트릭
        telemetryClient.TrackMetric("Equipment.Temperature",
            metrics.Temperature,
            new Dictionary<string, string>
            {
                {"EquipmentId", equipment.Id},
                {"EquipmentType", equipment.Type},
                {"Location", equipment.Location}
            });

        // 압력 메트릭
        telemetryClient.TrackMetric("Equipment.Pressure",
            metrics.Pressure,
            new Dictionary<string, string>
            {
                {"EquipmentId", equipment.Id},
                {"EquipmentType", equipment.Type}
            });

        // 처리량 메트릭
        telemetryClient.TrackMetric("Equipment.Throughput",
            metrics.WafersPerHour,
            new Dictionary<string, string>
            {
                {"EquipmentId", equipment.Id},
                {"ProcessType", metrics.CurrentProcess}
            });

        // 에러율 계산 및 추적
        var errorRate = await CalculateErrorRate(equipment.Id);
        telemetryClient.TrackMetric("Equipment.ErrorRate", errorRate);

        // 임계값 체크 및 알림
        await CheckThresholds(equipment, metrics);
    }

    private async Task CheckThresholds(Equipment equipment, EquipmentMetrics metrics)
    {
        var thresholds = await equipmentDataService.GetThresholdsAsync(equipment.Id);

        // 온도 임계값 체크
        if (metrics.Temperature > thresholds.MaxTemperature)
        {
            var alert = new Alert
            {
                Type = AlertType.HighTemperature,
                EquipmentId = equipment.Id,
                Value = metrics.Temperature,
                Threshold = thresholds.MaxTemperature,
                Severity = AlertSeverity.Critical,
                Timestamp = DateTime.UtcNow
            };

            await SendAlert(alert);
        }

        // 처리량 저하 체크
        if (metrics.WafersPerHour < thresholds.MinThroughput)
        {
            var alert = new Alert
            {
                Type = AlertType.LowThroughput,
                EquipmentId = equipment.Id,
                Value = metrics.WafersPerHour,
                Threshold = thresholds.MinThroughput,
                Severity = AlertSeverity.Warning,
                Timestamp = DateTime.UtcNow
            };

            await SendAlert(alert);
        }
    }

    private async Task SendAlert(Alert alert)
    {
        // Application Insights에 알림 이벤트 기록
        telemetryClient.TrackEvent("Equipment.Alert",
            new Dictionary<string, string>
            {
                {"AlertType", alert.Type.ToString()},
                {"EquipmentId", alert.EquipmentId},
                {"Severity", alert.Severity.ToString()},
                {"Value", alert.Value.ToString()},
                {"Threshold", alert.Threshold.ToString()}
            });

        // 심각한 알림의 경우 즉시 알림 발송
        if (alert.Severity == AlertSeverity.Critical)
        {
            await NotifyOpsTeam(alert);
        }

        logger.LogWarning("Equipment alert triggered: {AlertType} for equipment {EquipmentId}. " +
                         "Value: {Value}, Threshold: {Threshold}",
                         alert.Type, alert.EquipmentId, alert.Value, alert.Threshold);
    }

    private async Task NotifyOpsTeam(Alert alert)
    {
        // Teams/Slack 알림
        // SMS/이메일 알림
        // PagerDuty 연동 등
    }

    public void Dispose()
    {
        metricsTimer?.Dispose();
    }
}
```

</div>

---

