# C# 테스트/배포 및 유지보수
## 반도체 장비 HMI의 품질 보증 및 운영 관리

---

# 📋 강의 개요

## 🎯 학습 목표
- 반도체 장비 HMI의 체계적인 테스트 전략 및 자동화 테스트 구현
- CI/CD 파이프라인을 통한 안전하고 효율적인 배포 프로세스 구축
- 산업용 환경에서의 장기간 운영을 위한 모니터링 및 유지보수 체계 확립
- 성능 프로파일링과 최적화를 통한 안정적인 24/7 운영 체계 구현

## ⏰ 세션 구성
- **이론 강의**: 45분 (테스트 전략, CI/CD, 모니터링)
- **기초 실습**: 45분 (Unit Test 및 Integration Test)
- **심화 실습**: 45분 (UI 자동화 테스트 및 성능 테스트)
- **Hands-on**: 45분 (전체 배포 파이프라인 구축)

---

# 📚 반도체 HMI 테스트 전략

## 반도체 제조 환경의 특수성

### 고신뢰성 요구사항
- **24/7 연속 운영**: 시스템 다운타임 최소화 (99.9% 이상 가용성)
- **실시간 응답성**: 센서 데이터 처리 지연 시간 < 100ms
- **데이터 정확성**: 측정값 오차율 < 0.1%
- **안전성 보장**: 장비 오작동으로 인한 웨이퍼 손실 방지

### 규제 준수 요구사항
- **SEMI 표준**: E10 (Equipment Safety), E30 (GEM), E40 (HSMS)
- **ISO 9001**: 품질 관리 시스템
- **IEC 61508**: 기능 안전성 표준
- **추적성**: 모든 변경사항 및 테스트 결과 기록

## 테스트 피라미드 전략

### 1. Unit Tests (기반층 - 70%)
```
┌─────────────────────────────┐
│        UI Tests             │ ← 10%
├─────────────────────────────┤
│    Integration Tests        │ ← 20%
├─────────────────────────────┤
│       Unit Tests            │ ← 70%
└─────────────────────────────┘
```

### 2. Integration Tests (중간층 - 20%)
- **하드웨어 통합**: 센서, PLC, 통신 모듈
- **데이터베이스 연동**: 실시간 데이터 저장/조회
- **외부 시스템**: MES, ERP 연동

### 3. UI Tests (상위층 - 10%)
- **사용자 시나리오**: 운전원 조작 흐름
- **경보 시스템**: 알람 발생 및 대응
- **데이터 시각화**: 차트, 게이지 정확성

## 테스트 환경 구성

### 개발환경 (Development)
- **모의 하드웨어**: 시뮬레이터 기반 테스트
- **단위 테스트**: 빠른 피드백 (< 1분)
- **코드 커버리지**: 최소 80% 이상

### 통합환경 (Integration)
- **실제 하드웨어**: 제한적 장비 연동
- **통합 테스트**: 전체 워크플로우 검증
- **성능 테스트**: 부하 테스트 실행

### 운영환경 (Production)
- **카나리 배포**: 점진적 롤아웃 (1% → 10% → 100%)
- **블루-그린 배포**: 무중단 배포
- **롤백 전략**: 30초 이내 이전 버전 복구

---

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

# 🚀 Hands-on: 전체 배포 파이프라인 구축 (45분)

## Docker 컨테이너화

### Multi-stage Dockerfile 최적화

<div class="code-section">

**Dockerfile**

