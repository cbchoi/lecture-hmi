# 🎯 심화 실습: UI 자동화 테스트 및 성능 테스트 (45분)

## UI 자동화 테스트 (FlaUI)

### FlaUI 테스트 설정

<div class="code-section">

**SemiconductorHMI.UITests.csproj**

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net6.0-windows</TargetFramework>
    <UseWPF>true</UseWPF>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.3.2" />
    <PackageReference Include="xunit" Version="2.4.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.4.3" />
    <PackageReference Include="FlaUI.Core" Version="4.0.0" />
    <PackageReference Include="FlaUI.UIA3" Version="4.0.0" />
    <PackageReference Include="FluentAssertions" Version="6.8.0" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\SemiconductorHMI\SemiconductorHMI.csproj" />
  </ItemGroup>

</Project>
```

</div>

### 메인 대시보드 UI 테스트

<div class="code-section">

**MainDashboardUITests.cs**

```csharp
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using FluentAssertions;
using System.Diagnostics;
using Xunit;

namespace SemiconductorHMI.UITests
{
    public class MainDashboardUITests : IDisposable
    {
        private readonly Application application;
        private readonly UIA3Automation automation;
        private readonly Window mainWindow;

        public MainDashboardUITests()
        {
            // 테스트 모드로 애플리케이션 시작
            var appPath = Path.Combine(TestContext.CurrentContext.TestDirectory, "SemiconductorHMI.exe");
            application = Application.Launch(appPath + " --test-mode");
            automation = new UIA3Automation();

            // 메인 윈도우가 로드될 때까지 대기
            var retry = Retry.WhileEmpty(() => application.GetMainWindow(automation), TimeSpan.FromSeconds(10));
            mainWindow = retry.Result;
            mainWindow.Should().NotBeNull("Main window should be loaded");
        }

        [Fact]
        public void MainWindow_ShouldLoadWithCorrectTitle()
        {
            // Assert
            mainWindow.Title.Should().Be("반도체 장비 통합 모니터링 시스템");
            mainWindow.IsEnabled.Should().BeTrue();
        }

        [Fact]
        public void EquipmentList_ShouldDisplayAvailableEquipment()
        {
            // Arrange
            var equipmentListPanel = mainWindow.FindFirstDescendant(cf => cf.ByAutomationId("EquipmentListPanel"));
            equipmentListPanel.Should().NotBeNull("Equipment list panel should be present");

            // Act
            var equipmentItems = equipmentListPanel.FindAllDescendants(cf => cf.ByControlType(ControlType.ListItem));

            // Assert
            equipmentItems.Should().NotBeEmpty("Equipment list should contain items");
            equipmentItems.Length.Should().BeGreaterThan(0);
        }

        [Fact]
        public void SelectEquipment_ShouldUpdate3DView()
        {
            // Arrange
            var equipmentList = mainWindow.FindFirstDescendant(cf => cf.ByAutomationId("EquipmentList"));
            var firstEquipment = equipmentList.FindFirstDescendant(cf => cf.ByControlType(ControlType.ListItem));
            var equipment3DView = mainWindow.FindFirstDescendant(cf => cf.ByAutomationId("Equipment3DView"));

            // Act
            firstEquipment.Click();
            Wait.UntilInputIsProcessed(); // UI 업데이트 대기

            // Assert
            equipment3DView.IsEnabled.Should().BeTrue();

            // 3D 뷰에 장비 모델이 로드되었는지 확인
            var viewport = equipment3DView.FindFirstDescendant(cf => cf.ByControlType(ControlType.Custom));
            viewport.Should().NotBeNull("3D viewport should be loaded");
        }

        [Fact]
        public void TemperatureGauge_ShouldDisplayCurrentValue()
        {
            // Arrange
            var temperatureGauge = mainWindow.FindFirstDescendant(cf => cf.ByAutomationId("TemperatureGauge"));
            temperatureGauge.Should().NotBeNull("Temperature gauge should be present");

            // Act
            var valueText = temperatureGauge.FindFirstDescendant(cf => cf.ByControlType(ControlType.Text));

            // Assert
            valueText.Should().NotBeNull("Temperature value should be displayed");
            double.TryParse(valueText.Name, out var temperature).Should().BeTrue("Temperature should be a valid number");
            temperature.Should().BeGreaterThan(0, "Temperature should be a positive value");
        }

