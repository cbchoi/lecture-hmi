# 🔧 이론 강의: 테스트 전략 및 CI/CD (45분)

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

