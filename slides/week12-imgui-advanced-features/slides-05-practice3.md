#include <cstddef>

namespace SemiconductorHMI::Memory {

// 메모리 풀 블록
template<typename T>
class MemoryPool {
private:
    struct Block {
        alignas(T) char data[sizeof(T)];
        Block* next;
    };

    Block* free_list_;
    std::vector<std::unique_ptr<Block[]>> chunks_;
    size_t chunk_size_;
    std::mutex mutex_;

public:
    explicit MemoryPool(size_t chunk_size = 1024)
        : free_list_(nullptr), chunk_size_(chunk_size) {
        AllocateChunk();
    }

    ~MemoryPool() = default;

    template<typename... Args>
    T* Allocate(Args&&... args) {
        std::lock_guard<std::mutex> lock(mutex_);

        if (!free_list_) {
            AllocateChunk();
        }

        Block* block = free_list_;
        free_list_ = free_list_->next;

        // placement new로 객체 생성
        return new(block->data) T(std::forward<Args>(args)...);
    }

    void Deallocate(T* ptr) {
        if (!ptr) return;

        std::lock_guard<std::mutex> lock(mutex_);

        // 소멸자 호출
        ptr->~T();

        // 블록을 free list에 반환
        Block* block = reinterpret_cast<Block*>(ptr);
        block->next = free_list_;
        free_list_ = block;
    }

    size_t GetChunkCount() const { return chunks_.size(); }
    size_t GetTotalCapacity() const { return chunks_.size() * chunk_size_; }

private:
    void AllocateChunk() {
        auto chunk = std::make_unique<Block[]>(chunk_size_);

        // 새 청크의 블록들을 free list에 연결
        for (size_t i = 0; i < chunk_size_ - 1; ++i) {
            chunk[i].next = &chunk[i + 1];
        }
        chunk[chunk_size_ - 1].next = free_list_;
        free_list_ = chunk.get();

        chunks_.push_back(std::move(chunk));
    }
};

// 범용 메모리 관리자
class MemoryManager {
private:
    struct AllocationInfo {
        size_t size;
        std::chrono::time_point<std::chrono::steady_clock> allocation_time;
        std::string file;
        int line;
        std::string function;
    };

    std::unordered_map<void*, AllocationInfo> allocations_;
    std::mutex allocations_mutex_;

    size_t total_allocated_;
    size_t peak_allocated_;
    size_t allocation_count_;

public:
    static MemoryManager& GetInstance() {
        static MemoryManager instance;
        return instance;
    }

    MemoryManager() : total_allocated_(0), peak_allocated_(0), allocation_count_(0) {}

    void* Allocate(size_t size, const char* file = nullptr, int line = 0, const char* function = nullptr) {
        void* ptr = std::malloc(size);
        if (!ptr) {
            throw std::bad_alloc();
        }

        std::lock_guard<std::mutex> lock(allocations_mutex_);

        AllocationInfo info;
        info.size = size;
        info.allocation_time = std::chrono::steady_clock::now();
        if (file) info.file = file;
        info.line = line;
        if (function) info.function = function;

        allocations_[ptr] = info;
        total_allocated_ += size;
        peak_allocated_ = std::max(peak_allocated_, total_allocated_);
        allocation_count_++;

        return ptr;
    }

    void Deallocate(void* ptr) {
        if (!ptr) return;

        std::lock_guard<std::mutex> lock(allocations_mutex_);

        auto it = allocations_.find(ptr);
        if (it != allocations_.end()) {
            total_allocated_ -= it->second.size;
            allocations_.erase(it);
        }

        std::free(ptr);
    }