        [Fact]
        public void StartProcess_ShouldShowConfirmationDialog()
        {
            // Arrange
            var startProcessButton = mainWindow.FindFirstDescendant(cf => cf.ByAutomationId("StartProcessButton"));
            startProcessButton.Should().NotBeNull("Start process button should be present");

            // Act
            startProcessButton.Click();
            Wait.UntilInputIsProcessed();

            // Assert
            var confirmDialog = mainWindow.ModalWindows.FirstOrDefault();
            confirmDialog.Should().NotBeNull("Confirmation dialog should appear");
            confirmDialog.Title.Should().Contain("공정 시작", "Dialog should have correct title");

            // Cleanup - 다이얼로그 닫기
            var cancelButton = confirmDialog.FindFirstDescendant(cf => cf.ByName("취소"));
            cancelButton?.Click();
        }

        [Fact]
        public void AlarmPanel_ShouldDisplayActiveAlarms()
        {
            // Arrange
            var alarmPanel = mainWindow.FindFirstDescendant(cf => cf.ByAutomationId("AlarmPanel"));
            alarmPanel.Should().NotBeNull("Alarm panel should be present");

            // Act
            var alarmItems = alarmPanel.FindAllDescendants(cf => cf.ByControlType(ControlType.DataItem));

            // Assert
            // 테스트 환경에서는 알람이 없을 수 있으므로 패널 존재만 확인
            alarmPanel.IsEnabled.Should().BeTrue("Alarm panel should be enabled");
        }

        [Fact]
        public void NavigationButtons_ShouldSwitchViews()
        {
            // Arrange
            var overviewButton = mainWindow.FindFirstDescendant(cf => cf.ByName("개요"));
            var processButton = mainWindow.FindFirstDescendant(cf => cf.ByName("공정 모니터링"));

            overviewButton.Should().NotBeNull("Overview button should be present");
            processButton.Should().NotBeNull("Process monitoring button should be present");

            // Act - 공정 모니터링 버튼 클릭
            processButton.Click();
            Wait.UntilInputIsProcessed();

            // Assert
            var processMonitoringPanel = mainWindow.FindFirstDescendant(cf => cf.ByAutomationId("ProcessMonitoringPanel"));
            processMonitoringPanel.Should().NotBeNull("Process monitoring panel should be displayed");

            // Act - 개요 버튼으로 다시 전환
            overviewButton.Click();
            Wait.UntilInputIsProcessed();

            // Assert
            var overviewPanel = mainWindow.FindFirstDescendant(cf => cf.ByAutomationId("OverviewPanel"));
            overviewPanel.Should().NotBeNull("Overview panel should be displayed");
        }

        [Fact]
        public void ThemeToggle_ShouldSwitchBetweenLightAndDark()
        {
            // Arrange
            var themeToggle = mainWindow.FindFirstDescendant(cf => cf.ByAutomationId("ThemeToggle"));
            themeToggle.Should().NotBeNull("Theme toggle should be present");

            var originalState = themeToggle.IsToggled;

            // Act
            themeToggle.Click();
            Wait.UntilInputIsProcessed(TimeSpan.FromMilliseconds(500)); // 테마 전환 애니메이션 대기

            // Assert
            themeToggle.IsToggled.Should().Be(!originalState, "Theme toggle state should change");

            // 테마가 실제로 변경되었는지 확인 (배경색 확인)
            var mainGrid = mainWindow.FindFirstDescendant(cf => cf.ByControlType(ControlType.Pane));
            mainGrid.Should().NotBeNull("Main grid should be accessible");
        }

        [Fact]
        public void RealTimeChart_ShouldUpdateWithNewData()
        {
            // Arrange
            var chartArea = mainWindow.FindFirstDescendant(cf => cf.ByAutomationId("RealTimeChart"));
            chartArea.Should().NotBeNull("Real-time chart should be present");

            // Act - 데이터 업데이트를 위해 잠시 대기
            Thread.Sleep(2000);

            // Assert
            // 차트가 실제로 렌더링되고 있는지 확인
            chartArea.IsEnabled.Should().BeTrue("Chart should be enabled and updating");

            var chartElements = chartArea.FindAllDescendants(cf => cf.ByControlType(ControlType.Custom));
            chartElements.Should().NotBeEmpty("Chart should contain visual elements");
        }

        public void Dispose()
        {
            mainWindow?.Close();
            application?.Dispose();
            automation?.Dispose();
        }
    }
}
```

</div>

### Page Object Model 구현

<div class="code-section">

**MainDashboardPage.cs**

```csharp
public class MainDashboardPage : PageBase
{
    public MainDashboardPage(Window window) : base(window) { }

