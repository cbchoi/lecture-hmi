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

#### 2.1 인증 및 권한 관리

```cpp
// SecurityModule.cpp
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <jwt-cpp/jwt.h>

namespace SemiconductorHMI::Security {

enum class UserRole {
    OPERATOR,
    ENGINEER,
    SUPERVISOR,
    ADMINISTRATOR,
    SYSTEM
};

enum class Permission {
    READ_DATA,
    WRITE_DATA,
    MODIFY_SETTINGS,
    MANAGE_USERS,
    SYSTEM_CONTROL,
    SECURITY_AUDIT
};

struct UserSession {
    std::string user_id;
    std::string session_token;
    UserRole role;
    std::vector<Permission> permissions;
    std::chrono::system_clock::time_point login_time;
    std::chrono::system_clock::time_point last_activity;
    std::string client_ip;
    bool is_active = true;
};

class SecurityModule : public Enterprise::ISystemModule {
private:
    std::unordered_map<std::string, UserSession> active_sessions_;
    std::unordered_map<std::string, std::string> user_credentials_; // 실제로는 암호화된 DB
    mutable std::shared_mutex sessions_mutex_;

    // 보안 정책
    struct SecurityPolicy {
        int max_failed_attempts = 3;
        int session_timeout_minutes = 30;
        int password_min_length = 12;
        bool require_mfa = true;
        bool enable_audit_logging = true;
        int audit_retention_days = 90;
    } policy_;

    // 감사 로그
    struct AuditEntry {
        std::string timestamp;
        std::string user_id;
        std::string action;
        std::string resource;
        std::string client_ip;
        bool success;
        std::string details;
    };
    std::vector<AuditEntry> audit_log_;
    mutable std::mutex audit_mutex_;

public:
    bool Initialize() override {
        try {
            // OpenSSL 초기화
            if (!InitializeSSL()) {
                return false;
            }

            // 기본 관리자 계정 생성 (첫 실행시)
            CreateDefaultAdminAccount();

            // 보안 정책 로드
            LoadSecurityPolicy();

            return true;
        } catch (const std::exception& e) {
            return false;
        }
    }

    void Shutdown() override {
        // 모든 세션 종료
        std::unique_lock<std::shared_mutex> lock(sessions_mutex_);
        for (auto& [token, session] : active_sessions_) {
            session.is_active = false;
            LogAuditEvent(session.user_id, "LOGOUT", "SYSTEM", session.client_ip, true, "System shutdown");
        }
        active_sessions_.clear();

        // 감사 로그 저장
        SaveAuditLog();
    }

    void Update(float deltaTime) override {
        // 세션 타임아웃 체크
        CheckSessionTimeouts();

        // 주기적 보안 검사
        PerformSecurityChecks();
    }

    ModuleType GetModuleType() const override { return Enterprise::ModuleType::SECURITY; }
    std::string GetModuleName() const override { return "Security Module"; }
    bool IsHealthy() const override { return true; }

    Enterprise::SystemMetrics GetMetrics() const override {
        Enterprise::SystemMetrics metrics;
        metrics.cpu_usage = 2.0;
        metrics.memory_usage_mb = 30.0;

        std::shared_lock<std::shared_mutex> lock(sessions_mutex_);
        metrics.active_connections = active_sessions_.size();
        return metrics;
    }

    // 인증 관리
    std::string AuthenticateUser(const std::string& username, const std::string& password, const std::string& client_ip) {
        // 패스워드 검증
        if (!VerifyPassword(username, password)) {
            LogAuditEvent(username, "LOGIN_FAILED", "AUTHENTICATION", client_ip, false, "Invalid credentials");
            return "";
        }

        // 세션 생성
        std::string session_token = GenerateSessionToken();
        UserSession session;
        session.user_id = username;
        session.session_token = session_token;
        session.role = GetUserRole(username);
        session.permissions = GetUserPermissions(session.role);
        session.login_time = std::chrono::system_clock::now();
        session.last_activity = session.login_time;
        session.client_ip = client_ip;
        session.is_active = true;

        {
            std::unique_lock<std::shared_mutex> lock(sessions_mutex_);
            active_sessions_[session_token] = session;
        }

        LogAuditEvent(username, "LOGIN_SUCCESS", "AUTHENTICATION", client_ip, true, "User authenticated");
        return session_token;
    }

    bool ValidateSession(const std::string& session_token) {
        std::shared_lock<std::shared_mutex> lock(sessions_mutex_);
        auto it = active_sessions_.find(session_token);

        if (it == active_sessions_.end() || !it->second.is_active) {
            return false;
        }

        // 세션 타임아웃 체크
        auto now = std::chrono::system_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::minutes>(now - it->second.last_activity);

        if (elapsed.count() > policy_.session_timeout_minutes) {
            return false;
        }

        // 마지막 활동 시간 업데이트
        const_cast<UserSession&>(it->second).last_activity = now;
        return true;
    }

    bool CheckPermission(const std::string& session_token, Permission required_permission) {
        std::shared_lock<std::shared_mutex> lock(sessions_mutex_);
        auto it = active_sessions_.find(session_token);

        if (it == active_sessions_.end() || !it->second.is_active) {
            return false;
        }

        const auto& permissions = it->second.permissions;
        return std::find(permissions.begin(), permissions.end(), required_permission) != permissions.end();
    }

    void LogoutUser(const std::string& session_token) {
        std::unique_lock<std::shared_mutex> lock(sessions_mutex_);
        auto it = active_sessions_.find(session_token);

        if (it != active_sessions_.end()) {
            LogAuditEvent(it->second.user_id, "LOGOUT", "AUTHENTICATION", it->second.client_ip, true, "User logout");
            active_sessions_.erase(it);
        }
    }

    // 감사 로깅
    void LogAuditEvent(const std::string& user_id, const std::string& action,
                      const std::string& resource, const std::string& client_ip,
                      bool success, const std::string& details = "") {
        if (!policy_.enable_audit_logging) return;

        AuditEntry entry;
        entry.timestamp = GetCurrentTimestamp();
        entry.user_id = user_id;
        entry.action = action;
        entry.resource = resource;
        entry.client_ip = client_ip;
        entry.success = success;
        entry.details = details;

        {
            std::lock_guard<std::mutex> lock(audit_mutex_);
            audit_log_.push_back(entry);
        }

        // 실시간 보안 이벤트 알림
        if (!success || action.find("SECURITY") != std::string::npos) {
            SendSecurityAlert(entry);
        }
    }

private:
    bool InitializeSSL() {
        // OpenSSL 라이브러리 초기화
        EVP_add_cipher(EVP_aes_256_gcm());
        EVP_add_digest(EVP_sha256());
        return true;
    }

    bool VerifyPassword(const std::string& username, const std::string& password) {
        auto it = user_credentials_.find(username);
        if (it == user_credentials_.end()) {
            return false;
        }

        // 실제로는 bcrypt나 Argon2 사용
        std::string hashed_password = HashPassword(password);
        return hashed_password == it->second;
    }

    std::string HashPassword(const std::string& password) {
        // SHA-256 해싱 (실제로는 더 강력한 알고리즘 사용)
        unsigned char hash[SHA256_DIGEST_LENGTH];
        SHA256_CTX sha256;
        SHA256_Init(&sha256);
        SHA256_Update(&sha256, password.c_str(), password.length());
        SHA256_Final(hash, &sha256);

        std::stringstream ss;
        for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
            ss << std::hex << std::setw(2) << std::setfill('0') << (int)hash[i];
        }
        return ss.str();
    }

    std::string GenerateSessionToken() {
        // 암호학적으로 안전한 랜덤 토큰 생성
        unsigned char buffer[32];
        if (RAND_bytes(buffer, sizeof(buffer)) != 1) {
            throw std::runtime_error("Failed to generate random token");
        }

        std::stringstream ss;
        for (int i = 0; i < sizeof(buffer); i++) {
            ss << std::hex << std::setw(2) << std::setfill('0') << (int)buffer[i];
        }
        return ss.str();
    }

    UserRole GetUserRole(const std::string& username) {
        // 실제로는 데이터베이스에서 조회
        if (username == "admin") return UserRole::ADMINISTRATOR;
        if (username.find("supervisor") != std::string::npos) return UserRole::SUPERVISOR;
        if (username.find("engineer") != std::string::npos) return UserRole::ENGINEER;
        return UserRole::OPERATOR;
    }

    std::vector<Permission> GetUserPermissions(UserRole role) {
        switch (role) {
            case UserRole::ADMINISTRATOR:
                return {Permission::READ_DATA, Permission::WRITE_DATA, Permission::MODIFY_SETTINGS,
                       Permission::MANAGE_USERS, Permission::SYSTEM_CONTROL, Permission::SECURITY_AUDIT};
            case UserRole::SUPERVISOR:
                return {Permission::READ_DATA, Permission::WRITE_DATA, Permission::MODIFY_SETTINGS,
                       Permission::SYSTEM_CONTROL};
            case UserRole::ENGINEER:
                return {Permission::READ_DATA, Permission::WRITE_DATA, Permission::MODIFY_SETTINGS};
            case UserRole::OPERATOR:
                return {Permission::READ_DATA};
            case UserRole::SYSTEM:
                return {Permission::READ_DATA, Permission::WRITE_DATA, Permission::SYSTEM_CONTROL};
        }
        return {};
    }

    void CheckSessionTimeouts() {
        std::unique_lock<std::shared_mutex> lock(sessions_mutex_);
        auto now = std::chrono::system_clock::now();

        for (auto it = active_sessions_.begin(); it != active_sessions_.end();) {
            auto elapsed = std::chrono::duration_cast<std::chrono::minutes>(now - it->second.last_activity);

            if (elapsed.count() > policy_.session_timeout_minutes) {
                LogAuditEvent(it->second.user_id, "SESSION_TIMEOUT", "AUTHENTICATION",
                            it->second.client_ip, true, "Session expired");
                it = active_sessions_.erase(it);
            } else {
                ++it;
            }
        }
    }

    void PerformSecurityChecks() {
        // 비정상적인 활동 패턴 감지
        // 무차별 대입 공격 감지
        // 권한 상승 시도 감지
        // 시스템 무결성 검사
    }

    void CreateDefaultAdminAccount() {
        if (user_credentials_.empty()) {
            // 기본 관리자 계정 (첫 실행시만)
            user_credentials_["admin"] = HashPassword("TempAdmin123!");

            LogAuditEvent("SYSTEM", "CREATE_ADMIN", "USER_MANAGEMENT", "localhost", true,
                         "Default admin account created");
        }
    }

    void LoadSecurityPolicy() {
        // 설정 파일에서 보안 정책 로드
    }

    void SaveAuditLog() {
        // 감사 로그를 안전한 저장소에 저장
    }

    std::string GetCurrentTimestamp() {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);

        std::stringstream ss;
        ss << std::put_time(std::gmtime(&time_t), "%Y-%m-%dT%H:%M:%SZ");
        return ss.str();
    }

    void SendSecurityAlert(const AuditEntry& entry) {
        // 보안 담당자에게 실시간 알림 전송
        // SIEM 시스템으로 이벤트 전송
    }
};

} // namespace SemiconductorHMI::Security
```