    void ShowMemoryWindow() {
        if (ImGui::Begin("Memory Manager")) {

            // 메모리 통계
            ImGui::Text("Current Allocated: %.2f MB", total_allocated_ / (1024.0 * 1024.0));
            ImGui::Text("Peak Allocated: %.2f MB", peak_allocated_ / (1024.0 * 1024.0));
            ImGui::Text("Active Allocations: %zu", allocations_.size());
            ImGui::Text("Total Allocations: %zu", allocation_count_);

            ImGui::Separator();

            // 활성 할당 목록
            if (ImGui::CollapsingHeader("Active Allocations")) {
                std::lock_guard<std::mutex> lock(allocations_mutex_);

                if (ImGui::BeginTable("AllocTable", 5, ImGuiTableFlags_Borders | ImGuiTableFlags_Resizable)) {
                    ImGui::TableSetupColumn("Address");
                    ImGui::TableSetupColumn("Size (bytes)");
                    ImGui::TableSetupColumn("Age (sec)");
                    ImGui::TableSetupColumn("File");
                    ImGui::TableSetupColumn("Function");
                    ImGui::TableHeadersRow();

                    auto now = std::chrono::steady_clock::now();
                    for (const auto& [ptr, info] : allocations_) {
                        ImGui::TableNextRow();

                        ImGui::TableNextColumn();
                        ImGui::Text("%p", ptr);

                        ImGui::TableNextColumn();
                        ImGui::Text("%zu", info.size);

                        ImGui::TableNextColumn();
                        auto age = std::chrono::duration_cast<std::chrono::seconds>(now - info.allocation_time).count();
                        ImGui::Text("%ld", age);

                        ImGui::TableNextColumn();
                        ImGui::Text("%s:%d", info.file.c_str(), info.line);

                        ImGui::TableNextColumn();
                        ImGui::Text("%s", info.function.c_str());
                    }

                    ImGui::EndTable();
                }
            }

            // 메모리 누수 감지
            if (ImGui::Button("Check for Leaks")) {
                CheckForLeaks();
            }
        }
        ImGui::End();
    }

private:
    void CheckForLeaks() {
        std::lock_guard<std::mutex> lock(allocations_mutex_);

        auto now = std::chrono::steady_clock::now();
        size_t leak_count = 0;
        size_t leak_size = 0;

        for (const auto& [ptr, info] : allocations_) {
            auto age = std::chrono::duration_cast<std::chrono::minutes>(now - info.allocation_time).count();
            if (age > 10) { // 10분 이상 된 할당은 누수 의심
                leak_count++;
                leak_size += info.size;
            }
        }

        if (leak_count > 0) {
            // 로그나 경고 표시
            ImGui::OpenPopup("Memory Leak Warning");
        }
    }
};

// 커스텀 스마트 포인터 (메모리 풀 사용)
template<typename T>
class PoolPtr {
private:
    T* ptr_;
    MemoryPool<T>* pool_;

public:
    explicit PoolPtr(MemoryPool<T>* pool) : ptr_(nullptr), pool_(pool) {}

    template<typename... Args>
    PoolPtr(MemoryPool<T>* pool, Args&&... args)
        : pool_(pool) {
        ptr_ = pool_->Allocate(std::forward<Args>(args)...);
    }

    ~PoolPtr() {
        if (ptr_ && pool_) {
            pool_->Deallocate(ptr_);
        }
    }

    // 이동 생성자
    PoolPtr(PoolPtr&& other) noexcept
        : ptr_(other.ptr_), pool_(other.pool_) {
        other.ptr_ = nullptr;
        other.pool_ = nullptr;
    }

    // 이동 대입 연산자
    PoolPtr& operator=(PoolPtr&& other) noexcept {
        if (this != &other) {
            if (ptr_ && pool_) {
                pool_->Deallocate(ptr_);
            }
            ptr_ = other.ptr_;
            pool_ = other.pool_;
            other.ptr_ = nullptr;
            other.pool_ = nullptr;
        }
        return *this;
    }

    // 복사 생성자와 복사 대입 연산자는 삭제
    PoolPtr(const PoolPtr&) = delete;
    PoolPtr& operator=(const PoolPtr&) = delete;

    T* operator->() { return ptr_; }
    const T* operator->() const { return ptr_; }
    T& operator*() { return *ptr_; }
    const T& operator*() const { return *ptr_; }

    T* get() { return ptr_; }
    const T* get() const { return ptr_; }

    explicit operator bool() const { return ptr_ != nullptr; }

    void reset() {
        if (ptr_ && pool_) {
            pool_->Deallocate(ptr_);
            ptr_ = nullptr;
        }
    }
};

// 편의를 위한 팩토리 함수
template<typename T, typename... Args>
PoolPtr<T> MakePooled(MemoryPool<T>& pool, Args&&... args) {
    return PoolPtr<T>(&pool, std::forward<Args>(args)...);
}

} // namespace SemiconductorHMI::Memory

