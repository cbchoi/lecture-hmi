# Week 13: ImGUI C++ 통합 프로젝트 - 최종 산업용 HMI 솔루션

## 🎯 최종 프로젝트 목표
1. **시스템 통합**: 12주간 개발한 모든 컴포넌트 완전 통합
2. **배포 자동화**: Docker/K8s 기반 엔터프라이즈 배포 시스템
3. **보안 강화**: 산업용 표준 보안 적용
4. **성능 최적화**: 실시간 대용량 데이터 처리
5. **최종 시연**: 실제 팹 환경 시뮬레이션

---

## 🏗️ 통합 개발 (60분): 전체 시스템 아키텍처 완성

### 1. 마스터 아키텍처 설계 (20분)

#### 1.1 엔터프라이즈 시스템 아키텍처

```cpp
// MasterSystemArchitecture.h
#pragma once
#include <memory>
#include <vector>
#include <unordered_map>
#include <thread>
#include <atomic>
#include <chrono>

// 모든 이전 주차 헤더 통합
#include "WPFStyleUIFramework.h"          // Week 2-5
#include "PySideIntegration.h"            // Week 6-9
#include "AdvancedRenderingEngine.h"      // Week 10-11
#include "PluginManager.h"                // Week 12
#include "DataVisualizationEngine.h"
#include "ThreadSafeRenderer.h"
#include "InternationalizationSystem.h"
#include "AccessibilitySystem.h"
#include "MQTTIntegration.h"

namespace SemiconductorHMI::Enterprise {

// 시스템 전체 상태 관리
enum class SystemStatus {
    INITIALIZING,
    RUNNING,
    MAINTENANCE,
    ERROR,
    SHUTDOWN
};

// 모듈 타입 정의
enum class ModuleType {
    UI_FRAMEWORK,
    DATA_PROCESSING,
    VISUALIZATION,
    NETWORKING,
    SECURITY,
    MONITORING,
    PLUGIN_SYSTEM
};

// 시스템 메트릭스
struct SystemMetrics {
    double cpu_usage = 0.0;
    double memory_usage_mb = 0.0;
    double gpu_usage = 0.0;
    double gpu_memory_mb = 0.0;
    int active_connections = 0;
    int active_plugins = 0;
    int data_points_per_second = 0;
    std::chrono::system_clock::time_point last_update;
};

// 모듈 인터페이스
class ISystemModule {
public:
    virtual ~ISystemModule() = default;
    virtual bool Initialize() = 0;
    virtual void Shutdown() = 0;
    virtual void Update(float deltaTime) = 0;
    virtual ModuleType GetModuleType() const = 0;
    virtual std::string GetModuleName() const = 0;
    virtual bool IsHealthy() const = 0;
    virtual SystemMetrics GetMetrics() const = 0;
};

// 마스터 시스템 컨트롤러
class MasterSystemController {
private:
    std::vector<std::unique_ptr<ISystemModule>> modules_;
    std::unordered_map<ModuleType, ISystemModule*> module_registry_;

    SystemStatus current_status_ = SystemStatus::INITIALIZING;
    SystemMetrics global_metrics_;

    // 시스템 스레드들
    std::thread health_monitor_thread_;
    std::thread metrics_collector_thread_;
    std::thread backup_manager_thread_;

    std::atomic<bool> system_running_{false};

    // 설정 관리
    struct SystemConfiguration {
        std::string system_name = "SemiconductorHMI_Enterprise";
        std::string version = "1.0.0";
        std::string config_file_path = "./config/system.json";

        // 성능 설정
        int max_worker_threads = 8;
        int target_fps = 60;
        bool enable_gpu_acceleration = true;

        // 보안 설정
        bool enable_encryption = true;
        bool enable_audit_logging = true;
        std::string certificate_path = "./certs/";

        // 네트워크 설정
        std::string mqtt_broker = "localhost:1883";
        std::string database_connection = "postgresql://localhost:5432/hmi_db";
        std::string backup_location = "./backups/";

        // 모니터링 설정
        int health_check_interval_ms = 5000;
        int metrics_collection_interval_ms = 1000;
        int backup_interval_hours = 24;
    } config_;

public:
    MasterSystemController() = default;
    ~MasterSystemController() { Shutdown(); }

    // 시스템 초기화
    bool Initialize(const std::string& config_file = "") {
        if (!config_file.empty()) {
            LoadConfiguration(config_file);
        }

        try {
            // 핵심 모듈들 초기화
            InitializeCoreModules();

            // 플러그인 모듈들 로드
            LoadPluginModules();

            // 시스템 스레드 시작
            StartSystemThreads();

            current_status_ = SystemStatus::RUNNING;
            system_running_ = true;

            LogSystemEvent("System initialized successfully");
            return true;

        } catch (const std::exception& e) {
            current_status_ = SystemStatus::ERROR;
            LogSystemEvent("System initialization failed: " + std::string(e.what()));
            return false;
        }
    }

    // 메인 시스템 루프
    void Run() {
        auto last_frame_time = std::chrono::high_resolution_clock::now();

        while (system_running_ && current_status_ == SystemStatus::RUNNING) {
            auto current_time = std::chrono::high_resolution_clock::now();
            float delta_time = std::chrono::duration<float>(current_time - last_frame_time).count();
            last_frame_time = current_time;

            // 모든 모듈 업데이트
            UpdateAllModules(delta_time);

            // 글로벌 메트릭스 수집
            CollectGlobalMetrics();

            // 프레임 레이트 제한
            if (config_.target_fps > 0) {
                auto frame_duration = std::chrono::microseconds(1000000 / config_.target_fps);
                auto frame_end = current_time + frame_duration;
                std::this_thread::sleep_until(frame_end);
            }
        }
    }

    // 모듈 등록
    template<typename T, typename... Args>
    T* RegisterModule(Args&&... args) {
        auto module = std::make_unique<T>(std::forward<Args>(args)...);
        T* module_ptr = module.get();

        modules_.push_back(std::move(module));
        module_registry_[module_ptr->GetModuleType()] = module_ptr;

        return module_ptr;
    }

    // 모듈 가져오기
    template<typename T>
    T* GetModule(ModuleType type) {
        auto it = module_registry_.find(type);
        if (it != module_registry_.end()) {
            return dynamic_cast<T*>(it->second);
        }
        return nullptr;
    }

    // 시스템 상태 관리
    SystemStatus GetSystemStatus() const { return current_status_; }
    const SystemMetrics& GetGlobalMetrics() const { return global_metrics_; }
    const SystemConfiguration& GetConfiguration() const { return config_; }

    // 시스템 제어
    void RequestMaintenance() {
        current_status_ = SystemStatus::MAINTENANCE;
        LogSystemEvent("Maintenance mode requested");
    }

    void ResumFromMaintenance() {
        current_status_ = SystemStatus::RUNNING;
        LogSystemEvent("Resumed from maintenance mode");
    }

    void Shutdown() {
        if (system_running_) {
            current_status_ = SystemStatus::SHUTDOWN;
            system_running_ = false;

            // 시스템 스레드들 정리
            if (health_monitor_thread_.joinable()) health_monitor_thread_.join();
            if (metrics_collector_thread_.joinable()) metrics_collector_thread_.join();
            if (backup_manager_thread_.joinable()) backup_manager_thread_.join();

            // 모든 모듈 종료
            for (auto& module : modules_) {
                module->Shutdown();
            }

            LogSystemEvent("System shutdown completed");
        }
    }

private:
    void InitializeCoreModules() {
        // UI 프레임워크 모듈
        auto ui_module = RegisterModule<UIFrameworkModule>();
        ui_module->Initialize();

        // 데이터 처리 모듈
        auto data_module = RegisterModule<DataProcessingModule>();
        data_module->Initialize();

        // 시각화 모듈
        auto viz_module = RegisterModule<VisualizationModule>();
        viz_module->Initialize();

        // 네트워킹 모듈
        auto net_module = RegisterModule<NetworkingModule>();
        net_module->Initialize();

        // 보안 모듈
        auto security_module = RegisterModule<SecurityModule>();
        security_module->Initialize();

        // 모니터링 모듈
        auto monitor_module = RegisterModule<MonitoringModule>();
        monitor_module->Initialize();
    }

    void LoadPluginModules() {
        auto plugin_system = GetModule<PluginSystemModule>(ModuleType::PLUGIN_SYSTEM);
        if (plugin_system) {
            plugin_system->LoadAllPlugins("./plugins");
        }
    }

    void StartSystemThreads() {
        // 헬스 모니터링 스레드
        health_monitor_thread_ = std::thread([this]() {
            HealthMonitorLoop();
        });

        // 메트릭스 수집 스레드
        metrics_collector_thread_ = std::thread([this]() {
            MetricsCollectionLoop();
        });

        // 백업 관리 스레드
        backup_manager_thread_ = std::thread([this]() {
            BackupManagerLoop();
        });
    }

    void UpdateAllModules(float delta_time) {
        for (auto& module : modules_) {
            if (module->IsHealthy()) {
                module->Update(delta_time);
            } else {
                LogSystemEvent("Module " + module->GetModuleName() + " is unhealthy");
                // 모듈 재시작 로직
                RestartModule(module.get());
            }
        }
    }

    void CollectGlobalMetrics() {
        global_metrics_ = SystemMetrics{};
        global_metrics_.last_update = std::chrono::system_clock::now();

        for (const auto& module : modules_) {
            auto module_metrics = module->GetMetrics();
            global_metrics_.cpu_usage += module_metrics.cpu_usage;
            global_metrics_.memory_usage_mb += module_metrics.memory_usage_mb;
            global_metrics_.gpu_usage += module_metrics.gpu_usage;
            global_metrics_.gpu_memory_mb += module_metrics.gpu_memory_mb;
        }

        // 시스템 전체 리소스 사용률 계산
        global_metrics_.cpu_usage = std::min(global_metrics_.cpu_usage, 100.0);
        global_metrics_.gpu_usage = std::min(global_metrics_.gpu_usage, 100.0);
    }

    void HealthMonitorLoop() {
        while (system_running_) {
            // 모든 모듈의 헬스 체크
            for (auto& module : modules_) {
                if (!module->IsHealthy()) {
                    LogSystemEvent("Health check failed for " + module->GetModuleName());
                    // 알람 발생 또는 자동 복구 시도
                }
            }

            std::this_thread::sleep_for(
                std::chrono::milliseconds(config_.health_check_interval_ms)
            );
        }
    }

    void MetricsCollectionLoop() {
        while (system_running_) {
            CollectGlobalMetrics();

            // 메트릭스를 모니터링 시스템에 전송
            SendMetricsToMonitoring();

            std::this_thread::sleep_for(
                std::chrono::milliseconds(config_.metrics_collection_interval_ms)
            );
        }
    }

    void BackupManagerLoop() {
        while (system_running_) {
            // 시스템 백업 수행
            PerformSystemBackup();

            std::this_thread::sleep_for(
                std::chrono::hours(config_.backup_interval_hours)
            );
        }
    }

    void RestartModule(ISystemModule* module) {
        LogSystemEvent("Restarting module: " + module->GetModuleName());

        module->Shutdown();
        std::this_thread::sleep_for(std::chrono::seconds(1));

        if (module->Initialize()) {
            LogSystemEvent("Module restart successful: " + module->GetModuleName());
        } else {
            LogSystemEvent("Module restart failed: " + module->GetModuleName());
            current_status_ = SystemStatus::ERROR;
        }
    }

    void LoadConfiguration(const std::string& config_file) {
        // JSON 설정 파일 로드 로직
        // 실제 구현에서는 JSON 라이브러리 사용
    }

    void SendMetricsToMonitoring() {
        // Prometheus/Grafana 등으로 메트릭스 전송
    }

    void PerformSystemBackup() {
        // 시스템 설정 및 데이터 백업
    }

    void LogSystemEvent(const std::string& message) {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);

        // 실제 로깅 시스템에 전송 (spdlog 등 사용)
        printf("[%s] %s\n", std::ctime(&time_t), message.c_str());
    }
};

} // namespace SemiconductorHMI::Enterprise
```