### 3. 성능 최적화 및 모니터링 (20분)

#### 3.1 고급 성능 모니터링 시스템

```cpp
// PerformanceMonitoring.cpp
#include <chrono>
#include <thread>
#include <atomic>
#include <fstream>

namespace SemiconductorHMI::Monitoring {

struct PerformanceCounter {
    std::atomic<uint64_t> total_count{0};
    std::atomic<uint64_t> error_count{0};
    std::atomic<double> average_duration{0.0};
    std::atomic<double> min_duration{std::numeric_limits<double>::max()};
    std::atomic<double> max_duration{0.0};

    void Record(double duration, bool success = true) {
        total_count++;
        if (!success) error_count++;

        // 평균 계산 (단순화된 버전)
        double current_avg = average_duration.load();
        double new_avg = (current_avg * (total_count - 1) + duration) / total_count;
        average_duration.store(new_avg);

        // 최소/최대 업데이트
        double current_min = min_duration.load();
        while (duration < current_min && !min_duration.compare_exchange_weak(current_min, duration)) {}

        double current_max = max_duration.load();
        while (duration > current_max && !max_duration.compare_exchange_weak(current_max, duration)) {}
    }
};

class MonitoringModule : public Enterprise::ISystemModule {
private:
    std::unordered_map<std::string, PerformanceCounter> performance_counters_;
    std::mutex counters_mutex_;

    // 시스템 리소스 모니터링
    std::thread resource_monitor_thread_;
    std::atomic<bool> monitoring_active_{false};

    struct SystemResources {
        std::atomic<double> cpu_usage{0.0};
        std::atomic<double> memory_usage_mb{0.0};
        std::atomic<double> gpu_usage{0.0};
        std::atomic<double> gpu_memory_mb{0.0};
        std::atomic<double> disk_usage_percent{0.0};
        std::atomic<double> network_bandwidth_mbps{0.0};
    } system_resources_;

    // 알람 시스템
    struct AlertThreshold {
        double cpu_limit = 80.0;
        double memory_limit_mb = 8192.0;
        double gpu_limit = 90.0;
        double error_rate_limit = 0.05; // 5%
        double response_time_limit_ms = 1000.0;
    } alert_thresholds_;

    std::vector<std::string> active_alerts_;
    std::mutex alerts_mutex_;

public:
    bool Initialize() override {
        try {
            monitoring_active_ = true;

            // 리소스 모니터링 스레드 시작
            resource_monitor_thread_ = std::thread([this]() {
                ResourceMonitorLoop();
            });

            return true;
        } catch (const std::exception& e) {
            return false;
        }
    }

    void Shutdown() override {
        monitoring_active_ = false;

        if (resource_monitor_thread_.joinable()) {
            resource_monitor_thread_.join();
        }

        // 성능 데이터 저장
        SavePerformanceData();
    }

    void Update(float deltaTime) override {
        // 알람 조건 체크
        CheckAlarmConditions();

        // 성능 데이터 분석
        AnalyzePerformanceData();
    }

    ModuleType GetModuleType() const override { return Enterprise::ModuleType::MONITORING; }
    std::string GetModuleName() const override { return "Monitoring Module"; }
    bool IsHealthy() const override { return monitoring_active_.load(); }

    Enterprise::SystemMetrics GetMetrics() const override {
        Enterprise::SystemMetrics metrics;
        metrics.cpu_usage = system_resources_.cpu_usage.load();
        metrics.memory_usage_mb = system_resources_.memory_usage_mb.load();
        metrics.gpu_usage = system_resources_.gpu_usage.load();
        metrics.gpu_memory_mb = system_resources_.gpu_memory_mb.load();
        return metrics;
    }

    // 성능 측정 도구
    class PerformanceTimer {
    private:
        std::string operation_name_;
        std::chrono::high_resolution_clock::time_point start_time_;
        MonitoringModule* monitor_;

    public:
        PerformanceTimer(const std::string& operation_name, MonitoringModule* monitor)
            : operation_name_(operation_name), monitor_(monitor) {
            start_time_ = std::chrono::high_resolution_clock::now();
        }

        ~PerformanceTimer() {
            auto end_time = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration<double, std::milli>(end_time - start_time_).count();
            monitor_->RecordPerformance(operation_name_, duration);
        }
    };

    void RecordPerformance(const std::string& operation, double duration_ms, bool success = true) {
        std::lock_guard<std::mutex> lock(counters_mutex_);
        performance_counters_[operation].Record(duration_ms, success);
    }

    PerformanceCounter GetPerformanceStats(const std::string& operation) {
        std::lock_guard<std::mutex> lock(counters_mutex_);
        return performance_counters_[operation];
    }

    // 시스템 리소스 정보
    double GetCPUUsage() const { return system_resources_.cpu_usage.load(); }
    double GetMemoryUsage() const { return system_resources_.memory_usage_mb.load(); }
    double GetGPUUsage() const { return system_resources_.gpu_usage.load(); }
    double GetGPUMemoryUsage() const { return system_resources_.gpu_memory_mb.load(); }

    // 알람 관리
    std::vector<std::string> GetActiveAlerts() {
        std::lock_guard<std::mutex> lock(alerts_mutex_);
        return active_alerts_;
    }

    void SetAlertThresholds(const AlertThreshold& thresholds) {
        alert_thresholds_ = thresholds;
    }

private:
    void ResourceMonitorLoop() {
        while (monitoring_active_) {
            // CPU 사용률 측정
            system_resources_.cpu_usage.store(GetSystemCPUUsage());

            // 메모리 사용률 측정
            system_resources_.memory_usage_mb.store(GetSystemMemoryUsage());

            // GPU 사용률 측정 (NVIDIA GPU 기준)
            system_resources_.gpu_usage.store(GetSystemGPUUsage());
            system_resources_.gpu_memory_mb.store(GetSystemGPUMemoryUsage());

            // 디스크 및 네트워크 사용률
            system_resources_.disk_usage_percent.store(GetSystemDiskUsage());
            system_resources_.network_bandwidth_mbps.store(GetNetworkBandwidth());

            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }

    double GetSystemCPUUsage() {
        // Windows의 경우 Performance Counters 사용
        // Linux의 경우 /proc/stat 파싱
        // macOS의 경우 host_processor_info 사용

        // 간단한 시뮬레이션
        static double base_usage = 20.0;
        static std::random_device rd;
        static std::mt19937 gen(rd());
        static std::normal_distribution<double> dist(0.0, 5.0);

        return std::clamp(base_usage + dist(gen), 0.0, 100.0);
    }

    double GetSystemMemoryUsage() {
        // 실제 시스템 메모리 사용량 조회
        // Windows: GlobalMemoryStatusEx
        // Linux: /proc/meminfo
        // macOS: vm_statistics64

        // 시뮬레이션
        return 2048.0 + (std::rand() % 1024);
    }

    double GetSystemGPUUsage() {
        // NVIDIA ML API 또는 CUDA 사용
        // AMD의 경우 AMD GPU Services API

        // 시뮬레이션
        return 30.0 + (std::rand() % 40);
    }

    double GetSystemGPUMemoryUsage() {
        // GPU 메모리 사용량 조회
        return 1024.0 + (std::rand() % 2048);
    }

    double GetSystemDiskUsage() {
        // 디스크 사용률 조회
        return 45.0 + (std::rand() % 20);
    }

    double GetNetworkBandwidth() {
        // 네트워크 대역폭 사용량 조회
        return 10.0 + (std::rand() % 50);
    }

    void CheckAlarmConditions() {
        std::vector<std::string> new_alerts;

        // CPU 사용률 체크
        if (system_resources_.cpu_usage.load() > alert_thresholds_.cpu_limit) {
            new_alerts.push_back("High CPU usage: " + std::to_string(system_resources_.cpu_usage.load()) + "%");
        }

        // 메모리 사용량 체크
        if (system_resources_.memory_usage_mb.load() > alert_thresholds_.memory_limit_mb) {
            new_alerts.push_back("High memory usage: " + std::to_string(system_resources_.memory_usage_mb.load()) + " MB");
        }

        // GPU 사용률 체크
        if (system_resources_.gpu_usage.load() > alert_thresholds_.gpu_limit) {
            new_alerts.push_back("High GPU usage: " + std::to_string(system_resources_.gpu_usage.load()) + "%");
        }

        // 에러율 체크
        {
            std::lock_guard<std::mutex> lock(counters_mutex_);
            for (const auto& [operation, counter] : performance_counters_) {
                if (counter.total_count.load() > 100) { // 충분한 샘플이 있을 때만
                    double error_rate = static_cast<double>(counter.error_count.load()) / counter.total_count.load();
                    if (error_rate > alert_thresholds_.error_rate_limit) {
                        new_alerts.push_back("High error rate in " + operation + ": " +
                                           std::to_string(error_rate * 100) + "%");
                    }
                }
            }
        }

        // 알람 업데이트
        {
            std::lock_guard<std::mutex> lock(alerts_mutex_);
            active_alerts_ = new_alerts;
        }

        // 새로운 알람이 있으면 알림
        if (!new_alerts.empty()) {
            SendAlerts(new_alerts);
        }
    }

    void AnalyzePerformanceData() {
        // 성능 트렌드 분석
        // 병목 지점 식별
        // 최적화 권장사항 생성
    }

    void SavePerformanceData() {
        // 성능 데이터를 파일이나 데이터베이스에 저장
        std::ofstream file("performance_data.json");
        if (file.is_open()) {
            file << "{\n";
            file << "  \"timestamp\": \"" << GetCurrentTimestamp() << "\",\n";
            file << "  \"system_resources\": {\n";
            file << "    \"cpu_usage\": " << system_resources_.cpu_usage.load() << ",\n";
            file << "    \"memory_usage_mb\": " << system_resources_.memory_usage_mb.load() << ",\n";
            file << "    \"gpu_usage\": " << system_resources_.gpu_usage.load() << ",\n";
            file << "    \"gpu_memory_mb\": " << system_resources_.gpu_memory_mb.load() << "\n";
            file << "  },\n";
            file << "  \"performance_counters\": {\n";

            std::lock_guard<std::mutex> lock(counters_mutex_);
            bool first = true;
            for (const auto& [operation, counter] : performance_counters_) {
                if (!first) file << ",\n";
                first = false;

                file << "    \"" << operation << "\": {\n";
                file << "      \"total_count\": " << counter.total_count.load() << ",\n";
                file << "      \"error_count\": " << counter.error_count.load() << ",\n";
                file << "      \"average_duration\": " << counter.average_duration.load() << ",\n";
                file << "      \"min_duration\": " << counter.min_duration.load() << ",\n";
                file << "      \"max_duration\": " << counter.max_duration.load() << "\n";
                file << "    }";
            }
            file << "\n  }\n";
            file << "}\n";
            file.close();
        }
    }

    void SendAlerts(const std::vector<std::string>& alerts) {
        // 실시간 알림 발송
        // 이메일, SMS, 웹훅 등을 통한 알림
        for (const auto& alert : alerts) {
            printf("ALERT: %s\n", alert.c_str());
        }
    }

    std::string GetCurrentTimestamp() {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);

        std::stringstream ss;
        ss << std::put_time(std::gmtime(&time_t), "%Y-%m-%dT%H:%M:%SZ");
        return ss.str();
    }
};

// 성능 측정 매크로
#define PERF_TIMER(monitor, operation) \
    SemiconductorHMI::Monitoring::MonitoringModule::PerformanceTimer timer(operation, monitor)

} // namespace SemiconductorHMI::Monitoring

---

## 🚀 배포 시스템 (45분): 컨테이너화 및 CI/CD 파이프라인

### 1. Docker 컨테이너화 (15분)

#### 1.1 멀티 스테이지 Dockerfile

```dockerfile
# Dockerfile.production
# 멀티 스테이지 빌드를 통한 최적화된 프로덕션 이미지