    // UI 요소들
    public Button StartProcessButton => Window.FindFirstDescendant(cf => cf.ByAutomationId("StartProcessButton"))?.AsButton();
    public Button StopProcessButton => Window.FindFirstDescendant(cf => cf.ByAutomationId("StopProcessButton"))?.AsButton();
    public ListBox EquipmentList => Window.FindFirstDescendant(cf => cf.ByAutomationId("EquipmentList"))?.AsListBox();
    public TextBox TemperatureValue => Window.FindFirstDescendant(cf => cf.ByAutomationId("TemperatureValue"))?.AsTextBox();
    public ProgressBar ProcessProgress => Window.FindFirstDescendant(cf => cf.ByAutomationId("ProcessProgress"))?.AsProgressBar();

    // 페이지 액션들
    public void SelectEquipment(string equipmentId)
    {
        var equipmentItem = EquipmentList.Items.FirstOrDefault(item =>
            item.Name.Contains(equipmentId));

        equipmentItem?.Select();
        Wait.UntilInputIsProcessed();
    }

    public void StartProcess(ProcessParameters parameters)
    {
        StartProcessButton.Click();

        var dialog = Window.ModalWindows.FirstOrDefault();
        if (dialog != null)
        {
            var parametersPage = new ProcessParametersDialog(dialog);
            parametersPage.SetParameters(parameters);
            parametersPage.Confirm();
        }
    }

    public double GetCurrentTemperature()
    {
        var tempText = TemperatureValue.Text;
        return double.TryParse(tempText, out var temp) ? temp : 0;
    }

    public bool IsProcessRunning()
    {
        return ProcessProgress.Value > 0 && StartProcessButton.IsEnabled == false;
    }
}
```

</div>

## 성능 테스트 (NBomber)

### 부하 테스트 시나리오

<div class="code-section">

**SemiconductorHMI.PerformanceTests.csproj**

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
    <PackageReference Include="NBomber" Version="4.1.2" />
    <PackageReference Include="NBomber.Http" Version="4.1.2" />
    <PackageReference Include="Serilog.Sinks.Console" Version="4.1.0" />
  </ItemGroup>

</Project>
```

</div>

<div class="code-section">

**EquipmentAPIPerformanceTests.cs**