// 디버그 모드에서만 메모리 추적 활성화
#ifdef _DEBUG
#define TRACKED_MALLOC(size) SemiconductorHMI::Memory::MemoryManager::GetInstance().Allocate(size, __FILE__, __LINE__, __FUNCTION__)
#define TRACKED_FREE(ptr) SemiconductorHMI::Memory::MemoryManager::GetInstance().Deallocate(ptr)
#else
#define TRACKED_MALLOC(size) std::malloc(size)
#define TRACKED_FREE(ptr) std::free(ptr)
#endif
```

---

## 💡 **실전 프로젝트 확장 (30분) - 엔터프라이즈급 HMI 시스템**

### 7. 분산 시스템 통합

#### 7.1 마이크로서비스 아키텍처 연동
```cpp
// DistributedSystemClient.h
#pragma once
#include <string>
#include <vector>
#include <memory>
#include <future>
#include <functional>
#include <boost/asio.hpp>
#include <nlohmann/json.hpp>

namespace SemiconductorHMI::Distributed {

// RESTful API 클라이언트
class RestApiClient {
private:
    boost::asio::io_context io_context_;
    std::unique_ptr<std::thread> worker_thread_;
    std::string base_url_;
    std::string auth_token_;

public:
    RestApiClient(const std::string& base_url) : base_url_(base_url) {
        worker_thread_ = std::make_unique<std::thread>([this]() {
            io_context_.run();
        });
    }

    ~RestApiClient() {
        io_context_.stop();
        if (worker_thread_ && worker_thread_->joinable()) {
            worker_thread_->join();
        }
    }

    void SetAuthToken(const std::string& token) {
        auth_token_ = token;
    }

    std::future<nlohmann::json> GetAsync(const std::string& endpoint) {
        auto promise = std::make_shared<std::promise<nlohmann::json>>();
        auto future = promise->get_future();

        boost::asio::post(io_context_, [this, endpoint, promise]() {
            try {
                // HTTP GET 요청 수행 (실제 구현에서는 curl 또는 boost::beast 사용)
                nlohmann::json response = PerformHttpGet(base_url_ + endpoint);
                promise->set_value(response);
            } catch (const std::exception& e) {
                promise->set_exception(std::current_exception());
            }
        });

        return future;
    }

    std::future<nlohmann::json> PostAsync(const std::string& endpoint, const nlohmann::json& data) {
        auto promise = std::make_shared<std::promise<nlohmann::json>>();
        auto future = promise->get_future();

        boost::asio::post(io_context_, [this, endpoint, data, promise]() {
            try {
                nlohmann::json response = PerformHttpPost(base_url_ + endpoint, data);
                promise->set_value(response);
            } catch (const std::exception& e) {
                promise->set_exception(std::current_exception());
            }
        });

        return future;
    }

private:
    nlohmann::json PerformHttpGet(const std::string& url) {
        // HTTP GET 구현 (예시)
        // 실제로는 libcurl이나 boost::beast 사용
        nlohmann::json result;
        result["status"] = "success";
        result["data"] = nlohmann::json::array();
        return result;
    }

    nlohmann::json PerformHttpPost(const std::string& url, const nlohmann::json& data) {
        // HTTP POST 구현 (예시)
        nlohmann::json result;
        result["status"] = "success";
        result["message"] = "Data posted successfully";
        return result;
    }
};

// 마이크로서비스 관리자
class MicroserviceManager {
private:
    struct ServiceInfo {
        std::string name;
        std::string url;
        std::string version;
        bool is_healthy;
        std::chrono::time_point<std::chrono::steady_clock> last_health_check;
        std::unique_ptr<RestApiClient> client;
    };

    std::unordered_map<std::string, std::unique_ptr<ServiceInfo>> services_;
    std::thread health_check_thread_;
    std::atomic<bool> running_;

public:
    MicroserviceManager() : running_(true) {
        StartHealthCheckLoop();
    }

    ~MicroserviceManager() {
        running_ = false;
        if (health_check_thread_.joinable()) {
            health_check_thread_.join();
        }
    }

    void RegisterService(const std::string& name, const std::string& url, const std::string& version) {
        auto service = std::make_unique<ServiceInfo>();
        service->name = name;
        service->url = url;
        service->version = version;
        service->is_healthy = false;
        service->client = std::make_unique<RestApiClient>(url);

        services_[name] = std::move(service);
    }