# ===== 빌드 스테이지 =====
FROM ubuntu:22.04 AS builder

# 빌드 의존성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    pkg-config \
    libssl-dev \
    libcurl4-openssl-dev \
    libjsoncpp-dev \
    libmosquitto-dev \
    libicu-dev \
    libboost-all-dev \
    libopengl-dev \
    libglfw3-dev \
    libglew-dev \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /build

# ImGui 및 의존성 라이브러리 빌드
COPY third_party/ ./third_party/
RUN cd third_party && \
    # ImGui 빌드
    mkdir -p imgui/build && cd imgui/build && \
    cmake .. -GNinja -DCMAKE_BUILD_TYPE=Release && \
    ninja && \
    ninja install && \
    cd ../.. && \
    # GLM 설치
    cd glm && \
    cmake . -GNinja -DCMAKE_BUILD_TYPE=Release && \
    ninja install && \
    cd .. && \
    # Assimp 빌드
    cd assimp && \
    cmake . -GNinja -DCMAKE_BUILD_TYPE=Release -DASSIMP_BUILD_TESTS=OFF && \
    ninja && \
    ninja install

# 소스 코드 복사
COPY src/ ./src/
COPY CMakeLists.txt ./
COPY cmake/ ./cmake/

# 애플리케이션 빌드
RUN cmake . -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_STANDARD=20 \
    -DENABLE_OPTIMIZATION=ON \
    -DENABLE_SECURITY_HARDENING=ON \
    && ninja

# ===== 런타임 스테이지 =====
FROM ubuntu:22.04 AS runtime

# 런타임 의존성만 설치
RUN apt-get update && apt-get install -y \
    libssl3 \
    libcurl4 \
    libjsoncpp25 \
    libmosquitto1 \
    libicu70 \
    libboost-system1.74.0 \
    libboost-filesystem1.74.0 \
    libboost-thread1.74.0 \
    libopengl0 \
    libglfw3 \
    libglew2.2 \
    ca-certificates \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 비특권 사용자 생성
RUN groupadd -r hmiuser && useradd -r -g hmiuser hmiuser

# 애플리케이션 디렉토리 생성
RUN mkdir -p /app/{bin,config,logs,data,plugins,certs} && \
    chown -R hmiuser:hmiuser /app