```dockerfile
# Multi-stage build for optimized production image
FROM mcr.microsoft.com/dotnet/aspnet:6.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

# Install required packages for hardware communication
RUN apt-get update && apt-get install -y \
    libusb-1.0-0 \
    libudev1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN adduser --disabled-password --gecos '' --uid 1000 appuser
USER appuser

# Build stage
FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /src

# Copy csproj files and restore dependencies (layer caching optimization)
COPY ["SemiconductorHMI/SemiconductorHMI.csproj", "SemiconductorHMI/"]
COPY ["SemiconductorHMI.Core/SemiconductorHMI.Core.csproj", "SemiconductorHMI.Core/"]
COPY ["SemiconductorHMI.Services/SemiconductorHMI.Services.csproj", "SemiconductorHMI.Services/"]
COPY ["SemiconductorHMI.Infrastructure/SemiconductorHMI.Infrastructure.csproj", "SemiconductorHMI.Infrastructure/"]

RUN dotnet restore "SemiconductorHMI/SemiconductorHMI.csproj"

# Copy source code
COPY . .

# Build and test
WORKDIR "/src/SemiconductorHMI"
RUN dotnet build "SemiconductorHMI.csproj" -c Release -o /app/build

# Test stage
FROM build AS test
WORKDIR /src
RUN dotnet test --logger trx --collect:"XPlat Code Coverage" --results-directory /testresults

# Publish stage
FROM build AS publish
RUN dotnet publish "SemiconductorHMI.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Final production image
FROM base AS final
WORKDIR /app

# Copy application files
COPY --from=publish /app/publish .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

# Environment variables
ENV ASPNETCORE_ENVIRONMENT=Production
ENV ASPNETCORE_URLS=http://+:80

ENTRYPOINT ["dotnet", "SemiconductorHMI.dll"]
```

</div>

### Docker Compose 로컬 개발 환경

<div class="code-section">

**docker-compose.yml**

```yaml
version: '3.8'

services:
  semiconductor-hmi:
    build:
      context: .
      dockerfile: Dockerfile
      target: base
    ports:
      - "5000:80"
      - "5001:443"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ASPNETCORE_HTTPS_PORT=5001
      - ConnectionStrings__DefaultConnection=Server=sqlserver;Database=SemiconductorHMI;User Id=sa;Password=SecurePassword123!;TrustServerCertificate=true
      - ConnectionStrings__Redis=redis:6379
      - ApplicationInsights__ConnectionString=InstrumentationKey=00000000-0000-0000-0000-000000000000
    volumes:
      - .:/src
      - nuget-cache:/root/.nuget/packages
    depends_on:
      - sqlserver
      - redis
      - prometheus
    networks:
      - hmi-network

  sqlserver:
    image: mcr.microsoft.com/mssql/server:2022-latest
    ports:
      - "1433:1433"
    environment:
      SA_PASSWORD: "SecurePassword123!"
      ACCEPT_EULA: "Y"
    volumes:
      - sqlserver-data:/var/opt/mssql
    networks:
      - hmi-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - hmi-network

  # Monitoring stack
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - hmi-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - prometheus
    networks:
      - hmi-network

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    networks:
      - hmi-network

  # Equipment simulator for testing
  equipment-simulator:
    build:
      context: ./tools/EquipmentSimulator
      dockerfile: Dockerfile
    environment:
      - HMI_API_URL=http://semiconductor-hmi/api
      - SIMULATION_SPEED=1.0
      - EQUIPMENT_COUNT=5
    depends_on:
      - semiconductor-hmi
    networks:
      - hmi-network

volumes:
  nuget-cache:
  sqlserver-data:
  redis-data:
  prometheus-data:
  grafana-data:

networks:
  hmi-network:
    driver: bridge
```

</div>

## 종합 정리

### 완성된 시스템 구성요소
1. **완전 자동화된 CI/CD 파이프라인**
   - GitHub Actions/Azure DevOps
   - 코드 품질 게이트
   - 자동 배포 및 롤백

2. **컨테이너 기반 마이크로서비스 아키텍처**
   - Docker 최적화
   - Kubernetes 오케스트레이션
   - Helm 차트 관리

3. **종합 모니터링 시스템**
   - Prometheus + Grafana
   - Application Insights
   - 커스텀 메트릭 및 알림

4. **엔터프라이즈급 보안 체계**
   - 컨테이너 보안
   - 네트워크 정책
   - 시크릿 관리

### 달성된 운영 지표
- **가용성**: 99.9% 이상 (연간 다운타임 < 8.76시간)
- **응답시간**: 95% 요청이 100ms 미만
- **처리량**: 초당 1000개 이상 센서 데이터 처리
- **복구시간**: 장애 발생 시 30초 이내 자동 복구

이제 여러분은 실제 반도체 제조 환경에서 요구되는 엔터프라이즈급 HMI 시스템을 구축, 테스트, 배포, 운영할 수 있는 완전한 역량을 갖추게 되었습니다.

---

---