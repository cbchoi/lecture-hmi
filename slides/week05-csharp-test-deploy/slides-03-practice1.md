# 🧪 기초 실습: Unit Test 및 Integration Test (45분)

## xUnit 기반 Unit Test 구현

### 테스트 프로젝트 설정

<div class="code-section">

**SemiconductorHMI.UnitTests.csproj**

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.3.2" />
    <PackageReference Include="xunit" Version="2.4.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.4.3">
      <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
      <PrivateAssets>all</PrivateAssets>
    </PackageReference>
    <PackageReference Include="coverlet.collector" Version="3.1.2" />
    <PackageReference Include="Moq" Version="4.18.4" />
    <PackageReference Include="FluentAssertions" Version="6.8.0" />
    <PackageReference Include="AutoFixture" Version="4.18.0" />
    <PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="6.0.0" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\SemiconductorHMI.Core\SemiconductorHMI.Core.csproj" />
    <ProjectReference Include="..\SemiconductorHMI.Services\SemiconductorHMI.Services.csproj" />
  </ItemGroup>

</Project>
```

</div>

### Process Controller 테스트

<div class="code-section">

**ProcessControllerTests.cs**

```csharp
using AutoFixture;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using SemiconductorHMI.Core.Interfaces;
using SemiconductorHMI.Core.Models;
using SemiconductorHMI.Services;
using Xunit;

namespace SemiconductorHMI.UnitTests.Services
{
    public class ProcessControllerTests : IDisposable
    {
        private readonly Fixture fixture;
        private readonly Mock<ITemperatureSensor> mockTemperatureSensor;
        private readonly Mock<IPressureSensor> mockPressureSensor;
        private readonly Mock<IDataLogger> mockDataLogger;
        private readonly Mock<IAlarmSystem> mockAlarmSystem;
        private readonly Mock<ILogger<ProcessController>> mockLogger;
        private readonly ProcessController processController;

        public ProcessControllerTests()
        {
            fixture = new Fixture();
            mockTemperatureSensor = new Mock<ITemperatureSensor>();
            mockPressureSensor = new Mock<IPressureSensor>();
            mockDataLogger = new Mock<IDataLogger>();
            mockAlarmSystem = new Mock<IAlarmSystem>();
            mockLogger = new Mock<ILogger<ProcessController>>();

            processController = new ProcessController(
                mockTemperatureSensor.Object,
                mockPressureSensor.Object,
                mockDataLogger.Object,
                mockAlarmSystem.Object,
                mockLogger.Object);
        }

        [Fact]
        public async Task StartProcessAsync_ValidParameters_ShouldReturnSuccess()
        {
            // Arrange
            var processParams = fixture.Build<ProcessParameters>()
                .With(p => p.TargetTemperature, 150.0)
                .With(p => p.PressureSetpoint, 1.5)
                .With(p => p.Duration, TimeSpan.FromMinutes(30))
                .Create();

            mockTemperatureSensor.Setup(x => x.ReadTemperatureAsync())
                .ReturnsAsync(25.0); // 초기 온도

            mockPressureSensor.Setup(x => x.ReadPressureAsync())
                .ReturnsAsync(1.0); // 초기 압력

            // Act
            var result = await processController.StartProcessAsync(processParams);

            // Assert
            result.Should().NotBeNull();
            result.IsSuccess.Should().BeTrue();
            result.ProcessId.Should().NotBeEmpty();

            // 데이터 로깅이 시작되었는지 확인
            mockDataLogger.Verify(x => x.StartLoggingAsync(It.IsAny<string>()), Times.Once);
        }

        [Theory]
        [InlineData(-50.0)] // 너무 낮은 온도
        [InlineData(1000.0)] // 너무 높은 온도
        public async Task StartProcessAsync_InvalidTemperature_ShouldReturnFailure(double invalidTemperature)
        {
            // Arrange
            var processParams = fixture.Build<ProcessParameters>()
                .With(p => p.TargetTemperature, invalidTemperature)
                .Create();

            // Act
            var result = await processController.StartProcessAsync(processParams);

            // Assert
            result.IsSuccess.Should().BeFalse();
            result.ErrorMessage.Should().Contain("temperature");
        }

        [Fact]
        public async Task MonitorProcess_TemperatureExceedsThreshold_ShouldTriggerAlarm()
        {
            // Arrange
            var processId = Guid.NewGuid().ToString();
            var highTemperature = 200.0;
            var threshold = 180.0;

            mockTemperatureSensor.Setup(x => x.ReadTemperatureAsync())
                .ReturnsAsync(highTemperature);

            // 프로세스 시작
            var processParams = fixture.Build<ProcessParameters>()
                .With(p => p.TargetTemperature, 150.0)
                .With(p => p.MaxTemperatureThreshold, threshold)
                .Create();

            await processController.StartProcessAsync(processParams);

            // Act
            await Task.Delay(100); // 모니터링 사이클 대기

            // Assert
            mockAlarmSystem.Verify(x => x.TriggerAlarmAsync(
                It.Is<Alarm>(a => a.Type == AlarmType.HighTemperature &&
                                 a.Value == highTemperature)),
                Times.AtLeastOnce);
        }