# 빌드된 애플리케이션 복사
COPY --from=builder /build/SemiconductorHMI /app/bin/
COPY --from=builder /build/plugins/*.so /app/plugins/
COPY config/ /app/config/
COPY certs/ /app/certs/

# 실행 권한 설정
RUN chmod +x /app/bin/SemiconductorHMI && \
    chown -R hmiuser:hmiuser /app

# 헬스체크 스크립트
COPY scripts/healthcheck.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/healthcheck.sh

# 사용자 전환
USER hmiuser
WORKDIR /app

# 포트 노출
EXPOSE 8080 8443 1883

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# 환경 변수 설정
ENV HMI_CONFIG_PATH=/app/config \
    HMI_LOG_LEVEL=INFO \
    HMI_ENABLE_METRICS=true

# 엔트리포인트
ENTRYPOINT ["/app/bin/SemiconductorHMI"]
CMD ["--config", "/app/config/production.json"]
```

#### 1.2 Docker Compose 설정

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 메인 HMI 애플리케이션
  hmi-app:
    build:
      context: .
      dockerfile: Dockerfile.production
      target: runtime
    container_name: semiconductor-hmi
    restart: unless-stopped
    ports:
      - "8080:8080"   # HTTP
      - "8443:8443"   # HTTPS
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config:ro
      - ./certs:/app/certs:ro
    environment:
      - HMI_DB_HOST=postgres
      - HMI_MQTT_BROKER=mqtt-broker:1883
      - HMI_REDIS_HOST=redis:6379
      - HMI_LOG_LEVEL=INFO
    depends_on:
      - postgres
      - redis
      - mqtt-broker
    networks:
      - hmi-network
    healthcheck:
      test: ["CMD", "/usr/local/bin/healthcheck.sh"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # PostgreSQL 데이터베이스
  postgres:
    image: postgres:15-alpine
    container_name: hmi-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: hmi_database
      POSTGRES_USER: hmi_user
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d:ro
    ports:
      - "5432:5432"
    secrets:
      - postgres_password
    networks:
      - hmi-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hmi_user -d hmi_database"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Redis 캐시
  redis:
    image: redis:7-alpine
    container_name: hmi-redis
    restart: unless-stopped
    command: redis-server /usr/local/etc/redis/redis.conf
    volumes:
      - redis_data:/data
      - ./redis/redis.conf:/usr/local/etc/redis/redis.conf:ro
    ports:
      - "6379:6379"
    networks:
      - hmi-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # MQTT 브로커
  mqtt-broker:
    image: eclipse-mosquitto:2.0
    container_name: hmi-mqtt
    restart: unless-stopped
    volumes:
      - ./mqtt/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro
      - ./mqtt/passwd:/mosquitto/config/passwd:ro
      - mqtt_data:/mosquitto/data
      - mqtt_logs:/mosquitto/log
    ports:
      - "1883:1883"
      - "8883:8883"
    networks:
      - hmi-network

  # Prometheus 모니터링
  prometheus:
    image: prom/prometheus:latest
    container_name: hmi-prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - hmi-network

  # Grafana 대시보드
  grafana:
    image: grafana/grafana:latest
    container_name: hmi-grafana
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD_FILE=/run/secrets/grafana_password
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    ports:
      - "3000:3000"
    secrets:
      - grafana_password
    networks:
      - hmi-network
    depends_on:
      - prometheus

  # Nginx 리버스 프록시
  nginx:
    image: nginx:alpine
    container_name: hmi-nginx
    restart: unless-stopped
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    networks:
      - hmi-network
    depends_on:
      - hmi-app

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  mqtt_data:
    driver: local
  mqtt_logs:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local

networks:
  hmi-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

secrets:
  postgres_password:
    file: ./secrets/postgres_password.txt
  grafana_password:
    file: ./secrets/grafana_password.txt
```

### 2. Kubernetes 배포 (15분)

#### 2.1 Kubernetes 매니페스트

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: semiconductor-hmi
  labels:
    name: semiconductor-hmi
    environment: production

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: hmi-config
  namespace: semiconductor-hmi
data:
  production.json: |
    {
      "system": {
        "name": "SemiconductorHMI_Enterprise",
        "version": "1.0.0",
        "environment": "production"
      },
      "database": {
        "host": "postgres-service",
        "port": 5432,
        "name": "hmi_database",
        "username": "hmi_user"
      },
      "mqtt": {
        "broker": "mqtt-service:1883",
        "client_id": "hmi_k8s_cluster"
      },
      "redis": {
        "host": "redis-service",
        "port": 6379
      },
      "security": {
        "enable_encryption": true,
        "session_timeout_minutes": 30,
        "max_failed_attempts": 3
      },
      "monitoring": {
        "enable_metrics": true,
        "metrics_port": 8080,
        "health_check_interval_ms": 5000
      }
    }

---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: hmi-secrets
  namespace: semiconductor-hmi
type: Opaque
data:
  # Base64 인코딩된 값들
  postgres-password: aG1pX3Bhc3N3b3JkXzEyMw==
  jwt-secret: c3VwZXJfc2VjcmV0X2p3dF9rZXk=
  encryption-key: YWVzXzI1Nl9lbmNyeXB0aW9uX2tleQ==

---
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hmi-app
  namespace: semiconductor-hmi
  labels:
    app: hmi-app
    version: v1.0.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: hmi-app
  template:
    metadata:
      labels:
        app: hmi-app
        version: v1.0.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: hmi-service-account
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
      - name: hmi-app
        image: semiconductor-hmi:1.0.0
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
          name: http
          protocol: TCP
        - containerPort: 8443
          name: https
          protocol: TCP
        env:
        - name: HMI_CONFIG_PATH
          value: "/app/config"
        - name: HMI_LOG_LEVEL
          value: "INFO"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: hmi-secrets
              key: postgres-password
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: hmi-secrets
              key: jwt-secret
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /startup
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 30
      volumes:
      - name: config
        configMap:
          name: hmi-config
      - name: data
        persistentVolumeClaim:
          claimName: hmi-data-pvc
      - name: logs
        emptyDir: {}
      nodeSelector:
        node-type: application
      tolerations:
      - key: "application"
        operator: "Equal"
        value: "hmi"
        effect: "NoSchedule"

---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: hmi-service
  namespace: semiconductor-hmi
  labels:
    app: hmi-app
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
    name: http
  - port: 443
    targetPort: 8443
    protocol: TCP
    name: https
  selector:
    app: hmi-app

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hmi-ingress
  namespace: semiconductor-hmi
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTP"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - hmi.semiconductor.company.com
    secretName: hmi-tls-secret
  rules:
  - host: hmi.semiconductor.company.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: hmi-service
            port:
              number: 80

---
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: hmi-hpa
  namespace: semiconductor-hmi
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hmi-app
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

### 3. CI/CD 파이프라인 (15분)

#### 3.1 Jenkins 파이프라인

```groovy
// Jenkinsfile
pipeline {
    agent {
        kubernetes {
            yaml '''
                apiVersion: v1
                kind: Pod
                spec:
                  containers:
                  - name: docker
                    image: docker:20.10-dind
                    securityContext:
                      privileged: true
                    volumeMounts:
                    - name: docker-sock
                      mountPath: /var/run/docker.sock
                  - name: kubectl
                    image: bitnami/kubectl:latest
                    command:
                    - cat
                    tty: true
                  - name: helm
                    image: alpine/helm:latest
                    command:
                    - cat
                    tty: true
                  volumes:
                  - name: docker-sock
                    hostPath:
                      path: /var/run/docker.sock
            '''
        }
    }

    environment {
        DOCKER_REGISTRY = 'your-registry.com'
        IMAGE_NAME = 'semiconductor-hmi'
        KUBECONFIG = credentials('k8s-config')
        DOCKER_CREDENTIALS = credentials('docker-registry-creds')
        SONAR_TOKEN = credentials('sonar-token')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                    env.BUILD_VERSION = "${env.BUILD_NUMBER}-${env.GIT_COMMIT_SHORT}"
                }
            }
        }

        stage('Code Quality Analysis') {
            parallel {
                stage('Static Analysis') {
                    steps {
                        container('docker') {
                            sh '''
                                # SonarQube 분석
                                docker run --rm \
                                    -v ${WORKSPACE}:/usr/src \
                                    -e SONAR_HOST_URL=${SONAR_HOST_URL} \
                                    -e SONAR_LOGIN=${SONAR_TOKEN} \
                                    sonarsource/sonar-scanner-cli \
                                    -Dsonar.projectKey=semiconductor-hmi \
                                    -Dsonar.sources=src \
                                    -Dsonar.cfamily.build-wrapper-output=bw-output
                            '''
                        }
                    }
                }

                stage('Security Scan') {
                    steps {
                        container('docker') {
                            sh '''
                                # Trivy 보안 스캔
                                docker run --rm \
                                    -v ${WORKSPACE}:/workspace \
                                    aquasec/trivy fs \
                                    --security-checks vuln,secret,config \
                                    --format sarif \
                                    --output /workspace/trivy-report.sarif \
                                    /workspace
                            '''
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'trivy-report.sarif', fingerprint: true
                        }
                    }
                }
            }
        }

        stage('Build and Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        container('docker') {
                            sh '''
                                # 테스트용 Docker 이미지 빌드
                                docker build -f Dockerfile.test -t ${IMAGE_NAME}:test .

                                # 단위 테스트 실행
                                docker run --rm \
                                    -v ${WORKSPACE}/test-results:/app/test-results \
                                    ${IMAGE_NAME}:test \
                                    ctest --output-on-failure --output-junit test-results/junit.xml
                            '''
                        }
                    }
                    post {
                        always {
                            junit 'test-results/junit.xml'
                        }
                    }
                }

                stage('Integration Tests') {
                    steps {
                        container('docker') {
                            sh '''
                                # Docker Compose로 통합 테스트 환경 구성
                                docker-compose -f docker-compose.test.yml up -d

                                # 통합 테스트 실행
                                docker-compose -f docker-compose.test.yml exec -T hmi-app \
                                    ./run_integration_tests.sh
                            '''
                        }
                    }
                    post {
                        always {
                            sh 'docker-compose -f docker-compose.test.yml down -v'
                        }
                    }
                }
            }
        }

        stage('Build Production Image') {
            when {
                anyOf {
                    branch 'main'
                    branch 'release/*'
                }
            }
            steps {
                container('docker') {
                    sh '''
                        echo ${DOCKER_CREDENTIALS_PSW} | docker login -u ${DOCKER_CREDENTIALS_USR} --password-stdin ${DOCKER_REGISTRY}

                        # 프로덕션 이미지 빌드
                        docker build \
                            -f Dockerfile.production \
                            -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_VERSION} \
                            -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest \
                            .

                        # 이미지 보안 스캔
                        docker run --rm \
                            -v /var/run/docker.sock:/var/run/docker.sock \
                            aquasec/trivy image \
                            --exit-code 1 \
                            --severity HIGH,CRITICAL \
                            ${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_VERSION}

                        # 이미지 푸시
                        docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${BUILD_VERSION}
                        docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:latest
                    '''
                }
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'main'
            }
            steps {
                container('helm') {
                    sh '''
                        # Helm 차트로 스테이징 환경 배포
                        helm upgrade --install hmi-staging ./helm/semiconductor-hmi \
                            --namespace staging \
                            --create-namespace \
                            --set image.tag=${BUILD_VERSION} \
                            --set environment=staging \
                            --set replicaCount=1 \
                            --values helm/values-staging.yaml \
                            --wait --timeout=300s
                    '''
                }
            }
        }

        stage('Performance Tests') {
            when {
                branch 'main'
            }
            steps {
                container('docker') {
                    sh '''
                        # K6 성능 테스트 실행
                        docker run --rm \
                            -v ${WORKSPACE}/performance-tests:/tests \
                            -v ${WORKSPACE}/performance-results:/results \
                            loadimpact/k6 run \
                            --out junit=/results/performance-junit.xml \
                            --out json=/results/performance-results.json \
                            /tests/load-test.js
                    '''
                }
            }
            post {
                always {
                    junit 'performance-results/performance-junit.xml'
                    archiveArtifacts artifacts: 'performance-results/*', fingerprint: true
                }
            }
        }

        stage('Deploy to Production') {
            when {
                anyOf {
                    branch 'release/*'
                    tag 'v*'
                }
            }
            steps {
                script {
                    def deploy = input(
                        message: 'Deploy to production?',
                        parameters: [
                            choice(
                                name: 'DEPLOYMENT_STRATEGY',
                                choices: ['rolling', 'blue-green', 'canary'],
                                description: 'Deployment strategy'
                            )
                        ]
                    )

                    container('helm') {
                        sh """
                            helm upgrade --install hmi-production ./helm/semiconductor-hmi \
                                --namespace production \
                                --create-namespace \
                                --set image.tag=${BUILD_VERSION} \
                                --set environment=production \
                                --set deployment.strategy=${deploy} \
                                --values helm/values-production.yaml \
                                --wait --timeout=600s
                        """
                    }
                }
            }
        }

        stage('Smoke Tests') {
            when {
                anyOf {
                    branch 'main'
                    branch 'release/*'
                    tag 'v*'
                }
            }
            steps {
                container('docker') {
                    sh '''
                        # 배포 후 스모크 테스트
                        docker run --rm \
                            -v ${WORKSPACE}/smoke-tests:/tests \
                            postman/newman \
                            run /tests/smoke-tests.postman_collection.json \
                            --environment /tests/production.postman_environment.json \
                            --reporters junit \
                            --reporter-junit-export /tests/smoke-test-results.xml
                    '''
                }
            }
            post {
                always {
                    junit 'smoke-tests/smoke-test-results.xml'
                }
            }
        }
    }

    post {
        always {
            // 빌드 결과 알림
            script {
                def status = currentBuild.result ?: 'SUCCESS'
                def color = status == 'SUCCESS' ? 'good' : 'danger'

                slackSend(
                    channel: '#hmi-deployments',
                    color: color,
                    message: """
                        Build ${status}: ${env.JOB_NAME} - ${env.BUILD_NUMBER}
                        Branch: ${env.BRANCH_NAME}
                        Commit: ${env.GIT_COMMIT_SHORT}
                        Duration: ${currentBuild.durationString}
                        Build URL: ${env.BUILD_URL}
                    """
                )
            }
        }

        failure {
            // 실패시 추가 알림
            emailext(
                to: '${DEFAULT_RECIPIENTS}',
                subject: 'Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}',
                body: '''
                    Build failed for ${env.JOB_NAME} - ${env.BUILD_NUMBER}

                    Check the build logs: ${env.BUILD_URL}

                    Recent commits:
                    ${env.CHANGE_LOG}
                '''
            )
        }

        cleanup {
            // 정리 작업
            sh '''
                docker system prune -f
                kubectl delete pods --field-selector=status.phase=Succeeded -n semiconductor-hmi || true
            '''
        }
    }
}
```

---

## 🧪 테스트 및 시뮬레이션 (45분): 팹 환경 시뮬레이션 및 성능 검증

### 1. 실제 반도체 팹 환경 시뮬레이터 (20분)

#### 1.1 디지털 트윈 팹 시뮬레이터

```cpp
// FabSimulator.cpp
#include "MasterSystemArchitecture.h"
#include <random>
#include <thread>
#include <chrono>

namespace SemiconductorHMI::Simulation {

// 반도체 공정 단계
enum class ProcessStep {
    WAFER_INCOMING,
    CLEANING,
    LITHOGRAPHY,
    ETCHING,
    DEPOSITION_CVD,
    DEPOSITION_PVD,
    ION_IMPLANTATION,
    CMP,
    METROLOGY,
    FINAL_TEST,
    OUTGOING
};

// 장비 상태
enum class EquipmentState {
    IDLE,
    RUNNING,
    MAINTENANCE,
    ERROR,
    CLEANING_MODE
};

// 웨이퍼 정보
struct Wafer {
    std::string wafer_id;
    std::string lot_id;
    ProcessStep current_step;
    std::vector<ProcessStep> completed_steps;
    std::chrono::system_clock::time_point start_time;
    std::unordered_map<std::string, double> measurements;
    bool has_defects = false;
    int priority = 0;
};

// 장비 정보
struct Equipment {
    std::string equipment_id;
    std::string equipment_type;  // CVD, PVD, ETCH, CMP, etc.
    ProcessStep process_step;
    EquipmentState state;
    Wafer* current_wafer = nullptr;

    // 성능 지표
    double throughput_wafers_per_hour = 0.0;
    double uptime_percentage = 0.0;
    double yield_percentage = 0.0;
    std::chrono::system_clock::time_point last_maintenance;

    // 실시간 파라미터
    std::unordered_map<std::string, double> process_parameters;
    std::unordered_map<std::string, double> parameter_limits;
};

class FabSimulator {
private:
    // 팹 구성
    std::vector<Equipment> equipment_list_;
    std::queue<Wafer> wafer_queue_;
    std::vector<Wafer> completed_wafers_;

    // 시뮬레이션 제어
    std::atomic<bool> simulation_running_{false};
    std::thread simulation_thread_;
    std::thread equipment_thread_;
    std::thread wafer_generator_thread_;

    // 시뮬레이션 통계
    struct FabStatistics {
        std::atomic<int> total_wafers_processed{0};
        std::atomic<int> wafers_in_process{0};
        std::atomic<double> overall_yield{0.0};
        std::atomic<double> average_cycle_time_hours{0.0};
        std::atomic<int> equipment_downtime_minutes{0};
    } statistics_;

    // 현실적인 데이터 생성을 위한 랜덤 생성기
    mutable std::mutex random_mutex_;
    std::mt19937 random_generator_;

public:
    FabSimulator() : random_generator_(std::random_device{}()) {
        InitializeFabLayout();
    }

    ~FabSimulator() {
        StopSimulation();
    }

    bool StartSimulation() {
        if (simulation_running_) return false;

        simulation_running_ = true;

        // 시뮬레이션 스레드들 시작
        simulation_thread_ = std::thread([this]() { SimulationLoop(); });
        equipment_thread_ = std::thread([this]() { EquipmentSimulationLoop(); });
        wafer_generator_thread_ = std::thread([this]() { WaferGeneratorLoop(); });

        return true;
    }

    void StopSimulation() {
        if (simulation_running_) {
            simulation_running_ = false;

            if (simulation_thread_.joinable()) simulation_thread_.join();
            if (equipment_thread_.joinable()) equipment_thread_.join();
            if (wafer_generator_thread_.joinable()) wafer_generator_thread_.join();
        }
    }

    // 실시간 데이터 접근
    std::vector<Equipment> GetEquipmentStatus() const {
        return equipment_list_;
    }

    FabStatistics GetFabStatistics() const {
        return statistics_;
    }

    // 장비 제어 시뮬레이션
    bool StartEquipment(const std::string& equipment_id) {
        auto it = std::find_if(equipment_list_.begin(), equipment_list_.end(),
                              [&](const Equipment& eq) { return eq.equipment_id == equipment_id; });

        if (it != equipment_list_.end() && it->state == EquipmentState::IDLE) {
            it->state = EquipmentState::RUNNING;
            return true;
        }
        return false;
    }

    bool StopEquipment(const std::string& equipment_id) {
        auto it = std::find_if(equipment_list_.begin(), equipment_list_.end(),
                              [&](const Equipment& eq) { return eq.equipment_id == equipment_id; });

        if (it != equipment_list_.end() && it->state == EquipmentState::RUNNING) {
            it->state = EquipmentState::IDLE;
            return true;
        }
        return false;
    }

    bool TriggerMaintenance(const std::string& equipment_id) {
        auto it = std::find_if(equipment_list_.begin(), equipment_list_.end(),
                              [&](const Equipment& eq) { return eq.equipment_id == equipment_id; });

        if (it != equipment_list_.end()) {
            it->state = EquipmentState::MAINTENANCE;
            it->last_maintenance = std::chrono::system_clock::now();
            return true;
        }
        return false;
    }

private:
    void InitializeFabLayout() {
        // CVD 장비들
        for (int i = 1; i <= 4; ++i) {
            Equipment cvd;
            cvd.equipment_id = "CVD_" + std::to_string(i);
            cvd.equipment_type = "CVD";
            cvd.process_step = ProcessStep::DEPOSITION_CVD;
            cvd.state = EquipmentState::IDLE;
            cvd.throughput_wafers_per_hour = 25.0;
            cvd.uptime_percentage = 95.0;
            cvd.yield_percentage = 98.5;

            // 프로세스 파라미터 설정
            cvd.process_parameters["temperature"] = 250.0;
            cvd.process_parameters["pressure"] = 0.1;
            cvd.process_parameters["flow_rate"] = 50.0;
            cvd.process_parameters["power"] = 1500.0;

            cvd.parameter_limits["temperature"] = 280.0;  // 최대값
            cvd.parameter_limits["pressure"] = 0.15;
            cvd.parameter_limits["flow_rate"] = 60.0;
            cvd.parameter_limits["power"] = 2000.0;

            equipment_list_.push_back(cvd);
        }

        // PVD 장비들
        for (int i = 1; i <= 3; ++i) {
            Equipment pvd;
            pvd.equipment_id = "PVD_" + std::to_string(i);
            pvd.equipment_type = "PVD";
            pvd.process_step = ProcessStep::DEPOSITION_PVD;
            pvd.state = EquipmentState::IDLE;
            pvd.throughput_wafers_per_hour = 20.0;
            pvd.uptime_percentage = 92.0;
            pvd.yield_percentage = 97.8;

            pvd.process_parameters["temperature"] = 200.0;
            pvd.process_parameters["pressure"] = 0.05;
            pvd.process_parameters["power"] = 2000.0;
            pvd.process_parameters["voltage"] = 380.0;

            equipment_list_.push_back(pvd);
        }

        // ETCH 장비들
        for (int i = 1; i <= 5; ++i) {
            Equipment etch;
            etch.equipment_id = "ETCH_" + std::to_string(i);
            etch.equipment_type = "ETCH";
            etch.process_step = ProcessStep::ETCHING;
            etch.state = EquipmentState::IDLE;
            etch.throughput_wafers_per_hour = 30.0;
            etch.uptime_percentage = 90.0;
            etch.yield_percentage = 96.5;

            etch.process_parameters["pressure"] = 0.02;
            etch.process_parameters["flow_rate"] = 100.0;
            etch.process_parameters["power"] = 2500.0;
            etch.process_parameters["bias_voltage"] = 150.0;

            equipment_list_.push_back(etch);
        }

        // CMP 장비들
        for (int i = 1; i <= 2; ++i) {
            Equipment cmp;
            cmp.equipment_id = "CMP_" + std::to_string(i);
            cmp.equipment_type = "CMP";
            cmp.process_step = ProcessStep::CMP;
            cmp.state = EquipmentState::IDLE;
            cmp.throughput_wafers_per_hour = 15.0;
            cmp.uptime_percentage = 88.0;
            cmp.yield_percentage = 99.2;

            cmp.process_parameters["pressure"] = 5.0;  // psi
            cmp.process_parameters["rotation_speed"] = 120.0;  // rpm
            cmp.process_parameters["slurry_flow"] = 200.0;  // ml/min

            equipment_list_.push_back(cmp);
        }

        // 리소그래피 장비들
        for (int i = 1; i <= 3; ++i) {
            Equipment litho;
            litho.equipment_id = "LITHO_" + std::to_string(i);
            litho.equipment_type = "LITHOGRAPHY";
            litho.process_step = ProcessStep::LITHOGRAPHY;
            litho.state = EquipmentState::IDLE;
            litho.throughput_wafers_per_hour = 40.0;
            litho.uptime_percentage = 85.0;
            litho.yield_percentage = 94.0;

            equipment_list_.push_back(litho);
        }
    }

    void SimulationLoop() {
        while (simulation_running_) {
            // 웨이퍼 라우팅 및 스케줄링
            ProcessWaferQueue();

            // 통계 업데이트
            UpdateStatistics();

            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }

    void EquipmentSimulationLoop() {
        while (simulation_running_) {
            for (auto& equipment : equipment_list_) {
                SimulateEquipmentBehavior(equipment);
            }

            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
    }

    void WaferGeneratorLoop() {
        int wafer_counter = 1;

        while (simulation_running_) {
            // 새 웨이퍼 생성 (현실적인 간격)
            std::this_thread::sleep_for(std::chrono::minutes(2));

            Wafer new_wafer;
            new_wafer.wafer_id = "W" + std::to_string(wafer_counter++);
            new_wafer.lot_id = "LOT" + std::to_string((wafer_counter - 1) / 25 + 1);
            new_wafer.current_step = ProcessStep::WAFER_INCOMING;
            new_wafer.start_time = std::chrono::system_clock::now();
            new_wafer.priority = GenerateRandomInt(1, 5);

            wafer_queue_.push(new_wafer);
            statistics_.wafers_in_process++;
        }
    }

    void ProcessWaferQueue() {
        if (wafer_queue_.empty()) return;

        Wafer& wafer = wafer_queue_.front();

        // 다음 프로세스 단계에 맞는 장비 찾기
        auto available_equipment = FindAvailableEquipment(wafer.current_step);

        if (available_equipment) {
            // 웨이퍼를 장비에 할당
            available_equipment->current_wafer = &wafer;
            available_equipment->state = EquipmentState::RUNNING;

            wafer_queue_.pop();

            // 프로세스 완료 시뮬레이션 (별도 스레드에서 처리)
            std::thread([this, available_equipment]() {
                ProcessWaferOnEquipment(available_equipment);
            }).detach();
        }
    }

    Equipment* FindAvailableEquipment(ProcessStep step) {
        for (auto& equipment : equipment_list_) {
            if (equipment.process_step == step && equipment.state == EquipmentState::IDLE) {
                return &equipment;
            }
        }
        return nullptr;
    }

    void ProcessWaferOnEquipment(Equipment* equipment) {
        if (!equipment || !equipment->current_wafer) return;

        // 프로세스 시간 시뮬레이션
        double process_time_hours = 3600.0 / equipment->throughput_wafers_per_hour;
        int process_time_seconds = static_cast<int>(process_time_hours * 3600);

        std::this_thread::sleep_for(std::chrono::seconds(process_time_seconds));

        // 프로세스 완료 처리
        Wafer* wafer = equipment->current_wafer;
        wafer->completed_steps.push_back(wafer->current_step);

        // 다음 단계로 이동
        wafer->current_step = GetNextProcessStep(wafer->current_step);

        // 수율 시뮬레이션
        if (GenerateRandomDouble(0.0, 100.0) > equipment->yield_percentage) {
            wafer->has_defects = true;
        }

        // 장비에서 웨이퍼 제거
        equipment->current_wafer = nullptr;
        equipment->state = EquipmentState::IDLE;

        // 웨이퍼가 완료되었으면 완료 목록에 추가
        if (wafer->current_step == ProcessStep::OUTGOING) {
            completed_wafers_.push_back(*wafer);
            statistics_.total_wafers_processed++;
            statistics_.wafers_in_process--;
        } else {
            // 다음 단계를 위해 큐에 다시 추가
            wafer_queue_.push(*wafer);
        }
    }

    ProcessStep GetNextProcessStep(ProcessStep current) {
        switch (current) {
            case ProcessStep::WAFER_INCOMING: return ProcessStep::CLEANING;
            case ProcessStep::CLEANING: return ProcessStep::LITHOGRAPHY;
            case ProcessStep::LITHOGRAPHY: return ProcessStep::ETCHING;
            case ProcessStep::ETCHING: return ProcessStep::DEPOSITION_CVD;
            case ProcessStep::DEPOSITION_CVD: return ProcessStep::DEPOSITION_PVD;
            case ProcessStep::DEPOSITION_PVD: return ProcessStep::ION_IMPLANTATION;
            case ProcessStep::ION_IMPLANTATION: return ProcessStep::CMP;
            case ProcessStep::CMP: return ProcessStep::METROLOGY;
            case ProcessStep::METROLOGY: return ProcessStep::FINAL_TEST;
            case ProcessStep::FINAL_TEST: return ProcessStep::OUTGOING;
            default: return ProcessStep::OUTGOING;
        }
    }

    void SimulateEquipmentBehavior(Equipment& equipment) {
        // 프로세스 파라미터 변동 시뮬레이션
        for (auto& [param_name, value] : equipment.process_parameters) {
            double variation = GenerateRandomDouble(-2.0, 2.0);  // ±2% 변동
            double new_value = value * (1.0 + variation / 100.0);

            // 한계값 체크
            if (equipment.parameter_limits.count(param_name)) {
                double limit = equipment.parameter_limits[param_name];
                if (new_value > limit) {
                    // 알람 발생 시뮬레이션
                    equipment.state = EquipmentState::ERROR;
                    continue;
                }
            }

            equipment.process_parameters[param_name] = new_value;
        }

        // 장비 고장 시뮬레이션 (매우 낮은 확률)
        if (equipment.state == EquipmentState::RUNNING && GenerateRandomDouble(0.0, 1.0) < 0.0001) {
            equipment.state = EquipmentState::ERROR;
        }

        // 정기 유지보수 시뮬레이션
        auto now = std::chrono::system_clock::now();
        auto hours_since_maintenance = std::chrono::duration_cast<std::chrono::hours>(
            now - equipment.last_maintenance).count();

        if (hours_since_maintenance > 168) {  // 1주일마다 유지보수
            equipment.state = EquipmentState::MAINTENANCE;
        }
    }

    void UpdateStatistics() {
        // 전체 수율 계산
        if (!completed_wafers_.empty()) {
            int good_wafers = 0;
            for (const auto& wafer : completed_wafers_) {
                if (!wafer.has_defects) good_wafers++;
            }
            statistics_.overall_yield = (static_cast<double>(good_wafers) / completed_wafers_.size()) * 100.0;
        }

        // 평균 사이클 타임 계산
        if (!completed_wafers_.empty()) {
            double total_cycle_time = 0.0;
            auto now = std::chrono::system_clock::now();

            for (const auto& wafer : completed_wafers_) {
                auto cycle_time = std::chrono::duration_cast<std::chrono::hours>(
                    now - wafer.start_time).count();
                total_cycle_time += cycle_time;
            }

            statistics_.average_cycle_time_hours = total_cycle_time / completed_wafers_.size();
        }
    }

    double GenerateRandomDouble(double min, double max) {
        std::lock_guard<std::mutex> lock(random_mutex_);
        std::uniform_real_distribution<double> dist(min, max);
        return dist(random_generator_);
    }

    int GenerateRandomInt(int min, int max) {
        std::lock_guard<std::mutex> lock(random_mutex_);
        std::uniform_int_distribution<int> dist(min, max);
        return dist(random_generator_);
    }
};

} // namespace SemiconductorHMI::Simulation
```

### 2. 통합 성능 테스트 (15분)

#### 2.1 종합 성능 벤치마크

```cpp
// PerformanceBenchmark.cpp
#include "MasterSystemArchitecture.h"
#include "FabSimulator.h"
#include <chrono>
#include <fstream>

namespace SemiconductorHMI::Testing {

struct BenchmarkResult {
    std::string test_name;
    double duration_ms;
    double throughput_ops_per_sec;
    double memory_peak_mb;
    double cpu_peak_percent;
    bool success;
    std::string error_message;
};

class PerformanceBenchmark {
private:
    Enterprise::MasterSystemController* system_controller_;
    Simulation::FabSimulator* fab_simulator_;
    std::vector<BenchmarkResult> results_;

public:
    PerformanceBenchmark(Enterprise::MasterSystemController* controller,
                        Simulation::FabSimulator* simulator)
        : system_controller_(controller), fab_simulator_(simulator) {}

    std::vector<BenchmarkResult> RunAllBenchmarks() {
        results_.clear();

        // UI 렌더링 성능 테스트
        results_.push_back(BenchmarkUIRendering());

        // 데이터 처리 성능 테스트
        results_.push_back(BenchmarkDataProcessing());

        // 네트워크 처리 성능 테스트
        results_.push_back(BenchmarkNetworking());

        // 메모리 사용량 테스트
        results_.push_back(BenchmarkMemoryUsage());

        // 동시성 테스트
        results_.push_back(BenchmarkConcurrency());

        // 팹 시뮬레이션 성능 테스트
        results_.push_back(BenchmarkFabSimulation());

        // 전체 시스템 스트레스 테스트
        results_.push_back(BenchmarkSystemStress());

        return results_;
    }

    void GenerateReport(const std::string& filename) {
        std::ofstream report(filename);

        report << "# Semiconductor HMI Performance Benchmark Report\n\n";
        report << "Generated: " << GetCurrentTimestamp() << "\n\n";

        report << "## Summary\n\n";
        int passed = 0, failed = 0;
        for (const auto& result : results_) {
            if (result.success) passed++;
            else failed++;
        }

        report << "- Total Tests: " << results_.size() << "\n";
        report << "- Passed: " << passed << "\n";
        report << "- Failed: " << failed << "\n";
        report << "- Success Rate: " << (static_cast<double>(passed) / results_.size() * 100.0) << "%\n\n";

        report << "## Detailed Results\n\n";
        for (const auto& result : results_) {
            report << "### " << result.test_name << "\n\n";
            report << "- Status: " << (result.success ? "PASS" : "FAIL") << "\n";
            report << "- Duration: " << result.duration_ms << " ms\n";
            report << "- Throughput: " << result.throughput_ops_per_sec << " ops/sec\n";
            report << "- Peak Memory: " << result.memory_peak_mb << " MB\n";
            report << "- Peak CPU: " << result.cpu_peak_percent << "%\n";

            if (!result.success) {
                report << "- Error: " << result.error_message << "\n";
            }
            report << "\n";
        }

        report.close();
    }

private:
    BenchmarkResult BenchmarkUIRendering() {
        BenchmarkResult result;
        result.test_name = "UI Rendering Performance";

        auto start_time = std::chrono::high_resolution_clock::now();

        try {
            // UI 모듈 가져오기
            auto ui_module = system_controller_->GetModule<Enterprise::UIFrameworkModule>(
                Enterprise::ModuleType::UI_FRAMEWORK);

            if (!ui_module) {
                result.success = false;
                result.error_message = "UI Framework module not found";
                return result;
            }

            // 1000프레임 렌더링 시뮬레이션
            const int frame_count = 1000;
            auto frame_start = std::chrono::high_resolution_clock::now();

            for (int i = 0; i < frame_count; ++i) {
                ui_module->Update(1.0f / 60.0f);  // 60 FPS 시뮬레이션

                // 메모리 사용량 모니터링
                auto metrics = ui_module->GetMetrics();
                result.memory_peak_mb = std::max(result.memory_peak_mb, metrics.memory_usage_mb);
                result.cpu_peak_percent = std::max(result.cpu_peak_percent, metrics.cpu_usage);
            }

            auto end_time = std::chrono::high_resolution_clock::now();
            result.duration_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
            result.throughput_ops_per_sec = frame_count / (result.duration_ms / 1000.0);
            result.success = true;

        } catch (const std::exception& e) {
            result.success = false;
            result.error_message = e.what();
        }

        return result;
    }

    BenchmarkResult BenchmarkDataProcessing() {
        BenchmarkResult result;
        result.test_name = "Data Processing Performance";

        auto start_time = std::chrono::high_resolution_clock::now();

        try {
            auto data_module = system_controller_->GetModule<Enterprise::DataProcessingModule>(
                Enterprise::ModuleType::DATA_PROCESSING);

            if (!data_module) {
                result.success = false;
                result.error_message = "Data Processing module not found";
                return result;
            }

            // 대용량 데이터 처리 시뮬레이션
            const int data_points = 100000;
            std::vector<double> test_data;
            test_data.reserve(data_points);

            for (int i = 0; i < data_points; ++i) {
                test_data.push_back(static_cast<double>(rand()) / RAND_MAX * 1000.0);
            }

            // 데이터 처리 시뮬레이션
            for (int i = 0; i < data_points; ++i) {
                // 실제 데이터 버퍼에 추가하는 시뮬레이션
                auto buffer = data_module->GetDataBuffer("test_buffer");
                if (buffer) {
                    double timestamp = std::chrono::duration<double>(
                        std::chrono::system_clock::now().time_since_epoch()).count();
                    buffer->AddPoint({timestamp, test_data[i], 100});
                }

                if (i % 1000 == 0) {
                    auto metrics = data_module->GetMetrics();
                    result.memory_peak_mb = std::max(result.memory_peak_mb, metrics.memory_usage_mb);
                    result.cpu_peak_percent = std::max(result.cpu_peak_percent, metrics.cpu_usage);
                }
            }

            auto end_time = std::chrono::high_resolution_clock::now();
            result.duration_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
            result.throughput_ops_per_sec = data_points / (result.duration_ms / 1000.0);
            result.success = true;

        } catch (const std::exception& e) {
            result.success = false;
            result.error_message = e.what();
        }

        return result;
    }

    BenchmarkResult BenchmarkNetworking() {
        BenchmarkResult result;
        result.test_name = "Network Performance";

        auto start_time = std::chrono::high_resolution_clock::now();

        try {
            auto network_module = system_controller_->GetModule<Enterprise::NetworkingModule>(
                Enterprise::ModuleType::NETWORKING);

            if (!network_module) {
                result.success = false;
                result.error_message = "Networking module not found";
                return result;
            }

            // MQTT 메시지 처리 성능 테스트
            auto mqtt_client = network_module->GetMQTTClient();
            if (!mqtt_client) {
                result.success = false;
                result.error_message = "MQTT client not available";
                return result;
            }

            const int message_count = 10000;
            int messages_sent = 0;

            for (int i = 0; i < message_count; ++i) {
                std::string topic = "test/performance/" + std::to_string(i);
                std::string payload = "test_message_" + std::to_string(i);

                if (mqtt_client->Publish(topic, payload, 0)) {
                    messages_sent++;
                }

                if (i % 100 == 0) {
                    auto metrics = network_module->GetMetrics();
                    result.memory_peak_mb = std::max(result.memory_peak_mb, metrics.memory_usage_mb);
                    result.cpu_peak_percent = std::max(result.cpu_peak_percent, metrics.cpu_usage);
                }
            }

            auto end_time = std::chrono::high_resolution_clock::now();
            result.duration_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
            result.throughput_ops_per_sec = messages_sent / (result.duration_ms / 1000.0);
            result.success = (messages_sent == message_count);

        } catch (const std::exception& e) {
            result.success = false;
            result.error_message = e.what();
        }

        return result;
    }

    BenchmarkResult BenchmarkMemoryUsage() {
        BenchmarkResult result;
        result.test_name = "Memory Usage Test";

        auto start_time = std::chrono::high_resolution_clock::now();

        try {
            // 시스템 전체 메모리 사용량 모니터링
            const int iterations = 1000;
            double total_memory = 0.0;

            for (int i = 0; i < iterations; ++i) {
                auto global_metrics = system_controller_->GetGlobalMetrics();
                total_memory += global_metrics.memory_usage_mb;
                result.memory_peak_mb = std::max(result.memory_peak_mb, global_metrics.memory_usage_mb);

                // 메모리 사용량이 임계값을 초과하는지 확인
                if (global_metrics.memory_usage_mb > 4096.0) {  // 4GB 임계값
                    result.success = false;
                    result.error_message = "Memory usage exceeded 4GB limit";
                    return result;
                }

                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }

            auto end_time = std::chrono::high_resolution_clock::now();
            result.duration_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
            result.throughput_ops_per_sec = iterations / (result.duration_ms / 1000.0);
            result.success = true;

        } catch (const std::exception& e) {
            result.success = false;
            result.error_message = e.what();
        }

        return result;
    }

    BenchmarkResult BenchmarkConcurrency() {
        BenchmarkResult result;
        result.test_name = "Concurrency Test";

        auto start_time = std::chrono::high_resolution_clock::now();

        try {
            const int thread_count = 10;
            const int operations_per_thread = 1000;
            std::vector<std::thread> threads;
            std::atomic<int> total_operations{0};
            std::atomic<bool> test_failed{false};

            // 여러 스레드에서 동시에 시스템 접근
            for (int t = 0; t < thread_count; ++t) {
                threads.emplace_back([this, &total_operations, &test_failed, operations_per_thread]() {
                    try {
                        for (int i = 0; i < operations_per_thread; ++i) {
                            // 다양한 모듈에 동시 접근
                            auto ui_module = system_controller_->GetModule<Enterprise::UIFrameworkModule>(
                                Enterprise::ModuleType::UI_FRAMEWORK);
                            auto data_module = system_controller_->GetModule<Enterprise::DataProcessingModule>(
                                Enterprise::ModuleType::DATA_PROCESSING);

                            if (ui_module) ui_module->Update(0.016f);
                            if (data_module) data_module->Update(0.016f);

                            total_operations++;
                        }
                    } catch (const std::exception&) {
                        test_failed = true;
                    }
                });
            }

            // 모든 스레드 완료 대기
            for (auto& thread : threads) {
                thread.join();
            }

            auto end_time = std::chrono::high_resolution_clock::now();
            result.duration_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
            result.throughput_ops_per_sec = total_operations.load() / (result.duration_ms / 1000.0);
            result.success = !test_failed.load() && (total_operations.load() == thread_count * operations_per_thread);

            if (test_failed.load()) {
                result.error_message = "Concurrency test failed due to thread safety issues";
            }

        } catch (const std::exception& e) {
            result.success = false;
            result.error_message = e.what();
        }

        return result;
    }

    BenchmarkResult BenchmarkFabSimulation() {
        BenchmarkResult result;
        result.test_name = "Fab Simulation Performance";

        auto start_time = std::chrono::high_resolution_clock::now();

        try {
            if (!fab_simulator_) {
                result.success = false;
                result.error_message = "Fab simulator not available";
                return result;
            }

            // 팹 시뮬레이션 시작
            fab_simulator_->StartSimulation();

            // 30초간 시뮬레이션 실행
            std::this_thread::sleep_for(std::chrono::seconds(30));

            // 시뮬레이션 통계 수집
            auto stats = fab_simulator_->GetFabStatistics();
            auto equipment_status = fab_simulator_->GetEquipmentStatus();

            fab_simulator_->StopSimulation();

            auto end_time = std::chrono::high_resolution_clock::now();
            result.duration_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
            result.throughput_ops_per_sec = stats.total_wafers_processed.load() / (result.duration_ms / 1000.0);
            result.success = true;

            // 장비 상태 확인
            for (const auto& eq : equipment_status) {
                if (eq.state == Simulation::EquipmentState::ERROR) {
                    result.error_message += "Equipment " + eq.equipment_id + " in error state; ";
                }
            }

        } catch (const std::exception& e) {
            result.success = false;
            result.error_message = e.what();
        }

        return result;
    }

    BenchmarkResult BenchmarkSystemStress() {
        BenchmarkResult result;
        result.test_name = "System Stress Test";

        auto start_time = std::chrono::high_resolution_clock::now();

        try {
            // 모든 시스템에 동시에 부하 가하기
            std::vector<std::thread> stress_threads;
            std::atomic<bool> stress_test_running{true};

            // UI 스트레스
            stress_threads.emplace_back([this, &stress_test_running]() {
                while (stress_test_running) {
                    auto ui_module = system_controller_->GetModule<Enterprise::UIFrameworkModule>(
                        Enterprise::ModuleType::UI_FRAMEWORK);
                    if (ui_module) ui_module->Update(0.016f);
                    std::this_thread::sleep_for(std::chrono::milliseconds(1));
                }
            });

            // 데이터 처리 스트레스
            stress_threads.emplace_back([this, &stress_test_running]() {
                while (stress_test_running) {
                    auto data_module = system_controller_->GetModule<Enterprise::DataProcessingModule>(
                        Enterprise::ModuleType::DATA_PROCESSING);
                    if (data_module) data_module->Update(0.016f);
                    std::this_thread::sleep_for(std::chrono::milliseconds(1));
                }
            });

            // 네트워크 스트레스
            stress_threads.emplace_back([this, &stress_test_running]() {
                auto network_module = system_controller_->GetModule<Enterprise::NetworkingModule>(
                    Enterprise::ModuleType::NETWORKING);
                auto mqtt_client = network_module ? network_module->GetMQTTClient() : nullptr;

                int counter = 0;
                while (stress_test_running && mqtt_client) {
                    mqtt_client->Publish("stress/test", "stress_data_" + std::to_string(counter++), 0);
                    std::this_thread::sleep_for(std::chrono::milliseconds(10));
                }
            });

            // 60초간 스트레스 테스트 실행
            std::this_thread::sleep_for(std::chrono::seconds(60));

            stress_test_running = false;

            // 모든 스레드 종료 대기
            for (auto& thread : stress_threads) {
                thread.join();
            }

            // 시스템 상태 확인
            auto global_metrics = system_controller_->GetGlobalMetrics();
            result.memory_peak_mb = global_metrics.memory_usage_mb;
            result.cpu_peak_percent = global_metrics.cpu_usage;

            auto end_time = std::chrono::high_resolution_clock::now();
            result.duration_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
            result.success = (system_controller_->GetSystemStatus() == Enterprise::SystemStatus::RUNNING);

        } catch (const std::exception& e) {
            result.success = false;
            result.error_message = e.what();
        }

        return result;
    }

    std::string GetCurrentTimestamp() {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);

        std::stringstream ss;
        ss << std::put_time(std::gmtime(&time_t), "%Y-%m-%d %H:%M:%S UTC");
        return ss.str();
    }
};

} // namespace SemiconductorHMI::Testing
```

### 3. 최종 통합 애플리케이션 (10분)

#### 3.1 최종 엔터프라이즈 HMI 시스템

```cpp
// FinalIntegratedHMI.cpp
#include "MasterSystemArchitecture.h"
#include "FabSimulator.h"
#include "PerformanceBenchmark.h"

namespace SemiconductorHMI {

class FinalIntegratedHMISystem {
private:
    std::unique_ptr<Enterprise::MasterSystemController> system_controller_;
    std::unique_ptr<Simulation::FabSimulator> fab_simulator_;
    std::unique_ptr<Testing::PerformanceBenchmark> benchmark_;

public:
    FinalIntegratedHMISystem() = default;
    ~FinalIntegratedHMISystem() = default;

    bool Initialize() {
        try {
            // 마스터 시스템 컨트롤러 초기화
            system_controller_ = std::make_unique<Enterprise::MasterSystemController>();
            if (!system_controller_->Initialize("config/production.json")) {
                printf("Failed to initialize system controller\n");
                return false;
            }

            // 팹 시뮬레이터 초기화
            fab_simulator_ = std::make_unique<Simulation::FabSimulator>();
            fab_simulator_->StartSimulation();

            // 성능 벤치마크 도구 초기화
            benchmark_ = std::make_unique<Testing::PerformanceBenchmark>(
                system_controller_.get(), fab_simulator_.get());

            printf("=== Semiconductor HMI Enterprise System Started ===\n");
            printf("System Status: %s\n", GetSystemStatusString().c_str());
            printf("Active Modules: %d\n", GetActiveModuleCount());
            printf("Fab Simulation: RUNNING\n");
            printf("Performance Monitoring: ENABLED\n");
            printf("===============================================\n\n");

            return true;

        } catch (const std::exception& e) {
            printf("System initialization failed: %s\n", e.what());
            return false;
        }
    }

    void Run() {
        printf("Starting main application loop...\n");

        // 성능 벤치마크 실행 (시작 시 한 번)
        RunPerformanceBenchmark();

        // 메인 애플리케이션 루프
        system_controller_->Run();
    }

    void Shutdown() {
        printf("Shutting down Semiconductor HMI Enterprise System...\n");

        if (fab_simulator_) {
            fab_simulator_->StopSimulation();
        }

        if (system_controller_) {
            system_controller_->Shutdown();
        }

        printf("System shutdown completed.\n");
    }

    void RunPerformanceBenchmark() {
        printf("Running performance benchmark...\n");

        auto results = benchmark_->RunAllBenchmarks();
        benchmark_->GenerateReport("performance_report.md");

        printf("Performance Benchmark Results:\n");
        printf("=============================\n");

        int passed = 0, failed = 0;
        for (const auto& result : results) {
            printf("%-30s: %s\n", result.test_name.c_str(),
                   result.success ? "PASS" : "FAIL");

            if (result.success) {
                printf("  Duration: %.2f ms, Throughput: %.2f ops/sec\n",
                       result.duration_ms, result.throughput_ops_per_sec);
                passed++;
            } else {
                printf("  Error: %s\n", result.error_message.c_str());
                failed++;
            }
        }

        printf("=============================\n");
        printf("Total: %d, Passed: %d, Failed: %d\n",
               static_cast<int>(results.size()), passed, failed);
        printf("Success Rate: %.1f%%\n\n",
               (static_cast<double>(passed) / results.size()) * 100.0);
    }

    // 시스템 상태 모니터링
    void PrintSystemStatus() {
        auto metrics = system_controller_->GetGlobalMetrics();
        auto fab_stats = fab_simulator_->GetFabStatistics();

        printf("\n=== System Status ===\n");
        printf("System: %s\n", GetSystemStatusString().c_str());
        printf("CPU Usage: %.1f%%\n", metrics.cpu_usage);
        printf("Memory: %.1f MB\n", metrics.memory_usage_mb);
        printf("GPU Usage: %.1f%%\n", metrics.gpu_usage);
        printf("Active Connections: %d\n", metrics.active_connections);

        printf("\n=== Fab Simulation Status ===\n");
        printf("Wafers Processed: %d\n", fab_stats.total_wafers_processed.load());
        printf("Wafers In Process: %d\n", fab_stats.wafers_in_process.load());
        printf("Overall Yield: %.2f%%\n", fab_stats.overall_yield.load());
        printf("Avg Cycle Time: %.2f hours\n", fab_stats.average_cycle_time_hours.load());
        printf("=====================\n\n");
    }

private:
    std::string GetSystemStatusString() {
        auto status = system_controller_->GetSystemStatus();
        switch (status) {
            case Enterprise::SystemStatus::INITIALIZING: return "INITIALIZING";
            case Enterprise::SystemStatus::RUNNING: return "RUNNING";
            case Enterprise::SystemStatus::MAINTENANCE: return "MAINTENANCE";
            case Enterprise::SystemStatus::ERROR: return "ERROR";
            case Enterprise::SystemStatus::SHUTDOWN: return "SHUTDOWN";
            default: return "UNKNOWN";
        }
    }

    int GetActiveModuleCount() {
        // 실제 구현에서는 시스템 컨트롤러에서 활성 모듈 수를 반환
        return 6;  // UI, Data, Network, Security, Monitoring, Plugin
    }
};

} // namespace SemiconductorHMI

// 메인 애플리케이션 진입점
int main(int argc, char* argv[]) {
    printf("===============================================\n");
    printf("Semiconductor HMI Enterprise System v1.0.0\n");
    printf("Advanced Industrial HMI Platform\n");
    printf("===============================================\n\n");

    try {
        SemiconductorHMI::FinalIntegratedHMISystem hmi_system;

        if (!hmi_system.Initialize()) {
            printf("Failed to initialize HMI system\n");
            return -1;
        }

        // 시그널 핸들러 설정 (Ctrl+C 처리)
        std::signal(SIGINT, [](int) {
            printf("\nShutdown signal received...\n");
            // 실제 구현에서는 전역 변수로 시스템 참조 유지
            exit(0);
        });

        // 시스템 실행
        hmi_system.Run();

    } catch (const std::exception& e) {
        printf("Critical error: %s\n", e.what());
        return -1;
    }

    return 0;
}
```

---

## 🎤 최종 발표 (30분): 프로젝트 시연 및 성과 평가

### 📊 최종 프로젝트 성과 요약

#### ✅ 완성된 기술 스택
1. **C# WPF 기반 UI 프레임워크** (Week 2-5)
   - MVVM 아키텍처 및 반응형 UI
   - 실시간 데이터 바인딩 및 차트 시각화
   - 고급 애니메이션 및 테마 시스템
   - 자동화된 테스트 및 배포

2. **Python PySide6 크로스 플랫폼 시스템** (Week 6-9)
   - Qt 기반 네이티브 성능 UI
   - 실시간 데이터 처리 및 멀티스레딩
   - 고급 시각화 및 플러그인 아키텍처
   - Docker 컨테이너화 배포

3. **ImGUI C++ 고성능 엔진** (Week 10-13)
   - 즉시 모드 GUI 및 3D 통합
   - 고급 렌더링 및 커스텀 위젯
   - 플러그인 시스템 및 확장성
   - 엔터프라이즈급 시스템 통합

#### 🏭 산업용 HMI 솔루션 특징
- **실시간 성능**: 60 FPS 안정적 렌더링, 마이크로초 수준 응답시간
- **확장성**: 플러그인 아키텍처, 마이크로서비스 지원
- **보안**: 엔터프라이즈급 인증/권한, 암호화, 감사 로그
- **국제화**: 7개 언어 지원, 접근성 표준 준수
- **운영성**: Docker/K8s 배포, CI/CD 파이프라인, 모니터링

#### 📈 성능 지표 달성
- **처리량**: 100,000+ 데이터 포인트/초
- **동시 사용자**: 1,000+ 세션 지원
- **가용성**: 99.9% 업타임
- **응답시간**: <100ms 평균 응답시간
- **메모리 효율**: <2GB 메모리 사용

### 🔧 시스템 통합 검증 항목
1. **다중 기술 스택 연동**: C#, Python, C++ 모듈 간 데이터 흐름 검증
2. **실시간 성능 요구사항**: 마이크로초 수준 응답성 및 처리량 측정
3. **산업용 표준 준수**: 보안, 가용성, 확장성 테스트 수행
4. **DevOps 파이프라인**: 컨테이너화, 자동 배포, 모니터링 구성
5. **코드 품질 관리**: 정적 분석, 코드 리뷰, 문서화 프로세스

### 🔄 기술 확장 방향
1. **AI/ML 통합**: 예측 유지보수, 이상 탐지, 최적화 알고리즘
2. **클라우드 네이티브**: 서버리스 아키텍처, 마이크로서비스, 엣지 컴퓨팅
3. **AR/VR 지원**: 3D 시각화, 몰입형 인터페이스, 원격 모니터링
4. **블록체인 통합**: 공급망 추적, 스마트 계약, 데이터 무결성
5. **디지털 트윈**: 실시간 시뮬레이션, 예측 분석, 가상 검증