    RestApiClient* GetServiceClient(const std::string& name) {
        auto it = services_.find(name);
        if (it != services_.end() && it->second->is_healthy) {
            return it->second->client.get();
        }
        return nullptr;
    }

    void ShowServiceStatusWindow() {
        if (ImGui::Begin("Microservice Status")) {

            if (ImGui::BeginTable("ServiceTable", 4, ImGuiTableFlags_Borders | ImGuiTableFlags_Resizable)) {
                ImGui::TableSetupColumn("Service");
                ImGui::TableSetupColumn("URL");
                ImGui::TableSetupColumn("Version");
                ImGui::TableSetupColumn("Status");
                ImGui::TableHeadersRow();

                for (const auto& [name, service] : services_) {
                    ImGui::TableNextRow();

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", service->name.c_str());

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", service->url.c_str());

                    ImGui::TableNextColumn();
                    ImGui::Text("%s", service->version.c_str());

                    ImGui::TableNextColumn();
                    if (service->is_healthy) {
                        ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(0.0f, 1.0f, 0.0f, 1.0f));
                        ImGui::Text("Healthy");
                        ImGui::PopStyleColor();
                    } else {
                        ImGui::PushStyleColor(ImGuiCol_Text, ImVec4(1.0f, 0.0f, 0.0f, 1.0f));
                        ImGui::Text("Unhealthy");
                        ImGui::PopStyleColor();
                    }
                }

                ImGui::EndTable();
            }

            // 서비스 등록 UI
            static char service_name[128] = "";
            static char service_url[256] = "";
            static char service_version[32] = "";

            ImGui::Separator();
            ImGui::Text("Register New Service");
            ImGui::InputText("Name", service_name, sizeof(service_name));
            ImGui::InputText("URL", service_url, sizeof(service_url));
            ImGui::InputText("Version", service_version, sizeof(service_version));

            if (ImGui::Button("Register Service")) {
                if (strlen(service_name) > 0 && strlen(service_url) > 0) {
                    RegisterService(service_name, service_url, service_version);

                    // 입력 필드 초기화
                    service_name[0] = '\0';
                    service_url[0] = '\0';
                    service_version[0] = '\0';
                }
            }
        }
        ImGui::End();
    }

private:
    void StartHealthCheckLoop() {
        health_check_thread_ = std::thread([this]() {
            while (running_) {
                for (auto& [name, service] : services_) {
                    CheckServiceHealth(*service);
                }

                std::this_thread::sleep_for(std::chrono::seconds(30)); // 30초마다 헬스 체크
            }
        });
    }

    void CheckServiceHealth(ServiceInfo& service) {
        try {
            auto future = service.client->GetAsync("/health");
            auto status = future.wait_for(std::chrono::seconds(5));

            if (status == std::future_status::ready) {
                auto response = future.get();
                service.is_healthy = (response["status"] == "healthy");
            } else {
                service.is_healthy = false;
            }
        } catch (const std::exception&) {
            service.is_healthy = false;
        }

        service.last_health_check = std::chrono::steady_clock::now();
    }
};

} // namespace SemiconductorHMI::Distributed
```

#### 7.2 실시간 데이터 동기화 시스템
```cpp
// DataSynchronization.h
#pragma once
#include <vector>
#include <memory>
#include <atomic>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <functional>

namespace SemiconductorHMI::Sync {

// 데이터 변경 이벤트
struct DataChangeEvent {
    std::string entity_type;
    std::string entity_id;
    std::string change_type; // "create", "update", "delete"
    nlohmann::json data;
    std::chrono::time_point<std::chrono::system_clock> timestamp;
};

// 데이터 동기화 관리자
class DataSynchronizationManager {
private:
    std::queue<DataChangeEvent> event_queue_;
    std::mutex queue_mutex_;
    std::condition_variable queue_cv_;
    std::atomic<bool> running_;
    std::thread worker_thread_;

    std::vector<std::function<void(const DataChangeEvent&)>> event_handlers_;
    std::mutex handlers_mutex_;

    // 충돌 해결 전략
    enum class ConflictResolution {
        LAST_WRITE_WINS,
        FIRST_WRITE_WINS,
        MERGE_CHANGES,
        USER_DECISION
    };