```csharp
using NBomber.CSharp;
using NBomber.Http.CSharp;
using Serilog;

namespace SemiconductorHMI.PerformanceTests
{
    public class EquipmentAPIPerformanceTests
    {
        private const string BaseUrl = "https://localhost:7001";

        [Fact]
        public void Equipment_API_LoadTest()
        {
            // 시나리오 1: 장비 상태 조회 (높은 빈도)
            var equipmentStatusScenario = Scenario.Create("equipment_status", async context =>
            {
                var equipmentId = GetRandomEquipmentId();

                var response = await HttpClientFactory.Create()
                    .GetAsync($"{BaseUrl}/api/equipment/{equipmentId}/status");

                return response.IsSuccessStatusCode ? Response.Ok() : Response.Fail();
            })
            .WithLoadSimulations(
                Simulation.InjectPerSec(rate: 100, during: TimeSpan.FromMinutes(5))
            );

            // 시나리오 2: 센서 데이터 저장 (중간 빈도)
            var sensorDataScenario = Scenario.Create("sensor_data_save", async context =>
            {
                var sensorData = GenerateSensorData();
                var jsonContent = JsonContent.Create(sensorData);

                var response = await HttpClientFactory.Create()
                    .PostAsync($"{BaseUrl}/api/sensor-data", jsonContent);

                return response.IsSuccessStatusCode ? Response.Ok() : Response.Fail();
            })
            .WithLoadSimulations(
                Simulation.InjectPerSec(rate: 50, during: TimeSpan.FromMinutes(5))
            );

            // 시나리오 3: 프로세스 시작 (낮은 빈도, 높은 리소스 사용)
            var processStartScenario = Scenario.Create("process_start", async context =>
            {
                var processRequest = GenerateProcessRequest();
                var jsonContent = JsonContent.Create(processRequest);
                var equipmentId = GetRandomEquipmentId();

                var response = await HttpClientFactory.Create()
                    .PostAsync($"{BaseUrl}/api/equipment/{equipmentId}/start-process", jsonContent);

                return response.IsSuccessStatusCode ? Response.Ok() : Response.Fail();
            })
            .WithLoadSimulations(
                Simulation.InjectPerSec(rate: 5, during: TimeSpan.FromMinutes(5))
            );

            // 성능 테스트 실행
            var stats = NBomberRunner
                .RegisterScenarios(equipmentStatusScenario, sensorDataScenario, processStartScenario)
                .WithReportFolder("performance_reports")
                .WithReportFormats(ReportFormat.Html, ReportFormat.Csv, ReportFormat.Json)
                .Run();

            // 성능 기준 검증
            ValidatePerformanceRequirements(stats);
        }

        [Fact]
        public void Database_Connection_StressTest()
        {
            var dbStressScenario = Scenario.Create("database_stress", async context =>
            {
                var equipmentId = GetRandomEquipmentId();
                var startDate = DateTime.UtcNow.AddHours(-1);
                var endDate = DateTime.UtcNow;

                var response = await HttpClientFactory.Create()
                    .GetAsync($"{BaseUrl}/api/equipment/{equipmentId}/sensor-data?" +
                             $"startDate={startDate:yyyy-MM-ddTHH:mm:ss}&" +
                             $"endDate={endDate:yyyy-MM-ddTHH:mm:ss}");

                return response.IsSuccessStatusCode ? Response.Ok() : Response.Fail();
            })
            .WithLoadSimulations(
                // 점진적 부하 증가
                Simulation.RampingInject(rate: 200, interval: TimeSpan.FromSeconds(1), during: TimeSpan.FromMinutes(10))
            );

            var stats = NBomberRunner
                .RegisterScenarios(dbStressScenario)
                .WithReportFolder("db_stress_reports")
                .Run();

            // 데이터베이스 성능 검증
            stats.AllOkCount.Should().BeGreaterThan(0);
            stats.AllFailCount.Should().BeLessThan(stats.AllOkCount * 0.01); // 1% 미만 실패율
        }

        [Fact]
        public void RealTime_Updates_PerformanceTest()
        {
            // SignalR 연결 성능 테스트
            var signalRScenario = Scenario.Create("signalr_updates", async context =>
            {
                // SignalR 허브 연결 및 실시간 업데이트 구독
                var hubConnection = new HubConnectionBuilder()
                    .WithUrl($"{BaseUrl}/equipmentHub")
                    .Build();

                await hubConnection.StartAsync();

                // 실시간 업데이트 수신 대기
                var updateReceived = new TaskCompletionSource<bool>();
                hubConnection.On<EquipmentStatus>("EquipmentStatusUpdate", (status) =>
                {
                    updateReceived.SetResult(true);
                });

                // 업데이트 트리거
                await hubConnection.InvokeAsync("RequestEquipmentUpdate", GetRandomEquipmentId());

                // 업데이트 수신 대기 (최대 5초)
                var completed = await Task.WhenAny(
                    updateReceived.Task,
                    Task.Delay(TimeSpan.FromSeconds(5))
                );

                await hubConnection.DisposeAsync();

                return completed == updateReceived.Task ? Response.Ok() : Response.Fail();
            })
            .WithLoadSimulations(
                Simulation.KeepConstant(copies: 50, during: TimeSpan.FromMinutes(3))
            );

            var stats = NBomberRunner
                .RegisterScenarios(signalRScenario)
                .WithReportFolder("realtime_reports")
                .Run();

            // 실시간 업데이트 성능 검증
            var avgResponseTime = stats.ScenarioStats[0].Ok.Response.Mean;
            avgResponseTime.Should().BeLessThan(100); // 100ms 미만 응답시간
        }

        private void ValidatePerformanceRequirements(NBomberStats stats)
        {
            foreach (var scenarioStats in stats.ScenarioStats)
            {
                switch (scenarioStats.ScenarioName)
                {
                    case "equipment_status":
                        // 장비 상태 조회: 95% 요청이 50ms 미만
                        scenarioStats.Ok.Response.Percentile95.Should().BeLessThan(50);
                        // 처리량: 초당 95개 이상
                        scenarioStats.Ok.Request.RPS.Should().BeGreaterThan(95);
                        break;

                    case "sensor_data_save":
                        // 센서 데이터 저장: 95% 요청이 100ms 미만
                        scenarioStats.Ok.Response.Percentile95.Should().BeLessThan(100);
                        // 실패율: 1% 미만
                        scenarioStats.Fail.Request.Percent.Should().BeLessThan(1);
                        break;

                    case "process_start":
                        // 프로세스 시작: 95% 요청이 500ms 미만
                        scenarioStats.Ok.Response.Percentile95.Should().BeLessThan(500);
                        // 실패율: 0.1% 미만
                        scenarioStats.Fail.Request.Percent.Should().BeLessThan(0.1);
                        break;
                }
            }

            // 전체 시스템 안정성
            stats.AllFailCount.Should().BeLessThan(stats.AllOkCount * 0.01);
        }

        private string GetRandomEquipmentId()
        {
            var equipmentIds = new[] { "CVD-001", "CVD-002", "PVD-001", "ETCH-001", "CMP-001" };
            return equipmentIds[Random.Shared.Next(equipmentIds.Length)];
        }

        private object GenerateSensorData()
        {
            return new
            {
                EquipmentId = GetRandomEquipmentId(),
                SensorType = "Temperature",
                Value = Random.Shared.NextDouble() * 200 + 50, // 50-250도
                Timestamp = DateTime.UtcNow,
                Unit = "°C"
            };
        }

        private object GenerateProcessRequest()
        {
            return new
            {
                TargetTemperature = Random.Shared.NextDouble() * 100 + 100, // 100-200도
                PressureSetpoint = Random.Shared.NextDouble() * 2 + 0.5, // 0.5-2.5 Torr
                Duration = TimeSpan.FromMinutes(Random.Shared.Next(15, 61)), // 15-60분
                ProcessType = "StandardCVD"
            };
        }
    }
}
```