        [Fact]
        public async Task StopProcessAsync_RunningProcess_ShouldStopSuccessfully()
        {
            // Arrange
            var processParams = fixture.Create<ProcessParameters>();
            var startResult = await processController.StartProcessAsync(processParams);

            // Act
            var stopResult = await processController.StopProcessAsync(startResult.ProcessId);

            // Assert
            stopResult.Should().BeTrue();
            mockDataLogger.Verify(x => x.StopLoggingAsync(startResult.ProcessId), Times.Once);
        }

        [Fact]
        public async Task GetProcessStatus_ExistingProcess_ShouldReturnCorrectStatus()
        {
            // Arrange
            var processParams = fixture.Create<ProcessParameters>();
            var startResult = await processController.StartProcessAsync(processParams);

            // Act
            var status = await processController.GetProcessStatusAsync(startResult.ProcessId);

            // Assert
            status.Should().NotBeNull();
            status.ProcessId.Should().Be(startResult.ProcessId);
            status.Status.Should().Be(ProcessStatus.Running);
        }

        [Fact]
        public void Constructor_NullTemperatureSensor_ShouldThrowArgumentNullException()
        {
            // Act & Assert
            Assert.Throws<ArgumentNullException>(() => new ProcessController(
                null,
                mockPressureSensor.Object,
                mockDataLogger.Object,
                mockAlarmSystem.Object,
                mockLogger.Object));
        }

        public void Dispose()
        {
            processController?.Dispose();
        }
    }
}
```

</div>

### Data Service 테스트

<div class="code-section">

**EquipmentDataServiceTests.cs**

```csharp
public class EquipmentDataServiceTests : IAsyncLifetime
{
    private readonly ServiceProvider serviceProvider;
    private readonly IEquipmentDataService dataService;
    private readonly ITestDatabase testDatabase;

    public EquipmentDataServiceTests()
    {
        var services = new ServiceCollection();

        // In-Memory 데이터베이스 설정
        services.AddDbContext<EquipmentDbContext>(options =>
            options.UseInMemoryDatabase(Guid.NewGuid().ToString()));

        services.AddScoped<IEquipmentDataService, EquipmentDataService>();
        services.AddScoped<ITestDatabase, TestDatabase>();

        serviceProvider = services.BuildServiceProvider();
        dataService = serviceProvider.GetRequiredService<IEquipmentDataService>();
        testDatabase = serviceProvider.GetRequiredService<ITestDatabase>();
    }

    public async Task InitializeAsync()
    {
        await testDatabase.SeedTestDataAsync();
    }

    [Fact]
    public async Task GetEquipmentByIdAsync_ExistingId_ShouldReturnEquipment()
    {
        // Arrange
        var equipmentId = "CVD-001";

        // Act
        var equipment = await dataService.GetEquipmentByIdAsync(equipmentId);

        // Assert
        equipment.Should().NotBeNull();
        equipment.Id.Should().Be(equipmentId);
        equipment.Type.Should().Be(EquipmentType.CVD);
    }

    [Fact]
    public async Task SaveSensorDataAsync_ValidData_ShouldPersist()
    {
        // Arrange
        var sensorData = new SensorData
        {
            EquipmentId = "CVD-001",
            SensorType = SensorType.Temperature,
            Value = 150.5,
            Timestamp = DateTime.UtcNow,
            Unit = "°C"
        };

        // Act
        await dataService.SaveSensorDataAsync(sensorData);

        // Assert
        var savedData = await dataService.GetSensorDataAsync(
            sensorData.EquipmentId,
            sensorData.SensorType,
            DateTime.UtcNow.AddMinutes(-1),
            DateTime.UtcNow.AddMinutes(1));

        savedData.Should().ContainSingle();
        savedData.First().Value.Should().Be(sensorData.Value);
    }

    [Fact]
    public async Task GetEquipmentStatisticsAsync_ValidDateRange_ShouldReturnStatistics()
    {
        // Arrange
        var equipmentId = "CVD-001";
        var startDate = DateTime.UtcNow.AddDays(-7);
        var endDate = DateTime.UtcNow;

        // Act
        var statistics = await dataService.GetEquipmentStatisticsAsync(
            equipmentId, startDate, endDate);

        // Assert
        statistics.Should().NotBeNull();
        statistics.EquipmentId.Should().Be(equipmentId);
        statistics.UpTime.Should().BeGreaterThan(TimeSpan.Zero);
        statistics.TotalWafersProcessed.Should().BeGreaterThan(0);
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public async Task GetEquipmentByIdAsync_InvalidId_ShouldThrowArgumentException(string invalidId)
    {
        // Act & Assert
        await Assert.ThrowsAsync<ArgumentException>(() =>
            dataService.GetEquipmentByIdAsync(invalidId));
    }

    public async Task DisposeAsync()
    {
        await serviceProvider.DisposeAsync();
    }
}
```

</div>

## Integration Test 구현

### 테스트 환경 설정

<div class="code-section">

**IntegrationTestBase.cs**

```csharp
public class IntegrationTestBase : IAsyncLifetime
{
    protected readonly WebApplicationFactory<Program> Factory;
    protected readonly HttpClient Client;
    protected readonly IServiceScope Scope;
    protected readonly EquipmentDbContext DbContext;