    ConflictResolution conflict_resolution_ = ConflictResolution::LAST_WRITE_WINS;

public:
    DataSynchronizationManager() : running_(true) {
        worker_thread_ = std::thread(&DataSynchronizationManager::ProcessEvents, this);
    }

    ~DataSynchronizationManager() {
        running_ = false;
        queue_cv_.notify_all();
        if (worker_thread_.joinable()) {
            worker_thread_.join();
        }
    }

    void PublishChange(const DataChangeEvent& event) {
        std::lock_guard<std::mutex> lock(queue_mutex_);
        event_queue_.push(event);
        queue_cv_.notify_one();
    }

    void Subscribe(std::function<void(const DataChangeEvent&)> handler) {
        std::lock_guard<std::mutex> lock(handlers_mutex_);
        event_handlers_.push_back(handler);
    }

    void SetConflictResolution(ConflictResolution strategy) {
        conflict_resolution_ = strategy;
    }

    void ShowSyncStatusWindow() {
        if (ImGui::Begin("Data Synchronization")) {

            // 큐 상태
            {
                std::lock_guard<std::mutex> lock(queue_mutex_);
                ImGui::Text("Pending Events: %zu", event_queue_.size());
            }

            // 핸들러 수
            {
                std::lock_guard<std::mutex> lock(handlers_mutex_);
                ImGui::Text("Active Handlers: %zu", event_handlers_.size());
            }

            ImGui::Separator();

            // 충돌 해결 전략 설정
            const char* resolution_names[] = {
                "Last Write Wins",
                "First Write Wins",
                "Merge Changes",
                "User Decision"
            };

            int current_resolution = static_cast<int>(conflict_resolution_);
            if (ImGui::Combo("Conflict Resolution", &current_resolution, resolution_names, 4)) {
                conflict_resolution_ = static_cast<ConflictResolution>(current_resolution);
            }

            // 수동 동기화 트리거
            if (ImGui::Button("Force Sync All")) {
                TriggerFullSync();
            }

            ImGui::SameLine();
            if (ImGui::Button("Clear Queue")) {
                ClearEventQueue();
            }
        }
        ImGui::End();
    }

private:
    void ProcessEvents() {
        while (running_) {
            std::unique_lock<std::mutex> lock(queue_mutex_);
            queue_cv_.wait(lock, [this] { return !event_queue_.empty() || !running_; });

            if (!running_) break;

            if (!event_queue_.empty()) {
                DataChangeEvent event = event_queue_.front();
                event_queue_.pop();
                lock.unlock();

                // 이벤트 처리
                ProcessSingleEvent(event);
            }
        }
    }

    void ProcessSingleEvent(const DataChangeEvent& event) {
        std::lock_guard<std::mutex> lock(handlers_mutex_);

        for (const auto& handler : event_handlers_) {
            try {
                handler(event);
            } catch (const std::exception& e) {
                // 로그 기록
            }
        }
    }

    void TriggerFullSync() {
        // 전체 데이터 동기화 로직
        DataChangeEvent sync_event;
        sync_event.entity_type = "system";
        sync_event.entity_id = "full_sync";
        sync_event.change_type = "sync";
        sync_event.timestamp = std::chrono::system_clock::now();

        PublishChange(sync_event);
    }

    void ClearEventQueue() {
        std::lock_guard<std::mutex> lock(queue_mutex_);
        while (!event_queue_.empty()) {
            event_queue_.pop();
        }
    }
};

// 데이터 엔티티 베이스 클래스
class SyncableEntity {
private:
    std::string entity_id_;
    std::string entity_type_;
    std::chrono::time_point<std::chrono::system_clock> last_modified_;
    uint64_t version_;

protected:
    DataSynchronizationManager* sync_manager_;

public:
    SyncableEntity(const std::string& type, const std::string& id, DataSynchronizationManager* sync_manager)
        : entity_type_(type), entity_id_(id), sync_manager_(sync_manager), version_(0) {
        last_modified_ = std::chrono::system_clock::now();
    }

    virtual ~SyncableEntity() = default;

    void MarkModified() {
        last_modified_ = std::chrono::system_clock::now();
        version_++;

        if (sync_manager_) {
            DataChangeEvent event;
            event.entity_type = entity_type_;
            event.entity_id = entity_id_;
            event.change_type = "update";
            event.data = ToJson();
            event.timestamp = last_modified_;

            sync_manager_->PublishChange(event);
        }
    }

