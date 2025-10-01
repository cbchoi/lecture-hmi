
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

### 3. 성능 최적화 및 모니터링

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

## 🚀 배포 시스템: 컨테이너화 및 CI/CD 파이프라인

### 1. Docker 컨테이너화

#### 1.1 멀티 스테이지 Dockerfile

```dockerfile
# Dockerfile.production
# 멀티 스테이지 빌드를 통한 최적화된 프로덕션 이미지