    public IntegrationTestBase()
    {
        Factory = new WebApplicationFactory<Program>()
            .WithWebHostBuilder(builder =>
            {
                builder.ConfigureServices(services =>
                {
                    // 실제 데이터베이스를 테스트용으로 교체
                    var descriptor = services.SingleOrDefault(
                        d => d.ServiceType == typeof(DbContextOptions<EquipmentDbContext>));

                    if (descriptor != null)
                        services.Remove(descriptor);

                    services.AddDbContext<EquipmentDbContext>(options =>
                        options.UseInMemoryDatabase("TestDb"));

                    // 외부 의존성을 Mock으로 교체
                    services.AddSingleton<IEmailService, MockEmailService>();
                    services.AddSingleton<IHardwareInterface, MockHardwareInterface>();
                });

                builder.UseEnvironment("Testing");
            });

        Client = Factory.CreateClient();
        Scope = Factory.Services.CreateScope();
        DbContext = Scope.ServiceProvider.GetRequiredService<EquipmentDbContext>();
    }

    public async Task InitializeAsync()
    {
        await DbContext.Database.EnsureCreatedAsync();
        await SeedTestDataAsync();
    }

    protected virtual async Task SeedTestDataAsync()
    {
        var equipment = new Equipment
        {
            Id = "CVD-001",
            Name = "CVD Chamber 1",
            Type = EquipmentType.CVD,
            Location = "Fab1-Bay2",
            Status = EquipmentStatus.Running,
            InstallDate = DateTime.UtcNow.AddYears(-2)
        };

        DbContext.Equipment.Add(equipment);
        await DbContext.SaveChangesAsync();
    }

    public async Task DisposeAsync()
    {
        Scope.Dispose();
        await Factory.DisposeAsync();
    }
}
```

</div>

### API 통합 테스트

<div class="code-section">

**EquipmentControllerIntegrationTests.cs**

```csharp
public class EquipmentControllerIntegrationTests : IntegrationTestBase
{
    [Fact]
    public async Task GetEquipment_ExistingId_ShouldReturnOkWithEquipment()
    {
        // Arrange
        var equipmentId = "CVD-001";

        // Act
        var response = await Client.GetAsync($"/api/equipment/{equipmentId}");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var content = await response.Content.ReadAsStringAsync();
        var equipment = JsonSerializer.Deserialize<Equipment>(content, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        });

        equipment.Should().NotBeNull();
        equipment.Id.Should().Be(equipmentId);
    }

    [Fact]
    public async Task StartProcess_ValidRequest_ShouldReturnAccepted()
    {
        // Arrange
        var equipmentId = "CVD-001";
        var processRequest = new ProcessStartRequest
        {
            TargetTemperature = 150.0,
            PressureSetpoint = 1.5,
            Duration = TimeSpan.FromMinutes(30),
            ProcessType = "StandardCVD"
        };

        var jsonContent = JsonSerializer.Serialize(processRequest);
        var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

        // Act
        var response = await Client.PostAsync($"/api/equipment/{equipmentId}/start-process", content);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Accepted);

        var responseContent = await response.Content.ReadAsStringAsync();
        var result = JsonSerializer.Deserialize<ProcessStartResponse>(responseContent, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        });

        result.ProcessId.Should().NotBeEmpty();
        result.EstimatedDuration.Should().Be(processRequest.Duration);
    }

    [Fact]
    public async Task GetSensorData_ValidDateRange_ShouldReturnData()
    {
        // Arrange
        var equipmentId = "CVD-001";
        var startDate = DateTime.UtcNow.AddHours(-1);
        var endDate = DateTime.UtcNow;

        // Test data 추가
        await AddTestSensorDataAsync(equipmentId);

        // Act
        var response = await Client.GetAsync(
            $"/api/equipment/{equipmentId}/sensor-data?" +
            $"startDate={startDate:yyyy-MM-ddTHH:mm:ss}&" +
            $"endDate={endDate:yyyy-MM-ddTHH:mm:ss}");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);

        var content = await response.Content.ReadAsStringAsync();
        var sensorData = JsonSerializer.Deserialize<List<SensorDataDto>>(content, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        });

        sensorData.Should().NotBeEmpty();
    }

    private async Task AddTestSensorDataAsync(string equipmentId)
    {
        var testData = new[]
        {
            new SensorData
            {
                EquipmentId = equipmentId,
                SensorType = SensorType.Temperature,
                Value = 150.5,
                Timestamp = DateTime.UtcNow.AddMinutes(-30),
                Unit = "°C"
            },
            new SensorData
            {
                EquipmentId = equipmentId,
                SensorType = SensorType.Pressure,
                Value = 1.5,
                Timestamp = DateTime.UtcNow.AddMinutes(-30),
                Unit = "Torr"
            }
        };

        DbContext.SensorData.AddRange(testData);
        await DbContext.SaveChangesAsync();
    }
}
```

</div>

---