    virtual nlohmann::json ToJson() const = 0;
    virtual void FromJson(const nlohmann::json& data) = 0;

    const std::string& GetEntityId() const { return entity_id_; }
    const std::string& GetEntityType() const { return entity_type_; }
    uint64_t GetVersion() const { return version_; }
    auto GetLastModified() const { return last_modified_; }
};

// 예시: 동기화 가능한 센서 데이터
class SyncableSensorData : public SyncableEntity {
private:
    float temperature_;
    float pressure_;
    float flow_rate_;
    bool is_active_;

public:
    SyncableSensorData(const std::string& sensor_id, DataSynchronizationManager* sync_manager)
        : SyncableEntity("sensor_data", sensor_id, sync_manager)
        , temperature_(0.0f), pressure_(0.0f), flow_rate_(0.0f), is_active_(false) {}

    void SetTemperature(float temp) {
        if (temperature_ != temp) {
            temperature_ = temp;
            MarkModified();
        }
    }

    void SetPressure(float press) {
        if (pressure_ != press) {
            pressure_ = press;
            MarkModified();
        }
    }

    void SetFlowRate(float flow) {
        if (flow_rate_ != flow) {
            flow_rate_ = flow;
            MarkModified();
        }
    }

    void SetActive(bool active) {
        if (is_active_ != active) {
            is_active_ = active;
            MarkModified();
        }
    }

    nlohmann::json ToJson() const override {
        nlohmann::json json;
        json["temperature"] = temperature_;
        json["pressure"] = pressure_;
        json["flow_rate"] = flow_rate_;
        json["is_active"] = is_active_;
        json["version"] = GetVersion();
        return json;
    }

    void FromJson(const nlohmann::json& data) override {
        if (data.contains("temperature")) temperature_ = data["temperature"];
        if (data.contains("pressure")) pressure_ = data["pressure"];
        if (data.contains("flow_rate")) flow_rate_ = data["flow_rate"];
        if (data.contains("is_active")) is_active_ = data["is_active"];
    }

    float GetTemperature() const { return temperature_; }
    float GetPressure() const { return pressure_; }
    float GetFlowRate() const { return flow_rate_; }
    bool IsActive() const { return is_active_; }
};

} // namespace SemiconductorHMI::Sync
```

---

## 🎯 **최종 정리 및 심화 학습 방향**

### 8. Week 12 완성도 검증 및 확장 방안

#### 8.1 학습 내용 체크리스트
- ✅ 플러그인 아키텍처 설계 및 구현
- ✅ 동적 라이브러리 로딩 시스템
- ✅ 고급 데이터 시각화 엔진
- ✅ 멀티스레딩 렌더링 시스템
- ✅ 국제화 및 접근성 지원
- ✅ 외부 시스템 통합 (MQTT, OPC-UA)
- ✅ 커스텀 렌더링 파이프라인
- ✅ 성능 프로파일링 도구
- ✅ 고급 메모리 관리 시스템
- ✅ 분산 시스템 연동
- ✅ 실시간 데이터 동기화

#### 8.2 실무 적용을 위한 추가 고려사항

**보안 강화**
```cpp
// 보안 관련 추가 구현 방향
namespace SemiconductorHMI::Security {
    class SecurityManager {
        // - SSL/TLS 통신 암호화
        // - 사용자 인증 및 권한 관리
        // - 데이터 무결성 검증
        // - 감사 로그 시스템
        // - 침입 탐지 시스템
    };
}
```

**배포 및 운영**
```cpp
namespace SemiconductorHMI::Deployment {
    class DeploymentManager {
        // - 자동 업데이트 시스템
        // - 설정 관리 (환경별)
        // - 헬스 체크 및 모니터링
        // - 로그 수집 및 분석
        // - 장애 복구 시스템
    };
}
```

**확장성 고려사항**
- 수평적 확장 (Load Balancing)
- 데이터베이스 샤딩
- 캐싱 전략 (Redis, Memcached)
- 메시지 큐 시스템 (RabbitMQ, Apache Kafka)
- 클라우드 네이티브 아키텍처 (Kubernetes, Docker)
- 실제 반도체 팹 환경 시뮬레이션