#### 1.2 모듈별 통합 구현

```cpp
// IntegratedModules.cpp
#include "MasterSystemArchitecture.h"

namespace SemiconductorHMI::Enterprise {

// UI 프레임워크 모듈
class UIFrameworkModule : public ISystemModule {
private:
    std::unique_ptr<WPF::WPFStyleManager> wpf_manager_;
    std::unique_ptr<Visualization::AdvancedChartRenderer> chart_renderer_;
    std::unique_ptr<I18n::LocalizationManager> localization_;
    std::unique_ptr<Accessibility::AccessibilityManager> accessibility_;

public:
    bool Initialize() override {
        try {
            // WPF 스타일 시스템 초기화
            wpf_manager_ = std::make_unique<WPF::WPFStyleManager>();
            wpf_manager_->LoadDefaultThemes();

            // 차트 렌더러 초기화
            chart_renderer_ = std::make_unique<Visualization::AdvancedChartRenderer>();

            // 국제화 시스템 초기화
            localization_ = std::make_unique<I18n::LocalizationManager>();
            localization_->SetLanguage(I18n::Language::KOREAN);

            // 접근성 시스템 초기화
            accessibility_ = std::make_unique<Accessibility::AccessibilityManager>();
            accessibility_->Initialize();

            return true;
        } catch (const std::exception& e) {
            return false;
        }
    }

    void Shutdown() override {
        accessibility_.reset();
        localization_.reset();
        chart_renderer_.reset();
        wpf_manager_.reset();
    }

    void Update(float deltaTime) override {
        // UI 프레임워크 업데이트
        if (wpf_manager_) {
            wpf_manager_->UpdateAnimations(deltaTime);
        }
    }

    ModuleType GetModuleType() const override { return ModuleType::UI_FRAMEWORK; }
    std::string GetModuleName() const override { return "UI Framework Module"; }
    bool IsHealthy() const override { return wpf_manager_ && chart_renderer_; }

    SystemMetrics GetMetrics() const override {
        SystemMetrics metrics;
        metrics.cpu_usage = 5.0; // UI 렌더링 CPU 사용률
        metrics.memory_usage_mb = 150.0;
        metrics.gpu_usage = 20.0;
        metrics.gpu_memory_mb = 200.0;
        return metrics;
    }

    // UI 컴포넌트 접근자
    WPF::WPFStyleManager* GetWPFManager() { return wpf_manager_.get(); }
    Visualization::AdvancedChartRenderer* GetChartRenderer() { return chart_renderer_.get(); }
    I18n::LocalizationManager* GetLocalization() { return localization_.get(); }
    Accessibility::AccessibilityManager* GetAccessibility() { return accessibility_.get(); }
};

// 데이터 처리 모듈
class DataProcessingModule : public ISystemModule {
private:
    std::unordered_map<std::string, std::unique_ptr<Visualization::TimeSeriesBuffer>> data_buffers_;
    std::unique_ptr<Threading::MultiThreadedRenderer> thread_renderer_;

    // 실시간 데이터 스트림
    std::vector<std::thread> data_processors_;
    std::atomic<bool> processing_active_{false};

    // 데이터 통계
    std::atomic<int> data_points_processed_{0};
    std::atomic<int> data_points_per_second_{0};

public:
    bool Initialize() override {
        try {
            // 멀티스레드 렌더러 초기화
            thread_renderer_ = std::make_unique<Threading::MultiThreadedRenderer>(4);

            // 데이터 버퍼 초기화
            InitializeDataBuffers();

            // 데이터 처리 스레드 시작
            StartDataProcessors();

            processing_active_ = true;
            return true;
        } catch (const std::exception& e) {
            return false;
        }
    }

    void Shutdown() override {
        processing_active_ = false;

        // 데이터 처리 스레드 정리
        for (auto& processor : data_processors_) {
            if (processor.joinable()) {
                processor.join();
            }
        }

        thread_renderer_.reset();
        data_buffers_.clear();
    }

    void Update(float deltaTime) override {
        // 데이터 처리 성능 모니터링
        static auto last_count_time = std::chrono::steady_clock::now();
        static int last_count = 0;

        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(now - last_count_time);

        if (elapsed.count() >= 1) {
            int current_count = data_points_processed_.load();
            data_points_per_second_ = current_count - last_count;
            last_count = current_count;
            last_count_time = now;
        }
    }

    ModuleType GetModuleType() const override { return ModuleType::DATA_PROCESSING; }
    std::string GetModuleName() const override { return "Data Processing Module"; }
    bool IsHealthy() const override { return processing_active_ && thread_renderer_; }

    SystemMetrics GetMetrics() const override {
        SystemMetrics metrics;
        metrics.cpu_usage = 15.0; // 데이터 처리 CPU 사용률
        metrics.memory_usage_mb = 300.0;
        metrics.data_points_per_second = data_points_per_second_.load();
        return metrics;
    }

    // 데이터 버퍼 접근
    Visualization::TimeSeriesBuffer* GetDataBuffer(const std::string& name) {
        auto it = data_buffers_.find(name);
        return (it != data_buffers_.end()) ? it->second.get() : nullptr;
    }

    Threading::MultiThreadedRenderer* GetThreadRenderer() { return thread_renderer_.get(); }

private:
    void InitializeDataBuffers() {
        // 장비별 파라미터 버퍼 생성
        std::vector<std::string> equipment_types = {"CVD", "PVD", "ETCH", "CMP", "LITHO", "ION_IMPLANT"};
        std::vector<std::string> parameters = {"temperature", "pressure", "flow_rate", "power", "voltage", "current"};

        for (const auto& eq_type : equipment_types) {
            for (int i = 1; i <= 10; ++i) { // 각 타입별 10대씩
                for (const auto& param : parameters) {
                    std::string buffer_name = eq_type + "_" + std::to_string(i) + "_" + param;
                    data_buffers_[buffer_name] = std::make_unique<Visualization::TimeSeriesBuffer>(100000);
                }
            }
        }
    }

    void StartDataProcessors() {
        // 장비별 데이터 시뮬레이터 스레드
        for (int i = 0; i < 6; ++i) {
            data_processors_.emplace_back([this, i]() {
                DataProcessorWorker(i);
            });
        }
    }

    void DataProcessorWorker(int worker_id) {
        std::random_device rd;
        std::mt19937 gen(rd());

        while (processing_active_) {
            double current_time = std::chrono::duration<double>(
                std::chrono::system_clock::now().time_since_epoch()
            ).count();

            // 각 워커가 담당하는 장비들의 데이터 생성
            for (auto& [name, buffer] : data_buffers_) {
                if (std::hash<std::string>{}(name) % 6 == worker_id) {
                    // 현실적인 장비 데이터 시뮬레이션
                    double value = GenerateRealisticData(name, gen);
                    buffer->AddPoint({current_time, value, 100});
                    data_points_processed_++;
                }
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }

    double GenerateRealisticData(const std::string& parameter_name, std::mt19937& gen) {
        // 파라미터별 현실적인 데이터 생성
        if (parameter_name.find("temperature") != std::string::npos) {
            std::normal_distribution<double> dist(250.0, 15.0);
            return std::max(0.0, dist(gen));
        } else if (parameter_name.find("pressure") != std::string::npos) {
            std::normal_distribution<double> dist(0.1, 0.02);
            return std::max(0.0, dist(gen));
        } else if (parameter_name.find("flow_rate") != std::string::npos) {
            std::normal_distribution<double> dist(50.0, 5.0);
            return std::max(0.0, dist(gen));
        } else if (parameter_name.find("power") != std::string::npos) {
            std::normal_distribution<double> dist(1500.0, 100.0);
            return std::max(0.0, dist(gen));
        } else if (parameter_name.find("voltage") != std::string::npos) {
            std::normal_distribution<double> dist(380.0, 10.0);
            return std::max(0.0, dist(gen));
        } else if (parameter_name.find("current") != std::string::npos) {
            std::normal_distribution<double> dist(12.5, 1.0);
            return std::max(0.0, dist(gen));
        }

        return 0.0;
    }
};

// 네트워킹 모듈
class NetworkingModule : public ISystemModule {
private:
    std::unique_ptr<Integration::MQTTClient> mqtt_client_;
    std::vector<std::unique_ptr<Plugin::IDataSourcePlugin>> data_sources_;

    std::atomic<int> active_connections_{0};
    std::atomic<bool> network_healthy_{false};

public:
    bool Initialize() override {
        try {
            // MQTT 클라이언트 초기화
            mqtt_client_ = std::make_unique<Integration::MQTTClient>("HMI_Enterprise");

            // 콜백 설정
            mqtt_client_->SetConnectionCallback([this](bool connected) {
                network_healthy_ = connected;
                if (connected) {
                    active_connections_++;
                } else {
                    active_connections_--;
                }
            });

            // 기본 브로커 연결
            if (mqtt_client_->Connect("localhost", 1883)) {
                mqtt_client_->Subscribe("semiconductor/+/+/+", 1);
                return true;
            }

            return false;
        } catch (const std::exception& e) {
            return false;
        }
    }

    void Shutdown() override {
        if (mqtt_client_) {
            mqtt_client_->Disconnect();
        }
        data_sources_.clear();
        network_healthy_ = false;
        active_connections_ = 0;
    }

    void Update(float deltaTime) override {
        // 네트워크 상태 모니터링
        if (mqtt_client_ && !mqtt_client_->IsConnected()) {
            // 자동 재연결 시도
            mqtt_client_->Connect("localhost", 1883);
        }
    }

    ModuleType GetModuleType() const override { return ModuleType::NETWORKING; }
    std::string GetModuleName() const override { return "Networking Module"; }
    bool IsHealthy() const override { return network_healthy_.load(); }

    SystemMetrics GetMetrics() const override {
        SystemMetrics metrics;
        metrics.cpu_usage = 3.0; // 네트워크 처리 CPU 사용률
        metrics.memory_usage_mb = 50.0;
        metrics.active_connections = active_connections_.load();
        return metrics;
    }

    Integration::MQTTClient* GetMQTTClient() { return mqtt_client_.get(); }
};

} // namespace SemiconductorHMI::Enterprise
```

### 2. 보안 강화 시스템 (20분)