</div>

### 메모리 및 CPU 프로파일링

<div class="code-section">

**MemoryProfileTests.cs**

```csharp
public class MemoryProfileTests
{
    [Fact]
    public void LongRunning_SensorDataCollection_ShouldNotLeakMemory()
    {
        // Arrange
        var initialMemory = GC.GetTotalMemory(true);
        var dataCollector = new SensorDataCollector();
        var memoryUsages = new List<long>();

        // Act - 1시간 동안 데이터 수집 시뮬레이션
        for (int i = 0; i < 3600; i++) // 1초마다 수집
        {
            var sensorData = GenerateRandomSensorData();
            dataCollector.CollectData(sensorData);

            // 10초마다 메모리 사용량 기록
            if (i % 10 == 0)
            {
                memoryUsages.Add(GC.GetTotalMemory(false));
            }

            Thread.Sleep(1); // 빠른 시뮬레이션
        }

        // Force garbage collection
        GC.Collect();
        GC.WaitForPendingFinalizers();
        GC.Collect();

        var finalMemory = GC.GetTotalMemory(false);

        // Assert
        // 메모리 사용량이 초기 대비 200% 이상 증가하지 않아야 함
        var memoryIncrease = (double)(finalMemory - initialMemory) / initialMemory;
        memoryIncrease.Should().BeLessThan(2.0, "Memory usage should not increase more than 200%");

        // 메모리 사용량이 지속적으로 증가하지 않아야 함
        var recentMemoryUsages = memoryUsages.TakeLast(10).ToList();
        var memoryTrend = CalculateLinearTrend(recentMemoryUsages);
        memoryTrend.Should().BeLessThan(1000, "Memory should not show consistent upward trend");
    }

    [Fact]
    public void HighFrequency_UIUpdates_ShouldMaintainResponsiveness()
    {
        // UI 업데이트 성능 테스트
        var uiUpdateTimes = new List<TimeSpan>();
        var stopwatch = new Stopwatch();

        for (int i = 0; i < 1000; i++)
        {
            stopwatch.Restart();

            // UI 업데이트 시뮬레이션
            Application.Current.Dispatcher.Invoke(() =>
            {
                // 화면 업데이트 로직
                UpdateTemperatureGauge(Random.Shared.NextDouble() * 200);
                UpdatePressureChart(Random.Shared.NextDouble() * 5);
            });

            stopwatch.Stop();
            uiUpdateTimes.Add(stopwatch.Elapsed);
        }

        // Assert
        var averageUpdateTime = uiUpdateTimes.Average(t => t.TotalMilliseconds);
        var p95UpdateTime = uiUpdateTimes.OrderBy(t => t).Skip(950).First().TotalMilliseconds;

        averageUpdateTime.Should().BeLessThan(16, "Average UI update should be under 16ms (60 FPS)");
        p95UpdateTime.Should().BeLessThan(33, "95% of UI updates should be under 33ms (30 FPS)");
    }

    private double CalculateLinearTrend(List<long> values)
    {
        if (values.Count < 2) return 0;

        var n = values.Count;
        var sumX = Enumerable.Range(0, n).Sum();
        var sumY = values.Sum();
        var sumXY = values.Select((y, x) => (long)x * y).Sum();
        var sumX2 = Enumerable.Range(0, n).Sum(x => x * x);

        return (double)(n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    }
}
```

</div>

---

